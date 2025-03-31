from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from django.urls import reverse

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
