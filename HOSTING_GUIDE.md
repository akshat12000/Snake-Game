# 🚀 Snake Game Update Server - Hosting Guide

This guide will help you deploy the Snake Game Update Server to various cloud platforms, making it accessible to anyone worldwide.

## 📋 Prerequisites

- Python 3.8+ locally installed
- Git installed and configured
- Account on your chosen hosting platform
- Basic understanding of environment variables

## 🔧 Pre-Deployment Setup

1. **Prepare Your Files**
   ```bash
   # Ensure you have all deployment files:
   ls -la
   # Should show: update_server_production.py, requirements.txt, Procfile, Dockerfile, etc.
   ```

2. **Test Locally First**
   ```bash
   pip install -r requirements.txt
   python update_server_production.py
   # Visit http://localhost:5000 to verify it works
   ```

3. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your production values
   ```

## ☁️ Cloud Hosting Options

### 🟢 Option 1: Railway (Recommended - Easiest)

Railway offers simple deployment with automatic HTTPS and custom domains.

1. **Sign Up**: Visit [railway.app](https://railway.app) and create account
2. **Deploy from GitHub**:
   - Connect your GitHub repository
   - Select your Snake Game repository
   - Railway auto-detects Python and uses `railway.toml`

3. **Set Environment Variables**:
   ```bash
   # In Railway dashboard, go to Variables tab:
   FLASK_ENV=production
   BASE_URL=https://your-project-name.up.railway.app
   SECRET_KEY=your-secure-random-key-here
   LOG_LEVEL=INFO
   ```

4. **Deploy**:
   - Railway automatically deploys on git push
   - Your server will be live at: `https://your-project-name.up.railway.app`

**✅ Pros**: Free tier, automatic HTTPS, easy setup, good performance
**❌ Cons**: Limited free hours per month

---

### 🔵 Option 2: Heroku

Heroku is a veteran platform with excellent documentation and reliability.

