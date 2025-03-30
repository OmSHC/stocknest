import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import Stock, Watchlist, StockPrice
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample data for dashboard demo (stocks, watchlists, prices)'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create sample stocks if they don't exist
        self.create_sample_stocks()
        
        # Create sample users if they don't exist
        self.create_sample_users()
        
        # Create sample watchlists
        self.create_sample_watchlists()
        
        # Create sample stock prices
        self.create_sample_prices()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
    
    def create_sample_stocks(self):
        """Create sample stocks if they don't exist"""
        sample_stocks = [
            {'symbol': 'RELIANCE', 'name': 'Reliance Industries Ltd.', 'isin': 'INE002A01018', 'sector': 'Energy'},
            {'symbol': 'TCS', 'name': 'Tata Consultancy Services Ltd.', 'isin': 'INE467B01029', 'sector': 'Technology'},
            {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Ltd.', 'isin': 'INE040A01034', 'sector': 'Financial Services'},
            {'symbol': 'INFY', 'name': 'Infosys Ltd.', 'isin': 'INE009A01021', 'sector': 'Technology'},
            {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Ltd.', 'isin': 'INE090A01021', 'sector': 'Financial Services'},
            {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever Ltd.', 'isin': 'INE030A01027', 'sector': 'Consumer Goods'},
            {'symbol': 'BAJFINANCE', 'name': 'Bajaj Finance Ltd.', 'isin': 'INE296A01024', 'sector': 'Financial Services'},
            {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel Ltd.', 'isin': 'INE397D01024', 'sector': 'Telecommunications'},
            {'symbol': 'SBIN', 'name': 'State Bank of India', 'isin': 'INE062A01020', 'sector': 'Financial Services'},
            {'symbol': 'ADANIPORTS', 'name': 'Adani Ports & SEZ Ltd.', 'isin': 'INE742F01042', 'sector': 'Infrastructure'},
        ]
        
        for stock_data in sample_stocks:
            stock, created = Stock.objects.get_or_create(
                symbol=stock_data['symbol'],
                defaults={
                    'name': stock_data['name'],
                    'isin': stock_data['isin'],
                    'sector': stock_data['sector'],
                    'market_cap': Decimal(str(random.randint(50000, 1000000))),
                }
            )
            if created:
                self.stdout.write(f"Created stock: {stock.symbol}")
    
    def create_sample_users(self):
        """Create sample users if they don't exist"""
        # Ensure admin user exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f"Created admin user: {admin_user.username}")
        
        # Create regular user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='demouser',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User',
            }
        )
        
        if created:
            user.set_password('demopass')
            user.save()
            self.stdout.write(f"Created demo user: {user.username}")
    
    def create_sample_watchlists(self):
        """Create sample watchlists"""
        try:
            users = User.objects.all()
            stocks = Stock.objects.all()
            
            if not users.exists() or not stocks.exists():
                self.stdout.write(self.style.WARNING('No users or stocks available. Skipping watchlist creation.'))
                return
            
            for user in users:
                # Create a few watchlists for each user
                watchlist_configs = [
                    {
                        'name': 'Blue Chip Stocks',
                        'description': 'Portfolio of stable, large-cap companies with consistent performance',
                        'is_global': False,
                        'stock_indices': [0, 1, 2, 3, 4]  # Will pick these indices from the stocks list
                    },
                    {
                        'name': 'Tech Stocks',
                        'description': 'Technology companies with high growth potential',
                        'is_global': True if user.username == 'admin' else False,
                        'stock_indices': [1, 3, 7]  # Will pick these indices from the stocks list
                    },
                    {
                        'name': 'Banking & Financial',
                        'description': 'Banks and financial institutions',
                        'is_global': False,
                        'stock_indices': [2, 4, 6, 8]  # Will pick these indices from the stocks list
                    }
                ]
                
                stocks_list = list(stocks)
                
                for config in watchlist_configs:
                    # Check if watchlist already exists
                    existing = Watchlist.objects.filter(name=config['name'], created_by=user).exists()
                    if not existing:
                        watchlist = Watchlist.objects.create(
                            name=config['name'],
                            description=config['description'],
                            is_global=config['is_global'],
                            created_by=user
                        )
                        
                        # Add stocks to watchlist
                        watchlist_stocks = []
                        for idx in config['stock_indices']:
                            if idx < len(stocks_list):
                                watchlist_stocks.append(stocks_list[idx])
                        
                        watchlist.stocks.set(watchlist_stocks)
                        self.stdout.write(f"Created watchlist '{watchlist.name}' for user {user.username}")
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating watchlists: {str(e)}'))
    
    def create_sample_prices(self):
        """Create sample price history for stocks"""
        try:
            stocks = Stock.objects.all()
            today = timezone.now().date()
            
            # Generate price history for the last 30 days
            for stock in stocks:
                # Create a base price between 500 and 5000
                base_price = Decimal(str(random.randint(500, 5000)))
                
                # Generate daily prices with some randomness
                for day in range(30):
                    date = today - timedelta(days=29-day)
                    
                    # Check if price already exists for this date
                    if StockPrice.objects.filter(stock=stock, date=date).exists():
                        continue
                    
                    # Add some random fluctuation to simulate price movement
                    fluctuation = Decimal(str(random.uniform(-0.03, 0.03))) * base_price
                    close_price = base_price + fluctuation
                    
                    # Ensure price doesn't go negative
                    close_price = max(close_price, Decimal('0.01'))
                    
                    # Create realistic open, high, low prices
                    open_price = close_price - Decimal(str(random.uniform(-0.02, 0.02))) * close_price
                    high_price = max(open_price, close_price) + Decimal(str(random.uniform(0, 0.015))) * close_price
                    low_price = min(open_price, close_price) - Decimal(str(random.uniform(0, 0.015))) * close_price
                    
                    # Ensure prices are positive and in proper order
                    open_price = max(open_price, Decimal('0.01'))
                    high_price = max(high_price, open_price, close_price)
                    low_price = max(min(low_price, open_price, close_price), Decimal('0.01'))
                    
                    # Create a stock price entry
                    StockPrice.objects.create(
                        stock=stock,
                        date=date,
                        open_price=open_price.quantize(Decimal('0.01')),
                        high_price=high_price.quantize(Decimal('0.01')),
                        low_price=low_price.quantize(Decimal('0.01')),
                        close_price=close_price.quantize(Decimal('0.01')),
                        adjusted_close=close_price.quantize(Decimal('0.01')),
                        volume=random.randint(100000, 10000000)
                    )
                
                # Update the base price for the next day
                base_price = close_price
                
            self.stdout.write(f"Created price history for {stocks.count()} stocks over 30 days")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating stock prices: {str(e)}')) 