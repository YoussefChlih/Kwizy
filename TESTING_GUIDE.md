# 🧪 Authentication System - Testing & Troubleshooting Guide

## Quick Testing Checklist

### Before Testing
- [ ] Supabase project created
- [ ] `supabase_schema.sql` executed in SQL editor
- [ ] `.env` file with SUPABASE_URL and SUPABASE_KEY
- [ ] `pip install -r requirements.txt` run
- [ ] App running: `python app.py`

### Test Sequence (20 minutes)

#### 1. Health Check (1 min)
**Verify all components initialized**

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "components": {
    "authentication": "ok",
    "document_processor": "ok",
    "rag_system": "ok",
    "database": "ok"
  }
}
```

#### 2. Load Auth Page (1 min)
**Verify frontend loads**

1. Open browser: `http://localhost:5000/auth`
2. Check you see:
   - Left panel with gradient background
   - Right panel with login form
   - Email/password inputs
   - "Créer un compte" button
   - "Mot de passe oublié?" link

#### 3. Test Signup (5 min)
**Complete registration flow**

**Step 1: Navigate to signup**
- Click "Créer un compte" button
- Form should switch to signup fields

**Step 2: Fill form**
```
First Name:    Jean
Last Name:     Dupont
Email:         test@example.com
Company:       Acme Corporation
Job Title:     Développeur
Language:      Français
Password:      SecurePass123
Confirm:       SecurePass123
```

**Step 3: Validate password strength**
- Should show "Strong" (green)
- Checklist should show all items checked

**Step 4: Submit**
- Click "S'inscrire"
- Should show loading spinner
- After 2-3 seconds, should redirect to homepage

**Step 5: Verify in Supabase**
- Go to Supabase Dashboard → profiles table
- Should see new row with your data:
  - user_id (UUID)
  - first_name: "Jean"
  - last_name: "Dupont"
  - email: "test@example.com"
  - company: "Acme Corporation"
  - job_title: "Développeur"

#### 4. Test Login (3 min)
**Session creation and retrieval**

**Step 1: Navigate back to auth**
- Go to: `http://localhost:5000/auth`
- Click "Se connecter"
- Should show login form (click "J'ai déjà un compte" if on signup)

**Step 2: Login**
```
Email:    test@example.com
Password: SecurePass123
```

**Step 3: Submit**
- Click "Se connecter"
- Should redirect to homepage
- Check browser console for session data

**Step 4: Verify Session**
Open browser Developer Tools (F12):
```javascript
// In Console, type:
fetch('/api/auth/check-session').then(r => r.json()).then(d => console.log(d))

// Should output:
{
  "logged_in": true,
  "user_id": "...",
  "email": "test@example.com"
}
```

#### 5. Test Profile Access (2 min)
**Retrieve user profile**

```javascript
// In Console, type:
fetch('/api/auth/profile').then(r => r.json()).then(d => console.log(d))

// Should output:
{
  "success": true,
  "profile": {
    "user_id": "...",
    "email": "test@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "company": "Acme Corporation",
    "job_title": "Développeur",
    "language": "fr",
    "timezone": "Europe/Paris"
  }
}
```

#### 6. Test Profile Update (2 min)
**Update user profile**

```javascript
fetch('/api/auth/profile', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    company: "Nouvelle Entreprise",
    timezone: "America/New_York"
  })
}).then(r => r.json()).then(d => console.log(d))

// Should output:
{
  "success": true,
  "message": "Profil mis à jour avec succès"
}

// Verify in Supabase - company should be updated
```

#### 7. Test Logout (1 min)
**Session cleanup**

```javascript
fetch('/api/auth/logout', {method: 'POST'})
  .then(r => r.json())
  .then(d => console.log(d))

// Should output:
{
  "success": true,
  "message": "Déconnexion réussie"
}

// Check again:
fetch('/api/auth/check-session').then(r => r.json()).then(d => console.log(d))

// Should output:
{
  "logged_in": false
}
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: "Page not found" at /auth
**Problem:** Route not registered
**Solution:**
```bash
# Check app.py has auth route:
grep -n "@app.route('/auth')" app.py