1. **Install Heroku CLI**: [Download here](https://devcenter.heroku.com/articles/heroku-cli)

2. **Create and Deploy**:
   ```bash
   heroku login
   heroku create your-snake-server-name
   
   # Set environment variables
   heroku config:set FLASK_ENV=production
   heroku config:set BASE_URL=https://your-snake-server-name.herokuapp.com
   heroku config:set SECRET_KEY=your-secure-key
   heroku config:set LOG_LEVEL=INFO
   
   # Deploy
   git push heroku master
   ```

3. **Your server**: `https://your-snake-server-name.herokuapp.com`

**✅ Pros**: Very reliable, excellent docs, good free tier
**❌ Cons**: Apps sleep after 30 min inactivity (free tier)

---

### 🟠 Option 3: Render

Render offers modern hosting with good performance and competitive pricing.

1. **Sign Up**: Visit [render.com](https://render.com)
2. **Create Web Service**:
   - Connect GitHub repository
   - Choose "Web Service"
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python update_server_production.py`

3. **Environment Variables** (in Render dashboard):
   ```
   FLASK_ENV=production
   BASE_URL=https://your-service-name.onrender.com
   SECRET_KEY=your-secure-key
   LOG_LEVEL=INFO
   ```

4. **Deploy**: Render auto-deploys from your repository

**✅ Pros**: No sleep on free tier, good performance, modern platform
**❌ Cons**: Slower cold starts on free tier

---

### 🔴 Option 4: DigitalOcean App Platform

Professional-grade hosting with excellent scalability.

1. **Sign Up**: Visit [digitalocean.com](https://digitalocean.com)
2. **Create App**:
   - Choose GitHub repository
   - Select Python environment
   - Configure build and run commands

3. **Environment Variables**:
   ```
   FLASK_ENV=production
   BASE_URL=https://your-app-name.ondigitalocean.app
   SECRET_KEY=your-secure-key
   LOG_LEVEL=INFO
   ```

**✅ Pros**: Professional features, excellent scalability, no cold starts
**❌ Cons**: No free tier (starts at $5/month)

---

### 🐳 Option 5: Docker Deployment (Any Platform)

Use Docker for consistent deployment across any platform that supports containers.

1. **Build Docker Image**:
   ```bash
   docker build -t snake-update-server .
   ```

2. **Test Locally**:
   ```bash
   docker-compose up
   # Visit http://localhost:5000
   ```

3. **Deploy to Container Platform**:
   - **Google Cloud Run**: `gcloud run deploy`
   - **AWS Fargate**: Use ECS with Fargate
   - **Azure Container Instances**: `az container create`

---

## 🔧 Post-Deployment Configuration

### 1. Update Client Configuration

Once your server is deployed, update the client to use your production server:

**Option A: Environment-based (Recommended)**
```python
# In simple_update_checker.py, update the server URL:
SERVER_URL = os.environ.get('UPDATE_SERVER_URL', 'https://your-deployed-server.com')
```

**Option B: Configuration File**
```python
# Create config.json:
{
    "update_server_url": "https://your-deployed-server.com"
}
```

### 2. Test Your Deployment

```bash
# Test version endpoint
curl https://your-server.com/api/version

# Test health check
curl https://your-server.com/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-09-20T10:30:00",
  "uptime": "unknown"
}
```

### 3. Update Your Game

Rebuild your game executable with the new server URL:
```bash
python build_release.py
```

## 📊 Monitoring and Maintenance

### Check Server Status
```bash
# Quick status check
curl https://your-server.com/

# Detailed stats
curl https://your-server.com/api/stats
```

### View Logs
- **Railway**: Dashboard → Deployments → View Logs
- **Heroku**: `heroku logs --tail`
- **Render**: Dashboard → Logs tab
- **DigitalOcean**: Dashboard → Runtime Logs

### Update Your Server
1. Make changes to your code
2. Commit and push to GitHub
3. Most platforms auto-deploy on git push

## 🔒 Security Best Practices

1. **Use Strong Secret Keys**:
   ```bash
   # Generate secure key:
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Enable HTTPS** (most platforms do this automatically)

3. **Set Proper Environment Variables**:
   ```bash
   FLASK_ENV=production  # Never use 'development' in production
   SECRET_KEY=your-actual-secure-key
   LOG_LEVEL=WARNING     # Reduce log verbosity in production
   ```

4. **Monitor Your Server**:
   - Set up uptime monitoring (UptimeRobot, Pingdom)
   - Check logs regularly
   - Monitor resource usage

## 🆘 Troubleshooting

### Common Issues

**Issue**: Server returns 500 errors
```bash
# Check logs and ensure all environment variables are set
curl https://your-server.com/health
```

**Issue**: Files not found (404 on /api/download)
```bash
# Ensure updates/ directory exists and contains SnakeGame.exe
# Check server stats: curl https://your-server.com/api/stats
```

**Issue**: Client can't connect
```bash
# Verify CORS is enabled and server URL is correct
# Test with: curl https://your-server.com/api/version
```

### Getting Help

1. **Check server logs** first - they contain detailed error information
2. **Test endpoints manually** with curl or browser
3. **Verify environment variables** are set correctly
4. **Check platform-specific documentation**

## 🎯 Recommended Deployment

For most users, we recommend **Railway** because:
- ✅ Easiest setup (just connect GitHub)
- ✅ Automatic HTTPS
- ✅ Good free tier
- ✅ No server sleep issues
- ✅ Simple environment variable management

**Quick Railway Setup:**
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. "Deploy from GitHub repo"
4. Select your Snake Game repository
5. Set environment variables
6. Your server is live in 2-3 minutes! 🚀

---

## 🌐 Making It Public

Once deployed, your update server will be accessible worldwide at your chosen URL. Players using your Snake Game will automatically receive updates from your server.

**Share your game with the world:**
1. Deploy your update server using this guide
2. Build your game with the production server URL
3. Distribute your `SnakeGame.exe` to anyone
4. They'll automatically get updates from your hosted server! 

**Your game is now professionally deployed with worldwide accessibility!** 🎮✨