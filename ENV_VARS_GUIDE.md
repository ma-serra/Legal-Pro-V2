# 🔧 Environment Variables Configuration Guide

## Quick Reference

This document provides all environment variables needed for deployment.

---

## 🚂 Railway (Backend) Environment Variables

Copy these to your Railway project's Variables section:

### Required Variables

```bash
# ============================================
# DATABASE CONFIGURATION
# ============================================
# Get this from your PostgreSQL service (Railway, Neon, or other)
DATABASE_URL=postgresql://username:password@host:port/database

# ============================================
# FLASK CONFIGURATION
# ============================================
# Generate these using: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=generate-a-strong-random-32-character-secret-key
SESSION_SECRET=generate-another-different-32-character-secret
FLASK_ENV=production
FLASK_APP=main.py

# ============================================
# VECTOR DATABASE (QDRANT)
# ============================================
# Get these from Qdrant Cloud dashboard (https://cloud.qdrant.io)
QDRANT_URL=https://your-cluster-id.region.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key-here
```

### Optional but Recommended (For AI Features)

```bash
# ============================================
# AI API KEYS
# ============================================
# These enable AI assistant features
# Get from respective provider dashboards

# OpenAI (https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-...

# Anthropic Claude (https://console.anthropic.com/)
ANTHROPIC_API_KEY=sk-ant-...

# Google AI (https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=AIza...

# AssemblyAI for transcription (https://www.assemblyai.com/)
ASSEMBLYAI_API_KEY=...
```

### Optional (Performance)

```bash
# ============================================
# PERFORMANCE OPTIMIZATION
# ============================================
FAST_STARTUP=true
```

---

## ▲ Vercel (Frontend) Environment Variables

Copy this to your Vercel project's Environment Variables:

```bash
# ============================================
# BACKEND API URL
# ============================================
# Replace with your Railway backend URL from above deployment
VITE_API_URL=https://your-app-name.up.railway.app
```

**Important:** Do NOT include trailing slash in VITE_API_URL

---

## 🔒 How to Generate Secret Keys

### Option 1: Python (Recommended)

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate SESSION_SECRET (run again for different value)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Option 2: OpenSSL

```bash
openssl rand -base64 32
```

### Option 3: Online Generator

Use a secure password generator like:
- https://www.random.org/strings/
- Generate 32+ character alphanumeric strings

---

## 📝 Step-by-Step Setup

### Step 1: Prepare Your Credentials

1. **Database URL**
   - Railway PostgreSQL: Copy from Railway dashboard
   - Neon: Copy from Neon dashboard
   - Other: Format as `postgresql://user:password@host:port/database`

2. **Secret Keys**
   - Run the Python command above twice
   - Save both keys (they should be different)

3. **Qdrant** (if using vector database features)
   - Login to Qdrant Cloud
   - Create or access your cluster
   - Copy the URL and API key

4. **AI API Keys** (optional but recommended)
   - OpenAI: Get from platform.openai.com
   - Anthropic: Get from console.anthropic.com
   - Google: Get from makersuite.google.com

### Step 2: Add to Railway

1. Go to your Railway project
2. Click on your service
3. Go to "Variables" tab
4. Click "New Variable"
5. Add each variable one by one (or use "Raw Editor" to paste all at once)
6. Click "Deploy" or wait for auto-deploy

### Step 3: Add to Vercel

1. Go to your Vercel project
2. Go to "Settings" → "Environment Variables"
3. Add `VITE_API_URL` with your Railway URL
4. Redeploy your frontend

---

## ✅ Verification Checklist

After setting environment variables:

### Backend (Railway)
- [ ] DATABASE_URL is set and valid format
- [ ] SECRET_KEY is set (32+ characters)
- [ ] SESSION_SECRET is set and different from SECRET_KEY
- [ ] FLASK_ENV=production
- [ ] FLASK_APP=main.py
- [ ] QDRANT_URL and QDRANT_API_KEY set (if using)
- [ ] At least one AI API key set (if using AI features)

### Frontend (Vercel)
- [ ] VITE_API_URL is set
- [ ] VITE_API_URL points to your Railway backend
- [ ] VITE_API_URL has NO trailing slash

### Test After Setup
- [ ] Backend health check works: `curl https://your-app.railway.app/health`
- [ ] Frontend loads: Open Vercel URL in browser
- [ ] Can login: Try authentication
- [ ] No CORS errors: Check browser console (F12)

---

## 🔍 Troubleshooting

### Backend won't start
**Problem:** Railway deployment fails or crashes immediately

**Solutions:**
1. Check all required variables are set (especially DATABASE_URL, SECRET_KEY)
2. Verify DATABASE_URL format is correct
3. Check Railway logs for specific error messages
4. Ensure no trailing spaces in variable values

### Frontend can't connect to backend
**Problem:** API calls fail with CORS or connection errors

**Solutions:**
1. Verify VITE_API_URL is exactly your Railway URL
2. Make sure there's NO trailing slash in VITE_API_URL
3. Test backend directly: `curl https://your-railway-url/health`
4. Check browser console (F12) for specific error messages
5. Redeploy frontend after changing VITE_API_URL

### Database connection fails
**Problem:** "Unable to connect to database" error

**Solutions:**
1. Verify DATABASE_URL format: `postgresql://user:password@host:port/database`
2. Check if database service is running
3. Verify credentials are correct
4. Check if database accepts connections from Railway's IP ranges
5. Try connecting from Railway CLI: `railway run python -c "from database import db; print('OK')"`

### AI features not working
**Problem:** Assistants return errors or don't respond

**Solutions:**
1. Verify at least one AI API key is set (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY)
2. Check API key is valid and has credits/quota
3. Test API key directly with provider's API
4. Check Railway logs for specific API errors

---

## 📋 Environment Variables Quick Copy

### For Railway (Raw Editor)

```
# ⚠️ REPLACE ALL VALUES BELOW WITH YOUR ACTUAL CREDENTIALS
# These are examples only - do not use as-is

DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-generated-secret-key-here
SESSION_SECRET=your-different-session-secret-here
FLASK_ENV=production
FLASK_APP=main.py
QDRANT_URL=https://your-cluster.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-key-here
OPENAI_API_KEY=sk-proj-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=your-google-key
FAST_STARTUP=true
```

### For Vercel

```
VITE_API_URL=https://your-app-name.up.railway.app
```

**Remember:** Replace all placeholder values with your actual credentials!

---

## 🔐 Security Best Practices

1. ✅ **Never commit .env files to git**
2. ✅ **Use strong, unique secrets** (32+ characters)
3. ✅ **Rotate credentials regularly** (every 90 days)
4. ✅ **Use different credentials** for dev/staging/production
5. ✅ **Keep API keys secure** - don't share in public channels
6. ✅ **Monitor usage** of API keys for unusual activity
7. ✅ **Enable 2FA** on all service accounts
8. ✅ **Use environment variables** instead of hardcoding secrets

---

## 📚 Additional Resources

- [Railway Environment Variables Docs](https://docs.railway.app/develop/variables)
- [Vercel Environment Variables Docs](https://vercel.com/docs/projects/environment-variables)
- [Flask Configuration Best Practices](https://flask.palletsprojects.com/en/stable/config/)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)

---

**Last Updated:** 2025-12-22
**Next Review:** After first successful deployment
