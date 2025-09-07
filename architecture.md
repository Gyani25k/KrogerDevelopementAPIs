# Kroger API Integration Architecture

## System Architecture Diagram

```mermaid
graph TB
    %% User Interface Layer
    subgraph "Frontend Layer"
        UI[Web Interface<br/>HTML/CSS/JavaScript]
        Login[Login Button]
        Search[Product Search]
        Cart[Cart Operations]
        Checkout[Checkout Button]
    end

    %% Application Layer
    subgraph "Application Layer"
        Main[main.py<br/>Application Entry Point]
        Routes[routes.py<br/>Flask Routes & API Endpoints]
        Service[service.py<br/>Kroger API Service]
    end

    %% Authentication Flow
    subgraph "Authentication Flow"
        OAuth[OAuth2 Authorization<br/>Code Flow]
        ClientAuth[Client Credentials<br/>Flow]
        TokenMgmt[Token Management<br/>& Refresh]
    end

    %% External APIs
    subgraph "Kroger APIs"
        AuthAPI[Authorization API<br/>/v1/connect/oauth2/]
        LocationAPI[Location API<br/>/v1/locations]
        ProductAPI[Product API<br/>/v1/products]
        CartAPI[Cart API<br/>/v1/cart/add]
        IdentityAPI[Identity API<br/>/v1/identity/profile]
    end

    %% Data Flow
    UI --> Routes
    Routes --> Service
    Service --> OAuth
    Service --> ClientAuth
    OAuth --> AuthAPI
    ClientAuth --> AuthAPI
    Service --> LocationAPI
    Service --> ProductAPI
    Service --> CartAPI
    Service --> IdentityAPI

    %% Authentication Flow
    Login --> OAuth
    OAuth --> TokenMgmt
    ClientAuth --> TokenMgmt
    TokenMgmt --> Service

    %% User Actions
    Search --> ProductAPI
    Cart --> CartAPI
    Checkout --> UI

    %% Styling
    classDef frontend fill:#e1f5fe
    classDef application fill:#f3e5f5
    classDef auth fill:#fff3e0
    classDef api fill:#e8f5e8
    classDef external fill:#ffebee

    class UI,Login,Search,Cart,Checkout frontend
    class Main,Routes,Service application
    class OAuth,ClientAuth,TokenMgmt auth
    class AuthAPI,LocationAPI,ProductAPI,CartAPI,IdentityAPI api
```

## Detailed Component Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Web Interface
    participant R as Routes.py
    participant S as Service.py
    participant K as Kroger APIs

    %% App Initialization
    U->>UI: Load Page
    UI->>R: GET /
    R->>S: get_client_token()
    S->>K: POST /v1/connect/oauth2/token
    K-->>S: Client Token
    S-->>R: Token Response
    R-->>UI: Page Loaded

    %% Location Search
    U->>UI: Enter Coordinates
    UI->>R: GET /api/locations/search
    R->>S: search_locations()
    S->>K: GET /v1/locations
    K-->>S: Location Data
    S-->>R: Locations
    R-->>UI: Store List

    %% Product Search
    U->>UI: Select Store & Search Products
    UI->>R: GET /api/products/search
    R->>S: search_products()
    S->>K: GET /v1/products
    K-->>S: Product Data
    S-->>R: Products
    R-->>UI: Product List

    %% User Authentication
    U->>UI: Click Login
    UI->>R: GET /auth/login
    R->>S: get_authorization_url()
    S-->>R: Auth URL
    R-->>UI: Redirect to Kroger
    U->>K: Login & Authorize
    K-->>UI: Redirect with Code
    UI->>R: GET /auth/callback
    R->>S: exchange_code_for_token()
    S->>K: POST /v1/connect/oauth2/token
    K-->>S: User Token
    S-->>R: Token Stored
    R-->>UI: Redirect to Main Page

    %% Cart Operations
    U->>UI: Select Products & Add to Cart
    UI->>R: POST /api/cart/add
    R->>S: add_to_cart()
    S->>K: PUT /v1/cart/add
    K-->>S: Success Response
    S-->>R: Success
    R-->>UI: Success Message

    %% Checkout
    U->>UI: Click Checkout
    UI->>UI: Open Kroger Cart
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Client Side"
        Browser[Web Browser]
        JS[JavaScript<br/>Frontend Logic]
    end

    subgraph "Server Side"
        Flask[Flask Application]
        Routes[API Routes]
        Service[Kroger Service]
        Session[Session Management]
    end

    subgraph "External Services"
        Kroger[Kroger APIs]
        OAuth[OAuth2 Provider]
    end

    subgraph "Data Storage"
        Memory[In-Memory<br/>Token Storage]
        SessionStore[Session Store]
    end

    Browser --> JS
    JS --> Flask
    Flask --> Routes
    Routes --> Service
    Service --> Kroger
    Service --> OAuth
    Service --> Memory
    Routes --> Session
    Session --> SessionStore

    %% Token Flow
    OAuth -.->|Access Tokens| Service
    Service -.->|Store Tokens| Memory
    Memory -.->|Retrieve Tokens| Service
