from fyers_api import fyersModel, FyersModel
import os
from dotenv import load_dotenv
import logging
import json
import time
import urllib.parse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_access_token():
    """Get access token from Fyers API"""
    try:
        load_dotenv()
        app_id = os.getenv('FYERS_APP_ID')
        secret_key = os.getenv('FYERS_SECRET_KEY')
        
        if not app_id or not secret_key:
            raise ValueError("FYERS_APP_ID and FYERS_SECRET_KEY must be set in .env file")

        # Use the callback URL that matches your Fyers API app configuration
        redirect_uri = "http://localhost:8000/dashboard/api/fyers/callback/"
        
        session = fyersModel.SessionModel(
            client_id=app_id,
            secret_key=secret_key,
            redirect_uri=redirect_uri,
            response_type="code",
            grant_type="authorization_code"
        )

        auth_url = session.generate_authcode()
        logger.info("\nPlease follow these steps:")
        logger.info("1. Visit this URL in your browser: %s", auth_url)
        logger.info("2. Log in to your Fyers account if needed")
        logger.info("3. Authorize the application")
        logger.info("4. You will be redirected to: %s", redirect_uri)
        logger.info("5. Copy the ENTIRE redirect URL from your browser's address bar")
        logger.info("6. Paste it here when prompted\n")
        
        redirect_url = input("Enter the complete redirect URL: ")
        
        # Extract the authorization code from the redirect URL
        parsed_url = urllib.parse.urlparse(redirect_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        if 'code' not in query_params:
            logger.error("No authorization code found in the redirect URL")
            return None
            
        auth_code = query_params['code'][0]
        logger.info("Authorization code extracted successfully")

        session.set_token(auth_code)
        response = session.generate_token()
        
        if "access_token" in response:
            logger.info("Access token generated successfully")
            logger.info("\nPlease add this access token to your .env file:")
            logger.info(f"FYERS_ACCESS_TOKEN={response['access_token']}")
            return response["access_token"]
        else:
            logger.error(f"Failed to generate token: {response}")
            return None

    except Exception as e:
        logger.error(f"Error in get_access_token: {str(e)}")
        return None

def test_connection(access_token):
    """Test the Fyers API connection"""
    try:
        fyers = FyersModel(client_id=os.getenv('FYERS_APP_ID'), token=access_token)
        
        # Test market quotes
        symbols = ["NSE:SBIN-EQ", "NSE:RELIANCE-EQ"]  # Example symbols
        quotes = fyers.quotes({"symbols": ",".join(symbols)})
        logger.info(f"Market quotes response: {json.dumps(quotes, indent=2)}")

        return True

    except Exception as e:
        logger.error(f"Error in test_connection: {str(e)}")
        return False

def main():
    access_token = get_access_token()
    if access_token:
        if test_connection(access_token):
            logger.info("Connection test successful!")
        else:
            logger.error("Connection test failed!")
    else:
        logger.error("Failed to get access token")

if __name__ == "__main__":
    main() 