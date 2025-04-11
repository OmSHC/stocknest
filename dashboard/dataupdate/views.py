from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from ..models import Watchlist, Stock, StockPrice
from django.template.loader import render_to_string
import logging
import json
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

@login_required
def watchlist(request):
    print("\n=== DEBUG: watchlist view in dataupdate/views.py is being called ===")
    print("View: watchlist")
    print("Function: watchlist")
    print("Template: dataupdate.html")
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
    
    return render(request, 'dataupdate/dataupdate.html', context)

@login_required
def watchlist_detail(request, watchlist_id):
    print("\n=== DEBUG: watchlist_detail view in dataupdate/views.py is being called ===")
    print("View: watchlist_detail")
    print("Function: watchlist_detail")
    print("Template: dataupdate_watchlist_detail.html")
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
        return render(request, 'dataupdate/watchlist_detail_content.html', context)
    
    return render(request, 'dataupdate/watchlist_detail.html', context)

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
        return render(request, 'watchlist/edit_watchlist_content.html', context)
    
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

@login_required
def dataupdate(request):
    """Render the data update dashboard."""
    print("\n=== DEBUG: dataupdate view in dataupdate/views.py is being called ===")
    print("View: dataupdate")
    print("Function: dataupdate")
    print("Template: dataupdate.html")
    try:
        # Get all stocks for the data update page
        stocks = Stock.objects.all().order_by('symbol')
        
        context = {
            'stocks': stocks,
            'page_title': 'Data Update',
            'active_section': 'dataupdate'
        }
        
        logger.info(f"Rendering data update page with {len(stocks)} stocks")
        return render(request, 'dataupdate/dataupdate.html', context)
        
    except Exception as e:
        logger.error(f"Error in dataupdate view: {str(e)}")
        messages.error(request, 'Error loading data update page')
        return redirect('dashboard:index')

def fetch_stock_data(symbol, start_date=None, end_date=None):
    """
    Fetch stock data from Yahoo Finance with proper error handling and date management.
    
    Args:
        symbol (str): Stock symbol
        start_date (datetime.date, optional): Start date for data fetch. Defaults to None.
        end_date (datetime.date, optional): End date for data fetch. Defaults to None.
    
    Returns:
        tuple: (success (bool), message (str), data (pd.DataFrame or None))
    """
    try:
        # Set default dates if not provided
        if end_date is None:
            end_date = datetime.now().date()
        if start_date is None:
            start_date = end_date - timedelta(days=400)
            
        print(f"Fetching data for {symbol} from {start_date} to {end_date}")
        
        # Try with .NS suffix first
        yahoo_symbol = f"{symbol}.NS"
        print(f"Creating Ticker object for {yahoo_symbol}")
        ticker = yf.Ticker(yahoo_symbol)
        
        # Fetch historical data
        print(f"Fetching historical data from {start_date} to {end_date}")
        data = yf.download(yahoo_symbol, start=start_date, end=end_date, progress=False)
        
        # If no data with .NS suffix, try without it
        if data.empty:
            print(f"No data returned for {yahoo_symbol}. Trying without .NS suffix...")
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                print(f"No data returned for {symbol} (with or without .NS). Skipping.")
                return False, f"No data available for {symbol}", None
        
        # Print data shape and info for debugging
        print(f"Data shape: {data.shape}")
        print(f"Data columns: {data.columns.tolist()}")
        print("First few rows:")
        print(data.head())
        print("Last few rows:")
        print(data.tail())
        print("Data info:")
        print(data.info())
        
        return True, f"Successfully fetched data for {symbol}", data
        
    except Exception as e:
        error_msg = f"Error fetching data for {symbol}: {str(e)}"
        print(error_msg)
        return False, error_msg, None

