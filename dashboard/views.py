from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from decimal import Decimal
from datetime import datetime, timedelta
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
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
    return render(request, 'dashboard/market_insights.html')

@login_required
def risk_analysis(request):
    return render(request, 'dashboard/risk_analysis.html')

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

@login_required
def update_chart_data(request):
    portfolio = get_object_or_404(Portfolio, user=request.user)
    
    # Get performance history for chart
    performance_history = PortfolioPerformance.objects.filter(
        portfolio=portfolio
    ).order_by('date')[:30]  # Last 30 days
    
    performance_labels = [p.date.strftime('%Y-%m-%d') for p in performance_history]
    performance_data = [float(p.total_value) for p in performance_history]
    
    return JsonResponse({
        'labels': performance_labels,
        'data': performance_data
    })

@login_required
def search_stocks(request):
    query = request.GET.get('q', '')
    print(f"Searching for stocks with query: {query}")
    
    stocks = Stock.objects.filter(
        symbol__icontains=query
    ).order_by('symbol')[:10]
    
    print(f"Found {stocks.count()} matching stocks")
    for stock in stocks:
        print(f"Stock: {stock.symbol} - {stock.name}")
    
    results = [{
        'symbol': stock.symbol,
        'price': float(stock.current_price)
    } for stock in stocks]
    
    print(f"Returning results: {results}")
    return JsonResponse({'results': results})

@login_required
def get_stock_quotes(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({'error': 'Fyers service not available'}, status=503)
    
    try:
        symbols = request.GET.getlist('symbols[]')
        if not symbols:
            return JsonResponse({'error': 'No symbols provided'}, status=400)
        
        fyers = FyersService()
        quotes = fyers.get_quotes(symbols)
        
        return JsonResponse({'quotes': quotes})
        
    except Exception as e:
        logger.error(f"Error getting stock quotes: {str(e)}")
        return JsonResponse({'error': 'Error getting stock quotes'}, status=500)

@login_required
def get_all_symbols(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({'error': 'Fyers service not available'}, status=503)
    
    try:
        fyers = FyersService()
        symbols = fyers.get_all_symbols()
        
        return JsonResponse({'symbols': symbols})
        
    except Exception as e:
        logger.error(f"Error getting symbols: {str(e)}")
        return JsonResponse({'error': 'Error getting symbols'}, status=500)

@csrf_exempt
def fyers_callback(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({'error': 'Fyers service not available'}, status=503)
    
    try:
        auth_code = request.GET.get('auth_code')
        if not auth_code:
            return JsonResponse({'error': 'No auth code provided'}, status=400)
        
        fyers = FyersService()
        access_token = fyers.generate_access_token(auth_code)
        
        return JsonResponse({'access_token': access_token})
        
    except Exception as e:
        logger.error(f"Error in Fyers callback: {str(e)}")
        return JsonResponse({'error': 'Error processing callback'}, status=500)

@login_required
def get_live_quotes(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({'error': 'Fyers service not available'}, status=503)
    
    try:
        symbols = request.GET.getlist('symbols[]')
        if not symbols:
            return JsonResponse({'error': 'No symbols provided'}, status=400)
        
        fyers = FyersService()
        quotes = fyers.get_live_quotes(symbols)
        
        return JsonResponse({'quotes': quotes})
        
    except Exception as e:
        logger.error(f"Error getting live quotes: {str(e)}")
        return JsonResponse({'error': 'Error getting live quotes'}, status=500)

@login_required
def get_historical_quotes(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({'error': 'Fyers service not available'}, status=503)
    
    try:
        symbol = request.GET.get('symbol')
        timeframe = request.GET.get('timeframe', '1D')  # Default to 1 day
        
        if not symbol:
            return JsonResponse({'error': 'No symbol provided'}, status=400)
        
        fyers = FyersService()
        data = fyers.get_historical_data(symbol, timeframe)
        
        return JsonResponse({'data': data})
        
    except Exception as e:
        logger.error(f"Error getting historical quotes: {str(e)}")
        return JsonResponse({'error': 'Error getting historical quotes'}, status=500)

@login_required
def get_market_summary(request):
    if not FYERS_AVAILABLE:
        return JsonResponse({'error': 'Fyers service not available'}, status=503)
    
    try:
        fyers = FyersService()
        summary = fyers.get_market_summary()
        
        return JsonResponse({'summary': summary})
        
    except Exception as e:
        logger.error(f"Error getting market summary: {str(e)}")
        return JsonResponse({'error': 'Error getting market summary'}, status=500)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})
