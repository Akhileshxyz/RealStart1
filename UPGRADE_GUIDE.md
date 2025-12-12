# Security Upgrade Guide

This document outlines all security improvements made to the RealStart application.

## 🚨 CRITICAL: Before Running the Application

### 1. Update Environment Variables

Edit your `.env` file with the following changes:

```bash
# CRITICAL: Generate a new SECRET_KEY
# Run this command: python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=<YOUR_NEW_SECRET_KEY_HERE>

# CRITICAL: Update token expiration (CHANGED FROM 30000 to 30)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Update MongoDB connection with SSL
MONGODB_URL=mongodb+srv://username:password@cluster/?retryWrites=true&w=majority&ssl=true

# Add CORS allowed origins (your frontend URLs)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Set to False in production
DEBUG=False
```

### 2. Rotate MongoDB Credentials

The current MongoDB credentials in your `.env` file were exposed. You MUST:

1. Log into MongoDB Atlas
2. Create a new database user with a strong password
3. Delete the old user: `2021pavand_db_user`
4. Update `.env` with new credentials
5. Invalidate all existing JWT tokens by changing SECRET_KEY

### 3. Install Updated Dependencies

```bash
pip install --upgrade -r requirements.txt
```

## 📋 Complete List of Security Changes

### ✅ 1. Credential Protection
- **File**: `.gitignore` (already configured)
- **Action**: Ensure `.env` is never committed
- **Status**: ✅ .env.example created as template

### ✅ 2. Token Expiration Fixed
- **File**: `app/core/config.py`
- **Change**: ACCESS_TOKEN_EXPIRE_MINUTES from 30000 → 30
- **Impact**: Tokens now expire in 30 minutes instead of 20+ days

### ✅ 3. CORS Security
- **File**: `app/main.py`
- **Added**: CORS middleware with strict origin checking
- **Configuration**: Only allows origins from ALLOWED_ORIGINS env var

### ✅ 4. Security Headers
- **File**: `app/middleware/security.py` (NEW FILE)
- **Added Headers**:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security
  - Content-Security-Policy
  - Referrer-Policy
  - Permissions-Policy

### ✅ 5. Request Size Limits
- **File**: `app/middleware/security.py`
- **Added**: RequestSizeLimitMiddleware
- **Limit**: 10MB max request size (configurable)

### ✅ 6. Rate Limiting
- **File**: `app/middleware/rate_limit.py` (NEW FILE)
- **Applied to**:
  - Login: 5 attempts/minute
  - Registration: 5 attempts/5 minutes
  - Developer registration: 3 attempts/10 minutes
- **Note**: Current implementation is in-memory. For production with multiple instances, use Redis.

### ✅ 7. Password Policy
- **File**: `app/schemas/auth.py`
- **Requirements**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character

### ✅ 8. RBAC Authorization Fixed
- **File**: `app/api/v1/developer_leads.py`
- **Change**: Developers can only access their own project leads
- **Added**: `verify_developer_project_access()` function
- **Impact**: Prevents data leakage between developers

### ✅ 9. User Deletion Protection
- **File**: `app/api/v1/users.py`
- **Added Protections**:
  - Users cannot delete themselves
  - Only SUPER_ADMIN can delete other admins
  - All deletions are logged

### ✅ 10. Deprecated datetime.utcnow() Fixed
- **File**: `app/core/security.py`
- **Change**: `datetime.utcnow()` → `datetime.now(timezone.utc)`
- **Impact**: Proper timezone-aware datetimes

### ✅ 11. Comprehensive Logging
- **File**: `app/core/logging_config.py` (NEW FILE)
- **Logs**:
  - Application logs: `logs/app.log`
  - Error logs: `logs/error.log`
  - Security audit: `logs/security.log`
- **Logged Events**:
  - Failed login attempts
  - Registration attempts
  - User deletions
  - Unauthorized access attempts
  - Rate limit violations

### ✅ 12. Production API Docs Disabled
- **File**: `app/main.py`
- **Change**: API docs only available when DEBUG=True
- **Impact**: Documentation not exposed in production

## 🆕 New Files Created

1. `.env.example` - Template for environment variables
2. `app/middleware/__init__.py` - Middleware package
3. `app/middleware/security.py` - Security headers and request size limits
4. `app/middleware/rate_limit.py` - Rate limiting implementation
5. `app/core/logging_config.py` - Centralized logging configuration
6. `SECURITY.md` - Security policy and best practices
7. `UPGRADE_GUIDE.md` - This file