@login_required
def refresh_stock_data(request):
    """Refresh all data for a specific stock."""
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol')
        
        if not symbol:
            return JsonResponse({
                'success': False,
                'message': 'No symbol provided'
            }, status=400)
            
        print("refresh_stock_data called")
        
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Stock with symbol {symbol} not found'
            }, status=404)
            
        # Get the latest date from existing data
        latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
        
        # Set the start date based on whether we have existing data
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        if latest_price:
            try:
                # Convert latest_price.date to the correct format
                latest_date = latest_price.date
                if isinstance(latest_date, str):
                    latest_date = datetime.strptime(latest_date, "%Y-%m-%d").date()
                elif isinstance(latest_date, int):  # If stored as a timestamp
                    latest_date = datetime.fromtimestamp(latest_date / 1000).date()
                elif isinstance(latest_date, datetime):
                    latest_date = latest_date.date()
                else:
                    latest_date = pd.to_datetime(latest_date).date()
                
                # If we already have today's or yesterday's data, no need to update
                if latest_date >= yesterday:
                    print(f"Stock {symbol} already has data for {latest_date} (today: {today})")
                    return JsonResponse({
                        'success': True,
                        'message': f'Stock {symbol} is already up to date (last update: {latest_date})'
                    })
                    
                # If we have data, fetch from the day after the latest date
                start_date = latest_date + timedelta(days=1)
                
                print(f"Latest date in DB: {latest_date}, Start date: {start_date}, Today: {today}")
            except Exception as e:
                logger.error(f"Error converting date for {symbol}: {e}")
                # If date conversion fails, default to 400 days
                start_date = today - timedelta(days=400)
        else:
            # If no data exists, fetch 400 days of historical data
            start_date = today - timedelta(days=400)
        
        # Use the new fetch_stock_data function
        success, message, data = fetch_stock_data(symbol, start_date, today)
        
        if not success:
            return JsonResponse({
                'success': False,
                'message': message
            }, status=500)
            
        rows_processed = 0
        
        for index, row in data.iterrows():
            try:
                date = pd.Timestamp(index).date()
                
                # Get values using iloc to avoid deprecation warnings
                open_price = round(float(row.iloc[data.columns.get_loc('Open')]), 2)
                high_price = round(float(row.iloc[data.columns.get_loc('High')]), 2)
                low_price = round(float(row.iloc[data.columns.get_loc('Low')]), 2)
                close_price = round(float(row.iloc[data.columns.get_loc('Close')]), 2)
                volume = round(float(row.iloc[data.columns.get_loc('Volume')]), 0)
                
                # Calculate adjusted close if not available
                adjusted_close = close_price
                if 'Adj Close' in data.columns:
                    adjusted_close = round(float(row.iloc[data.columns.get_loc('Adj Close')]), 2)
                
                print(f"Processing data for {symbol} on {date}: Close={close_price}")
                
                # Store in database
                StockPrice.objects.update_or_create(
                    stock=stock,
                    date=date,
                    defaults={
                        'open_price': open_price,
                        'high_price': high_price,
                        'low_price': low_price,
                        'close_price': close_price,
                        'adjusted_close': adjusted_close,
                        'volume': volume
                    }
                )
                rows_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing row for {symbol} on {date}: {e}")
                continue
        
        # Update stock's last_updated timestamp
        stock.last_updated = datetime.now()
        stock.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully updated {rows_processed} days of data for {symbol}',
            'rows_processed': rows_processed
        })
        
    except Stock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': f'Stock with symbol {symbol} not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error in refresh_stock_data: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error updating stock data: {str(e)}'
        }, status=500)

@login_required
def fetch_yahoo_data(request):
    """Fetch data from Yahoo Finance for a specific stock."""
    try:
        symbol = request.POST.get('symbol')
        if not symbol:
            return JsonResponse({
                'success': False,
                'message': 'Symbol is required'
            }, status=400)
            
        # Add .NS suffix for NSE stocks
        yahoo_symbol = f"{symbol}.NS"
        ticker = yf.Ticker(yahoo_symbol)
        info = ticker.info
        
        if not info:
            return JsonResponse({
                'success': False,
                'message': f'Could not find data for stock {symbol}'
            }, status=404)
            
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        hist = ticker.history(start=start_date, end=end_date)
        
        data = {
            'info': info,
            'historical_data': hist.reset_index().to_dict('records') if not hist.empty else []
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Error in fetch_yahoo_data: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error fetching Yahoo Finance data: {str(e)}'
        }, status=500)

@login_required
def watchlist_detail_content(request):
    """Serve the watchlist detail content template"""
    print("\n=== DEBUG: watchlist_detail_content view in dataupdate/views.py is being called ===")
    
    # Get all stocks with their latest prices
    stocks = Stock.objects.all().order_by('symbol')
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
        'stocks_with_prices': stocks_with_prices,
        'total_stocks': len(stocks_with_prices)
    }
    
    return render(request, 'dataupdate/watchlist_detail_content.html', context)

@login_required
def all_stocks(request):
    """Serve the all stocks content without the watchlist group structure"""
    print("\n=== DEBUG: all_stocks view in dataupdate/views.py is being called ===")
    
    # Get all stocks with their latest prices
    stocks = Stock.objects.all().order_by('symbol')
    stocks_with_prices = []
    
    for stock in stocks:
        # Get the latest price data for this stock
        latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
        
        # Calculate price change and percentage if we have data
        price = 0
        change = 0
        change_percentage = 0
        date_str = "N/A"
        
        if latest_price:
            price = latest_price.close_price
            
            # Get the previous day's price to calculate change
            previous_price = StockPrice.objects.filter(
                stock=stock, 
                date__lt=latest_price.date
            ).order_by('-date').first()
            
            if previous_price:
                change = price - previous_price.close_price
                change_percentage = (change / previous_price.close_price) * 100 if previous_price.close_price > 0 else 0
            
            # Format the date
            date_str = latest_price.date.strftime("%Y-%m-%d")
        
        stock_data = {
            'stock': stock,
            'latest_price': {
                'price': price,
                'change': change,
                'change_percentage': change_percentage,
                'date': date_str,
                'volume': latest_price.volume if latest_price else 0
            }
        }
        stocks_with_prices.append(stock_data)
    
    context = {
        'stocks_with_prices': stocks_with_prices,
        'total_stocks': len(stocks_with_prices)
    }
    
    # Return just the table content without the watchlist group structure
    return render(request, 'dataupdate/all_stocks_content.html', context)