# Should show: @app.route('/auth')
# If not, auth route is missing - check app.py integration
```

### Issue 2: "ModuleNotFoundError: No module named 'supabase'"
**Problem:** Missing dependency
**Solution:**
```bash
pip install supabase
pip install PyJWT
```

### Issue 3: "SUPABASE_URL not configured"
**Problem:** Environment variables not set
**Solution:**
```bash
# Check .env exists:
cat .env | grep SUPABASE

# Should show:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-key

# If missing, create .env:
cat > .env << 'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
FLASK_SECRET_KEY=your-secret-key
EOF

# Restart app (Ctrl+C, then python app.py)
```

### Issue 4: Signup form won't submit
**Problem:** Password doesn't meet requirements
**Solution:**
Verify password has:
- [ ] At least 8 characters
- [ ] At least 1 uppercase letter (A-Z)
- [ ] At least 1 digit (0-9)

Example valid: `SecurePass123`
Example invalid: `password123` (no uppercase)

### Issue 5: "Email already exists" error
**Problem:** User already registered
**Solution:**
1. Use different email: `test2@example.com`
2. Or delete user in Supabase:
   - Go to profiles table
   - Find row with email
   - Click delete row
   - Try signup again

### Issue 6: API returns 500 error
**Problem:** Server exception
**Solution:**
1. Check server logs (terminal output)
2. Look for error message with traceback
3. Check Supabase connection:
   ```bash
   python -c "from auth_service import AuthService; a = AuthService(); print('OK' if a.client else 'FAILED')"
   ```

### Issue 7: Form submits but nothing happens
**Problem:** JavaScript error
**Solution:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for red error messages
4. Check Network tab → see request/response

### Issue 8: Can login but can't access profile
**Problem:** Session not saved
**Solution:**
1. Check browser cookies: DevTools → Application → Cookies
2. Should see `session` cookie
3. If not, check server logs for session errors
4. Verify `Flask` secret key is set in `.env`

### Issue 9: Updated profile but changes don't appear
**Problem:** Cache issue or update failed
**Solution:**
1. Refresh Supabase dashboard page
2. Check server logs for update error
3. Verify only whitelisted fields being sent
4. Try again with single field update

### Issue 10: "Passwords do not match" on signup
**Problem:** Confirmation password differs
**Solution:**
1. Re-enter password in both fields
2. Use copy-paste to avoid typos
3. Check CAPS LOCK not accidentally on

---

## 🔍 Advanced Debugging

### Check Database Tables
```sql
-- In Supabase SQL Editor:

-- See all profiles:
SELECT user_id, email, first_name, last_name, created_at FROM profiles;

-- See recent activity:
SELECT user_id, action, created_at FROM activity_logs ORDER BY created_at DESC LIMIT 10;

-- See active sessions:
SELECT user_id, ip_address, expires_at FROM user_sessions WHERE expires_at > NOW();
```

### Check Server Logs
```bash
# Start app with verbose output:
python app.py 2>&1 | tee app.log

# Watch logs in real-time:
tail -f app.log

# Search for errors:
grep -i "error" app.log
grep -i "auth" app.log
```

### Test API Directly
```bash
# Test signup with curl:
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "curl@test.com",
    "password": "TestPass123",
    "first_name": "Curl",
    "last_name": "User",
    "language": "en"
  }'

