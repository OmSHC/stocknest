import threading
import time
import logging
from fyers_apiv2 import FyersModel
import websocket
import json
import os
from django.conf import settings
from ..models import StockQuote
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)

class FyersBackgroundService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.fyers = None
            self.ws = None
            self.is_connected = False
            self.symbols = [
                "NSE:NIFTY50-INDEX",  # NIFTY 50 Index
                "NSE:NIFTYBANK-INDEX",  # Bank NIFTY Index
                # Add more symbols as needed
                "NSE:RELIANCE-EQ",
                "NSE:TCS-EQ",
                "NSE:HDFCBANK-EQ",
                "NSE:INFY-EQ",
                "NSE:ICICIBANK-EQ",
                "NSE:HINDUNILVR-EQ",
                "NSE:ITC-EQ",
                "NSE:SBIN-EQ",
                "NSE:BHARTIARTL-EQ",
                "NSE:KOTAKBANK-EQ"
            ]
            self.initialized = True

    def initialize_fyers(self):
        """Initialize Fyers connection with API credentials"""
        try:
            app_id = os.getenv('FYERS_APP_ID')
            access_token = os.getenv('FYERS_ACCESS_TOKEN')  # We'll need to set this up
            
            if not access_token:
                logger.error("No access token found. Please set FYERS_ACCESS_TOKEN in environment")
                return False
                
            self.fyers = FyersModel(client_id=app_id, token=access_token, log_path="")
            return True
        except Exception as e:
            logger.error(f"Error initializing Fyers: {str(e)}")
            return False

    def connect_websocket(self):
        """Establish WebSocket connection with Fyers"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                self.process_market_data(data)
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")

        def on_error(ws, error):
            logger.error(f"WebSocket error: {str(error)}")
            self.is_connected = False
            self._reconnect()

        def on_close(ws, close_status_code, close_msg):
            logger.info("WebSocket connection closed")
            self.is_connected = False
            self._reconnect()

        def on_open(ws):
            logger.info("WebSocket connection established")
            self.is_connected = True
            # Subscribe to symbols
            subscribe_data = {
                "symbol": self.symbols,
                "dataType": "symbolUpdate"
            }
            ws.send(json.dumps(subscribe_data))

        try:
            self.ws = websocket.WebSocketApp(
                f"wss://websocket.fyers.in/socket/v2?token={self.fyers.token}",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # Start WebSocket connection in a separate thread
            ws_thread = threading.Thread(target=self.ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {str(e)}")
            return False
        
        return True

    def process_market_data(self, data):
        """Process incoming market data"""
        try:
            # Update cache with latest quotes
            cache_key = f"stock_quote_{data['symbol']}"
            cache.set(cache_key, data, timeout=300)  # Cache for 5 minutes

            # Store in database (you might want to batch this for better performance)
            StockQuote.objects.create(
                symbol=data['symbol'],
                ltp=data.get('ltp', 0),
                change=data.get('change', 0),
                change_percentage=data.get('change_percentage', 0),
                volume=data.get('volume', 0),
                timestamp=timezone.now()
            )
        except Exception as e:
            logger.error(f"Error processing market data: {str(e)}")

    def _reconnect(self, max_retries=5, delay=5):
        """Attempt to reconnect the WebSocket"""
        retries = 0
        while not self.is_connected and retries < max_retries:
            logger.info(f"Attempting to reconnect (attempt {retries + 1}/{max_retries})")
            try:
                if self.ws:
                    self.ws.close()
                time.sleep(delay)
                success = self.initialize_fyers() and self.connect_websocket()
                if success:
                    logger.info("Successfully reconnected")
                    break
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {str(e)}")
            retries += 1

    def start(self):
        """Start the background service"""
        if self.initialize_fyers():
            return self.connect_websocket()
        return False

    def stop(self):
        """Stop the background service"""
        try:
            if self.ws:
                self.ws.close()
            self.is_connected = False
            logger.info("Background service stopped")
        except Exception as e:
            logger.error(f"Error stopping service: {str(e)}")

# Global instance
background_service = FyersBackgroundService() 