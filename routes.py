"""
Kroger API Routes
Flask routes implementing the complete Kroger API integration flow.
"""

from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
import asyncio
import uuid
import os
from service import KrogerAPIService
import logging

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Initialize Kroger API service
# These should be set as environment variables in production
KROGER_CLIENT_ID = os.environ.get('KROGER_CLIENT_ID', 'your-client-id')
KROGER_CLIENT_SECRET = os.environ.get('KROGER_CLIENT_SECRET', 'your-client-secret')
REDIRECT_URI = os.environ.get('REDIRECT_URI', 'http://localhost:8080/auth/callback')

kroger_service = KrogerAPIService(KROGER_CLIENT_ID, KROGER_CLIENT_SECRET)

def ensure_session():
    """Ensure session is properly initialized"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True
        logger.info(f"Initialized new session: {session['session_id']}")
    return session['session_id']

# HTML templates for the web interface
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kroger API Integration</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
        #checkout-btn { background: #28a745; font-weight: bold; }
        #checkout-btn:hover:not(:disabled) { background: #218838; }
        input, select { padding: 8px; margin: 5px; width: 200px; }
        .location-item { padding: 10px; margin: 5px 0; border: 1px solid #eee; border-radius: 3px; cursor: pointer; }
        .location-item:hover { background: #f5f5f5; }
        .product-item { padding: 10px; margin: 5px 0; border: 1px solid #eee; border-radius: 3px; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin: 20px 0; }
        @media (max-width: 768px) {
            .products-grid { grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }
        }
        .product-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .product-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
        .product-image { width: 100%; height: 200px; object-fit: cover; border-radius: 4px; margin-bottom: 10px; }
        .product-title { font-weight: bold; font-size: 16px; margin-bottom: 8px; color: #333; }
        .product-brand { color: #666; font-size: 14px; margin-bottom: 5px; }
        .product-price { font-size: 18px; font-weight: bold; color: #28a745; margin-bottom: 5px; }
        .product-stock { font-size: 12px; margin-bottom: 10px; }
        .product-upc { font-size: 11px; color: #999; margin-bottom: 10px; }
        .product-checkbox { margin-right: 8px; }
        .quantity-selector { display: none; align-items: center; margin: 10px 0; }
        .quantity-selector.show { display: flex; }
        .product-card.selected { border-color: #007bff; box-shadow: 0 4px 8px rgba(0,123,255,0.2); }
        .view-details-btn { background: #6c757d; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-top: 10px; width: 100%; }
        .view-details-btn:hover { background: #5a6268; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }
        .modal-content { background-color: #fefefe; margin: 5% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 600px; border-radius: 8px; max-height: 80vh; overflow-y: auto; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .modal-title { font-size: 24px; font-weight: bold; color: #333; }
        .close { color: #aaa; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close:hover { color: #000; }
        .modal-body { line-height: 1.6; }
        .product-detail-section { margin-bottom: 15px; }
        .product-detail-label { font-weight: bold; color: #555; margin-bottom: 5px; }
        .product-detail-value { color: #333; }
        .product-images { display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0; }
        .product-image-modal { width: 100px; height: 100px; object-fit: cover; border-radius: 4px; }
        .quantity-input { width: 60px; padding: 4px 8px; margin: 0 5px; border: 1px solid #ddd; border-radius: 4px; text-align: center; }
        .quantity-btn { width: 30px; height: 30px; border: 1px solid #ddd; background: #f8f9fa; cursor: pointer; border-radius: 4px; display: flex; align-items: center; justify-content: center; }
        .quantity-btn:hover { background: #e9ecef; }
        .quantity-btn:disabled { background: #f8f9fa; cursor: not-allowed; opacity: 0.5; }
        .stock-high { color: #28a745; }
        .stock-low { color: #ffc107; }
        .stock-out { color: #dc3545; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Kroger API Integration Demo</h1>
        
        <div class="section">
            <h3>1. Initialize App</h3>
            <button onclick="initializeApp()">Get Client Token</button>
            <div id="init-status"></div>
        </div>
        
        <div class="section">
            <h3>2. Find Store Location</h3>
            <input type="number" id="latitude" placeholder="Latitude" step="any" value="39.306346">
            <input type="number" id="longitude" placeholder="Longitude" step="any" value="-84.278902">
            <input type="number" id="radius" placeholder="Radius (miles)" value="10">
            <button onclick="searchLocations()">Search Locations</button>
            <div id="locations"></div>
        </div>
        
        <div class="section">
            <h3>3. Search Products</h3>
            <input type="text" id="search-term" placeholder="Search term (e.g., milk)" value="milk">
            <input type="text" id="brand" placeholder="Brand (optional)">
            <button onclick="searchProducts()">Search Products</button>
            <div id="products"></div>
        </div>
        
        <div class="section">
            <h3>4. User Authentication & Cart</h3>
            <button onclick="authenticateUser()" id="login-btn">Login to Kroger</button>
            <button onclick="addToCart()" id="add-cart-btn" disabled>Add Selected to Cart</button>
            <button onclick="checkout()" id="checkout-btn" disabled>Checkout</button>
            <button onclick="logout()" id="logout-btn" style="display:none;">Logout</button>
            <div id="auth-status"></div>
        </div>
    </div>

    <!-- Product Details Modal -->
    <div id="productModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title" id="modalProductTitle">Product Details</h2>
                <span class="close">&times;</span>
            </div>
            <div class="modal-body" id="modalProductBody">
                <!-- Product details will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        let selectedLocationId = null;
        let selectedProducts = [];
        let isAuthenticated = false;
        
        // Check authentication status on page load
        window.onload = function() {
            checkAuthStatus();
            initializeModal();
        };
        
        function initializeModal() {
            // Get the modal
            const modal = document.getElementById('productModal');
            const closeBtn = document.getElementsByClassName('close')[0];
            
            // Close modal when clicking the X
            closeBtn.onclick = function() {
                modal.style.display = 'none';
            }
            
            // Close modal when clicking outside of it
            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            }
        }
        
        async function checkAuthStatus() {
            try {
                const response = await fetch('/api/debug/session');
                const data = await response.json();
                
                if (data.has_user_token) {
                    isAuthenticated = true;
                    document.getElementById('login-btn').style.display = 'none';
                    document.getElementById('logout-btn').style.display = 'inline-block';
                    document.getElementById('add-cart-btn').disabled = false;
                    document.getElementById('checkout-btn').disabled = false;
                    document.getElementById('auth-status').innerHTML = 
                        '<div class="success">✓ Authenticated with Kroger</div>';
                } else {
                    isAuthenticated = false;
                    document.getElementById('login-btn').style.display = 'inline-block';
                    document.getElementById('logout-btn').style.display = 'none';
                    document.getElementById('add-cart-btn').disabled = true;
                    document.getElementById('checkout-btn').disabled = true;
                    document.getElementById('auth-status').innerHTML = 
                        '<div class="error">✗ Not authenticated</div>';
                }
            } catch (error) {
                console.error('Error checking auth status:', error);
            }
        }
        
        async function initializeApp() {
            try {
                const response = await fetch('/api/initialize', { method: 'POST' });
                const data = await response.json();
                if (response.ok) {
                    document.getElementById('init-status').innerHTML = 
                        '<div class="success">✓ App initialized successfully</div>';
                } else {
                    document.getElementById('init-status').innerHTML = 
                        '<div class="error">✗ Initialization failed: ' + data.error + '</div>';
                }
            } catch (error) {
                document.getElementById('init-status').innerHTML = 
                    '<div class="error">✗ Error: ' + error.message + '</div>';
            }
        }
        
        async function searchLocations() {
            const lat = document.getElementById('latitude').value;
            const lon = document.getElementById('longitude').value;
            const radius = document.getElementById('radius').value;
            
            try {
                const response = await fetch(`/api/locations/search?lat=${lat}&lon=${lon}&radius=${radius}`);
                const data = await response.json();
                
                if (response.ok) {
                    let html = '<h4>Select a Store:</h4>';
                    data.data.forEach(location => {
                        html += `<div class="location-item" onclick="selectLocation('${location.locationId}', '${location.name}')">
                            <strong>${location.name}</strong><br>
                            ${location.address.addressLine1}, ${location.address.city}, ${location.address.state} ${location.address.zipCode}<br>
                            Phone: ${location.phone}
                        </div>`;
                    });
                    document.getElementById('locations').innerHTML = html;
                } else {
                    document.getElementById('locations').innerHTML = 
                        '<div class="error">✗ Location search failed: ' + data.error + '</div>';
                }
            } catch (error) {
                document.getElementById('locations').innerHTML = 
                    '<div class="error">✗ Error: ' + error.message + '</div>';
            }
        }
        
        function selectLocation(locationId, name) {
            selectedLocationId = locationId;
            document.getElementById('locations').innerHTML = 
                `<div class="success">✓ Selected: ${name} (${locationId})</div>`;
        }
        
        async function searchProducts() {
            if (!selectedLocationId) {
                alert('Please select a store location first');
                return;
            }
            
            const searchTerm = document.getElementById('search-term').value;
            const brand = document.getElementById('brand').value;
            
            try {
                let url = `/api/products/search?location_id=${selectedLocationId}`;
                if (searchTerm) url += `&term=${searchTerm}`;
                if (brand) url += `&brand=${brand}`;
                
                const response = await fetch(url);
                const data = await response.json();
                
                if (response.ok) {
                    let html = '<h4>Products:</h4><div class="products-grid">';
                    selectedProducts = [];
                    data.data.forEach(product => {
                        const price = product.items && product.items[0] && product.items[0].price ? 
                            `$${product.items[0].price.regular}` : 'Price N/A';
                        const stock = product.items && product.items[0] && product.items[0].inventory ? 
                            product.items[0].inventory.stockLevel : 'Stock N/A';
                        
                        // Get product image
                        let imageUrl = '';
                        if (product.images && product.images.length > 0) {
                            const image = product.images[0];
                            if (image.sizes && image.sizes.length > 0) {
                                // Try to find medium or large image
                                const mediumImage = image.sizes.find(s => s.size === 'medium') || 
                                                 image.sizes.find(s => s.size === 'large') || 
                                                 image.sizes[0];
                                imageUrl = mediumImage.url;
                            }
                        }
                        
                        // Set stock color class
                        let stockClass = 'stock-high';
                        if (stock === 'LOW') stockClass = 'stock-low';
                        if (stock === 'TEMPORARILY_OUT_OF_STOCK') stockClass = 'stock-out';
                        
                        html += `<div class="product-card">
                            <input type="checkbox" class="product-checkbox" id="prod-${product.productId}" value="${product.upc}" onchange="updateProductQuantity('${product.upc}')">
                            ${imageUrl ? 
                                `<img src="${imageUrl}" alt="${product.description}" class="product-image" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxwYXRoIGQ9Ik0xMDAgNTBMMTUwIDEwMEgxMzBWMTUwSDcwVjEwMEg1MEwxMDAgNTBaIiBmaWxsPSIjQ0NDQ0NDIi8+Cjx0ZXh0IHg9IjEwMCIgeT0iMTgwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOTk5OTk5IiBmb250LXNpemU9IjEyIj5ObyBJbWFnZTwvdGV4dD4KPC9zdmc+'; this.onerror=null;">` : 
                                `<div class="product-image" style="background: #f5f5f5; display: flex; align-items: center; justify-content: center; color: #999; font-size: 14px;">No Image</div>`
                            }
                            <div class="product-title">${product.description}</div>
                            <div class="product-brand">${product.brand || 'N/A'}</div>
                            <div class="product-price">${price}</div>
                            <div class="product-stock ${stockClass}">Stock: ${stock}</div>
                            <div class="product-upc">UPC: ${product.upc}</div>
                            <div class="quantity-selector">
                                <button type="button" class="quantity-btn" onclick="decreaseQuantity('${product.upc}')" id="dec-${product.productId}">-</button>
                                <input type="number" class="quantity-input" id="qty-${product.productId}" value="1" min="1" max="10" onchange="updateQuantityInput('${product.upc}')">
                                <button type="button" class="quantity-btn" onclick="increaseQuantity('${product.upc}')" id="inc-${product.productId}">+</button>
                            </div>
                            <button class="view-details-btn" onclick="viewProductDetails('${product.productId}')">View Details</button>
                        </div>`;
                        selectedProducts.push({
                            upc: product.upc,
                            quantity: 1,
                            modality: 'PICKUP'
                        });
                    });
                    html += '</div>';
                    document.getElementById('products').innerHTML = html;
                    
                    // Initialize quantity displays (hidden by default)
                    selectedProducts.forEach(product => {
                        updateQuantityDisplay(product.upc, product.quantity);
                    });
                } else {
                    document.getElementById('products').innerHTML = 
                        '<div class="error">✗ Product search failed: ' + data.error + '</div>';
                }
            } catch (error) {
                document.getElementById('products').innerHTML = 
                    '<div class="error">✗ Error: ' + error.message + '</div>';
            }
        }
        
        function authenticateUser() {
            window.location.href = '/auth/login';
        }
        
        async function logout() {
            try {
                const response = await fetch('/api/logout', { method: 'GET' });
                const data = await response.json();
                
                if (response.ok) {
                    // Refresh the page to update UI
                    window.location.reload();
                } else {
                    alert('Logout failed: ' + data.error);
                }
            } catch (error) {
                alert('Error during logout: ' + error.message);
            }
        }
        
        function checkout() {
            if (!isAuthenticated) {
                alert('Please login to Kroger first');
                return;
            }
            
            // Redirect to Kroger cart page
            window.open('https://www.kroger.com/cart', '_blank');
        }
        
        async function viewProductDetails(productId) {
            if (!selectedLocationId) {
                alert('Please select a store location first');
                return;
            }
            
            try {
                // Show loading state
                const modal = document.getElementById('productModal');
                const modalBody = document.getElementById('modalProductBody');
                const modalTitle = document.getElementById('modalProductTitle');
                
                modalTitle.textContent = 'Loading Product Details...';
                modalBody.innerHTML = '<div style="text-align: center; padding: 20px;">Loading...</div>';
                modal.style.display = 'block';
                
                // Fetch detailed product information
                const response = await fetch(`/api/products/${productId}?location_id=${selectedLocationId}`);
                const data = await response.json();
                
                if (response.ok) {
                    displayProductDetails(data.data);
                } else {
                    modalTitle.textContent = 'Error';
                    modalBody.innerHTML = `<div class="error">Failed to load product details: ${data.error}</div>`;
                }
            } catch (error) {
                const modal = document.getElementById('productModal');
                const modalBody = document.getElementById('modalProductBody');
                const modalTitle = document.getElementById('modalProductTitle');
                
                modalTitle.textContent = 'Error';
                modalBody.innerHTML = `<div class="error">Error loading product details: ${error.message}</div>`;
                modal.style.display = 'block';
            }
        }
        
        function displayProductDetails(product) {
            const modal = document.getElementById('productModal');
            const modalBody = document.getElementById('modalProductBody');
            const modalTitle = document.getElementById('modalProductTitle');
            
            modalTitle.textContent = product.description || 'Product Details';
            
            // Get product images
            let imagesHtml = '';
            if (product.images && product.images.length > 0) {
                imagesHtml = '<div class="product-detail-section"><div class="product-detail-label">Images:</div><div class="product-images">';
                product.images.forEach(image => {
                    if (image.sizes && image.sizes.length > 0) {
                        const imageUrl = image.sizes[0].url;
                        imagesHtml += `<img src="${imageUrl}" alt="${product.description}" class="product-image-modal" onerror="this.style.display='none'">`;
                    }
                });
                imagesHtml += '</div></div>';
            }
            
            // Get pricing information
            let pricingHtml = '';
            if (product.items && product.items[0]) {
                const item = product.items[0];
                if (item.price) {
                    pricingHtml = `
                        <div class="product-detail-section">
                            <div class="product-detail-label">Pricing:</div>
                            <div class="product-detail-value">
                                Regular Price: $${item.price.regular || 'N/A'}<br>
                                ${item.price.promo ? `Sale Price: $${item.price.promo}<br>` : ''}
                                ${item.price.regularPerUnitEstimate ? `Per Unit: $${item.price.regularPerUnitEstimate}<br>` : ''}
                            </div>
                        </div>
                    `;
                }
                
                if (item.nationalPrice) {
                    pricingHtml += `
                        <div class="product-detail-section">
                            <div class="product-detail-label">National Pricing:</div>
                            <div class="product-detail-value">
                                Regular: $${item.nationalPrice.regular || 'N/A'}<br>
                                ${item.nationalPrice.promo ? `Sale: $${item.nationalPrice.promo}<br>` : ''}
                            </div>
                        </div>
                    `;
                }
            }
            
            // Get fulfillment information
            let fulfillmentHtml = '';
            if (product.items && product.items[0] && product.items[0].fulfillment) {
                const fulfillment = product.items[0].fulfillment;
                fulfillmentHtml = `
                    <div class="product-detail-section">
                        <div class="product-detail-label">Availability:</div>
                        <div class="product-detail-value">
                            In Store: ${fulfillment.instore ? 'Yes' : 'No'}<br>
                            Delivery: ${fulfillment.delivery ? 'Yes' : 'No'}<br>
                            Curbside Pickup: ${fulfillment.curbside ? 'Yes' : 'No'}<br>
                            Ship to Home: ${fulfillment.shiptohome ? 'Yes' : 'No'}
                        </div>
                    </div>
                `;
            }
            
            // Get aisle locations
            let aisleHtml = '';
            if (product.aisleLocations && product.aisleLocations.length > 0) {
                aisleHtml = '<div class="product-detail-section"><div class="product-detail-label">Aisle Locations:</div><div class="product-detail-value">';
                product.aisleLocations.forEach(location => {
                    aisleHtml += `${location.description || 'Aisle ' + location.number}<br>`;
                });
                aisleHtml += '</div></div>';
            }
            
            modalBody.innerHTML = `
                ${imagesHtml}
                <div class="product-detail-section">
                    <div class="product-detail-label">Product ID:</div>
                    <div class="product-detail-value">${product.productId}</div>
                </div>
                <div class="product-detail-section">
                    <div class="product-detail-label">UPC:</div>
                    <div class="product-detail-value">${product.upc}</div>
                </div>
                <div class="product-detail-section">
                    <div class="product-detail-label">Brand:</div>
                    <div class="product-detail-value">${product.brand || 'N/A'}</div>
                </div>
                <div class="product-detail-section">
                    <div class="product-detail-label">Categories:</div>
                    <div class="product-detail-value">${product.categories ? product.categories.join(', ') : 'N/A'}</div>
                </div>
                <div class="product-detail-section">
                    <div class="product-detail-label">Country of Origin:</div>
                    <div class="product-detail-value">${product.countryOrigin || 'N/A'}</div>
                </div>
                ${pricingHtml}
                ${fulfillmentHtml}
                ${aisleHtml}
                <div class="product-detail-section">
                    <div class="product-detail-label">Product Page:</div>
                    <div class="product-detail-value">
                        <a href="https://www.kroger.com${product.productPageURI}" target="_blank" style="color: #007bff;">
                            View on Kroger.com
                        </a>
                    </div>
                </div>
            `;
            
            modal.style.display = 'block';
        }
        
        function increaseQuantity(upc) {
            const input = document.querySelector(`input[value="${upc}"]`);
            if (!input.checked) return; // Only work if product is selected
            
            const product = selectedProducts.find(p => p.upc === upc);
            if (product && product.quantity < 10) {
                product.quantity++;
                updateQuantityDisplay(upc, product.quantity);
            }
        }
        
        function decreaseQuantity(upc) {
            const input = document.querySelector(`input[value="${upc}"]`);
            if (!input.checked) return; // Only work if product is selected
            
            const product = selectedProducts.find(p => p.upc === upc);
            if (product && product.quantity > 1) {
                product.quantity--;
                updateQuantityDisplay(upc, product.quantity);
            }
        }
        
        function updateQuantityInput(upc) {
            const input = document.querySelector(`input[value="${upc}"]`);
            if (!input.checked) return; // Only work if product is selected
            
            const product = selectedProducts.find(p => p.upc === upc);
            if (product) {
                const quantityInput = input.closest('.product-card').querySelector('.quantity-input');
                let newQuantity = parseInt(quantityInput.value);
                
                // Validate quantity
                if (isNaN(newQuantity) || newQuantity < 1) {
                    newQuantity = 1;
                } else if (newQuantity > 10) {
                    newQuantity = 10;
                }
                
                product.quantity = newQuantity;
                updateQuantityDisplay(upc, newQuantity);
            }
        }
        
        function updateQuantityDisplay(upc, quantity) {
            const product = selectedProducts.find(p => p.upc === upc);
            if (product) {
                const input = document.querySelector(`input[value="${upc}"]`);
                const card = input.closest('.product-card');
                const quantityInput = card.querySelector('.quantity-input');
                const decBtn = card.querySelector('[onclick*="decreaseQuantity"]');
                const incBtn = card.querySelector('[onclick*="increaseQuantity"]');
                
                // Update input value
                quantityInput.value = quantity;
                
                // Update button states
                decBtn.disabled = quantity <= 1;
                incBtn.disabled = quantity >= 10;
            }
        }
        
        function updateProductQuantity(upc) {
            const input = document.querySelector(`input[value="${upc}"]`);
            const card = input.closest('.product-card');
            const quantitySelector = card.querySelector('.quantity-selector');
            const quantityInput = card.querySelector('.quantity-input');
            const quantity = parseInt(quantityInput.value) || 1;
            
            const product = selectedProducts.find(p => p.upc === upc);
            
            if (input.checked) {
                // Show quantity selector when product is selected
                quantitySelector.classList.add('show');
                card.classList.add('selected');
                if (product) {
                    product.quantity = quantity;
                }
            } else {
                // Hide quantity selector when product is deselected
                quantitySelector.classList.remove('show');
                card.classList.remove('selected');
                if (product) {
                    product.quantity = 1; // Reset to default
                }
            }
        }
        
        async function addToCart() {
            if (!isAuthenticated) {
                alert('Please login to Kroger first');
                return;
            }
            const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
            if (checkboxes.length === 0) {
                alert('Please select products to add to cart');
                return;
            }
            
            const items = Array.from(checkboxes).map(cb => {
                const product = selectedProducts.find(p => p.upc === cb.value);
                return {
                    upc: product?.upc,
                    quantity: product?.quantity || 1,
                    modality: 'PICKUP'
                };
            }).filter(item => item.upc);
            
            try {
                const response = await fetch('/api/cart/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ items })
                });
                const data = await response.json();
                
                if (response.ok) {
                    // Show success message in auth status area
                    document.getElementById('auth-status').innerHTML = 
                        '<div class="success">✓ Items added to cart successfully!</div>';
                    // Uncheck all checkboxes after successful add
                    checkboxes.forEach(cb => cb.checked = false);
                    // Reset auth status after 3 seconds
                    setTimeout(checkAuthStatus, 3000);
                } else {
                    document.getElementById('auth-status').innerHTML = 
                        '<div class="error">✗ Failed to add to cart: ' + data.error + '</div>';
                    setTimeout(checkAuthStatus, 3000);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with the integration demo"""
    return render_template_string(INDEX_TEMPLATE)

