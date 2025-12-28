# Vercel Deployment Checklist

## Pre-Deployment Tasks

- [ ] All code is committed to your Git repository (GitHub, GitLab, or Bitbucket)
- [ ] `vercel.json` is configured ✓
- [ ] `.vercelignore` is created ✓
- [ ] `requirements.txt` is optimized for production ✓
- [ ] `wsgi.py` is created for production entry point ✓
- [ ] `.env` file is NOT committed (it's in .gitignore) ✓
- [ ] `DEPLOYMENT_GUIDE.md` is reviewed

## Environment Variables Setup

Before deploying on Vercel, you'll need to set these environment variables in the Vercel dashboard:

### Required Variables:
```
SECRET_KEY = <generate-a-strong-random-string>
MISTRAL_API_KEY = <your-mistral-api-key>
FLASK_ENV = production
```

### Database (choose one):
**Option A: PostgreSQL**
```
DATABASE_URL = postgresql://user:password@host:5432/database
```

**Option B: Supabase**
```
DATABASE_URL = postgresql://user:password@host:5432/database
SUPABASE_URL = https://your-project.supabase.co
SUPABASE_KEY = your-supabase-api-key
USE_SUPABASE = true
```

### Optional Variables:
```
UPLOAD_FOLDER = /tmp/uploads  # Don't change - this is where Vercel allows writes
MAX_CONTENT_LENGTH = 16777216
```

## Deployment Steps

1. **Push to GitHub** (or your Git provider):
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Deploy to Vercel**:
   - Go to https://vercel.com/dashboard
   - Click "Add New" → "Project"
   - Select your repository
   - Set Root Directory to: `quiz-generate`
   - Add all environment variables from above
   - Click "Deploy"

   OR use CLI:
   ```bash
   npm i -g vercel
   vercel
   ```

3. **Configure Database** (if using PostgreSQL):
   - Ensure your database allows connections from Vercel
   - Add Vercel IP allowlist in your database provider

4. **Test Deployment**:
   - Visit your deployment URL
   - Test key endpoints
   - Check Vercel logs for errors

## Important Notes

⚠️ **Critical Issues to Address:**

1. **SQLite Won't Work** - Vercel has ephemeral filesystem
   - Switch to PostgreSQL or Supabase
   - Update `DATABASE_URL` environment variable

2. **File Uploads** - Only `/tmp` directory is writable
   - Uploads are automatically saved to `/tmp/uploads`
   - Consider moving to cloud storage (S3, Supabase Storage)
   - Files are deleted when deployment updates

3. **ChromaDB Vector Store** - Requires persistent storage
   - Current in-memory/local setup won't persist across deploys
   - Consider using cloud vector store (Pinecone, Weaviate)
   - Or set up with PostgreSQL pgvector extension

4. **WebSockets (SocketIO)** - Limited support on Vercel
   - Vercel supports WebSocket on Pro and above
   - Check your plan before deploying real-time features

## Post-Deployment Verification

- [ ] App loads without errors
- [ ] API endpoints respond
- [ ] Database queries work
- [ ] File uploads work (using /tmp)
- [ ] Authentication works
- [ ] Check Vercel logs for warnings

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Add to `requirements.txt` and redeploy |
| Database connection error | Check `DATABASE_URL` and database firewall rules |
| 500 Internal Server Error | Check Vercel logs in dashboard |
| Uploads not saving | Use `/tmp/uploads` or cloud storage |
| Slow builds | Remove unused dependencies, optimize imports |

## Monitoring & Maintenance

- Check Vercel dashboard regularly for errors
- Monitor function execution time
- Set up error tracking (Sentry, LogRocket)
- Monitor database performance

## Support Resources

- Vercel Docs: https://vercel.com/docs
- Flask Documentation: https://flask.palletsprojects.com/
- Python on Vercel: https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python
- Common Issues: https://vercel.com/support

---

**Ready to deploy?** Start with Step 1 above! 🚀
