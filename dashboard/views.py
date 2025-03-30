from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from decimal import Decimal
from datetime import datetime, timedelta
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from .models import (
    Portfolio, Stock, PortfolioHolding, Transaction,
    Watchlist, AssetAllocation, PortfolioPerformance, StockPrice, StockQuote
)
from .forms import WatchlistForm
from django.urls import reverse
import pdb
import traceback
import json
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.utils import timezone
import sys
import logging

logger = logging.getLogger(__name__)

# Only try to import Fyers if not running migrations
FYERS_AVAILABLE = False
if not ('makemigrations' in sys.argv or 'migrate' in sys.argv):
    try:
        from .services.fyers_service import FyersService
        FYERS_AVAILABLE = True
    except ImportError:
        logger.warning("Fyers service not available - some features will be disabled")

def signup(request):
    print('Signup view called')
    print('Request method:', request.method)
    print('POST data:', request.POST)
    print('CSRF token:', request.POST.get('csrfmiddlewaretoken'))
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        print('Form data received:', {
            'email': email,
            'password1': password1,
            'password2': password2
        })
        
        if not email or not password1 or not password2:
            print('Missing required fields')
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'dashboard/signup.html')
        
        if password1 != password2:
            print('Passwords do not match')
            messages.error(request, 'Passwords do not match.')
            return render(request, 'dashboard/signup.html')
            
        if User.objects.filter(email=email).exists():
            print('Email already exists')
            messages.error(request, 'Email already exists.')
            return render(request, 'dashboard/signup.html')
            
        try:
            # Create username from email (remove domain)
            username = email.split('@')[0]
            print('Creating user with username:', username)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            print('User created successfully')
            
            # Create portfolio for the new user
            Portfolio.objects.create(user=user)
            print('Portfolio created')
            
            # Create watchlist for the new user
            Watchlist.objects.create(
                name="My First Watchlist",
                description="Default watchlist created on signup",
                created_by=user
            )
            print('Watchlist created')
            
            # Log the user in
            auth_login(request, user)
            print('User logged in')
            
            messages.success(request, 'Account created successfully!')
            print('Redirecting to dashboard')
            return redirect('dashboard:dashboard')
            
        except Exception as e:
            print('Error creating user:', str(e))
            messages.error(request, 'An error occurred while creating your account. Please try again.')
            return render(request, 'dashboard/signup.html')
        
    print('Rendering signup form')
    return render(request, 'dashboard/signup.html')

