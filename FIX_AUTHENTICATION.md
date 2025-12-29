FIX GUIDE - Authentication Issues

PROBLEM 1: Signup Error - RLS Policy Violation
Error: "new row violates row-level security policy for table 'profiles'"

PROBLEM 2: Login Not Working
Error: Login endpoint doesn't work with valid credentials

ROOT CAUSE:
- The 'profiles' table doesn't exist or has incorrect RLS policies
- The service role backend cannot insert profiles due to RLS restrictions
- Missing proper authentication flow between Flask and Supabase

SOLUTION STEPS:

Step 1: Apply Database Migration
==============================
1. Go to your Supabase Dashboard
2. Click "SQL Editor" in the left sidebar
3. Click "New Query"
4. Copy the entire content from: supabase_migration_fix.sql
5. Paste it in the SQL Editor
6. Click "Run"
7. Wait for execution to complete (should see success message)

Step 2: Update auth_service.py
==============================
The signup method needs to use a service_role client for inserting profiles.

Step 3: Verify Supabase Configuration
======================================
Check your .env file has:
- SUPABASE_URL=https://your-project.supabase.co
- SUPABASE_KEY=your-anon-key (this is the anon key, not service role)

Step 4: Restart Application
============================
1. Stop Flask server (Ctrl+C)
2. Stop npm React server (Ctrl+C)
3. Start Flask: python app.py
4. Start React: npm start
5. Try signup again

Step 5: Test Authentication
===========================
1. Go to http://localhost:3000
2. Click "Sign Up"
3. Enter:
   - First Name: Test
   - Last Name: User
   - Email: testuser@example.com
   - Password: TestPass123!
   - Click "Create Account"
4. Wait for success message
5. Should redirect to login
6. Login with same credentials

DEBUGGING IF STILL NOT WORKING:

Check 1: Verify Supabase Tables
- Go to Supabase Dashboard > Table Editor
- Look for "profiles" table (should exist after migration)
- Check "activity_logs" table exists

Check 2: Check RLS Policies
- In Supabase: Authentication > Policies
- Under "profiles" table, verify these policies exist:
  * Service role can insert profiles
  * Users can view own profile
  * Users can update own profile

Check 3: Check Backend Logs
- Look at Flask terminal for error messages
- Should show "Supabase client initialized" on startup
- Any SQL errors should be visible there

Check 4: Check Browser Console
- Open DevTools (F12)
- Go to Console tab
- Look for any fetch errors or API errors
- Check Network tab to see API response codes

Check 5: Verify .env File
- Make sure SUPABASE_URL is correct format
- Make sure SUPABASE_KEY is the anon key, not service role key
- Reload Flask app after changing .env

EXPECTED BEHAVIOR AFTER FIX:

Signup:
1. User enters form data
2. React sends POST to /api/auth/signup
3. Backend validates data
4. Backend calls Supabase auth.sign_up()
5. Supabase creates auth user
6. Backend inserts profile into profiles table
7. Success message appears
8. Redirect to login page

Login:
1. User enters email and password
2. React sends POST to /api/auth/login
3. Backend calls Supabase auth.sign_in_with_password()
4. If valid, returns access token
5. Backend fetches user profile from profiles table
6. Stores session in Flask
7. Success message appears
8. Redirect to dashboard

If you still have issues after these steps:
1. Check Flask console for specific error messages
2. Look at browser Network tab (F12) for API responses
3. Verify migration script ran without errors
4. Make sure you're using correct Supabase credentials
