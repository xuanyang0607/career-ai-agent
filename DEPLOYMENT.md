# 🚀 Production Deployment Guide

This guide will help you deploy your Career AI Agent to the cloud so you can share it with 1-2 people securely.

## 🎯 **Deployment Options**

### **Option 1: Railway (Recommended - Free & Easy)**

Railway is perfect for small-scale deployments and offers a generous free tier.

#### **Step 1: Prepare Your Code**

1. **Update authentication credentials** in `auth.py`:
   ```python
   USERS = {
       "admin": generate_password_hash("your-secure-password-here"),
       "user1": generate_password_hash("user1-password"),
       "user2": generate_password_hash("user2-password")
   }
   ```

2. **Set environment variables** in Railway dashboard:
   - `GOOGLE_API_KEY` - Your Google AI API key
   - `SECRET_KEY` - A secure random string for session encryption

#### **Step 2: Deploy to Railway**

1. **Install Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy via GitHub** (recommended):
   - Push your code to GitHub
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect it's a Python app

3. **Set Environment Variables**:
   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     SECRET_KEY=your-secure-secret-key-here
     ```

4. **Deploy**:
   - Railway will automatically build and deploy
   - You'll get a URL like: `https://your-app-name.railway.app`

#### **Step 3: Share with Users**

Share the login credentials with your users:
- **URL**: `https://your-app-name.railway.app`
- **Username**: `user1` or `user2`
- **Password**: The password you set in `auth.py`

---

### **Option 2: Render (Alternative - Free)**

Render is another great option with a free tier.

#### **Step 1: Create render.yaml**

```yaml
services:
  - type: web
    name: career-ai-agent
    env: python
    buildCommand: pip install -r requirements.txt && python -m spacy download en_core_web_sm
    startCommand: python production.py
    envVars:
      - key: GOOGLE_API_KEY
        value: your_google_api_key_here
      - key: SECRET_KEY
        value: your-secure-secret-key-here
```

#### **Step 2: Deploy**

1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Render will automatically deploy

---

### **Option 3: Heroku (Paid but Reliable)**

Heroku is more established but requires a credit card.

#### **Step 1: Install Heroku CLI**

```bash
# macOS
brew tap heroku/brew && brew install heroku
```

#### **Step 2: Deploy**

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-career-ai-agent

# Set environment variables
heroku config:set GOOGLE_API_KEY=your_google_api_key_here
heroku config:set SECRET_KEY=your-secure-secret-key-here

# Deploy
git push heroku main
```

---

## 🔐 **Security Configuration**

### **Update Authentication**

Edit `auth.py` and change the default passwords:

```python
USERS = {
    "admin": generate_password_hash("your-secure-admin-password"),
    "user1": generate_password_hash("user1-secure-password"),
    "user2": generate_password_hash("user2-secure-password")
}
```

### **Generate Secure Secret Key**

```python
import secrets
print(secrets.token_hex(32))
```

Use this as your `SECRET_KEY` environment variable.

---

## 🌐 **Domain & SSL**

### **Custom Domain (Optional)**

Most platforms provide free SSL certificates. For a custom domain:

1. **Railway**: Add custom domain in dashboard
2. **Render**: Add custom domain in dashboard
3. **Heroku**: `heroku domains:add yourdomain.com`

---

## 📊 **Monitoring & Logs**

### **View Logs**

- **Railway**: Dashboard → Deployments → View logs
- **Render**: Dashboard → Your service → Logs
- **Heroku**: `heroku logs --tail`

### **Health Check**

Your app includes a health check endpoint:
- `https://your-app.railway.app/health`

---

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Build Fails**:
   - Check if all dependencies are in `requirements.txt`
   - Ensure spaCy model is downloaded in build command

2. **App Crashes**:
   - Check logs for error messages
   - Verify environment variables are set correctly

3. **Authentication Issues**:
   - Ensure `SECRET_KEY` is set
   - Check if passwords are correctly hashed

### **Performance Optimization**

For better performance:

1. **Enable Caching**:
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

2. **Rate Limiting**:
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=get_remote_address)
   ```

---

## 📱 **Sharing with Users**

### **User Instructions**

Send this to your users:

```
🔐 Career AI Agent Access

URL: https://your-app-name.railway.app
Username: user1
Password: user1-password

Features:
- Resume analysis and parsing
- Career intelligence and market insights
- Personalized upskilling plans
- Real job search from LinkedIn, Indeed, Glassdoor, etc.

Contact admin if you need help or want to change your password.
```

### **User Management**

To add/remove users, edit the `USERS` dictionary in `auth.py` and redeploy.

---

## 💰 **Costs**

- **Railway**: Free tier includes 500 hours/month
- **Render**: Free tier includes 750 hours/month
- **Heroku**: $7/month for basic dyno

For 1-2 users, the free tiers should be sufficient.

---

## 🎉 **Success!**

Once deployed, your Career AI Agent will be:
- ✅ **Secure** - Password protected
- ✅ **Accessible** - Available 24/7
- ✅ **Scalable** - Can handle multiple users
- ✅ **Professional** - Production-ready

Your users can now access the tool from anywhere with just a web browser!
