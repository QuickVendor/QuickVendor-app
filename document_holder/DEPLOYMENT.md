# QuickVendor - Render Deployment Guide

## Overview

QuickVendor is a complete e-commerce platform that allows vendors to create online stores and sell products through WhatsApp integration. This guide covers deployment to Render.

## Features

- **User Authentication** - Secure registration and login
- **Product Management** - Create, edit, delete products with multiple images
- **Shareable Storefronts** - Public store pages for each vendor
- **WhatsApp Integration** - Direct customer contact links
- **Click Tracking** - Product interest analytics
- **Mobile Responsive** - Works on all devices
- **PostgreSQL Database** - Production-ready data storage

---

## Prerequisites

- GitHub account with your QuickVendor repository
- Render account (free tier available)
- Basic knowledge of environment variables

---

## Deployment Steps

### Step 1: Deploy PostgreSQL Database (2 minutes)

1. **Create Database Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **"New"** → **"PostgreSQL"**
   - Configure:
     ```
     Name: quickvendor-db
     Database: quickvendor
     User: quickvendor_user
     Region: Choose closest to your users
     Plan: Free (development) or Starter ($7/month)
     ```
   - Click **"Create Database"**

2. **Copy Connection String**
   - After creation, go to database info page
   - Copy the **External Database URL**
   - Save this for Step 2

### Step 2: Deploy Backend Service (5 minutes)

1. **Create Web Service**
   - Click **"New"** → **"Web Service"**
   - Connect your GitHub repository

2. **Configure Backend**
   ```
   Name: quickvendor-backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Root Directory: backend
   ```

3. **Add Environment Variables**
   ```bash
   DATABASE_URL=<your-postgresql-connection-string>
   SECRET_KEY=<generate-secure-32-char-key>
   ENVIRONMENT=production
   PYTHONPATH=/opt/render/project/src
   ```

   **Generate SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Deploy**
   - Click **"Create Web Service"**
   - Wait for deployment (~3-5 minutes)
   - Copy your backend URL

### Step 3: Deploy Frontend Service (3 minutes)

1. **Create Static Site**
   - Click **"New"** → **"Static Site"**
   - Connect same GitHub repository

2. **Configure Frontend**
   ```
   Name: quickvendor-frontend
   Build Command: npm install && npm run build
   Publish Directory: dist
   Root Directory: frontend
   ```

3. **Add Environment Variable**
   ```bash
   VITE_API_BASE_URL=<your-backend-url-from-step-2>
   ```

4. **Deploy**
   - Click **"Create Static Site"**
   - Wait for deployment (~2-3 minutes)

---

## Testing Your Deployment

### Backend Health Check
```bash
curl https://your-backend-url.onrender.com/api/health
```

**Expected Response:**
```json
{"status": "OK", "message": "QuickVendor API is healthy"}
```

### Frontend Testing
1. Visit your frontend URL
2. Test user registration
3. Test product creation
4. Verify WhatsApp links work
5. Check mobile responsiveness

---

## Environment Variables Reference

### Backend Required Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secure-32-character-key
ENVIRONMENT=production
PYTHONPATH=/opt/render/project/src
```

### Frontend Required Variables
```bash
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```

---

## Troubleshooting

### Common Issues

**Build Failures:**
- Check service logs in Render dashboard
- Verify all dependencies in requirements.txt/package.json

**Database Connection Errors:**
- Ensure DATABASE_URL is correctly formatted
- Verify PostgreSQL service is running

**CORS Errors:**
- Check VITE_API_BASE_URL matches backend URL exactly
- Ensure ENVIRONMENT=production is set on backend

**File Upload Issues:**
- Render has ephemeral storage - uploaded files may not persist
- Consider using cloud storage (AWS S3, Cloudinary) for production

---

## Production Considerations

### Performance
- Free tier services sleep after inactivity
- Consider paid plans for production use
- Database connections may have limits

### Storage
- Uploaded files are stored in ephemeral storage
- For production, integrate cloud storage services

### Security
- Always use HTTPS in production
- Regularly update SECRET_KEY
- Monitor for security vulnerabilities

---

## Post-Deployment

### Custom Domains (Optional)
1. Add custom domain in Render dashboard
2. Update DNS records as instructed
3. SSL certificates are automatically provided

### Monitoring
- Check service logs regularly
- Monitor database usage
- Set up alerts for downtime

---

## Support

For deployment issues:
1. Check Render service logs
2. Verify environment variables
3. Test API endpoints individually
4. Review browser console for frontend errors

---

**Your QuickVendor platform is now live! **

**Frontend:** `https://your-frontend-url.onrender.com`  
**Backend API:** `https://your-backend-url.onrender.com`
