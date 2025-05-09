from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from ..models import TechnicalScreener, Stock, StockPrice, ScreenerCondition
import json
import logging
from django.db.utils import OperationalError
from django.db import transaction

logger = logging.getLogger(__name__)

def create_screener_with_conditions(user, name, description, visibility, conditions):
    """
    Utility function to create a screener with its conditions.
    
    Args:
        user: The user creating the screener
        name: Screener name
        description: Screener description
        visibility: 'public' or 'private'
        conditions: List of condition dictionaries, each containing:
            - condition: dict with condition details
            - order: int for condition order
    
    Returns:
        tuple: (screener, list of created conditions)
    """
    with transaction.atomic():
        # Create the screener
        screener = TechnicalScreener.objects.create(
            name=name,
            description=description,
            created_by=user,
            is_global=(visibility == 'public')
        )
        
        # Create conditions
        created_conditions = []
        for condition_data in conditions:
            condition = ScreenerCondition.objects.create(
                screener=screener,
                condition=condition_data.get('condition', {}),
                order=condition_data.get('order', 0)
            )
            created_conditions.append(condition)
        
        return screener, created_conditions

def validate_condition(condition):
    """
    Validate a condition dictionary.
    
    Args:
        condition: dict containing condition details
    
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['indicator', 'operator', 'value']
    for field in required_fields:
        if field not in condition:
            return False, f"Missing required field: {field}"
    
    valid_operators = ['>', '<', '=', '>=', '<=', '!=']
    if condition['operator'] not in valid_operators:
        return False, f"Invalid operator: {condition['operator']}"
    
    try:
        float(condition['value'])
    except (ValueError, TypeError):
        return False, "Value must be a number"
    
    return True, None

@login_required
def screener_list(request):
    # Do not access the database at all if the table might not exist
    context = {
        'personal_screeners': [],
        'global_screeners': [],
        'db_unavailable': True,  # flag for the template to show only the create button
    }
    return render(request, 'technical/screener_list.html', context)

@login_required
def create_screener(request):
    """Create a new technical screener"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')
            conditions = data.get('conditions', [])  # Changed to expect list
            visibility = data.get('visibility', 'private')
            
            if not name:
                return JsonResponse({
                    'success': False,
                    'message': 'Screener name is required'
                }, status=400)
            
            if not conditions:
                return JsonResponse({
                    'success': False,
                    'message': 'At least one condition is required'
                }, status=400)
            
            # Validate conditions
            for condition_data in conditions:
                is_valid, error_message = validate_condition(condition_data.get('condition', {}))
                if not is_valid:
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    }, status=400)
            
            # Create screener and conditions
            screener, created_conditions = create_screener_with_conditions(
                request.user, name, description, visibility, conditions
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Screener created successfully',
                'screener': {
                    'id': screener.id,
                    'name': screener.name,
                    'description': screener.description,
                    'is_global': screener.is_global,
                    'created_at': screener.created_at,
                    'updated_at': screener.updated_at,
                    'conditions': [{
                        'id': cond.id,
                        'condition': cond.condition,
                        'order': cond.order
                    } for cond in created_conditions]
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error creating screener: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Error creating screener'
            }, status=500)
    
    return render(request, 'technical/create_screener.html')

@login_required
def screener_detail(request, screener_id):
    """View details of a specific screener"""
    screener = get_object_or_404(TechnicalScreener, id=screener_id)
    
    # Check if user has access to this screener
    if not screener.is_global and screener.created_by != request.user:
        messages.error(request, 'You do not have access to this screener')
        return redirect('dashboard:technical:screener_list')
    
    context = {
        'screener': screener,
        'is_owner': screener.created_by == request.user,
        'is_subscriber': request.user in screener.subscribers.all()
    }
    
    return render(request, 'technical/screener_detail.html', context)

@login_required
def run_screener(request, screener_id):
    """Run the screener and return matching stocks"""
    screener = get_object_or_404(TechnicalScreener, id=screener_id)
    
    try:
        # Get the conditions from the screener
        conditions = screener.conditions
        
        # Start with all stocks
        stocks = Stock.objects.all()
        
        # Apply each condition
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            # Get the latest price data for each stock
            latest_prices = StockPrice.objects.filter(
                stock__in=stocks
            ).order_by('stock', '-date').distinct('stock')
            
            # Filter based on the condition
            if field in ['open', 'high', 'low', 'close', 'volume']:
                if operator == '>':
                    stocks = stocks.filter(
                        stockprice__in=latest_prices,
                        **{f'stockprice__{field}__gt': value}
                    )
                elif operator == '<':
                    stocks = stocks.filter(
                        stockprice__in=latest_prices,
                        **{f'stockprice__{field}__lt': value}
                    )
                elif operator == '=':
                    stocks = stocks.filter(
                        stockprice__in=latest_prices,
                        **{f'stockprice__{field}': value}
                    )
        
        # Get the latest price data for the filtered stocks
        results = []
        for stock in stocks:
            latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
            if latest_price:
                results.append({
                    'stock': stock,
                    'latest_price': latest_price
                })
        
        return JsonResponse({
            'success': True,
            'results': [{
                'symbol': r['stock'].symbol,
                'name': r['stock'].name,
                'sector': r['stock'].sector,
                'open': r['latest_price'].open_price,
                'high': r['latest_price'].high_price,
                'low': r['latest_price'].low_price,
                'close': r['latest_price'].close_price,
                'volume': r['latest_price'].volume,
                'date': r['latest_price'].date
            } for r in results]
        })
        
    except Exception as e:
        logger.error(f"Error running screener: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error running screener'
        }, status=500)

