"""
NSE Bhavcopy data fetching and processing module.

This module provides functionality to fetch and process daily bhavcopy data from NSE India.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import logging
from decimal import Decimal
from django.db import transaction
from dashboard.models import Stock, StockPrice
import re
import os
import tempfile
from io import StringIO
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

class BhavcopyProcessor:
    """Class to handle fetching and processing of NSE bhavcopy data."""
    
    @staticmethod
    def get_bhavcopy_url(date):
        """
        Get the URL for bhavcopy data for a specific date.
        
        Args:
            date (datetime.date): The date to fetch data for
            
        Returns:
            str: The URL for the bhavcopy file
        """
        date_str = date.strftime('%d%m%y')
        return f"https://archives.nseindia.com/content/indices/mkt/indices{date_str}.csv"
    
    @staticmethod
    def get_latest_bhavcopy_url():
        """
        Find the latest bhavcopy URL from NSE India website.
        
        Returns:
            tuple: (url, date) or (None, None) if not found
        """
        try:
            # NSE website URL for bhavcopy
            base_url = "https://www.nseindia.com/market-data/securities-available-for-trading"
            
            # Send a request to the website
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(base_url, headers=headers)
            response.raise_for_status()
            
            # Look for the latest bhavcopy link in the HTML
            html_content = response.text
            
            # Pattern to find bhavcopy links
            pattern = r'href="(/content/indices/mkt/indices\d{6}\.csv)"'
            matches = re.findall(pattern, html_content)
            
            if not matches:
                logger.error("No bhavcopy links found on the NSE website")
                return None, None
            
            # Get the latest link (first match)
            latest_link = matches[0]
            
            # Extract date from the link
            date_match = re.search(r'indices(\d{6})\.csv', latest_link)
            if not date_match:
                logger.error("Could not extract date from bhavcopy link")
                return None, None
                
            date_str = date_match.group(1)
            date = datetime.strptime(date_str, '%d%m%y').date()
            
            # Construct full URL
            url = f"https://www.nseindia.com{latest_link}"
            
            return url, date
            
        except Exception as e:
            logger.error(f"Error finding latest bhavcopy: {str(e)}")
            return None, None
    
    @staticmethod
    def download_bhavcopy(url, date):
        """
        Download bhavcopy file from NSE India.
        
        Args:
            url (str): URL of the bhavcopy file
            date (datetime.date): Date of the bhavcopy
            
        Returns:
            str: Path to the downloaded file or None if download failed
        """
        try:
            # Create a temporary file
            temp_dir = tempfile.gettempdir()
            filename = f"bhavcopy_{date.strftime('%Y%m%d')}.csv"
            file_path = os.path.join(temp_dir, filename)
            
            # Headers required for NSE website
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.nseindia.com/',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }

            # Create a session to maintain cookies
            session = requests.Session()
            
            # First visit the NSE homepage to get cookies
            session.get('https://www.nseindia.com/', headers=headers, timeout=30)
            
            # Download the file
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check if we got HTML instead of CSV (which would indicate an error)
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type.lower():
                logger.error(f"Received HTML instead of CSV. NSE might be blocking the request.")
                return None
            
            # Save the file
            with open(file_path, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"Downloaded bhavcopy to {file_path}")
            
            # Verify the file is not empty and is valid CSV
            if os.path.getsize(file_path) == 0:
                logger.error("Downloaded file is empty")
                return None
                
            try:
                # Try reading the CSV file with different encodings
                encodings = ['utf-8', 'latin1', 'cp1252']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        if not df.empty:
                            break
                    except Exception:
                        continue
                
                if df is None or df.empty:
                    logger.error("Could not read the CSV file with any encoding")
                    return None
                    
                # Print the columns to help with debugging
                logger.info(f"CSV columns: {', '.join(df.columns)}")
                
            except Exception as e:
                logger.error(f"Downloaded file is not a valid CSV: {str(e)}")
                return None
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading bhavcopy: {str(e)}")
            return None
    
    @staticmethod
    def fetch_bhavcopy_data(date):
        """
        Fetch bhavcopy data from NSE for a specific date.
        
        Args:
            date (datetime.date): The date to fetch data for
            
        Returns:
            pandas.DataFrame: The bhavcopy data as a DataFrame
            None: If there was an error fetching the data
        """
        url = BhavcopyProcessor.get_bhavcopy_url(date)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Read the CSV data
            df = pd.read_csv(pd.StringIO(response.text))
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching bhavcopy data: {str(e)}")
            return None
    
    @staticmethod
    def process_bhavcopy_data(df, target_date):
        """
        Process bhavcopy data and update stock prices in the database.
        
        Args:
            df (pandas.DataFrame): The bhavcopy data
            target_date (datetime.date): The date of the data
            
        Returns:
            tuple: (total_stocks, processed_stocks, updated_stocks, failed_stocks)
        """
        if df is None or df.empty:
            logger.error("No data to process")
            return 0, 0, 0, 0
            
        # Print columns and first few rows for debugging
        logger.info(f"CSV columns: {', '.join(df.columns)}")
        logger.info(f"First few rows:\n{df.head()}")
            
        # Initialize counters
        total_stocks = len(df)
        processed_stocks = 0
        updated_stocks = 0
        failed_stocks = 0
        
        # Process each stock
        with transaction.atomic():
            for _, row in df.iterrows():
                symbol = None  # Initialize symbol variable
                try:
                    # Check if 'SYMBOL' column exists (new format) or 'Symbol' (old format)
                    if 'SYMBOL' in row:
                        symbol = row['SYMBOL'].strip()
                    elif 'Symbol' in row:
                        symbol = row['Symbol'].strip()
                    else:
                        logger.warning(f'No symbol column found in row: {row}')
                        failed_stocks += 1
                        continue
                    
                    # Find the stock in our database
                    stock = Stock.objects.filter(symbol=symbol).first()
                    if not stock:
                        logger.warning(f'Stock not found in database: {symbol}')
                        failed_stocks += 1
                        continue
                    
                    # Extract price data - handle different column names
                    open_price = None
                    high_price = None
                    low_price = None
                    close_price = None
                    volume = None
                    
                    # Try different possible column names
                    if 'OPEN' in row:
                        open_price = Decimal(str(row['OPEN']))
                    elif 'Open' in row:
                        open_price = Decimal(str(row['Open']))
                        
                    if 'HIGH' in row:
                        high_price = Decimal(str(row['HIGH']))
                    elif 'High' in row:
                        high_price = Decimal(str(row['High']))
                        
                    if 'LOW' in row:
                        low_price = Decimal(str(row['LOW']))
                    elif 'Low' in row:
                        low_price = Decimal(str(row['Low']))
                        
                    if 'CLOSE' in row:
                        close_price = Decimal(str(row['CLOSE']))
                    elif 'Close' in row:
                        close_price = Decimal(str(row['Close']))
                        
                    if 'VOLUME' in row:
                        volume = int(row['VOLUME'])
                    elif 'Volume' in row:
                        volume = int(row['Volume'])
                    
                    # Check if we have all required data
                    if not all([open_price, high_price, low_price, close_price, volume]):
                        logger.warning(f'Missing price data for {symbol}')
                        failed_stocks += 1
                        continue
                    
                    # Update or create stock price
                    stock_price, created = StockPrice.objects.update_or_create(
                        stock=stock,
                        date=target_date,
                        defaults={
                            'open_price': open_price,
                            'high_price': high_price,
                            'low_price': low_price,
                            'close_price': close_price,
                            'adjusted_close': close_price,  # NSE doesn't provide adjusted close
                            'volume': volume
                        }
                    )
                    
                    if created:
                        logger.info(f'Created price for {symbol}: ₹{close_price}')
                    else:
                        logger.info(f'Updated price for {symbol}: ₹{close_price}')
                    
                    updated_stocks += 1
                    processed_stocks += 1
                    
                except Exception as e:
                    logger.error(f'Error processing stock {symbol if symbol else "unknown"}: {str(e)}')
                    failed_stocks += 1
                    continue
        
        return total_stocks, processed_stocks, updated_stocks, failed_stocks
    
    @staticmethod
    def update_stock_prices(date=None):
        """
        Update stock prices from bhavcopy data for a specific date.
        
        Args:
            date (datetime.date, optional): The date to update prices for. Defaults to yesterday.
            
        Returns:
            tuple: (success, message, stats)
                success (bool): Whether the update was successful
                message (str): A message describing the result
                stats (dict): Statistics about the update
        """
        try:
            # Get the date to fetch data for
            if date is None:
                date = datetime.now().date() - timedelta(days=1)
            
            # Skip if it's a weekend
            if date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                return False, f'Skipping weekend date: {date}', {}
            
            # Fetch and process the data
            df = BhavcopyProcessor.fetch_bhavcopy_data(date)
            if df is None:
                return False, f'Failed to fetch bhavcopy data for {date}', {}
            
            processor = BhavcopyProcessor()
            total_stocks, processed_stocks, updated_stocks, failed_stocks = processor.process_bhavcopy_dataframe(df, date)
            
            stats = {
                'total_stocks': total_stocks,
                'processed_stocks': processed_stocks,
                'updated_stocks': updated_stocks,
                'failed_stocks': failed_stocks
            }
            
            if failed_stocks > 0:
                message = f'Updated {updated_stocks} stocks, {failed_stocks} failed'
                success = False
            else:
                message = f'Successfully updated {updated_stocks} stocks'
                success = True
            
            return success, message, stats
            
        except Exception as e:
            logger.error(f'Error updating stock prices: {str(e)}')
            return False, f'Error: {str(e)}', {}
    
    @staticmethod
    def update_from_latest_bhavcopy():
        """
        Find the latest bhavcopy, download it, and update stock prices.
        
        Returns:
            tuple: (success, message, stats)
                success (bool): Whether the update was successful
                message (str): A message describing the result
                stats (dict): Statistics about the update
        """
        try:
            # Find the latest bhavcopy URL
            url, date = BhavcopyProcessor.get_latest_bhavcopy_url()
            if not url or not date:
                return False, "Could not find latest bhavcopy URL", {}
            
            logger.info(f"Found latest bhavcopy for date: {date}")
            
            # Download the bhavcopy file
            file_path = BhavcopyProcessor.download_bhavcopy(url, date)
            if not file_path:
                return False, f"Failed to download bhavcopy for {date}", {}
            
            # Read the CSV data
            try:
                df = pd.read_csv(file_path)
                
                # Clean column names
                df.columns = df.columns.str.strip()
                
                # Process the data
                processor = BhavcopyProcessor()
                total_stocks, processed_stocks, updated_stocks, failed_stocks = processor.process_bhavcopy_dataframe(df, date)
                
                stats = {
                    'total_stocks': total_stocks,
                    'processed_stocks': processed_stocks,
                    'updated_stocks': updated_stocks,
                    'failed_stocks': failed_stocks,
                    'date': date.strftime('%Y-%m-%d')
                }
                
                if failed_stocks > 0:
                    message = f'Updated {updated_stocks} stocks, {failed_stocks} failed'
                    success = False
                else:
                    message = f'Successfully updated {updated_stocks} stocks'
                    success = True
                
                return success, message, stats
                
            except Exception as e:
                logger.error(f"Error processing downloaded bhavcopy: {str(e)}")
                return False, f"Error processing bhavcopy: {str(e)}", {}
                
        except Exception as e:
            logger.error(f"Error updating from latest bhavcopy: {str(e)}")
            return False, f"Error: {str(e)}", {}
            
    @staticmethod
    def process_specific_bhavcopy_url(url):
        """
        Process a specific bhavcopy URL provided by the user.
        
        Args:
            url (str): The URL of the bhavcopy file
            
        Returns:
            tuple: (success, message, stats)
                success (bool): Whether the update was successful
                message (str): A message describing the result
                stats (dict): Statistics about the update
        """
        try:
            # Extract date from URL
            date_match = re.search(r'sec_bhavdata_full_(\d{8})\.csv', url)
            if not date_match:
                return False, "Could not extract date from URL", {}
                
            date_str = date_match.group(1)
            date = datetime.strptime(date_str, '%d%m%Y').date()
            
            logger.info(f"Processing bhavcopy for date: {date}")
            
            # Download the bhavcopy file
            file_path = BhavcopyProcessor.download_bhavcopy(url, date)
            if not file_path:
                return False, f"Failed to download bhavcopy from {url}", {}
            
            # Read the CSV data
            try:
                df = pd.read_csv(file_path)
                
                # Clean column names
                df.columns = df.columns.str.strip()
                
                # Process the data
                processor = BhavcopyProcessor()
                total_stocks, processed_stocks, updated_stocks, failed_stocks = processor.process_bhavcopy_dataframe(df, date)
                
                stats = {
                    'total_stocks': total_stocks,
                    'processed_stocks': processed_stocks,
                    'updated_stocks': updated_stocks,
                    'failed_stocks': failed_stocks,
                    'date': date.strftime('%Y-%m-%d')
                }
                
                if failed_stocks > 0:
                    message = f'Updated {updated_stocks} stocks, {failed_stocks} failed'
                    success = False
                else:
                    message = f'Successfully updated {updated_stocks} stocks'
                    success = True
                
                return success, message, stats
                
            except Exception as e:
                logger.error(f"Error processing downloaded bhavcopy: {str(e)}")
                return False, f"Error processing bhavcopy: {str(e)}", {}
                
        except Exception as e:
            logger.error(f"Error processing specific bhavcopy URL: {str(e)}")
            return False, f"Error: {str(e)}", {}

    def process_bhavcopy_dataframe(self, df, bhavcopy_date):
        """
        Process bhavcopy data from a DataFrame and update stock prices.
        
        Args:
            df (pd.DataFrame): DataFrame containing bhavcopy data
            bhavcopy_date (datetime.date): Date of the bhavcopy data
            
        Returns:
            tuple: (total_stocks, processed_stocks, updated_stocks, failed_stocks)
        """
        total_stocks = len(df)
        processed_stocks = 0
        updated_stocks = 0
        failed_stocks = 0

        # Map of possible column names to our expected column names
        column_mapping = {
            'SYMBOL': 'SYMBOL',
            'OPEN': 'OPEN_PRICE',
            'HIGH': 'HIGH_PRICE',
            'LOW': 'LOW_PRICE',
            'CLOSE': 'CLOSE_PRICE',
            'VOLUME': 'TTL_TRD_QNTY',
            'Open': 'OPEN_PRICE',
            'High': 'HIGH_PRICE',
            'Low': 'LOW_PRICE',
            'Close': 'CLOSE_PRICE',
            'Volume': 'TTL_TRD_QNTY',
            'Symbol': 'SYMBOL'
        }

        # Check if we have the required columns
        required_columns = ['SYMBOL', 'OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE', 'CLOSE_PRICE', 'TTL_TRD_QNTY']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns in bhavcopy data. Required: {required_columns}, Found: {df.columns.tolist()}")
            return total_stocks, processed_stocks, updated_stocks, failed_stocks

        for _, row in df.iterrows():
            try:
                symbol = row['SYMBOL'].strip()
                if not symbol:
                    logger.warning(f"Empty symbol found in row: {row}")
                    failed_stocks += 1
                    continue

                # Convert price values to Decimal
                try:
                    open_price = Decimal(str(row['OPEN_PRICE']))
                    high_price = Decimal(str(row['HIGH_PRICE']))
                    low_price = Decimal(str(row['LOW_PRICE']))
                    close_price = Decimal(str(row['CLOSE_PRICE']))
                    volume = int(row['TTL_TRD_QNTY'])
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid price/volume data for {symbol}: {e}")
                    failed_stocks += 1
                    continue

                # Find the stock in our database
                stock = Stock.objects.filter(symbol=symbol).first()
                if not stock:
                    logger.warning(f"Stock not found in database: {symbol}")
                    failed_stocks += 1
                    continue

                # Update or create StockPrice record
                stock_price, created = StockPrice.objects.update_or_create(
                    stock=stock,
                    date=bhavcopy_date,
                    defaults={
                        'open_price': open_price,
                        'high_price': high_price,
                        'low_price': low_price,
                        'close_price': close_price,
                        'adjusted_close': close_price,  # Using close price as adjusted close
                        'volume': volume
                    }
                )

                processed_stocks += 1
                if created:
                    updated_stocks += 1
                    logger.info(f"Created new price record for {symbol} on {bhavcopy_date}")
                else:
                    logger.info(f"Updated price record for {symbol} on {bhavcopy_date}")

            except Exception as e:
                logger.error(f"Error processing row for symbol {row.get('SYMBOL', 'UNKNOWN')}: {str(e)}")
                failed_stocks += 1
                continue

        return total_stocks, processed_stocks, updated_stocks, failed_stocks

    def process_bhavcopy_data(self, bhavcopy_date: datetime.date, csv_data: str) -> Tuple[bool, str, Dict[str, int]]:
        try:
            # Read CSV data into DataFrame
            df = pd.read_csv(StringIO(csv_data))
            
            # Print detailed CSV information
            print("\n" + "="*80)
            print("CSV DATA INFORMATION")
            print("="*80)
            print(f"\nTotal rows: {len(df)}")
            print(f"Total columns: {len(df.columns)}")
            print("\nColumns:", df.columns.tolist())
            print("\nFirst 10 rows:")
            print(df.head(10).to_string())
            print("\nData types:")
            print(df.dtypes)
            print("\nBasic statistics:")
            print(df.describe())
            print("="*80 + "\n")
            
            # Clean column names
            df.columns = [col.strip().upper() for col in df.columns]
            
            # Print cleaned columns
            print("\nCleaned Columns:", df.columns.tolist())
            
            # Process the data
            total_stocks, processed_stocks, updated_stocks, failed_stocks = self.process_bhavcopy_dataframe(df, bhavcopy_date)
            
            stats = {
                'total_stocks': total_stocks,
                'processed_stocks': processed_stocks,
                'updated_stocks': updated_stocks,
                'failed_stocks': failed_stocks
            }
            
            if failed_stocks > 0:
                message = f'Updated {updated_stocks} stocks, {failed_stocks} failed'
                success = False
            else:
                message = f'Successfully updated {updated_stocks} stocks'
                success = True
            
            return success, message, stats
            
        except Exception as e:
            logger.error(f"Error processing bhavcopy data: {str(e)}")
            return False, f"Error: {str(e)}", {} 