```

## API Integration Flow

```mermaid
graph TD
    Start([Start]) --> Init[Initialize App]
    Init --> ClientToken[Get Client Token]
    ClientToken --> LocationSearch[Search Locations]
    LocationSearch --> StoreSelect[Select Store]
    StoreSelect --> ProductSearch[Search Products]
    ProductSearch --> UserAuth{User Authenticated?}
    
    UserAuth -->|No| Login[Login to Kroger]
    Login --> OAuthFlow[OAuth2 Flow]
    OAuthFlow --> UserToken[Get User Token]
    UserToken --> CartOps[Cart Operations]
    
    UserAuth -->|Yes| CartOps
    CartOps --> AddToCart[Add Items to Cart]
    AddToCart --> Checkout[Checkout]
    Checkout --> KrogerCart[Redirect to Kroger Cart]
    
    %% Error Handling
    ClientToken -->|Error| AuthError[Authentication Error]
    LocationSearch -->|Error| LocationError[Location Error]
    ProductSearch -->|Error| ProductError[Product Error]
    OAuthFlow -->|Error| OAuthError[OAuth Error]
    CartOps -->|Error| CartError[Cart Error]
    
    %% Styling
    classDef process fill:#e3f2fd
    classDef decision fill:#fff3e0
    classDef error fill:#ffebee
    classDef external fill:#e8f5e8
    
    class Init,ClientToken,LocationSearch,StoreSelect,ProductSearch,Login,OAuthFlow,UserToken,CartOps,AddToCart,Checkout process
    class UserAuth decision
    class AuthError,LocationError,ProductError,OAuthError,CartError error
    class KrogerCart external
```

## Component Responsibilities

### Frontend Layer
- **Web Interface**: User interaction and display
- **JavaScript**: Client-side logic and API calls
- **UI Components**: Login, search, cart, checkout buttons

### Application Layer
- **main.py**: Application entry point and configuration
- **routes.py**: Flask routes and API endpoints
- **service.py**: Core Kroger API integration logic

### Authentication Layer
- **OAuth2 Flow**: User authentication with Kroger
- **Client Credentials**: App-level authentication
- **Token Management**: Automatic token refresh and storage

### External APIs
- **Authorization API**: Token management
- **Location API**: Store search and details
- **Product API**: Product search and details
- **Cart API**: Cart operations
- **Identity API**: User profile information

## Key Features

1. **Modular Architecture**: Clear separation of concerns
2. **Token Management**: Automatic refresh and session handling
3. **Error Handling**: Comprehensive error management
4. **Session Management**: Persistent user sessions
5. **API Integration**: Complete Kroger API coverage
6. **User Experience**: Seamless authentication flow