@login_required
def delete_screener(request, screener_id):
    """Delete a screener"""
    screener = get_object_or_404(TechnicalScreener, id=screener_id, created_by=request.user)
    
    if request.method == 'POST':
        screener.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def subscribe_screener(request, screener_id):
    """Subscribe to a screener"""
    screener = get_object_or_404(TechnicalScreener, id=screener_id)
    
    if request.method == 'POST':
        screener.subscribers.add(request.user)
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def unsubscribe_screener(request, screener_id):
    """Unsubscribe from a screener"""
    screener = get_object_or_404(TechnicalScreener, id=screener_id)
    
    if request.method == 'POST':
        screener.subscribers.remove(request.user)
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def create_technical_screener_api(request):
    """API endpoint to create a new technical screener"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name')
        description = data.get('description', '')
        visibility = data.get('visibility', 'private')
        conditions = data.get('conditions', [])
        
        if not name:
            return JsonResponse({'error': 'Screener name is required'}, status=400)
        
        if not conditions:
            return JsonResponse({'error': 'At least one condition is required'}, status=400)
        
        # Validate conditions
        for condition_data in conditions:
            is_valid, error_message = validate_condition(condition_data.get('condition', {}))
            if not is_valid:
                return JsonResponse({
                    'error': error_message
                }, status=400)
        
        # Create screener and conditions
        screener, created_conditions = create_screener_with_conditions(
            request.user, name, description, visibility, conditions
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Technical screener created successfully',
            'screener': {
                'id': screener.id,
                'name': screener.name,
                'description': screener.description,
                'is_global': screener.is_global,
                'created_at': screener.created_at,
                'updated_at': screener.updated_at,
                'conditions': [{
                    'id': cond.id,
                    'condition': cond.condition,
                    'order': cond.order
                } for cond in created_conditions]
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error creating technical screener: {str(e)}")
        return JsonResponse({'error': 'Error creating technical screener'}, status=500)

@login_required
def get_technical_screeners(request):
    """API endpoint to get all technical screeners"""
    try:
        # Get personal screeners
        personal_screeners = TechnicalScreener.objects.filter(
            created_by=request.user,
            is_global=False
        ).prefetch_related('conditions')
        
        # Get global screeners
        global_screeners = TechnicalScreener.objects.filter(
            is_global=True
        ).prefetch_related('conditions')
        
        data = {
            'personal': [{
                'id': scr.id,
                'name': scr.name,
                'description': scr.description,
                'is_global': scr.is_global,
                'created_at': scr.created_at,
                'updated_at': scr.updated_at,
                'conditions': [{
                    'id': cond.id,
                    'condition': cond.condition,
                    'order': cond.order
                } for cond in scr.conditions.all().order_by('order')]
            } for scr in personal_screeners],
            'global': [{
                'id': scr.id,
                'name': scr.name,
                'description': scr.description,
                'is_global': scr.is_global,
                'created_at': scr.created_at,
                'updated_at': scr.updated_at,
                'conditions': [{
                    'id': cond.id,
                    'condition': cond.condition,
                    'order': cond.order
                } for cond in scr.conditions.all().order_by('order')]
            } for scr in global_screeners]
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error getting technical screeners: {str(e)}")
        return JsonResponse({'error': 'Error getting technical screeners'}, status=500)

@login_required
def delete_technical_screener(request, screener_id):
    """API endpoint to delete a technical screener"""
    screener = get_object_or_404(TechnicalScreener, id=screener_id, created_by=request.user)
    if request.method == 'POST':
        screener.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def edit_technical_screener(request, screener_id):
    """API endpoint to edit a technical screener"""
    screener = get_object_or_404(TechnicalScreener, id=screener_id, created_by=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')
            visibility = data.get('visibility', 'private')
            conditions = data.get('conditions', [])
            
            if not name:
                return JsonResponse({'error': 'Screener name is required'}, status=400)
            
            # Update screener details
            screener.name = name
            screener.description = description
            screener.is_global = (visibility == 'public')
            screener.save()
            
            # Update conditions
            # First, delete existing conditions
            screener.conditions.all().delete()
            
            # Then create new conditions
            for condition_data in conditions:
                ScreenerCondition.objects.create(
                    screener=screener,
                    condition=condition_data.get('condition', {}),
                    order=condition_data.get('order', 0)
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Technical screener updated successfully',
                'screener': {
                    'id': screener.id,
                    'name': screener.name,
                    'description': screener.description,
                    'is_global': screener.is_global,
                    'created_at': screener.created_at,
                    'updated_at': screener.updated_at,
                    'conditions': [{
                        'id': condition.id,
                        'condition': condition.condition,
                        'order': condition.order
                    } for condition in screener.conditions.all().order_by('order')]
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Error updating technical screener: {str(e)}")
            return JsonResponse({'error': 'Error updating technical screener'}, status=500)
    
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405) 