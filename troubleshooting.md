# Troubleshooting Guide

## Common Authentication Issues

### 1. 401 Unauthorized Error

**Error:** `Authentication failed: 401 Client Error: Unauthorized`

**Possible Causes:**

#### A. Invalid Credentials
- **Check:** Your `KROGER_CLIENT_ID` and `KROGER_CLIENT_SECRET` are correct
- **Solution:** Verify credentials in Kroger Developer Portal
- **Debug:** Visit `http://localhost:5000/api/debug/auth` to check configuration

#### B. Credentials Not Set
- **Check:** Environment variables are properly set
- **Solution:** 
  ```bash
  export KROGER_CLIENT_ID="your-actual-client-id"
  export KROGER_CLIENT_SECRET="your-actual-client-secret"
  ```

#### C. Wrong Environment
- **Check:** You're using the correct environment (Production vs Certification)
- **Solution:** Ensure you're using Production credentials for `https://api.kroger.com`

#### D. Base64 Encoding Issues
- **Check:** Client ID and secret contain special characters
- **Solution:** Ensure no extra spaces or newlines in credentials

### 2. Debug Steps

1. **Check Configuration:**
   ```bash
   curl http://localhost:5000/api/debug/auth
   ```

2. **Verify Environment Variables:**
   ```bash
   echo $KROGER_CLIENT_ID
   echo $KROGER_CLIENT_SECRET
   ```

3. **Test Manual Authentication:**
   ```bash
   curl -X POST https://api.kroger.com/v1/connect/oauth2/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -H "Authorization: Basic $(echo -n 'YOUR_CLIENT_ID:YOUR_CLIENT_SECRET' | base64)" \
     -d "grant_type=client_credentials&scope=product.compact"
   ```

### 3. Common Solutions

#### Solution 1: Verify Kroger Developer Portal
1. Go to [Kroger Developer Portal](https://developer.kroger.com)
2. Check your application credentials
3. Ensure the application is approved and active
4. Verify you're using the correct environment

#### Solution 2: Check Credential Format
```python
# Test credential format
import base64
client_id = "your-client-id"
client_secret = "your-client-secret"
credentials = f"{client_id}:{client_secret}"
encoded = base64.b64encode(credentials.encode()).decode()
print(f"Auth header: Basic {encoded}")
```

#### Solution 3: Environment Variable Issues
```bash
# Check if variables are set
env | grep KROGER

# Set variables correctly (no spaces around =)
export KROGER_CLIENT_ID="your-id"
export KROGER_CLIENT_SECRET="your-secret"

# Verify they're set
echo "Client ID: $KROGER_CLIENT_ID"
echo "Client Secret: $KROGER_CLIENT_SECRET"
```

### 4. Testing Authentication

#### Test 1: Debug Endpoint
```bash
curl http://localhost:5000/api/debug/auth
```

Expected output:
```json
{
  "client_id_configured": true,
  "client_secret_configured": true,
  "client_id_length": 32,
  "client_secret_length": 64,
  "auth_header_preview": "Basic YWJjZGVmZ2hp...",
  "base_url": "https://api.kroger.com",
  "environment_vars": {
    "KROGER_CLIENT_ID": "Set",
    "KROGER_CLIENT_SECRET": "Set"
  }
}
```

#### Test 2: Manual API Call
```bash
# Replace with your actual credentials
CLIENT_ID="your-client-id"
CLIENT_SECRET="your-client-secret"
AUTH_HEADER=$(echo -n "$CLIENT_ID:$CLIENT_SECRET" | base64)

curl -X POST https://api.kroger.com/v1/connect/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Basic $AUTH_HEADER" \
  -d "grant_type=client_credentials&scope=product.compact"
```

### 5. Environment-Specific Issues

#### Development Environment
- Use `https://api-ce.kroger.com` for testing
- Ensure you have certification environment credentials

#### Production Environment
- Use `https://api.kroger.com`
- Ensure you have production credentials
- Verify your application is approved for production

### 6. Log Analysis

Check the application logs for detailed error information:
```bash
# View logs
tail -f kroger_api.log

# Look for these patterns:
# - "Authentication failed with status 401"
# - "Response body: ..."
# - "Request headers: ..."
```

### 7. Still Having Issues?

1. **Double-check credentials** in Kroger Developer Portal
2. **Verify environment** (Production vs Certification)
3. **Check application status** in Kroger Developer Portal
4. **Contact Kroger API Support** if credentials are correct but still failing
5. **Check rate limits** - you might have exceeded daily limits

### 8. Quick Fix Checklist

- [ ] Credentials are set correctly
- [ ] No extra spaces in environment variables
- [ ] Using correct environment (Production)
- [ ] Application is approved in Kroger Developer Portal
- [ ] No special characters causing encoding issues
- [ ] Check logs for detailed error messages
