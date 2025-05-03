from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from ..models import Watchlist, Stock, StockPrice, WatchlistColumn, WatchlistDisplaySettings
from django.template.loader import render_to_string
import logging
import json

logger = logging.getLogger(__name__)

@login_required
def watchlist_detail(request, watchlist_id):
    print("\n=== DEBUG: watchlist_detail view in watchlist/views.py is being called ===")
    print("View: watchlist_detail")
    print("Function: watchlist_detail")
    print("Template: watchlist_detail.html")
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, created_by=request.user)
    
    # Get all stocks with their latest prices
    stocks = watchlist.stocks.all().order_by('symbol')
    stocks_with_prices = []
    
    for stock in stocks:
        # Get the latest price data for this stock
        latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
        
        # Calculate price change and percentage if we have data
        price = 0
        open_price = 0
        high_price = 0
        low_price = 0
        change = 0
        change_percentage = 0
        volume = 0
        date_str = "N/A"
        
        if latest_price:
            price = latest_price.close_price
            open_price = latest_price.open_price
            high_price = latest_price.high_price
            low_price = latest_price.low_price
            
            # Get the previous day's price to calculate change
            previous_price = StockPrice.objects.filter(
                stock=stock, 
                date__lt=latest_price.date
            ).order_by('-date').first()
            
            if previous_price:
                change = price - previous_price.close_price
                change_percentage = (change / previous_price.close_price) * 100 if previous_price.close_price > 0 else 0
            
            volume = latest_price.volume
            date_str = latest_price.date.strftime("%Y-%m-%d")
        
        stock_data = {
            'stock': stock,
            'latest_price': {
                'price': price,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'change': change,
                'change_percentage': change_percentage,
                'volume': volume,
                'date': date_str
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
        return render(request, 'watchlist/watchlist_detail_content.html', context)
    
    return render(request, 'watchlist/watchlist_detail.html', context)

@login_required
def create_watchlist(request):
    print("\n=== DEBUG: create_watchlist view called ===")
    print(f"Request method: {request.method}")
    print(f"User: {request.user}")
    print(f"Request path: {request.path}")
    if request.method == 'GET':
        # Get all stocks for the create watchlist form
        stocks = Stock.objects.all().order_by('symbol')
        
        # Get all watchlist columns
        watchlist_columns = WatchlistColumn.objects.filter(
            is_active=True
        ).order_by('order')
        
        # Print watchlist columns for debugging
        print("\n=== Watchlist Columns Debug ===")
        print("Active Watchlist Columns:")
        for column in watchlist_columns:
            print(f"  - ID: {column.id}")
            print(f"    Name: {column.name}")
            print(f"    Display Name: {column.display_name}")
            print(f"    Type: {column.column_type}")
            print(f"    Order: {column.order}")
            print(f"    Required: {column.is_required}")
            print("    ---")
        
        print("\n=== DEBUG: Rendering create watchlist form ===")
        print(f"Total stocks available: {stocks.count()}")
        print(f"Total columns available: {watchlist_columns.count()}")
        
        context = {
            'stocks': stocks,
            'watchlist_columns': watchlist_columns,
        }
        return render(request, 'watchlist/edit_watchlist_content.html', context)
    
    elif request.method == 'POST':
        print("\n=== DEBUG: Processing POST to create_watchlist ===")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        stocks = request.POST.getlist('stocks')
        print(f"Parsed name: {name}")
        print(f"Parsed description: {description}")
        print(f"Parsed stocks: {stocks}")
        if not name:
            print("ERROR: No name provided!")
            return JsonResponse({'success': False, 'message': 'Watchlist name is required.'})
        if not stocks:
            print("ERROR: No stocks selected!")
            return JsonResponse({'success': False, 'message': 'Please select at least one stock.'})
        try:
            print("Attempting to create Watchlist object...")
            watchlist = Watchlist.objects.create(
                created_by=request.user,
                name=name,
                description=description
            )
            print(f"Watchlist created: {watchlist} (ID: {watchlist.id})")
            for stock_id in stocks:
                print(f"Adding stock ID: {stock_id}")
                stock = Stock.objects.get(id=stock_id)
                watchlist.stocks.add(stock)
            print(f"All stocks added to watchlist {watchlist.id}")
            print("Returning success JsonResponse...")
            return JsonResponse({
                'success': True,
                'message': 'Watchlist created successfully!',
                'redirect_url': f'/dashboard/watchlist/{watchlist.id}/'
            })
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
            
    print("ERROR: Invalid request method!")
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

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
    print("\n=== DEBUG: edit_watchlist view in watchlist/views.py is being called ===")
    print(f"Request method: {request.method}")
    print(f"User: {request.user}")
    print(f"Request path: {request.path}")
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, created_by=request.user)
    print(f"Watchlist object: {watchlist} (ID: {watchlist.id})")
    
    if request.method == 'GET':
        print("\n=== DEBUG: Rendering edit watchlist form ===")
        # Get all stocks for the edit form
        stocks = Stock.objects.all().order_by('symbol')
        print(f"Total stocks available: {stocks.count()}")
        context = {
            'watchlist': watchlist,
            'stocks': stocks,
        }
        return render(request, 'watchlist/edit_watchlist_content.html', context)
    
    elif request.method == 'POST':
        print("\n=== DEBUG: Processing POST to edit_watchlist ===")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        name = request.POST.get('name')
        description = request.POST.get('description')
        visibility = request.POST.get('visibility', 'private')
        stock_ids = request.POST.getlist('stocks')
        print(f"Parsed name: {name}")
        print(f"Parsed description: {description}")
        print(f"Parsed visibility: {visibility}")
        print(f"Parsed stock_ids: {stock_ids}")
        try:
            # Update watchlist details
            watchlist.name = name
            watchlist.description = description
            watchlist.is_global = (visibility == 'public')
            watchlist.save()
            print(f"Watchlist updated: {watchlist} (ID: {watchlist.id})")
            # Update stocks
            stocks = Stock.objects.filter(id__in=stock_ids)
            watchlist.stocks.set(stocks)
            print(f"Stocks set for watchlist {watchlist.id}: {[s.id for s in stocks]}")
            print("Returning success JsonResponse...")
            return JsonResponse({
                'success': True,
                'message': 'Watchlist updated successfully',
                'redirect_url': reverse('dashboard:watchlist:detail', kwargs={'watchlist_id': watchlist.id})
            })
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            logger.error(f"Error updating watchlist: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Failed to update watchlist'
            }, status=500)

@login_required
def watchlist(request):
    print("\n=== DEBUG: watchlist view in watchlist/views.py is being called ===")
    print("View: watchlist")
    print("Function: watchlist")
    print("Template: watchlist.html")
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
    
    return render(request, 'watchlist/watchlist.html', context)