@login_required
def dashboard(request):
    portfolio = get_object_or_404(Portfolio, user=request.user)
    
    # Get portfolio overview data
    total_value = portfolio.total_value
    cash_balance = portfolio.cash_balance
    total_investments = portfolio.holdings.aggregate(
        total=Sum('total_invested')
    )['total'] or Decimal('0')
    
    # Calculate total returns
    total_returns = total_value - total_investments
    returns_percentage = (total_returns / total_investments * 100) if total_investments > 0 else 0
    
    # Get daily change
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    today_performance = PortfolioPerformance.objects.filter(
        portfolio=portfolio,
        date=today
    ).first()
    yesterday_performance = PortfolioPerformance.objects.filter(
        portfolio=portfolio,
        date=yesterday
    ).first()
    
    daily_change = Decimal('0')
    if today_performance and yesterday_performance:
        daily_change = today_performance.daily_change_percentage
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        portfolio=portfolio
    ).order_by('-date')[:5]
    
    # Get watchlist
    watchlist = Watchlist.objects.filter(created_by=request.user).first()
    watchlist_stocks = []
    if watchlist:
        watchlist_stocks = watchlist.stocks.all()
    
    # Get asset allocation
    allocations = AssetAllocation.objects.filter(portfolio=portfolio)
    allocation_data = [float(alloc.value) for alloc in allocations]
    
    # Get performance history for chart
    performance_history = PortfolioPerformance.objects.filter(
        portfolio=portfolio
    ).order_by('date')[:30]  # Last 30 days
    
    performance_labels = [p.date.strftime('%Y-%m-%d') for p in performance_history]
    performance_data = [float(p.total_value) for p in performance_history]
    
    watchlists = Watchlist.objects.filter(created_by=request.user)
    stocks = Stock.objects.all().order_by('symbol')
    
    context = {
        'total_value': total_value,
        'cash_balance': cash_balance,
        'total_investments': total_investments,
        'total_returns': total_returns,
        'returns_percentage': returns_percentage,
        'daily_change': daily_change,
        'recent_transactions': recent_transactions,
        'watchlist': watchlist_stocks,
        'allocation_data': allocation_data,
        'performance_labels': performance_labels,
        'performance_data': performance_data,
        'watchlists': watchlists,
        'stocks': stocks
    }
    
    return render(request, 'dashboard/index.html', context)

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
def portfolio(request):
    portfolio = get_object_or_404(Portfolio, user=request.user)
    holdings = PortfolioHolding.objects.filter(portfolio=portfolio)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        symbol = request.POST.get('symbol')
        shares = int(request.POST.get('shares', 0))
        
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
            
            if action == 'buy':
                # Calculate total cost
                total_cost = stock.current_price * shares
                
                # Check if user has enough cash
                if portfolio.cash_balance >= total_cost:
                    # Create or update holding
                    holding, created = PortfolioHolding.objects.get_or_create(
                        portfolio=portfolio,
                        stock=stock,
                        defaults={'shares': 0, 'average_cost': stock.current_price}
                    )
                    
                    if not created:
                        # Update average cost
                        total_shares = holding.shares + shares
                        total_invested = (holding.shares * holding.average_cost) + (shares * stock.current_price)
                        holding.average_cost = total_invested / total_shares
                        holding.shares = total_shares
                    else:
                        holding.shares = shares
                    
                    holding.save()
                    
                    # Update portfolio cash balance
                    portfolio.cash_balance -= total_cost
                    portfolio.save()
                    
                    # Create transaction record
                    Transaction.objects.create(
                        portfolio=portfolio,
                        stock=stock,
                        transaction_type='BUY',
                        shares=shares,
                        price=stock.current_price,
                        total_amount=total_cost
                    )
                    
                    messages.success(request, f'Successfully bought {shares} shares of {symbol}')
                else:
                    messages.error(request, 'Insufficient funds for this purchase')
                    
            elif action == 'sell':
                holding = PortfolioHolding.objects.get(portfolio=portfolio, stock=stock)
                
                if holding.shares >= shares:
                    # Calculate total proceeds
                    total_proceeds = stock.current_price * shares
                    
                    # Update holding
                    holding.shares -= shares
                    if holding.shares == 0:
                        holding.delete()
                    else:
                        holding.save()
                    
                    # Update portfolio cash balance
                    portfolio.cash_balance += total_proceeds
                    portfolio.save()
                    
                    # Create transaction record
                    Transaction.objects.create(
                        portfolio=portfolio,
                        stock=stock,
                        transaction_type='SELL',
                        shares=shares,
                        price=stock.current_price,
                        total_amount=total_proceeds
                    )
                    
                    messages.success(request, f'Successfully sold {shares} shares of {symbol}')
                else:
                    messages.error(request, 'Insufficient shares to sell')
                    
        except Stock.DoesNotExist:
            messages.error(request, f'Stock {symbol} not found')
        except PortfolioHolding.DoesNotExist:
            messages.error(request, f'You do not own any shares of {symbol}')
    
    context = {
        'holdings': holdings,
        'portfolio': portfolio
    }
    return render(request, 'dashboard/portfolio.html', context)

