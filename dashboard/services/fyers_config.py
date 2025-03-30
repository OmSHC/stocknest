import os
from dotenv import load_dotenv

load_dotenv()

# Fyers API Credentials
FYERS_APP_ID = os.getenv('FYERS_APP_ID')
FYERS_SECRET_KEY = os.getenv('FYERS_SECRET_KEY')
FYERS_REDIRECT_URI = os.getenv('FYERS_REDIRECT_URI', 'http://localhost:8000/fyers/callback')

# Fyers API Endpoints
FYERS_API_URL = "https://api.fyers.in/api/v2"
FYERS_WEBSOCKET_URL = "wss://api.fyers.in/websocket/v1" 