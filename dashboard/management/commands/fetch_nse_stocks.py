from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.models import Stock
import pandas as pd
import requests
from datetime import datetime
import time
from io import StringIO

class Command(BaseCommand):
    help = 'Fetches all NSE listed stocks and updates the database'

    def handle(self, *args, **options):
        self.stdout.write('Starting to fetch NSE listed stocks...')
        
        try:
            # Fetch the list of NSE listed stocks
            url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
            response = requests.get(url)
            response.raise_for_status()
            
            # Read the CSV data using StringIO from io module
            df = pd.read_csv(StringIO(response.text))
            
            # Clean column names by stripping whitespace
            df.columns = df.columns.str.strip()
            
            # Log initial data
            self.stdout.write(f'Found {len(df)} stocks in the CSV file')
            
            # Initialize counters
            total_stocks = len(df)
            processed_stocks = 0
            created_stocks = 0
            updated_stocks = 0
            failed_stocks = 0
            
            # Process each stock
            with transaction.atomic():
                for _, row in df.iterrows():
                    try:
                        # Validate required fields
                        if pd.isna(row['SYMBOL']) or pd.isna(row['NAME OF COMPANY']) or pd.isna(row['ISIN NUMBER']):
                            self.stdout.write(self.style.WARNING(f'Skipping stock with missing required data: {row["SYMBOL"]}'))
                            failed_stocks += 1
                            continue
                        
                        # Parse date and face value
                        try:
                            listing_date = datetime.strptime(row['DATE OF LISTING'].strip(), '%d-%b-%Y').date() if pd.notna(row['DATE OF LISTING']) else None
                        except:
                            listing_date = None
                            
                        try:
                            face_value = float(row['FACE VALUE']) if pd.notna(row['FACE VALUE']) else None
                        except:
                            face_value = None
                        
                        # Create or update stock
                        stock, created = Stock.objects.update_or_create(
                            symbol=row['SYMBOL'].strip(),
                            defaults={
                                'name': row['NAME OF COMPANY'].strip(),
                                'isin': row['ISIN NUMBER'].strip(),
                                'face_value': face_value,
                                'listing_date': listing_date,
                            }
                        )
                        
                        if created:
                            created_stocks += 1
                            self.stdout.write(self.style.SUCCESS(f'Created stock: {stock.symbol} - {stock.name}'))
                        else:
                            updated_stocks += 1
                            self.stdout.write(self.style.SUCCESS(f'Updated stock: {stock.symbol} - {stock.name}'))
                            
                        processed_stocks += 1
                        
                        # Show progress every 100 stocks
                        if processed_stocks % 100 == 0:
                            self.stdout.write(f'Progress: {processed_stocks}/{total_stocks} stocks processed')
                            
                        # Add a small delay to avoid overwhelming the server
                        time.sleep(0.1)
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error processing stock {row["SYMBOL"]}: {str(e)}'))
                        failed_stocks += 1
                        continue
            
            # Print final summary
            self.stdout.write('\n=== Final Summary ===')
            self.stdout.write(f'Total stocks in CSV: {total_stocks}')
            self.stdout.write(f'Successfully processed: {processed_stocks}')
            self.stdout.write(f'Created: {created_stocks}')
            self.stdout.write(f'Updated: {updated_stocks}')
            self.stdout.write(f'Failed: {failed_stocks}')
            
            if failed_stocks > 0:
                self.stdout.write(self.style.WARNING(f'\nWarning: {failed_stocks} stocks failed to process'))
            else:
                self.stdout.write(self.style.SUCCESS('\nSuccessfully completed fetching all NSE stocks'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching NSE stocks: {str(e)}')) 