# Kroger API Integration

A complete Flask-based integration with Kroger's APIs for location search, product browsing, and cart operations.

## Features

- **OAuth2 Authentication**: Client credentials and authorization code flows
- **Location Search**: Find Kroger stores near user coordinates
- **Product Search**: Search products with location-specific pricing and inventory
- **Cart Operations**: Add items to authenticated user's cart
- **Token Management**: Automatic token refresh and session management
- **Web Interface**: Interactive demo interface

## Files Overview

- **`main.py`** - Application entry point with environment validation and logging
- **`service.py`** - Core API service with all Kroger API integrations
- **`routes.py`** - Flask web application with REST API endpoints
- **`requirements.txt`** - Python dependencies
- **`config_guide.md`** - Configuration setup guide

## API Flow

1. **App Initialization**: Get client credentials token
2. **Location Search**: Find stores near user coordinates
3. **Product Search**: Browse products with location-specific data
4. **User Authentication**: OAuth2 authorization code flow
5. **Cart Operations**: Add items to user's cart

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file or set these environment variables:

```bash
export KROGER_CLIENT_ID="your-kroger-client-id"
export KROGER_CLIENT_SECRET="your-kroger-client-secret"
export REDIRECT_URI="http://localhost:5000/auth/callback"
export SECRET_KEY="your-secret-key-for-sessions"
```

### 3. Run the Application

**Option 1: Using main.py (Recommended)**
```bash
python main.py
```

**Option 2: Using routes.py directly**
```bash
python routes.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/initialize` - Initialize app with client credentials
- `GET /auth/login` - Redirect to Kroger authorization
- `GET /auth/callback` - Handle OAuth callback
- `GET /api/logout` - Logout user

### Locations
- `GET /api/locations/search?lat={lat}&lon={lon}&radius={radius}` - Search locations
- `GET /api/locations/{location_id}` - Get location details

### Products
- `GET /api/products/search?location_id={id}&term={term}` - Search products
- `GET /api/products/{product_id}?location_id={id}` - Get product details

### User Operations
- `GET /api/profile` - Get user profile
- `POST /api/cart/add` - Add items to cart

## Usage Example

### 1. Initialize the Service

```python
from service import KrogerAPIService

# Initialize with your credentials
kroger_service = KrogerAPIService(
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Get client token
client_token = await kroger_service.get_client_token()
```

### 2. Search Locations

```python
# Search for stores near coordinates
locations = await kroger_service.search_locations(
    lat=39.306346,
    lon=-84.278902,
    radius_miles=10
)
```

### 3. Search Products

```python
# Search products at a specific location
products = await kroger_service.search_products(
    location_id="01400376",
    search_term="milk"
)
```

### 4. User Authentication

```python
# Get authorization URL
auth_url = kroger_service.get_authorization_url(
    redirect_uri="http://localhost:5000/auth/callback"
)

# Exchange code for token (after user authorization)
token_data = await kroger_service.exchange_code_for_token(
    code="authorization_code",
    redirect_uri="http://localhost:5000/auth/callback"
)

# Store token for user session
kroger_service.store_user_token("session_id", token_data)
```

### 5. Add to Cart

```python
# Add items to user's cart
items = [
    {
        "upc": "0001200016268",
        "quantity": 2,
        "modality": "PICKUP"
    }
]

success = await kroger_service.add_to_cart("session_id", items)
```

## Web Interface

The application includes a web interface at `http://localhost:5000` that demonstrates:

1. **App Initialization**: Get client credentials token
2. **Location Search**: Enter coordinates to find nearby stores
3. **Store Selection**: Choose a store from search results
4. **Product Search**: Search for products at the selected store
5. **User Authentication**: Login with Kroger credentials
6. **Cart Operations**: Add selected products to cart

## Token Management

The service automatically handles:

- **Client Token Refresh**: Automatically renews when expired
- **User Token Refresh**: Uses refresh tokens to maintain user sessions
- **Session Storage**: Stores tokens per user session
- **Error Handling**: Graceful handling of token expiration

## Rate Limits

- **Products API**: 10,000 calls per day
- **Locations API**: 1,600 calls per day per endpoint
- **Cart API**: 5,000 calls per day
- **Identity API**: 5,000 calls per day

## Error Handling

The service includes comprehensive error handling for:

- Authentication failures
- Token expiration
- API rate limits
- Network errors
- Invalid parameters

## Security Notes

- Store credentials securely (use environment variables)
- Use HTTPS in production
- Implement proper session management
- Validate all user inputs
- Handle OAuth state parameters securely

## Production Considerations

1. **Environment Variables**: Use secure environment variable management
2. **HTTPS**: Always use HTTPS in production
3. **Session Security**: Use secure session keys and proper session management
4. **Error Logging**: Implement proper logging and monitoring
5. **Rate Limiting**: Implement client-side rate limiting
6. **Database**: Consider using a database for token storage in production

## API Documentation

For detailed API documentation, refer to the Kroger Developer Portal:
- [Authorization Endpoints](https://developer.kroger.com/reference/api/authorization-endpoints-public)
- [Locations API](https://developer.kroger.com/reference/api/locations-api-public)
- [Products API](https://developer.kroger.com/reference/api/products-api-public)
- [Cart API](https://developer.kroger.com/reference/api/cart-api-public)
- [Identity API](https://developer.kroger.com/reference/api/identity-api-public)
