from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio')
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Portfolio"

class Stock(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    isin = models.CharField(max_length=12, unique=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    listing_date = models.DateField(null=True, blank=True)
    face_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['isin']),
            models.Index(fields=['sector']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.name}"

class PortfolioHolding(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=6, validators=[MinValueValidator(Decimal('0.000001'))])
    average_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_invested = models.DecimalField(max_digits=15, decimal_places=2)
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.portfolio.user.username} - {self.stock.symbol}"

    def calculate_gain_loss(self):
        return self.current_value - self.total_invested

    def calculate_gain_loss_percentage(self):
        if self.total_invested == 0:
            return 0
        return ((self.current_value - self.total_invested) / self.total_invested) * 100

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=15, decimal_places=6, validators=[MinValueValidator(Decimal('0.000001'))])
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.upper()} {self.quantity} {self.stock.symbol}"

class Watchlist(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='created_watchlists'
    )
    is_global = models.BooleanField(default=False)
    stocks = models.ManyToManyField(Stock, blank=True, related_name='watchlists')
    subscribers = models.ManyToManyField(User, blank=True, related_name='subscribed_watchlists')

    def __str__(self):
        return f"{self.name} (Created by: {self.created_by.username if self.created_by else 'None'})"

    def get_absolute_url(self):
        return reverse('dashboard:watchlist:detail', kwargs={'watchlist_id': self.id})

    class Meta:
        ordering = ['-created_at']
        unique_together = ['name', 'created_by']

    @property
    def subscriber_count(self):
        return self.subscribers.count()

    def add_stock(self, stock):
        """Add a stock to the watchlist if it's not already present"""
        if not self.stocks.filter(id=stock.id).exists():
            self.stocks.add(stock)
            return True
        return False

    def save(self, *args, **kwargs):
        print(f"\n=== WATCHLIST SAVE DEBUG ===")
        print(f"1. Saving watchlist: {self.name}")
        print(f"2. Created by: {self.created_by.username if self.created_by else 'None'}")
        print(f"3. Is new instance: {not self.pk}")
        
        if not self.pk and not self.created_by:
            from django.contrib.auth import get_user
            try:
                current_user = get_user()
                print(f"4. Current user from get_user(): {current_user.username if current_user and current_user.is_authenticated else 'None'}")
                if current_user and current_user.is_authenticated:
                    self.created_by = current_user
                    print(f"5. Set created_by to current user: {self.created_by.username}")
            except Exception as e:
                print(f"6. Error getting current user: {str(e)}")
        
        super().save(*args, **kwargs)
        print(f"7. Save completed. Watchlist ID: {self.pk}")

class AssetAllocation(models.Model):
    ASSET_TYPES = [
        ('stocks', 'Stocks'),
        ('etfs', 'ETFs'),
        ('crypto', 'Cryptocurrency'),
        ('cash', 'Cash'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='allocations')
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.portfolio.user.username} - {self.asset_type}"

class PortfolioPerformance(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='performance_history')
    date = models.DateField()
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    daily_change = models.DecimalField(max_digits=5, decimal_places=2)
    daily_change_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.portfolio.user.username} - {self.date}"

class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    adjusted_close = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['stock', 'date']),
            models.Index(fields=['date']),
        ]
        unique_together = ['stock', 'date']  # Ensure only one price entry per stock per day

    def __str__(self):
        return f"{self.stock.symbol} - {self.date} - Close: {self.close_price}"

    @property
    def price_change(self):
        """Calculate the price change from previous close"""
        return self.close_price - self.open_price

    @property
    def price_change_percentage(self):
        """Calculate the percentage price change"""
        if self.open_price == 0:
            return 0
        return (self.price_change / self.open_price) * 100

    @property
    def day_range(self):
        """Get the day's price range"""
        return f"{self.low_price} - {self.high_price}"

    @classmethod
    def get_latest_price(cls, stock):
        """Get the most recent price for a stock"""
        return cls.objects.filter(stock=stock).order_by('-date').first()

    @classmethod
    def get_price_history(cls, stock, days=30):
        """Get price history for a stock for the specified number of days"""
        from django.utils import timezone
        from datetime import timedelta
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        return cls.objects.filter(
            stock=stock,
            date__range=[start_date, end_date]
        ).order_by('date')

class StockQuote(models.Model):
    symbol = models.CharField(max_length=50)
    ltp = models.DecimalField(max_digits=10, decimal_places=2)  # Last Traded Price
    change = models.DecimalField(max_digits=10, decimal_places=2)
    change_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    volume = models.BigIntegerField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['symbol', '-timestamp']),
        ]
        
    def __str__(self):
        return f"{self.symbol} - ₹{self.ltp} ({self.change_percentage}%)"