@login_required
def market_insights(request):
    # Sample market news data
    market_news = [
        {
            'title': 'Federal Reserve Maintains Interest Rates',
            'source': 'Financial Times',
            'date': '2024-03-20',
            'summary': 'The Federal Reserve kept interest rates unchanged at its latest meeting, citing stable inflation and continued economic growth.'
        },
        {
            'title': 'Tech Sector Shows Strong Growth',
            'source': 'Bloomberg',
            'date': '2024-03-19',
            'summary': 'Major technology companies report better-than-expected earnings, driving market optimism.'
        },
        {
            'title': 'Global Markets React to Economic Data',
            'source': 'Reuters',
            'date': '2024-03-18',
            'summary': 'International markets respond positively to latest economic indicators, with Asian markets leading gains.'
        }
    ]
    
    # Sample sector performance data
    sector_performance = {
        'Technology': 2.5,
        'Healthcare': -1.2,
        'Finance': 0.8,
        'Energy': 3.1,
        'Consumer Goods': -0.5,
        'Real Estate': 1.7
    }
    
    # Sample market trends data
    market_trends = [
        {
            'title': 'AI Investment Surge',
            'description': 'Growing investor interest in artificial intelligence companies drives sector performance.',
            'date': '2024-03-20',
            'impact': 'positive'
        },
        {
            'title': 'Supply Chain Concerns',
            'description': 'Recent disruptions in global supply chains affect manufacturing sector.',
            'date': '2024-03-19',
            'impact': 'negative'
        },
        {
            'title': 'Green Energy Transition',
            'description': 'Increasing focus on renewable energy investments creates new market opportunities.',
            'date': '2024-03-18',
            'impact': 'positive'
        }
    ]
    
    context = {
        'market_news': market_news,
        'market_trends': market_trends,
        'sector_performance': sector_performance
    }
    return render(request, 'dashboard/market_insights.html', context)

@login_required
def risk_analysis(request):
    portfolio = get_object_or_404(Portfolio, user=request.user)
    
    # Calculate portfolio risk metrics
    holdings = PortfolioHolding.objects.filter(portfolio=portfolio)
    total_value = portfolio.total_value
    
    # Calculate sector concentration
    sector_exposure = {}
    for holding in holdings:
        # This would typically come from the Stock model
        sector = "Technology"  # Placeholder
        if sector in sector_exposure:
            sector_exposure[sector] += float(holding.current_value)
        else:
            sector_exposure[sector] = float(holding.current_value)
    
    # Convert to percentages
    for sector in sector_exposure:
        sector_exposure[sector] = (sector_exposure[sector] / float(total_value)) * 100
    
    # Calculate holding percentages
    holdings_with_percentages = []
    for holding in holdings:
        percentage = (float(holding.current_value) / float(total_value)) * 100
        holdings_with_percentages.append({
            'holding': holding,
            'percentage': percentage
        })
    
    # Calculate portfolio beta (placeholder)
    portfolio_beta = 1.2
    
    # Calculate Sharpe ratio (placeholder)
    sharpe_ratio = 1.8
    
    # Calculate volatility (placeholder)
    volatility = 12.5
    
    # Calculate Value at Risk (placeholder)
    var = -2.3
    
    # Calculate correlation matrix (placeholder)
    correlation_matrix = {
        'Market Index': 0.85,
        'Bonds': -0.15,
        'Gold': 0.05
    }
    
    # Calculate risk decomposition (placeholder)
    risk_decomposition = {
        'Market Risk': 65,
        'Company Risk': 25,
        'Currency Risk': 10
    }
    
    context = {
        'sector_exposure': sector_exposure,
        'holdings_with_percentages': holdings_with_percentages,
        'portfolio': portfolio,
        'portfolio_beta': portfolio_beta,
        'sharpe_ratio': sharpe_ratio,
        'volatility': volatility,
        'var': var,
        'correlation_matrix': correlation_matrix,
        'risk_decomposition': risk_decomposition
    }
    return render(request, 'dashboard/risk_analysis.html', context)

@login_required
def reports(request):
    portfolio = get_object_or_404(Portfolio, user=request.user)
    
    # Get performance history
    performance_history = PortfolioPerformance.objects.filter(
        portfolio=portfolio
    ).order_by('-date')[:30]
    
    # Get transaction history
    transactions = Transaction.objects.filter(
        portfolio=portfolio
    ).order_by('-date')
    
    context = {
        'performance_history': performance_history,
        'transactions': transactions
    }
    return render(request, 'dashboard/reports.html', context)

