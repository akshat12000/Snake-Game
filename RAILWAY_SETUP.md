# Railway Deployment Setup

## Quick Setup for GitHub → Railway Integration

### 1. Connect to Railway
1. Go to [Railway](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose this repository (`Snake-Game`)

### 2. Railway will automatically:
- Detect `Procfile` → runs `python update_server.py`
- Install dependencies from `requirements.txt`
- Set up environment variables from Railway dashboard
- Deploy your update server

### 3. Configure Environment Variables in Railway
Go to your Railway project → Variables → Add:
```
PORT=8080
SERVER_HOST=0.0.0.0
DEBUG=false
```

### 4. Get Your Server URL
After deployment, Railway will provide a URL like:
`https://your-app-name.railway.app`

### 5. Update Your Local Config
Add the Railway URL to your local `.env` file:
```
PRODUCTION_SERVER_URL=https://your-app-name.railway.app
```

## How It Works
- **Push to GitHub** → Railway auto-deploys
- **Publisher GUI** → Creates releases locally
- **Update Server** → Serves from Railway (always latest from GitHub)
- **Game Updates** → Downloads from your Railway server

No manual deployment scripts needed! 🎯