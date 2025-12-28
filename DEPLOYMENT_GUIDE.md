# Vercel Deployment Guide for Kwizy_Collab

## Prerequisites
- A Vercel account (https://vercel.com)
- Git repository pushed to GitHub/GitLab/Bitbucket
- Required environment variables

## Pre-Deployment Checklist

### 1. Environment Variables Setup
Create these environment variables in your Vercel project dashboard:

```
SECRET_KEY = <strong-random-key>
MISTRAL_API_KEY = <your-mistral-api-key>
DATABASE_URL = <your-postgresql-connection-string>
SUPABASE_URL = <your-supabase-url> (if using)
SUPABASE_KEY = <your-supabase-key> (if using)
USE_SUPABASE = true/false
UPLOAD_FOLDER = /tmp/uploads
MAX_CONTENT_LENGTH = 16777216
FLASK_ENV = production
```

### 2. Database Setup
- **SQLite won't work** on Vercel (ephemeral filesystem)
- Use PostgreSQL or Supabase instead
- Update `DATABASE_URL` in your Vercel environment variables

### 3. File Upload Handling
- Vercel has read-only filesystem except `/tmp`
- Uploads are automatically moved to `/tmp/uploads`
- For persistent storage, use cloud storage (AWS S3, Supabase Storage, etc.)

## Deployment Steps

### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub:**
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

2. **Connect to Vercel:**
   - Go to https://vercel.com/dashboard
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Select the `quiz-generate` folder as root directory

3. **Configure Environment Variables:**
   - In Vercel dashboard, go to Settings → Environment Variables
   - Add all variables from the checklist above

4. **Deploy:**
   - Click "Deploy"
   - Vercel will automatically build and deploy

### Option B: Deploy from CLI

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Deploy:**
```bash
cd quiz-generate
vercel
```

3. **Follow the prompts:**
   - Link to GitHub repo
   - Confirm settings
   - Add environment variables

## Post-Deployment

### Verify Deployment
- Check the Vercel dashboard for deployment status
- Visit your deployment URL
- Test API endpoints

### Monitor Logs
- View logs in Vercel dashboard under "Logs"
- Check for any runtime errors

### Custom Domain (Optional)
- Add custom domain in Vercel Settings → Domains
- Update DNS records as instructed

## Common Issues & Solutions

### Issue: Database Connection Failed
**Solution:** 
- Verify `DATABASE_URL` is correct
- Ensure database allows connections from Vercel IPs
- Use PostgreSQL instead of SQLite

### Issue: Uploads Not Working
**Solution:**
- Use cloud storage (S3, Supabase Storage)
- Check `/tmp` directory permissions
- Implement cleanup for temporary files

### Issue: Large Dependencies Timeout
**Solution:**
- Optimize `requirements.txt` - remove unused packages
- Consider using lightweight alternatives
- Increase build timeout in vercel.json

### Issue: Missing Modules
**Solution:**
- Ensure all requirements are in `requirements.txt`
- Clear build cache and redeploy
- Check Python version compatibility

## Optimization Tips

1. **Reduce package size:**
   - Remove test dependencies from production
   - Use lighter alternatives where possible

2. **Cold start optimization:**
   - Lazy load heavy imports
   - Consider splitting into multiple functions

3. **Environment-specific settings:**
   - Use `FLASK_ENV=production`
   - Disable debug mode in production

## Rollback

If deployment fails:
1. Check deployment logs in Vercel dashboard
2. Fix the issue locally
3. Commit and push to GitHub
4. Vercel will auto-redeploy

Or manually trigger a redeploy from dashboard.

## Support

- Vercel Docs: https://vercel.com/docs
- Flask Guide: https://flask.palletsprojects.com/
- Troubleshooting: Check `/logs` in Vercel dashboard