# Expected response:
{
  "success": true,
  "message": "Inscription réussie",
  "user": { "id": "...", "email": "curl@test.com", ... }
}
```

### Monitor Supabase Logs
1. Supabase Dashboard → Logs panel
2. Filter by "API" or "Database"
3. Look for errors during signup/login
4. Check timestamps match your test actions

---

## ✅ Testing Verification Checklist

After completing all tests, verify:

- [ ] Auth page loads at `/auth`
- [ ] Signup form shows all required fields
- [ ] Password strength meter works
- [ ] Can successfully signup
- [ ] New user appears in Supabase profiles table
- [ ] Can login with created account
- [ ] Redirects to homepage after login
- [ ] `/api/auth/check-session` returns logged_in: true
- [ ] Can retrieve profile via API
- [ ] Can update profile fields
- [ ] Updated data appears in Supabase
- [ ] Can logout successfully
- [ ] Session cookie is cleared after logout
- [ ] `/api/auth/check-session` returns logged_in: false
- [ ] Health check shows authentication: ok
- [ ] No errors in server logs
- [ ] No errors in browser console

---

## 🚀 Deployment Testing

### Pre-Deployment
1. ✅ Local testing complete (above)
2. ✅ All API endpoints working
3. ✅ Database schema in Supabase
4. ✅ Environment variables configured

### Vercel Deployment Tests
After deploying to Vercel:

```bash
# Test 1: Health check
curl https://your-domain.vercel.app/api/health

# Test 2: Load auth page
curl https://your-domain.vercel.app/auth | head -20

# Test 3: Signup
curl -X POST https://your-domain.vercel.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{...}'

# Test 4: Verify in Supabase
# Go to Supabase dashboard and check new user was created
```

---

## 📊 Performance Checklist

### Response Times (target: <500ms)
- [ ] GET `/auth` < 100ms
- [ ] POST `/api/auth/signup` < 300ms
- [ ] POST `/api/auth/login` < 300ms
- [ ] GET `/api/auth/profile` < 200ms
- [ ] PUT `/api/auth/profile` < 300ms

### Database Performance
- [ ] Profiles table has index on user_id
- [ ] Queries use indexes (check explain plans)
- [ ] No N+1 queries
- [ ] Aggregates cached when possible

---

## 📝 Test Results Template

Use this template to document your testing:

```
# Testing Results - [DATE]

## Environment
- Python Version: 3.11.x
- Flask Version: 3.0.x
- Supabase: Yes/No
- Local/Production: Local/Vercel

## Tests Completed
- [ ] Health check: PASS/FAIL
- [ ] Load auth page: PASS/FAIL
- [ ] Signup: PASS/FAIL
- [ ] Login: PASS/FAIL
- [ ] Profile access: PASS/FAIL
- [ ] Profile update: PASS/FAIL
- [ ] Logout: PASS/FAIL

## Issues Found
[List any issues with details]

## Performance
- Signup time: X ms
- Login time: X ms
- Profile fetch: X ms

## Browser Compatibility Tested
- Chrome: Yes/No
- Firefox: Yes/No
- Safari: Yes/No
- Edge: Yes/No
- Mobile: Yes/No

## Notes
[Any additional observations]

## Status: READY/NOT READY FOR PRODUCTION
```

---

## 📞 Quick Support Reference

**If signup doesn't work:**
1. Check password has uppercase + digit + 8 chars
2. Check SUPABASE_URL in .env is correct
3. Check supabase_schema.sql was executed
4. Check server logs for errors

**If login doesn't work:**
1. Verify user exists in Supabase profiles table
2. Check password is correct
3. Look at server logs
4. Verify session storage working

**If profile update doesn't work:**
1. Verify user is logged in (check-session)
2. Check only sending allowed fields
3. Verify data format (timezone, language, etc.)
4. Check Supabase RLS policies

**If nothing works:**
1. Restart Python app: `Ctrl+C` then `python app.py`
2. Clear browser cache: Ctrl+Shift+Delete
3. Check .env file is in correct directory
4. Run: `pip install -r requirements.txt --force-reinstall`
5. Check Supabase logs for database errors

---

**Last Updated:** 2025-01-04
**Status:** Testing guide complete and ready
**Next:** Follow test sequence above and document results