# API endpoints for AJAX requests
@login_required
def update_chart_data(request):
    timeframe = request.GET.get('timeframe', '1D')
    portfolio = get_object_or_404(Portfolio, user=request.user)
    
    # Get performance data based on timeframe
    if timeframe == '1D':
        days = 1
    elif timeframe == '1W':
        days = 7
    elif timeframe == '1M':
        days = 30
    else:  # 1Y
        days = 365
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    performance_data = PortfolioPerformance.objects.filter(
        portfolio=portfolio,
        date__range=[start_date, end_date]
    ).order_by('date')
    
    labels = [p.date.strftime('%Y-%m-%d') for p in performance_data]
    data = [float(p.total_value) for p in performance_data]
    
    return JsonResponse({
        'labels': labels,
        'data': data
    })

@login_required
def search_stocks(request):
    query = request.GET.get('q', '')
    print(f"Search query received: {query}")
    
    if len(query) < 2:
        print("Query too short, returning empty results")
        return JsonResponse({'results': []})
    
    stocks = Stock.objects.filter(
        symbol__icontains=query
    )[:5]
    
    print(f"Found {stocks.count()} matching stocks")
    for stock in stocks:
        print(f"Stock: {stock.symbol} - {stock.name}")
    
    results = [{
        'symbol': stock.symbol,
        'name': stock.name,
        'price': float(stock.current_price)
    } for stock in stocks]
    
    print(f"Returning results: {results}")
    return JsonResponse({'results': results})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('dashboard:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})

@login_required
def watchlist_detail(request, watchlist_id):
    watchlist = get_object_or_404(Watchlist, id=watchlist_id)
    
    # Check if user has access to this watchlist
    if not watchlist.is_global and watchlist.created_by != request.user and not request.user in watchlist.subscribers.all():
        messages.error(request, "You don't have access to this watchlist.")
        return redirect('dashboard:watchlist')
    
    context = {
        'watchlist': watchlist,
        'stocks': watchlist.stocks.all(),
    }
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'dashboard/watchlist_detail_content.html', context)
    
    return render(request, 'dashboard/watchlist_detail.html', context)

