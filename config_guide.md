# Configuration Guide

## Environment Variables Setup

Create a `.env` file in the project root with the following variables:

```bash
# Required: Kroger API Credentials
KROGER_CLIENT_ID=your-kroger-client-id-here
KROGER_CLIENT_SECRET=your-kroger-client-secret-here

# Optional: Application Configuration
REDIRECT_URI=http://localhost:8080/auth/callback
SECRET_KEY=your-secret-key-for-sessions-change-this-in-production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   # Option 1: Create .env file
   cp .env.example .env
   # Edit .env with your actual values
   
   # Option 2: Export environment variables
   export KROGER_CLIENT_ID="your-client-id"
   export KROGER_CLIENT_SECRET="your-client-secret"
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Open your browser:**
   ```
   http://localhost:5000
   ```

## Production Configuration

For production deployment, ensure you:

1. Set a strong `SECRET_KEY`
2. Use HTTPS for `REDIRECT_URI`
3. Set `FLASK_DEBUG=False`
4. Use a proper WSGI server (gunicorn, uwsgi, etc.)
5. Set up proper logging and monitoring

## Troubleshooting

- **Missing credentials**: Ensure `KROGER_CLIENT_ID` and `KROGER_CLIENT_SECRET` are set
- **Port already in use**: Change `FLASK_PORT` to a different port
- **CORS issues**: Ensure `REDIRECT_URI` matches your registered redirect URI in Kroger Developer Portal
