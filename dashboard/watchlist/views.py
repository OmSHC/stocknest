from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from ..models import Watchlist, Stock
from django.template.loader import render_to_string
import logging
import json

logger = logging.getLogger(__name__)

@login_required
def watchlist(request):
    # Get user's personal watchlists
    personal_watchlists = Watchlist.objects.filter(
        created_by=request.user,
        is_global=False
    ).prefetch_related('stocks')
    
    # Get all stocks for the create watchlist modal
    stocks = Stock.objects.all().order_by('symbol')
    
    context = {
        'personal_watchlists': personal_watchlists,
        'stocks': stocks,
    }
    
    return render(request, 'dashboard/watchlist.html', context)

@login_required
def watchlist_detail(request, watchlist_id):
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, created_by=request.user)
    
    # Get all stocks with their latest prices
    stocks = watchlist.stocks.all().order_by('symbol')
    stocks_with_prices = []
    
    for stock in stocks:
        stock_data = {
            'stock': stock,
            'latest_price': {
                'price': 0,
                'change': 0,
                'change_percentage': 0,
                'volume': 0
            }
        }
        stocks_with_prices.append(stock_data)
    
    context = {
        'watchlist': watchlist,
        'stocks_with_prices': stocks_with_prices,
        'is_owner': watchlist.created_by == request.user,
        'is_subscriber': request.user in watchlist.subscribers.all(),
        'total_stocks': len(stocks_with_prices)
    }
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'dashboard/watchlist_detail_content.html', context)
    
    return render(request, 'dashboard/watchlist_detail.html', context)

