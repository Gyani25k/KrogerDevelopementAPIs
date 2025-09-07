"""
Kroger API Service
Handles all API interactions with Kroger's services including authentication,
location search, product search, and cart operations.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from dotenv import load_dotenv

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KrogerAPIService:
    """Main service class for Kroger API interactions"""
    
    def __init__(self, client_id: str, client_secret: str, base_url: str = "https://api.kroger.com"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.client_token = None
        self.client_token_expires_at = None
        self.user_tokens = {}  # Store user tokens by session_id
        
    def _get_auth_header(self) -> str:
        """Generate base64 encoded authorization header for client credentials"""
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    def _is_token_expired(self, expires_at: Optional[datetime]) -> bool:
        """Check if token is expired or will expire in the next 5 minutes"""
        if not expires_at:
            return True
        return datetime.now() >= (expires_at - timedelta(minutes=5))
    
    async def get_client_token(self) -> Dict:
        """
        Get or refresh client credentials token
        POST /v1/connect/oauth2/token (client_credentials)
        """
        if self.client_token and not self._is_token_expired(self.client_token_expires_at):
            return {
                "access_token": self.client_token,
                "expires_in": int((self.client_token_expires_at - datetime.now()).total_seconds()),
                "token_generated_at": self.client_token_expires_at - timedelta(seconds=1800)
            }
        
        url = f"{self.base_url}/v1/connect/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self._get_auth_header()
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "product.compact"
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            
            # Log detailed error information for debugging
            if response.status_code != 200:
                logger.error(f"Authentication failed with status {response.status_code}")
                logger.error(f"Response headers: {dict(response.headers)}")
                logger.error(f"Response body: {response.text}")
                logger.error(f"Request headers: {headers}")
                logger.error(f"Request data: {data}")
                
                # Try to parse error response
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error_description', error_data.get('error', 'Unknown error'))
                except:
                    error_msg = response.text
                
                raise Exception(f"Authentication failed (HTTP {response.status_code}): {error_msg}")
            
            response.raise_for_status()
            token_data = response.json()
            self.client_token = token_data["access_token"]
            expires_in = token_data["expires_in"]
            self.client_token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Client token obtained successfully")
            return {
                "access_token": self.client_token,
                "expires_in": expires_in,
                "token_generated_at": datetime.now()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get client token: {e}")
            raise Exception(f"Authentication failed: {e}")
    
    async def search_locations(self, lat: float, lon: float, radius_miles: int = 10) -> Dict:
        """
        Search for Kroger locations near given coordinates
        GET /v1/locations
        """
        await self.get_client_token()  # Ensure we have a valid token
        
        url = f"{self.base_url}/v1/locations"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.client_token}"
        }
        params = {
            "filter.lat.near": lat,
            "filter.lon.near": lon,
            "filter.radiusInMiles": radius_miles
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search locations: {e}")
            raise Exception(f"Location search failed: {e}")
    
    async def get_location_details(self, location_id: str) -> Dict:
        """
        Get details for a specific location
        GET /v1/locations/{locationId}
        """
        await self.get_client_token()
        
        url = f"{self.base_url}/v1/locations/{location_id}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.client_token}"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get location details: {e}")
            raise Exception(f"Location details failed: {e}")
    
    async def search_products(self, location_id: str, search_term: str = None, 
                            brand: str = None, product_id: str = None, 
                            limit: int = 10, start: int = 0) -> Dict:
        """
        Search for products at a specific location
        GET /v1/products
        """
        await self.get_client_token()
        
        url = f"{self.base_url}/v1/products"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.client_token}"
        }
        params = {
            "filter.locationId": location_id,
            "filter.limit": limit,
            "filter.start": start
        }
        
        # Add search criteria (at least one is required)
        if search_term:
            params["filter.term"] = search_term
        elif brand:
            params["filter.brand"] = brand
        elif product_id:
            params["filter.productId"] = product_id
        else:
            raise ValueError("At least one search criteria (term, brand, or product_id) is required")
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search products: {e}")
            raise Exception(f"Product search failed: {e}")
    
    async def get_product_details(self, product_id: str, location_id: str) -> Dict:
        """
        Get detailed information for a specific product
        GET /v1/products/{id}
        """
        await self.get_client_token()
        
        url = f"{self.base_url}/v1/products/{product_id}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.client_token}"
        }
        params = {
            "filter.locationId": location_id
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get product details: {e}")
            raise Exception(f"Product details failed: {e}")
    
    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """
        Generate authorization URL for user login
        GET /v1/connect/oauth2/authorize
        """
        if not state:
            state = f"kroger_auth_{int(time.time())}"
        
        params = {
            "scope": "cart.basic:write profile.compact",
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}/v1/connect/oauth2/authorize?{query_string}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict:
        """
        Exchange authorization code for user access token
        POST /v1/connect/oauth2/token (authorization_code)
        """
        url = f"{self.base_url}/v1/connect/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self._get_auth_header()
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise Exception(f"Token exchange failed: {e}")
    
    async def refresh_user_token(self, refresh_token: str) -> Dict:
        """
        Refresh user access token using refresh token
        POST /v1/connect/oauth2/token (refresh_token)
        """
        url = f"{self.base_url}/v1/connect/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self._get_auth_header()
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh user token: {e}")
            raise Exception(f"Token refresh failed: {e}")
    
    def store_user_token(self, session_id: str, token_data: Dict):
        """Store user token data for a session"""
        expires_at = datetime.now() + timedelta(seconds=token_data.get("expires_in", 1800))
        self.user_tokens[session_id] = {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": expires_at,
            "token_type": token_data.get("token_type", "bearer")
        }
    
    def get_user_token(self, session_id: str) -> Optional[Dict]:
        """Get stored user token for a session"""
        return self.user_tokens.get(session_id)
    
    async def get_user_profile(self, session_id: str) -> Dict:
        """
        Get user profile information
        GET /v1/identity/profile
        """
        user_token_data = self.get_user_token(session_id)
        if not user_token_data:
            raise Exception("No user token found for session")
        
        # Check if token needs refresh
        if self._is_token_expired(user_token_data["expires_at"]):
            if user_token_data.get("refresh_token"):
                try:
                    refreshed_data = await self.refresh_user_token(user_token_data["refresh_token"])
                    self.store_user_token(session_id, refreshed_data)
                    user_token_data = self.get_user_token(session_id)
                except:
                    raise Exception("Token refresh failed")
            else:
                raise Exception("Token expired and no refresh token available")
        
        url = f"{self.base_url}/v1/identity/profile"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {user_token_data['access_token']}"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get user profile: {e}")
            raise Exception(f"Profile retrieval failed: {e}")
    
    async def add_to_cart(self, session_id: str, items: List[Dict]) -> bool:
        """
        Add items to user's cart
        PUT /v1/cart/add
        """
        user_token_data = self.get_user_token(session_id)
        if not user_token_data:
            raise Exception("No user token found for session")
        
        # Check if token needs refresh
        if self._is_token_expired(user_token_data["expires_at"]):
            if user_token_data.get("refresh_token"):
                try:
                    refreshed_data = await self.refresh_user_token(user_token_data["refresh_token"])
                    self.store_user_token(session_id, refreshed_data)
                    user_token_data = self.get_user_token(session_id)
                except:
                    raise Exception("Token refresh failed")
            else:
                raise Exception("Token expired and no refresh token available")
        
        url = f"{self.base_url}/v1/cart/add"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {user_token_data['access_token']}",
            "Content-Type": "application/json"
        }
        data = {"items": items}
        
        try:
            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to add to cart: {e}")
            raise Exception(f"Add to cart failed: {e}")
    
    def clear_user_session(self, session_id: str):
        """Clear user token data for a session"""
        if session_id in self.user_tokens:
            del self.user_tokens[session_id]
