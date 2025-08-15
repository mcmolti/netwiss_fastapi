# CORS Configuration Implementation

This document describes the CORS (Cross-Origin Resource Sharing) configuration implemented for the Netwiss FastAPI project.

## Overview

The implementation provides environment-specific CORS configuration with security best practices for both the FastAPI backend and Next.js frontend.

## Backend Configuration

### Files Added/Modified

- `backend/app/config/cors.py` - New CORS configuration module
- `backend/app/main.py` - Updated to use new CORS configuration
- `backend/.env.example` - Added CORS environment variables

### Environment Variables

Add these variables to your `.env` file:

```bash
# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
CORS_ALLOW_CREDENTIALS=true
CORS_MAX_AGE=86400
ENVIRONMENT=development  # development, staging, production
```

### Features

- **Environment-specific origins**: Different allowed origins for dev/staging/production
- **Security validation**: Automatic validation of origin URLs
- **Production safety**: Strict HTTPS-only origins in production
- **Credentials handling**: Secure credential handling with origin validation
- **Logging**: Comprehensive CORS logging for debugging

## Frontend Configuration

### Files Added/Modified

- `frontend/.env.local` - Updated with comprehensive environment variables
- `frontend/.env.development` - Development-specific configuration
- `frontend/.env.production` - Production-specific configuration
- `frontend/src/lib/api.ts` - Enhanced API client with CORS handling
- `frontend/src/lib/health.ts` - Health check and CORS testing utilities
- `frontend/src/components/CORSTest.tsx` - CORS testing component
- `frontend/next.config.ts` - Security headers configuration

### Environment Variables

The frontend now supports these environment variables:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_API_RETRY_ATTEMPTS=3
NEXT_PUBLIC_API_RETRY_DELAY=1000

# Environment and Security
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_ENABLE_CORS_LOGGING=true

# Feature Flags
NEXT_PUBLIC_ENABLE_DEBUG_MODE=true
NEXT_PUBLIC_ENABLE_ERROR_REPORTING=false
NEXT_PUBLIC_ENABLE_REQUEST_LOGGING=true
```

### Enhanced API Client Features

- **Automatic retry logic**: Retries failed requests with exponential backoff
- **CORS error handling**: Specific handling for CORS-related errors
- **Request/response logging**: Configurable logging for debugging
- **Timeout handling**: Configurable request timeouts
- **Credentials management**: Automatic inclusion of credentials for CORS

## Testing

### Automated CORS Testing

1. **Backend Health Check**: Test backend CORS configuration
   ```bash
   curl -H "Origin: http://localhost:3000" http://localhost:8000/health
   ```

2. **Frontend Component**: Use the `CORSTest` component in your app:
   ```tsx
   import CORSTest from '@/components/CORSTest'
   
   // In your component
   <CORSTest showDetails={true} />
   ```

3. **Node.js Test Script**: Run the comprehensive CORS test:
   ```bash
   node test-cors.js
   ```

### Manual Testing

1. **Check CORS headers** in browser dev tools Network tab
2. **Verify preflight requests** for POST/PUT/DELETE operations
3. **Test with different origins** to ensure security

## Environment-Specific Configuration

### Development
- Allows `localhost` origins on multiple ports
- Permissive CORS settings for easier development
- Detailed logging enabled

### Staging
- Requires HTTPS origins
- Validates all configured origins
- Moderate logging

### Production
- Strict HTTPS-only origins
- No wildcard origins allowed
- Minimal logging for performance
- Additional security headers

## Security Considerations

1. **Never use wildcard origins with credentials** in production
2. **Always use HTTPS** in staging and production
3. **Validate all origins** before adding to configuration
4. **Monitor CORS violations** in production logs
5. **Regular security audits** of CORS configuration

## Troubleshooting

### Common Issues

1. **CORS error in browser**:
   - Check backend CORS origins configuration
   - Verify frontend is using correct API URL
   - Check browser console for specific error

2. **Preflight request failing**:
   - Ensure OPTIONS method is allowed
   - Check Access-Control-Allow-Headers configuration
   - Verify request headers match allowed headers

3. **Credentials not working**:
   - Ensure `allow_credentials=True` in backend
   - Verify frontend is sending `credentials: 'include'`
   - Check that origins don't include wildcards

### Debug Commands

```bash
# Test backend health
curl -H "Origin: http://localhost:3000" http://localhost:8000/health

# Test preflight request
curl -X OPTIONS -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     http://localhost:8000/api/v1/templates/

# Run comprehensive test
node test-cors.js
```

## Next Steps

For production deployment:

1. Update `CORS_ORIGINS` with actual production domains
2. Set `ENVIRONMENT=production`
3. Configure HTTPS certificates
4. Set up monitoring for CORS violations
5. Review and update security headers

## Support

For issues or questions about the CORS configuration, check:

1. Browser console for CORS errors
2. Backend logs for CORS violations
3. Network tab for failed preflight requests
4. Use the built-in testing tools provided