@app.route('/api/initialize', methods=['POST'])
def initialize_app():
    """Initialize the app by getting client credentials token"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(kroger_service.get_client_token())
        loop.close()
        
        return jsonify({
            "success": True,
            "message": "App initialized successfully",
            "token_info": result
        })
    except Exception as e:
        logger.error(f"App initialization failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/locations/search')
def search_locations():
    """Search for Kroger locations near given coordinates"""
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = int(request.args.get('radius', 10))
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            kroger_service.search_locations(lat, lon, radius)
        )
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Location search failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/locations/<location_id>')
def get_location_details(location_id):
    """Get details for a specific location"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            kroger_service.get_location_details(location_id)
        )
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Location details failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/search')
def search_products():
    """Search for products at a specific location"""
    try:
        location_id = request.args.get('location_id')
        search_term = request.args.get('term')
        brand = request.args.get('brand')
        product_id = request.args.get('product_id')
        limit = int(request.args.get('limit', 10))
        start = int(request.args.get('start', 0))
        
        if not location_id:
            return jsonify({"error": "location_id is required"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            kroger_service.search_products(
                location_id, search_term, brand, product_id, limit, start
            )
        )
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Product search failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<product_id>')
def get_product_details(product_id):
    """Get detailed information for a specific product"""
    try:
        location_id = request.args.get('location_id')
        if not location_id:
            return jsonify({"error": "location_id is required"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            kroger_service.get_product_details(product_id, location_id)
        )
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Product details failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/auth/login')
def login():
    """Redirect user to Kroger authorization page"""
    # Ensure session is properly initialized
    session_id = ensure_session()
    
    state = f"kroger_auth_{session_id}"
    auth_url = kroger_service.get_authorization_url(REDIRECT_URI, state)
    
    logger.info(f"Redirecting to auth URL for session: {session_id}")
    return redirect(auth_url)

@app.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback from Kroger"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        logger.info(f"Auth callback received - Code: {bool(code)}, State: {state}, Error: {error}")
        
        if error:
            logger.error(f"Authorization failed: {error}")
            return jsonify({"error": f"Authorization failed: {error}"}), 400
        
        if not code:
            logger.error("No authorization code received")
            return jsonify({"error": "No authorization code received"}), 400
        
        # Ensure session exists (create if missing)
        current_session_id = ensure_session()
        
        # Verify state matches session (more flexible matching)
        if not state:
            logger.error("No state parameter received")
            return jsonify({"error": "Invalid state parameter"}), 400
        
        # Check if state contains our session ID
        if not state.endswith(current_session_id):
            logger.warning(f"State mismatch - Expected: {current_session_id}, Got: {state}")
            # For development, we'll be more lenient
            if not state.startswith('kroger_auth_'):
                return jsonify({"error": "Invalid state parameter format"}), 400
            logger.info("Allowing callback despite state mismatch (development mode)")
        
        # Exchange code for token
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        token_data = loop.run_until_complete(
            kroger_service.exchange_code_for_token(code, REDIRECT_URI)
        )
        loop.close()
        
        # Store token in session
        kroger_service.store_user_token(current_session_id, token_data)
        
        logger.info(f"Authentication successful for session: {current_session_id}")
        # Redirect to the main page instead of returning JSON
        return redirect("/")
        
    except Exception as e:
        logger.error(f"Auth callback failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/profile')
def get_user_profile():
    """Get user profile information"""
    try:
        session_id = ensure_session()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            kroger_service.get_user_profile(session_id)
        )
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Profile retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add items to user's cart"""
    try:
        session_id = ensure_session()
        
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({"error": "No items provided"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            kroger_service.add_to_cart(session_id, items)
        )
        loop.close()
        
        if success:
            return jsonify({"success": True, "message": "Items added to cart successfully"})
        else:
            return jsonify({"error": "Failed to add items to cart"}), 500
            
    except Exception as e:
        logger.error(f"Add to cart failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout')
def logout():
    """Logout user and clear session"""
    session_id = session.get('session_id')
    if session_id:
        kroger_service.clear_user_session(session_id)
        session.pop('session_id', None)
    
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route('/api/status')
def api_status():
    """Get API status and configuration"""
    return jsonify({
        "status": "active",
        "base_url": kroger_service.base_url,
        "client_id": kroger_service.client_id[:8] + "..." if kroger_service.client_id else "Not set",
        "has_client_token": kroger_service.client_token is not None,
        "active_user_sessions": len(kroger_service.user_tokens)
    })

@app.route('/api/debug/auth')
def debug_auth():
    """Debug authentication configuration"""
    try:
        # Test the auth header generation
        auth_header = kroger_service._get_auth_header()
        
        # Check if credentials are properly set
        client_id_set = bool(kroger_service.client_id and kroger_service.client_id != "your-client-id")
        client_secret_set = bool(kroger_service.client_secret and kroger_service.client_secret != "your-client-secret")
        
        return jsonify({
            "client_id_configured": client_id_set,
            "client_secret_configured": client_secret_set,
            "client_id_length": len(kroger_service.client_id) if kroger_service.client_id else 0,
            "client_secret_length": len(kroger_service.client_secret) if kroger_service.client_secret else 0,
            "auth_header_preview": auth_header[:20] + "..." if auth_header else "Not generated",
            "base_url": kroger_service.base_url,
            "environment_vars": {
                "KROGER_CLIENT_ID": "Set" if os.environ.get('KROGER_CLIENT_ID') else "Not set",
                "KROGER_CLIENT_SECRET": "Set" if os.environ.get('KROGER_CLIENT_SECRET') else "Not set"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/session')
def debug_session():
    """Debug session information"""
    try:
        session_id = session.get('session_id')
        has_user_token = bool(session_id and kroger_service.get_user_token(session_id))
        
        return jsonify({
            "session_id": session_id,
            "has_session": bool(session_id),
            "has_user_token": has_user_token,
            "session_permanent": session.permanent,
            "user_tokens_count": len(kroger_service.user_tokens),
            "redirect_uri": REDIRECT_URI
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Set environment variables for development
    if not os.environ.get('KROGER_CLIENT_ID'):
        print("Warning: KROGER_CLIENT_ID not set. Please set environment variables.")
    if not os.environ.get('KROGER_CLIENT_SECRET'):
        print("Warning: KROGER_CLIENT_SECRET not set. Please set environment variables.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