class WatchlistColumn(models.Model):
    """Model to define available columns for watchlist display"""
    COLUMN_TYPES = [
        ('basic', 'Basic Stock Info'),
        ('price', 'Price Data'),
        ('technical', 'Technical Indicator'),
        ('fundamental', 'Fundamental Data'),
        ('custom', 'Custom Calculation'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    field_name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    column_type = models.CharField(max_length=20, choices=COLUMN_TYPES, default='basic')
    data_field = models.CharField(max_length=50, blank=True, help_text="Field name in the data source model")
    calculation_formula = models.TextField(blank=True, help_text="Python expression for custom calculations")
    is_default = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, blank=True)
    format_string = models.CharField(max_length=50, blank=True, help_text="Format string for displaying the value (e.g., '{:.2f}' for 2 decimal places)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_columns')

    class Meta:
        ordering = ['order', 'display_name']
        permissions = [
            ("manage_watchlist_columns", "Can manage watchlist columns"),
        ]

    def __str__(self):
        return self.display_name

    @classmethod
    def initialize_default_columns(cls):
        """Initialize default columns if they don't exist"""
        # This method should only be called by a super admin or during initial setup
        default_columns = [
            {'name': 'symbol', 'field_name': 'symbol', 'display_name': 'Symbol', 'description': 'Stock symbol', 'column_type': 'basic', 'data_field': 'symbol', 'is_default': True, 'is_required': True, 'order': 1, 'icon': 'fa-tag'},
            {'name': 'name', 'field_name': 'name', 'display_name': 'Name', 'description': 'Company name', 'column_type': 'basic', 'data_field': 'name', 'is_default': True, 'is_required': False, 'order': 2, 'icon': 'fa-building'},
            {'name': 'sector', 'field_name': 'sector', 'display_name': 'Sector', 'description': 'Industry sector', 'column_type': 'basic', 'data_field': 'sector', 'is_default': True, 'is_required': False, 'order': 3, 'icon': 'fa-industry'},
            {'name': 'price', 'field_name': 'price', 'display_name': 'Price', 'description': 'Current price', 'column_type': 'price', 'data_field': 'close_price', 'is_default': True, 'is_required': True, 'order': 4, 'icon': 'fa-dollar-sign', 'format_string': '{:.2f}'},
            {'name': 'open', 'field_name': 'open_price', 'display_name': 'Open', 'description': 'Opening price', 'column_type': 'price', 'data_field': 'open_price', 'is_default': False, 'is_required': False, 'order': 5, 'icon': 'fa-door-open', 'format_string': '{:.2f}'},
            {'name': 'high', 'field_name': 'high_price', 'display_name': 'High', 'description': 'Highest price', 'column_type': 'price', 'data_field': 'high_price', 'is_default': False, 'is_required': False, 'order': 6, 'icon': 'fa-arrow-up', 'format_string': '{:.2f}'},
            {'name': 'low', 'field_name': 'low_price', 'display_name': 'Low', 'description': 'Lowest price', 'column_type': 'price', 'data_field': 'low_price', 'is_default': False, 'is_required': False, 'order': 7, 'icon': 'fa-arrow-down', 'format_string': '{:.2f}'},
            {'name': 'change', 'field_name': 'change', 'display_name': 'Change', 'description': 'Price change', 'column_type': 'price', 'calculation_formula': 'latest_price.close_price - previous_price.close_price if latest_price and previous_price else 0', 'is_default': True, 'is_required': False, 'order': 8, 'icon': 'fa-exchange-alt', 'format_string': '{:+.2f}'},
            {'name': 'change_percentage', 'field_name': 'change_percentage', 'display_name': 'Change %', 'description': 'Percentage price change', 'column_type': 'price', 'calculation_formula': '((latest_price.close_price - previous_price.close_price) / previous_price.close_price * 100) if latest_price and previous_price and previous_price.close_price > 0 else 0', 'is_default': True, 'is_required': False, 'order': 9, 'icon': 'fa-percentage', 'format_string': '{:+.2f}%'},
            {'name': 'volume', 'field_name': 'volume', 'display_name': 'Volume', 'description': 'Trading volume', 'column_type': 'price', 'data_field': 'volume', 'is_default': True, 'is_required': False, 'order': 10, 'icon': 'fa-chart-bar', 'format_string': '{:,}'},
            {'name': 'date', 'field_name': 'date', 'display_name': 'Date', 'description': 'Latest price date', 'column_type': 'price', 'data_field': 'date', 'is_default': True, 'is_required': False, 'order': 11, 'icon': 'fa-calendar', 'format_string': '{:%Y-%m-%d}'},
            {'name': 'actions', 'field_name': 'actions', 'display_name': 'Actions', 'description': 'Available actions', 'column_type': 'basic', 'is_default': True, 'is_required': True, 'order': 12, 'icon': 'fa-cog'},
        ]
        
        for column_data in default_columns:
            cls.objects.get_or_create(
                name=column_data['name'],
                defaults=column_data
            )
    
    def get_value(self, stock, latest_price=None, previous_price=None):
        """Get the value for this column for a specific stock"""
        # If there's a calculation formula, use it
        if self.calculation_formula:
            try:
                # Create a local namespace with available variables
                namespace = {
                    'stock': stock,
                    'latest_price': latest_price,
                    'previous_price': previous_price,
                }
                # Evaluate the formula in the namespace
                value = eval(self.calculation_formula, {"__builtins__": {}}, namespace)
                return value
            except Exception as e:
                print(f"Error calculating {self.name}: {str(e)}")
                return None
        
        # Otherwise, try to get the value from the appropriate source
        if self.column_type == 'basic':
            # Get value from Stock model
            return getattr(stock, self.data_field, None)
        elif self.column_type == 'price' and latest_price:
            # Get value from StockPrice model
            return getattr(latest_price, self.data_field, None)
        
        return None
    
    def format_value(self, value):
        """Format the value according to the format_string"""
        if value is None:
            return "N/A"
        
        if self.format_string:
            try:
                return self.format_string.format(value)
            except Exception:
                return str(value)
        return str(value)
    
    def save(self, *args, **kwargs):
        """Override save method to ensure only super admins can add or modify columns"""
        # Get the user from the request if available
        from threading import local
        _thread_locals = local()
        user = getattr(_thread_locals, 'request_user', None)
        
        # If no user is found in the thread local storage, try to get it from the created_by field
        if not user and self.created_by:
            user = self.created_by
        
        # If still no user, try to get the first super user
        if not user:
            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                user = superuser
                self.created_by = superuser
            else:
                raise PermissionDenied("No user found to check permissions")
        
        # Check if the user is a super admin
        if not user.is_superuser:
            raise PermissionDenied("Only super admins can add or modify watchlist columns")
        
        super().save(*args, **kwargs)

class WatchlistDisplaySettings(models.Model):
    """Model to store user preferences for watchlist display settings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist_display_settings')
    watchlist = models.ForeignKey('Watchlist', on_delete=models.CASCADE, related_name='display_settings')
    columns = models.ManyToManyField(WatchlistColumn, related_name='user_settings')
    column_order = models.JSONField(default=dict, blank=True, help_text="JSON field to store custom column order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'watchlist')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Display settings for {self.user.username}'s watchlist: {self.watchlist.name}"

    @classmethod
    def get_or_create_settings(cls, user, watchlist):
        """Get existing settings or create default settings for a user's watchlist"""
        settings, created = cls.objects.get_or_create(
            user=user,
            watchlist=watchlist,
            defaults={'column_order': {}}
        )
        
        if created:
            # Add default columns to new settings
            default_columns = WatchlistColumn.objects.filter(is_default=True)
            settings.columns.add(*default_columns)
            
            # Initialize column order with default order
            column_order = {}
            for column in default_columns:
                column_order[column.id] = column.order
            settings.column_order = column_order
            settings.save()
        
        return settings
    
    def get_visible_columns(self):
        """Get all visible columns in the correct order"""
        # Get all columns that the user has selected
        selected_columns = self.columns.all()
        
        # Ensure symbol and actions columns are always included
        symbol_column = WatchlistColumn.objects.filter(name='symbol').first()
        actions_column = WatchlistColumn.objects.filter(name='actions').first()
        
        if symbol_column and symbol_column not in selected_columns:
            self.columns.add(symbol_column)
            selected_columns = self.columns.all()
        
        if actions_column and actions_column not in selected_columns:
            self.columns.add(actions_column)
            selected_columns = self.columns.all()
        
        # Sort columns based on user's custom order or default order
        if self.column_order:
            # Convert to list of tuples (name, order) for sorting
            order_map = {col.name: self.column_order.get(col.name, col.order) for col in selected_columns}
            return sorted(selected_columns, key=lambda col: order_map.get(col.name, col.order))
        else:
            # Use default order if no custom order is set
            return sorted(selected_columns, key=lambda col: col.order)
    
    def is_column_visible(self, column_name):
        """Check if a specific column is visible"""
        # Symbol and actions columns are always visible
        if column_name in ['symbol', 'actions']:
            return True
        return self.columns.filter(name=column_name).exists()
    
    def update_column_order(self, new_order):
        """Update the column order with a new order dictionary"""
        self.column_order = new_order
        self.save()
    
    def toggle_column(self, column_name, visible=True):
        """Toggle a column's visibility"""
        column = WatchlistColumn.objects.filter(name=column_name).first()
        
        if not column:
            return False
        
        # Symbol and actions columns cannot be hidden
        if column_name in ['symbol', 'actions'] and not visible:
            return False
        
        if visible:
            self.columns.add(column)
        else:
            self.columns.remove(column)
        
        return True
