# Quick Start Guide - Authentication System

## Prerequisites
- Python 3.11+
- Supabase account (free at supabase.com)
- Git

## Local Setup (5 minutes)

### 1. Clone & Install
```bash
cd quiz-generate
pip install -r requirements.txt
```

### 2. Configure Supabase
1. Go to https://supabase.com → Sign in
2. Create new project or use existing
3. Go to Settings → API
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **Anon/Public Key** → `SUPABASE_KEY`

### 3. Create `.env` file
```bash
# Create .env in quiz-generate folder
cat > .env << EOF
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
FLASK_SECRET_KEY=your-long-random-secret-key-minimum-32-characters
MISTRAL_API_KEY=your-mistral-key
DEBUG=True
EOF
```

### 4. Create Database Tables
1. Go to Supabase Dashboard → SQL Editor
2. Click "New Query"
3. Open `supabase_schema.sql` from project folder
4. Copy entire content
5. Paste in SQL Editor
6. Click "Run"
7. Wait for success message

### 5. Run App
```bash
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Authentication routes registered
 * Document processor initialized
 * RAG system initialized
```

### 6. Test Authentication
1. Open http://localhost:5000/auth
2. Click "Créer un compte" (Create Account)
3. Fill signup form:
   - Email: test@example.com
   - Password: SecurePass123
   - First Name: Jean
   - Last Name: Dupont
4. Click "S'inscrire"
5. Should redirect to homepage

## Troubleshooting

### "ModuleNotFoundError: No module named 'supabase'"
```bash
pip install supabase
```

### "SUPABASE_URL not configured"
- Check .env file exists in quiz-generate folder
- Verify SUPABASE_URL has correct value
- Restart app after editing .env

### "Auth routes not registered"
- Check auth_routes.py exists in quiz-generate folder
- Check for import errors: `python -c "from auth_routes import auth_bp"`

### Cannot connect to Supabase
- Verify SUPABASE_URL matches your project
- Check SUPABASE_KEY is correct (copy again from dashboard)
- Try without firewall/proxy if issues persist

### Form validation errors
- Password must be 8+ chars, with uppercase and digit
- Email format must be valid (user@domain.com)
- All required fields must be filled

## What's Now Available

### Pages
- `/` - Main dashboard (after login)
- `/auth` - Login/Signup page
- `/api/health` - Health check with component status

### API Endpoints
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout
- `GET /api/auth/profile` - Get user profile (requires login)
- `PUT /api/auth/profile` - Update profile (requires login)
- `POST /api/auth/forgot-password` - Reset password
- `GET /api/auth/check-session` - Check if logged in

## Files Modified/Created

### New Files
- `auth_service.py` - 237 lines - Authentication service
- `auth_routes.py` - 285 lines - API routes
- `templates/auth.html` - 1500+ lines - Creative UI
- `supabase_schema.sql` - 500+ lines - Database schema
- `AUTHENTICATION_SETUP.md` - Complete setup guide

### Modified Files
- `app.py` - Added auth blueprint, auth route, session config
- `requirements.txt` - Added supabase and PyJWT

## Next Steps

1. ✅ Install packages
2. ✅ Configure Supabase credentials
3. ✅ Create database tables
4. Run app locally & test
5. Deploy to Vercel

## Deployment to Vercel

### 1. Commit changes
```bash
git add .
git commit -m "Complete authentication system implementation"
git push origin main
```

### 2. Set Vercel Environment Variables
```bash
# Install Vercel CLI (optional)
npm install -g vercel

# Or set in Vercel dashboard:
# Settings → Environment Variables
SUPABASE_URL=your-url
SUPABASE_KEY=your-key
FLASK_SECRET_KEY=your-secret
MISTRAL_API_KEY=your-api-key
```

### 3. Deploy
```bash
vercel deploy --prod
```

### 4. Test live
- Go to `https://your-domain.vercel.app/auth`
- Test signup with new account
- Check Supabase for new user in profiles table

## Key Features Implemented

### Authentication
- ✅ Signup with email/password
- ✅ Login with validation
- ✅ Session management (7-day expiry)
- ✅ Logout
- ✅ Password reset via email
- ✅ Profile management

### Database
- ✅ 10 PostgreSQL tables with indexes
- ✅ Row Level Security (RLS) for data isolation
- ✅ Automatic audit trail (activity_logs)
- ✅ User statistics tracking
- ✅ Rich data model (preferences, timezone, language)

### Frontend
- ✅ Modern responsive design
- ✅ Dual panels (branding + forms)
- ✅ Password strength indicator
- ✅ Real-time form validation
- ✅ Error/success alerts
- ✅ Mobile-friendly

### Security
- ✅ Password validation (8+ chars, uppercase, digit)
- ✅ CORS protection
- ✅ Session cookies (HTTP-only)
- ✅ Field whitelisting for updates
- ✅ Input sanitization
- ✅ Database-level RLS policies

## Support & Issues

### Check Logs
```bash
# Server logs (terminal where app runs)
python app.py

# Browser console (F12)
# Check Network tab for API responses
```

### Common Issues
1. **Blank signup form** → Check browser console for JS errors
2. **API 500 error** → Check server logs for exception
3. **Can't submit form** → Check password meets requirements
4. **Data not saving** → Run supabase_schema.sql in SQL editor

### Get Help
1. Check AUTHENTICATION_SETUP.md for detailed docs
2. Check server logs: `python app.py 2>&1 | tee app.log`
3. Check Supabase logs: Dashboard → Logs panel
4. Test API directly: `curl -X POST http://localhost:5000/api/auth/signup ...`

---

**Status:** ✅ Complete authentication system ready
**Last Updated:** 2025-01-04