@login_required
def create_watchlist(request):
    """Handle watchlist creation"""
    if request.method == 'GET':
        # Get all stocks for the create watchlist form
        stocks = Stock.objects.all().order_by('symbol')
        context = {
            'stocks': stocks,
        }
        return render(request, 'watchlist/create_watchlist_content.html', context)
    
    elif request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        visibility = request.POST.get('visibility', 'private')
        stock_ids = request.POST.getlist('stocks')
        
        # Debug prints
        print("\n=== Create Watchlist Debug ===")
        print(f"1. Form Data:")
        print(f"   - Name: {name}")
        print(f"   - Description: {description}")
        print(f"   - Visibility: {visibility}")
        print(f"   - Stock IDs: {stock_ids}")
        
        try:
            watchlist = Watchlist.objects.create(
                name=name,
                description=description,
                created_by=request.user,
                is_global=(visibility == 'public')
            )
            
            print(f"\n2. Watchlist Created:")
            print(f"   - ID: {watchlist.id}")
            print(f"   - Name: {watchlist.name}")
            
            # Add selected stocks
            stocks = Stock.objects.filter(id__in=stock_ids)
            print(f"\n3. Found Stocks:")
            for stock in stocks:
                print(f"   - ID: {stock.id}")
                print(f"   - Symbol: {stock.symbol}")
                print(f"   - Name: {stock.name}")
            
            watchlist.stocks.add(*stocks)
            
            # Verify stocks were added
            print(f"\n4. Verifying Saved Stocks:")
            saved_stocks = watchlist.stocks.all()
            for stock in saved_stocks:
                print(f"   - ID: {stock.id}")
                print(f"   - Symbol: {stock.symbol}")
                print(f"   - Name: {stock.name}")
            
            # If it's an AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Watchlist created successfully',
                    'redirect_url': reverse('dashboard:watchlist:detail', kwargs={'watchlist_id': watchlist.id})
                })
            
            # For regular form submission, redirect to the watchlist detail page
            return redirect('dashboard:watchlist:detail', watchlist_id=watchlist.id)
            
        except Exception as e:
            print(f"\n5. Error creating watchlist: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            messages.error(request, str(e))
            return redirect('dashboard:watchlist:list')
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def create_watchlist_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name')
        description = data.get('description')
        visibility = data.get('visibility', 'private')
        
        if not name:
            return JsonResponse({'error': 'Watchlist name is required'}, status=400)
        
        # Create the watchlist
        watchlist = Watchlist.objects.create(
            name=name,
            description=description,
            created_by=request.user,
            is_global=(visibility == 'public')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Watchlist created successfully',
            'watchlist': {
                'id': watchlist.id,
                'name': watchlist.name,
                'description': watchlist.description,
                'is_global': watchlist.is_global,
                'created_at': watchlist.created_at,
                'updated_at': watchlist.updated_at
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error creating watchlist: {str(e)}")
        return JsonResponse({'error': 'Error creating watchlist'}, status=500)

@login_required
def get_watchlists(request):
    try:
        # Get personal watchlists
        personal_watchlists = Watchlist.objects.filter(
            created_by=request.user,
            is_global=False
        ).prefetch_related('stocks')
        
        # Get global watchlists
        global_watchlists = Watchlist.objects.filter(
            is_global=True
        ).prefetch_related('stocks')
        
        data = {
            'personal': [{
                'id': wl.id,
                'name': wl.name,
                'description': wl.description,
                'is_global': wl.is_global,
                'created_at': wl.created_at,
                'updated_at': wl.updated_at,
                'stocks': [{
                    'id': stock.id,
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'sector': stock.sector
                } for stock in wl.stocks.all()]
            } for wl in personal_watchlists],
            'global': [{
                'id': wl.id,
                'name': wl.name,
                'description': wl.description,
                'is_global': wl.is_global,
                'created_at': wl.created_at,
                'updated_at': wl.updated_at,
                'stocks': [{
                    'id': stock.id,
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'sector': stock.sector
                } for stock in wl.stocks.all()]
            } for wl in global_watchlists]
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error getting watchlists: {str(e)}")
        return JsonResponse({'error': 'Error getting watchlists'}, status=500)

@login_required
def delete_watchlist(request, watchlist_id):
    """Delete watchlist"""
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, created_by=request.user)
    if request.method == 'POST':
        watchlist.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def add_stock_to_watchlist(request, watchlist_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        watchlist = get_object_or_404(Watchlist, id=watchlist_id)
        
        # Check if user owns the watchlist
        if watchlist.created_by != request.user:
            return JsonResponse({'error': 'You do not have permission to modify this watchlist'}, status=403)
        
        data = json.loads(request.body)
        stock_id = data.get('stock_id')
        
        if not stock_id:
            return JsonResponse({'error': 'Stock ID is required'}, status=400)
        
        stock = get_object_or_404(Stock, id=stock_id)
        watchlist.stocks.add(stock)
        
        return JsonResponse({
            'success': True,
            'message': f'{stock.symbol} added to watchlist successfully'
        })
        
    except Exception as e:
        logger.error(f"Error adding stock to watchlist: {str(e)}")
        return JsonResponse({'error': 'Error adding stock to watchlist'}, status=500)

@login_required
def remove_stock_from_watchlist(request, watchlist_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        watchlist = get_object_or_404(Watchlist, id=watchlist_id)
        
        # Check if user owns the watchlist
        if watchlist.created_by != request.user:
            return JsonResponse({'error': 'You do not have permission to modify this watchlist'}, status=403)
        
        data = json.loads(request.body)
        symbol = data.get('symbol')
        
        if not symbol:
            return JsonResponse({'error': 'Stock symbol is required'}, status=400)
        
        stock = get_object_or_404(Stock, symbol=symbol)
        watchlist.stocks.remove(stock)
        
        return JsonResponse({
            'success': True,
            'message': f'{symbol} removed from watchlist successfully'
        })
        
    except Exception as e:
        logger.error(f"Error removing stock from watchlist: {str(e)}")
        return JsonResponse({'error': 'Error removing stock from watchlist'}, status=500)

@login_required
def edit_watchlist(request, watchlist_id):
    """Handle watchlist editing"""
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, created_by=request.user)
    
    if request.method == 'GET':
        # Get all stocks for the edit form
        stocks = Stock.objects.all().order_by('symbol')
        context = {
            'watchlist': watchlist,
            'stocks': stocks,
        }
        return render(request, 'dashboard/edit_watchlist_content.html', context)
    
    elif request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        visibility = request.POST.get('visibility', 'private')
        stock_ids = request.POST.getlist('stocks')
        
        try:
            # Update watchlist details
            watchlist.name = name
            watchlist.description = description
            watchlist.is_global = (visibility == 'public')
            watchlist.save()
            
            # Update stocks
            stocks = Stock.objects.filter(id__in=stock_ids)
            watchlist.stocks.set(stocks)
            
            return JsonResponse({
                'success': True,
                'message': 'Watchlist updated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error updating watchlist: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Failed to update watchlist'
            }, status=500)
