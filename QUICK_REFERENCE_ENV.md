# Quick Reference: Missing Environment Variables

## Summary of Changes

### ✅ What was added to `.env`:

1. **ALLOWED_ORIGINS** - CORS configuration for frontend URLs
2. **SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM** - Email configuration
3. **RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET** - Payment gateway credentials
4. **MAPPLS_CLIENT_ID, MAPPLS_CLIENT_SECRET** - Location services OAuth credentials
5. **MAPPLS_AUTH_URL** - Mappls OAuth token endpoint
6. **Updated MAPPLS_BASE_URL** - Corrected to use atlas.mappls.com

### ⚠️ What you need to configure NOW:

| Variable | Priority | Status | Where to get it |
|----------|----------|--------|-----------------|
| `ALLOWED_ORIGINS` | 🔴 HIGH | ⚠️ Update for production | Your frontend domain |
| `MAPPLS_CLIENT_ID` | 🔴 HIGH | ⚠️ Empty | https://www.mappls.com/ |
| `MAPPLS_CLIENT_SECRET` | 🔴 HIGH | ⚠️ Empty | https://www.mappls.com/ |
| `RAZORPAY_KEY_ID` | 🟡 MEDIUM | ⚠️ Empty | https://dashboard.razorpay.com/ |
| `RAZORPAY_KEY_SECRET` | 🟡 MEDIUM | ⚠️ Empty | https://dashboard.razorpay.com/ |
| `SMTP_USER` | 🟡 MEDIUM | ⚠️ Empty | Your email provider |
| `SMTP_PASSWORD` | 🟡 MEDIUM | ⚠️ Empty | Your email provider |
| `EMAIL_FROM` | 🟡 MEDIUM | ⚠️ Update | Your email address |

### 🔍 What each API is used for:

**Mappls (Location Services)**:
- Used in: `app/api/v1/locality.py`
- Features: Reverse geocoding, location resolution, landmark creation
- Impact if missing: Location features won't work

**Razorpay (Payments)**:
- Used in: `app/api/v1/developer_subscriptions.py`
- Features: Subscription payments, payment verification
- Impact if missing: Payment features won't work

**SMTP (Email)**:
- Configured in: `app/core/config.py`
- Features: Email verification, password reset, notifications
- Impact if missing: Email features won't work

**CORS**:
- Used in: `app/main.py`
- Features: Allow frontend to communicate with backend
- Impact if wrong: Frontend will get CORS errors

### 📋 Next Steps:

1. **For local development**: Application will work, but location/payment/email features won't function
2. **For production**: You MUST configure all these values

3. **Testing checklist**:
   - [ ] Update ALLOWED_ORIGINS with your frontend URL
   - [ ] Get Mappls credentials and test location features
   - [ ] Get Razorpay credentials and test payments
   - [ ] Configure SMTP and test email sending

### 🛠️ Where to register for API keys:

1. **Mappls/MapMyIndia**: https://www.mappls.com/api/
2. **Razorpay**: https://razorpay.com/
3. **Email (Gmail)**: Use App Passwords: https://support.google.com/accounts/answer/185833

### 📝 Notes:

- All changes have been made to both `.env` and `.env.example`
- These files are already in `.gitignore` and won't be committed
- The configuration summary has been saved to `.env_configuration_summary.md`