@login_required
def update_all_stocks(request):
    """Update data for all stocks from Yahoo Finance."""
    try:
        # Get all stocks
        stocks = Stock.objects.all()
        total_stocks = stocks.count()
        updated_stocks = 0
        skipped_stocks = 0
        failed_stocks = []

        # Get current date (today)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        print(f"Current date: {today}")

        for stock in stocks:
            try:
                # Get the latest date from existing data
                latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
                
                # Set the start date based on whether we have existing data
                if latest_price:
                    try:
                        # Convert latest_price.date to the correct format
                        latest_date = latest_price.date
                        if isinstance(latest_date, str):
                            latest_date = datetime.strptime(latest_date, "%Y-%m-%d").date()
                        elif isinstance(latest_date, int):
                            latest_date = datetime.fromtimestamp(latest_date / 1000).date()
                        elif isinstance(latest_date, datetime):
                            latest_date = latest_date.date()
                        else:
                            latest_date = pd.to_datetime(latest_date).date()
                            
                        # If we already have today's or yesterday's data, skip this stock
                        if latest_date >= yesterday:
                            print(f"Stock {stock.symbol} already has data for {latest_date} (today: {today})")
                            skipped_stocks += 1
                            continue
                            
                        # If we have data, fetch from the day after the latest date
                        start_date = latest_date + timedelta(days=1)
                        
                        print(f"Stock {stock.symbol} - Latest date in DB: {latest_date}, Start date: {start_date}")
                    except Exception as e:
                        logger.error(f"Error converting date for {stock.symbol}: {e}")
                        # If date conversion fails, default to 400 days
                        start_date = today - timedelta(days=400)
                else:
                    # If no data exists, fetch 400 days of historical data
                    start_date = today - timedelta(days=400)
                
                # Add .NS suffix for NSE stocks
                yahoo_symbol = f"{stock.symbol}.NS"
                print(f"Fetching data for {yahoo_symbol} from {start_date} to {today}")
                
                data = yf.download(yahoo_symbol, start=start_date, end=today, progress=False)
                
                if data.empty:
                    print(f"No data returned for {yahoo_symbol}. Trying without .NS suffix...")
                    # Try without .NS suffix
                    data = yf.download(stock.symbol, start=start_date, end=today, progress=False)
                    
                    if data.empty:
                        print(f"No data returned for {stock.symbol} (with or without .NS). Skipping.")
                        failed_stocks.append(stock.symbol)
                        continue
                
                rows_processed = 0
                
                for index, row in data.iterrows():
                    try:
                        date = pd.Timestamp(index).date()
                        
                        open_price = round(float(row["Open"]), 2)
                        high_price = round(float(row["High"]), 2)
                        low_price = round(float(row["Low"]), 2)
                        close_price = round(float(row["Close"]), 2)
                        volume = round(float(row["Volume"]), 0)
                        adjusted_close = round(float(row["Adj Close"]), 2)
                        
                        # Calculate previous close
                        prev_close = close_price if index == data.index[0] else round(
                            float(data.iloc[data.index.get_loc(index) - 1]["Close"]), 2)
                        
                        # Store in database
                        StockPrice.objects.update_or_create(
                            stock=stock,
                            date=date,
                            defaults={
                                'open_price': open_price,
                                'high_price': high_price,
                                'low_price': low_price,
                                'close_price': close_price,
                                'adjusted_close': adjusted_close,
                                'volume': volume,
                                'previous_close': prev_close
                            }
                        )
                        rows_processed += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing row for {stock.symbol} on {date}: {e}")
                        continue
                
                # Update stock's last_updated timestamp
                stock.last_updated = datetime.now()
                stock.save()
                
                print(f"Successfully updated {rows_processed} days of data for {stock.symbol}")
                updated_stocks += 1
                
            except Exception as e:
                logger.error(f"Error updating stock {stock.symbol}: {str(e)}")
                failed_stocks.append(stock.symbol)
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully updated {updated_stocks} out of {total_stocks} stocks (skipped {skipped_stocks} already up-to-date stocks)',
            'updated_count': updated_stocks,
            'skipped_count': skipped_stocks,
            'failed_stocks': failed_stocks
        })
        
    except Exception as e:
        logger.error(f"Error in update_all_stocks: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error updating stocks: {str(e)}'
        }, status=500)
