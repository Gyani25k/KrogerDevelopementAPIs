#!/usr/bin/env python3
"""
Kroger API Integration - Main Application Entry Point
Run this file to start the Flask application with proper configuration.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from routes import app


from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('kroger_api.log')
    ]
)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file if it exists"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info("Loaded environment variables from .env file")
    else:
        logger.warning("No .env file found. Using system environment variables.")

def validate_environment():
    """Validate that required environment variables are set"""
    required_vars = [
        'KROGER_CLIENT_ID',
        'KROGER_CLIENT_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set the following environment variables:")
        for var in missing_vars:
            logger.error(f"  export {var}='your-value'")
        return False
    
    return True

def setup_application():
    """Setup and configure the Flask application"""
    # Load environment variables
    load_environment()
    
    # Validate required environment variables
    if not validate_environment():
        sys.exit(1)
    
    # Set default values for optional environment variables
    if not os.environ.get('REDIRECT_URI'):
        os.environ['REDIRECT_URI'] = 'http://localhost:8080/auth/callback'
        logger.info("Using default REDIRECT_URI: http://localhost:8080/auth/callback")
    
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        logger.warning("Using default SECRET_KEY. Change this in production!")
    
    # Configure Flask app
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY'),
        'DEBUG': os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        'HOST': os.environ.get('FLASK_HOST', '0.0.0.0'),
        'PORT': int(os.environ.get('FLASK_PORT', 5000))
    })
    
    logger.info("Flask application configured successfully")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    logger.info(f"Host: {app.config['HOST']}")
    logger.info(f"Port: {app.config['PORT']}")

def print_startup_info():
    """Print startup information and available endpoints"""
    print("\n" + "="*60)
    print("🚀 KROGER API INTEGRATION")
    print("="*60)
    print(f"🌐 Web Interface: http://localhost:{app.config['PORT']}")
    print(f"📊 API Status: http://localhost:{app.config['PORT']}/api/status")
    print("\n📋 Available Endpoints:")
    print("  • GET  /                    - Web interface")
    print("  • POST /api/initialize      - Initialize app")
    print("  • GET  /api/locations/search - Search locations")
    print("  • GET  /api/products/search  - Search products")
    print("  • GET  /auth/login          - User authentication")
    print("  • POST /api/cart/add        - Add to cart")
    print("  • GET  /api/status          - API status")
    print("\n🔧 Environment:")
    print(f"  • Client ID: {os.environ.get('KROGER_CLIENT_ID', 'Not set')[:8]}...")
    print(f"  • Redirect URI: {os.environ.get('REDIRECT_URI')}")
    print(f"  • Debug Mode: {app.config['DEBUG']}")
    print("="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")

def main():
    """Main application entry point"""
    try:
        # Setup application
        setup_application()
        
        # Print startup information
        print_startup_info()
        
        # Start the Flask development server
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'],
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        print("\n👋 Application stopped. Goodbye!")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
