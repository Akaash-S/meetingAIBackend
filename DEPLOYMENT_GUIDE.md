# 🚀 Backend Deployment Guide for Render

## 📋 **Prerequisites**

1. **Render Account** - Sign up at [render.com](https://render.com)
2. **GitHub Repository** - Push your code to GitHub
3. **Neon PostgreSQL Database** - Set up your database
4. **Environment Variables** - Prepare your API keys

## 🐳 **Docker Setup**

### **Files Created:**
- `Dockerfile` - Multi-stage Docker build
- `docker-compose.yml` - Local development setup
- `nginx.conf` - Production reverse proxy
- `requirements.txt` - Python dependencies
- `env.production` - Production environment template

### **Docker Features:**
- ✅ **Python 3.12** slim image
- ✅ **Gunicorn** WSGI server
- ✅ **PostgreSQL** client libraries
- ✅ **WebSocket** support
- ✅ **Health checks** for monitoring
- ✅ **Security** hardening
- ✅ **Nginx** reverse proxy (optional)

## 🚀 **Deployment Steps**

### **Step 1: Prepare Your Repository**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Docker configuration for Render deployment"
   git push origin main
   ```

2. **Verify Files:**
   - `backend/Dockerfile` ✅
   - `backend/requirements.txt` ✅
   - `backend/app.py` ✅
   - `backend/routes/` directory ✅

### **Step 2: Create Render Service**

1. **Go to Render Dashboard:**
   - Visit [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"

2. **Connect Repository:**
   - Connect your GitHub account
   - Select your repository
   - Choose the branch (usually `main`)

3. **Configure Service:**
   - **Name:** `ai-meeting-assistant-backend`
   - **Root Directory:** `backend`
   - **Runtime:** `Docker`
   - **Dockerfile Path:** `backend/Dockerfile`

### **Step 3: Environment Variables**

Add these environment variables in Render dashboard:

```bash
# Required
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=your-super-secret-key-here

# Optional (for full functionality)
RAPIDAPI_KEY=your-rapidapi-key
GEMINI_API_KEY=your-gemini-key
SENDGRID_API_KEY=your-sendgrid-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

### **Step 4: Deploy**

1. **Click "Create Web Service"**
2. **Wait for deployment** (5-10 minutes)
3. **Check logs** for any errors
4. **Test the service** at the provided URL

## 🔧 **Configuration Details**

### **Docker Configuration:**
```dockerfile
# Multi-stage build for optimization
FROM python:3.12-slim

# Security hardening
RUN useradd --create-home --shell /bin/bash app
USER app

# Health checks
HEALTHCHECK --interval=30s --timeout=10s

# Production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4"]
```

### **Gunicorn Configuration:**
- **Workers:** 4 (adjust based on Render plan)
- **Timeout:** 120 seconds
- **Keep-alive:** 2 seconds
- **Max requests:** 1000 per worker

### **Nginx Configuration (Optional):**
- **Rate limiting** for API endpoints
- **CORS headers** for cross-origin requests
- **WebSocket support** for real-time features
- **File upload** optimization

## 📊 **Monitoring & Health Checks**

### **Health Endpoint:**
```
GET https://your-service.onrender.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### **WebSocket Endpoint:**
```
WSS://your-service.onrender.com/audio
```

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **Build Fails:**
   - Check Dockerfile syntax
   - Verify requirements.txt
   - Check build logs in Render

2. **Service Won't Start:**
   - Check environment variables
   - Verify DATABASE_URL format
   - Check application logs

3. **Database Connection Fails:**
   - Verify Neon PostgreSQL URL
   - Check SSL mode requirement
   - Test connection locally

4. **WebSocket Issues:**
   - Check if WSS is supported
   - Verify CORS configuration
   - Test with browser console

### **Debug Commands:**
```bash
# Test locally with Docker
docker build -t ai-meeting-backend .
docker run -p 5000:5000 --env-file .env ai-meeting-backend

# Check logs
docker logs <container-id>

# Test health endpoint
curl https://your-service.onrender.com/api/health
```

## 🚀 **Production Optimization**

### **Render Plan Recommendations:**
- **Starter Plan:** Good for development/testing
- **Standard Plan:** Recommended for production
- **Pro Plan:** For high-traffic applications

### **Performance Tuning:**
```python
# In app.py, add these for production
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year
```

### **Security Enhancements:**
- Use strong SECRET_KEY
- Enable HTTPS only
- Set up rate limiting
- Monitor for suspicious activity

## 📈 **Scaling Considerations**

### **Auto-scaling:**
- Render automatically scales based on traffic
- Monitor CPU and memory usage
- Set up alerts for high usage

### **Database Optimization:**
- Use connection pooling
- Monitor query performance
- Set up database backups

### **CDN Integration:**
- Use Cloudflare for static assets
- Enable gzip compression
- Cache API responses appropriately

## 🎯 **Post-Deployment Checklist**

- [ ] Service is running and healthy
- [ ] Database connection works
- [ ] WebSocket endpoint accessible
- [ ] File uploads work
- [ ] CORS headers configured
- [ ] Environment variables set
- [ ] Monitoring enabled
- [ ] SSL certificate active
- [ ] Health checks passing
- [ ] Extension can connect

## 🔗 **Update Extension Configuration**

After deployment, update your extension to use the production URL:

```javascript
// In popup.js, update the backend URL
this.backendUrl = 'wss://your-service.onrender.com/audio';
```

## 🎉 **Success!**

Your AI Meeting Assistant backend is now deployed and ready for production use! The extension will be able to connect to the deployed backend and provide real-time meeting recording and AI processing capabilities.

**Next Steps:**
1. Test the deployed service
2. Update extension configuration
3. Monitor performance and usage
4. Scale as needed based on traffic