@login_required
def create_watchlist(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            visibility = request.POST.get('visibility', 'private')
            stock_ids = request.POST.getlist('stocks')
            
            if not name:
                messages.error(request, 'Watchlist name is required')
                return JsonResponse({'error': 'Watchlist name is required'}, status=400) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render(request, 'dashboard/create_watchlist.html', {'stocks': Stock.objects.all().order_by('symbol')})
            
            # Create the watchlist
            watchlist = Watchlist.objects.create(
                name=name,
                description=description,
                created_by=request.user,
                is_global=(visibility == 'public')
            )
            
            # Add selected stocks to the watchlist
            if stock_ids:
                stocks = Stock.objects.filter(id__in=stock_ids)
                watchlist.stocks.add(*stocks)
            
            messages.success(request, 'Watchlist created successfully')
            
            # Return appropriate response based on request type
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Watchlist created successfully',
                    'redirect': reverse('dashboard:watchlist_detail', args=[watchlist.id])
                })
            return redirect('dashboard:watchlist_detail', watchlist_id=watchlist.id)
            
        except Exception as e:
            logger.error(f"Error creating watchlist: {str(e)}")
            messages.error(request, 'Error creating watchlist')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=500)
            return render(request, 'dashboard/create_watchlist.html', {'stocks': Stock.objects.all().order_by('symbol')})
    
    # If it's a GET request, show the create form
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'dashboard/create_watchlist_content.html', {'stocks': Stock.objects.all().order_by('symbol')})
    
    # For direct access, redirect to watchlist page
    return redirect('dashboard:watchlist')

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
    print("=== GET_WATCHLISTS DEBUG ===")
    print(f"User: {request.user.username}")
    print(f"User ID: {request.user.id}")
    
    try:
        # Get personal watchlists
        personal_watchlists = Watchlist.objects.filter(
            created_by=request.user,
            is_global=False
        ).prefetch_related('stocks')
        
        print(f"Found {personal_watchlists.count()} personal watchlists")
        
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
        print(f"Error in get_watchlists: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_stock_quotes(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({"error": "Fyers service not available"}, status=503)
    """
    API endpoint to get stock quotes from Fyers
    """
    try:
        fyers_service = FyersService()
        
        # Get symbols from query parameters or use default symbols
        symbols = request.GET.get('symbols', 'NSE:RELIANCE,NSE:TCS,NSE:INFY')
        symbols_list = symbols.split(',')
        
        # Get quotes
        quotes = fyers_service.get_quotes(symbols_list)
        
        if quotes:
            return JsonResponse({
                'status': 'success',
                'data': quotes
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to fetch quotes'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_all_symbols(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({"error": "Fyers service not available"}, status=503)
    """
    API endpoint to get all available NSE symbols
    """
    try:
        fyers_service = FyersService()
        symbols = fyers_service.get_all_nse_symbols()
        
        return JsonResponse({
            'status': 'success',
            'data': symbols
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def fyers_callback(request):
    """
    Callback handler for Fyers OAuth authentication
    """
    try:
        auth_code = request.GET.get('auth_code')
        if not auth_code:
            return JsonResponse({
                'status': 'error',
                'message': 'No auth code received'
            }, status=400)
            
        fyers_service = FyersService()
        # Store the auth code or process it as needed
        # You might want to store this in the user's session or database
        
        return JsonResponse({
            'status': 'success',
            'message': 'Authentication successful',
            'auth_code': auth_code
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_live_quotes(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({"error": "Fyers service not available"}, status=503)
    """Get live quotes for all tracked symbols"""
    try:
        symbols = request.GET.get('symbols', '').split(',')
        if not symbols[0]:  # If no symbols provided, get all
            symbols = background_service.symbols
            
        quotes = {}
        for symbol in symbols:
            cache_key = f"stock_quote_{symbol}"
            quote = cache.get(cache_key)
            if quote:
                quotes[symbol] = quote
            
        return JsonResponse({
            'status': 'success',
            'data': quotes
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_historical_quotes(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({"error": "Fyers service not available"}, status=503)
    """Get historical quotes for analysis"""
    try:
        symbol = request.GET.get('symbol')
        hours = int(request.GET.get('hours', 24))
        
        if not symbol:
            return JsonResponse({
                'status': 'error',
                'message': 'Symbol is required'
            }, status=400)
            
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours)
        
        quotes = StockQuote.objects.filter(
            symbol=symbol,
            timestamp__range=(start_time, end_time)
        ).order_by('timestamp')
        
        data = [{
            'timestamp': quote.timestamp.isoformat(),
            'ltp': float(quote.ltp),
            'change': float(quote.change),
            'change_percentage': float(quote.change_percentage),
            'volume': quote.volume
        } for quote in quotes]
        
        return JsonResponse({
            'status': 'success',
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_market_summary(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({"error": "Fyers service not available"}, status=503)
    """Get summary of market movements"""
    try:
        # Get latest quotes for indices
        nifty = cache.get('stock_quote_NSE:NIFTY50-INDEX')
        bank_nifty = cache.get('stock_quote_NSE:NIFTYBANK-INDEX')
        
        # Get top gainers and losers
        latest_quotes = StockQuote.objects.filter(
            timestamp__gte=timezone.now() - timedelta(minutes=5)
        ).exclude(
            symbol__in=['NSE:NIFTY50-INDEX', 'NSE:NIFTYBANK-INDEX']
        )
        
        gainers = latest_quotes.order_by('-change_percentage')[:5]
        losers = latest_quotes.order_by('change_percentage')[:5]
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'indices': {
                    'nifty50': nifty,
                    'banknifty': bank_nifty
                },
                'top_gainers': [{
                    'symbol': quote.symbol,
                    'change_percentage': float(quote.change_percentage),
                    'ltp': float(quote.ltp)
                } for quote in gainers],
                'top_losers': [{
                    'symbol': quote.symbol,
                    'change_percentage': float(quote.change_percentage),
                    'ltp': float(quote.ltp)
                } for quote in losers]
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
