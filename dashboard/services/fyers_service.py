from fyers_apiv2 import FyersModel, fyersModel
from fyers_apiv2.accessToken import accessToken
from fyers_config import FYERS_APP_ID, FYERS_SECRET_KEY, FYERS_REDIRECT_URI
import websocket
import json
import threading
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FyersService:
    def __init__(self):
        self.fyers = None
        self.ws = None
        self.session = None
        self.is_connected = False
        self.callbacks = []
        self._initialize_session()

    def _initialize_session(self):
        """Initialize the Fyers session"""
        try:
            self.session = accessToken(
                app_id=FYERS_APP_ID,
                secret_key=FYERS_SECRET_KEY,
                redirect_uri=FYERS_REDIRECT_URI,
                response_type="code",
                grant_type="authorization_code"
            )
            self.fyers = FyersModel(client_id=FYERS_APP_ID, token=None, log_path="")
            logger.info("Fyers session initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Fyers session: {str(e)}")
            raise

    def set_access_token(self, auth_code):
        """Set the access token after OAuth authentication"""
        try:
            self.session.set_token(auth_code)
            access_token = self.session.generate_token()['access_token']
            self.fyers.set_token(access_token)
            logger.info("Access token set successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting access token: {str(e)}")
            return False

    def connect_websocket(self, symbols):
        """
        Connect to Fyers WebSocket for live market data
        symbols: List of symbols to subscribe to (e.g., ["NSE:SBIN-EQ", "NSE:RELIANCE-EQ"])
        """
        def on_message(ws, message):
            try:
                data = json.loads(message)
                # Process the message and notify callbacks
                for callback in self.callbacks:
                    callback(data)
            except Exception as e:
                logger.error(f"Error processing websocket message: {str(e)}")

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
                "symbol": symbols,
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
            raise

    def _reconnect(self, max_retries=5, delay=5):
        """Attempt to reconnect the WebSocket"""
        retries = 0
        while not self.is_connected and retries < max_retries:
            logger.info(f"Attempting to reconnect (attempt {retries + 1}/{max_retries})")
            try:
                if self.ws:
                    self.ws.close()
                time.sleep(delay)
                self.connect_websocket()
                if self.is_connected:
                    logger.info("Successfully reconnected")
                    break
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {str(e)}")
            retries += 1

    def add_data_callback(self, callback):
        """Add a callback function to handle incoming market data"""
        self.callbacks.append(callback)

    def remove_data_callback(self, callback):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def get_market_depth(self, symbols):
        """Get market depth (order book) for specified symbols"""
        try:
            data = {
                "symbols": ",".join(symbols),
                "dataType": "depth"
            }
            response = self.fyers.depth(data)
            return response
        except Exception as e:
            logger.error(f"Error fetching market depth: {str(e)}")
            return None

    def get_quotes(self, symbols):
        """
        Get quotes for multiple symbols
        :param symbols: List of symbols (e.g., ['NSE:RELIANCE', 'NSE:TCS'])
        :return: Dictionary containing quotes
        """
        try:
            data = {"symbols": ",".join(symbols)}
            response = self.fyers.quotes(data)
            return response
        except Exception as e:
            logger.error(f"Error fetching quotes: {str(e)}")
            return None

    def get_historical_data(self, symbol, timeframe="1D", from_date=None, to_date=None):
        """
        Get historical data for a symbol
        timeframe: "1D", "1H", "15M", "5M", "1M"
        """
        try:
            if not from_date:
                from_date = int(time.time()) - (30 * 24 * 60 * 60)  # Last 30 days
            if not to_date:
                to_date = int(time.time())

            data = {
                "symbol": symbol,
                "resolution": timeframe,
                "date_format": "1",
                "range_from": from_date,
                "range_to": to_date,
                "cont_flag": "1"
            }
            response = self.fyers.history(data)
            return response
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return None

    def disconnect(self):
        """Disconnect from WebSocket and cleanup"""
        try:
            if self.ws:
                self.ws.close()
            self.is_connected = False
            self.callbacks = []
            logger.info("Successfully disconnected from Fyers")
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")

    def get_all_nse_symbols(self):
        """
        Get all NSE symbols
        :return: List of NSE symbols
        """
        try:
            response = self.fyers.market_status()
            if response.get('s') == 'ok':
                return response.get('d', [])
            return []
        except Exception as e:
            print(f"Error fetching NSE symbols: {str(e)}")
            return [] 