## 🔧 Modified Files

1. `app/main.py` - Added middleware and disabled docs in production
2. `app/core/config.py` - Added new configuration options
3. `app/core/security.py` - Fixed deprecated datetime
4. `app/schemas/auth.py` - Added password validation
5. `app/api/v1/users.py` - Added user deletion protection
6. `app/api/v1/developer_leads.py` - Fixed RBAC authorization
7. `app/api/v1/public_auth.py` - Added rate limiting and logging
8. `requirements.txt` - Updated dependencies

## 🧪 Testing the Changes

### 1. Test Password Validation

```python
# This should fail
POST /api/v1/auth/register
{
    "email": "test@example.com",
    "password": "weak",  # Too short, no uppercase, no number, no special char
    "full_name": "Test User"
}

# This should succeed
POST /api/v1/auth/register
{
    "email": "test@example.com",
    "password": "Strong@Pass123",
    "full_name": "Test User"
}
```

### 2. Test Rate Limiting

```bash
# Try logging in 6 times within a minute with wrong password
# The 6th attempt should return 429 Too Many Requests
```

### 3. Test CORS

```bash
# Request from unauthorized origin should be blocked
curl -H "Origin: http://evil.com" http://localhost:8000/api/v1/auth/me
```

### 4. Test User Deletion Protection

```bash
# Admin trying to delete themselves should fail
DELETE /api/v1/admin/users/{own_user_id}
# Should return 400: "Cannot delete your own account"

# Regular admin trying to delete super admin should fail
DELETE /api/v1/admin/users/{super_admin_id}
# Should return 403: "Only super admins can delete admin users"
```

### 5. Test Developer Authorization

```bash
# Developer A trying to access Developer B's leads should fail
GET /api/v1/developers/leads/projects/{developer_b_project_slug}/leads
# Should return 403: "Not authorized to view these leads"
```

## 📊 Monitoring Recommendations

1. **Set up log monitoring**:
   ```bash
   tail -f logs/security.log
   ```

2. **Monitor rate limit violations**:
   ```bash
   grep "Rate limit exceeded" logs/security.log
   ```

3. **Monitor failed logins**:
   ```bash
   grep "Failed login attempt" logs/security.log
   ```

4. **Monitor unauthorized access**:
   ```bash
   grep "Unauthorized" logs/security.log
   ```

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] Update `.env` with production values
- [ ] Generate new SECRET_KEY
- [ ] Rotate MongoDB credentials
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_ORIGINS with actual frontend URLs
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure Redis for rate limiting (replace in-memory implementation)
- [ ] Set up log rotation
- [ ] Enable monitoring and alerting
- [ ] Test all security features
- [ ] Review SECURITY.md
- [ ] Back up database
- [ ] Update firewall rules

## ⚠️ Breaking Changes

1. **Token Expiration**: Existing tokens will expire much faster (30 min vs 20 days)
   - Impact: Users will need to re-login more frequently
   - Action: Implement refresh token mechanism if needed

2. **Password Policy**: Existing users with weak passwords can still login
   - Impact: Only new users/password changes are affected
   - Action: Consider password reset for existing users

3. **CORS**: Only configured origins can access API
   - Impact: Unauthorized origins will be blocked
   - Action: Update ALLOWED_ORIGINS with all legitimate frontend URLs

4. **Rate Limiting**: May affect automated testing/scripts
   - Impact: Rapid successive requests will be blocked
   - Action: Add rate limit bypasses for testing or adjust limits

## 🔄 Migration Steps

1. **Backup current database**:
   ```bash
   # Use MongoDB Atlas backup or mongodump
   ```

2. **Update code**:
   ```bash
   git pull
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Update environment**:
   ```bash
   cp .env .env.backup
   # Update .env with new values
   ```

5. **Test locally**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. **Deploy to production**:
   ```bash
   # Follow your deployment process
   ```

## 📞 Support

If you encounter issues after upgrading:

1. Check logs in `logs/` directory
2. Verify `.env` configuration
3. Ensure all dependencies are installed
4. Review this guide
5. Check SECURITY.md for best practices

## 🔐 Security Contact

For security-related questions or to report vulnerabilities:
- Email: security@yourdomain.com (update this)
- Do not create public issues for security problems

---

**Last Updated**: 2025-12-12
**Version**: 1.0.0
**Security Patch Level**: Complete
