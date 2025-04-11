from django.core.management.base import BaseCommand
from dashboard.models import Stock
from dashboard.dataupdate.views import update_stock_data_background
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update all stocks data daily'

    def add_arguments(self, parser):
        parser.add_argument(
            '--throttle',
            type=int,
            default=2,
            help='Seconds to wait between each stock update'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting daily stock data update...')
        
        # Get all stocks
        stocks = Stock.objects.all()
        total_stocks = stocks.count()
        processed = 0
        failed = 0
        
        self.stdout.write(f'Found {total_stocks} stocks to update')
        
        for stock in stocks:
            try:
                # Get the latest price date
                latest_price = stock.prices.order_by('-date').first()
                
                if latest_price:
                    # If we have data, fetch from the day after the latest date
                    start_date = latest_price.date + timedelta(days=1)
                    self.stdout.write(f"Stock {stock.symbol} - Latest date in DB: {latest_price.date}, Start date: {start_date}")
                else:
                    # If no data exists, fetch 400 days of historical data
                    start_date = datetime.now().date() - timedelta(days=400)
                    self.stdout.write(f"Stock {stock.symbol} - No data in DB, fetching 400 days of history from {start_date}")
                
                # Convert dates to strings for JSON serialization
                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = datetime.now().date().strftime("%Y-%m-%d")
                
                # Schedule the background task
                update_stock_data_background(
                    stock.symbol,
                    start_date_str=start_date_str,
                    end_date_str=end_date_str
                )
                
                processed += 1
                self.stdout.write(self.style.SUCCESS(
                    f'[{processed}/{total_stocks}] Scheduled update for {stock.symbol}'
                ))
                
                # Throttle the requests
                time.sleep(options['throttle'])
                
            except Exception as e:
                failed += 1
                logger.error(f"Error scheduling update for {stock.symbol}: {str(e)}")
                self.stdout.write(self.style.ERROR(
                    f'Error scheduling update for {stock.symbol}: {str(e)}'
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nUpdate complete: {processed} stocks processed, {failed} failed'
        )) 