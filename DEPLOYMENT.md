# Deployment Guide

This guide covers deploying your Spam Email Classification web application to various hosting platforms.

## Prerequisites

Before deploying, ensure you have:
1. ✅ A Supabase project set up with the `users` table created
2. ✅ Your Supabase URL and API key ready
3. ✅ A GitHub account (for most platforms)
4. ✅ Your repository pushed to GitHub

## Environment Variables

You'll need to set these environment variables on your hosting platform:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SECRET_KEY=your-secret-key-here (generate a secure random string)
FLASK_ENV=production
```

**Generate a secure SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

---

## Option 1: Render (Recommended - Free Tier Available)

[Render](https://render.com) offers a free tier with automatic deployments from GitHub.

### Steps:

1. **Sign up** at [render.com](https://render.com) (use GitHub to sign in)

2. **Create a New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure the service:**
   - **Name**: spam-email-classifier (or your preferred name)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or choose a paid plan)

4. **Set Environment Variables:**
   - Go to "Environment" tab
   - Add:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `SECRET_KEY`
     - `FLASK_ENV=production`

5. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Your app will be available at `https://your-app-name.onrender.com`

### Render Free Tier Limits:
- Apps spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- 750 hours/month free

---

## Option 2: Railway

[Railway](https://railway.app) offers a simple deployment experience with a free tier.

### Steps:

1. **Sign up** at [railway.app](https://railway.app) (use GitHub)

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure:**
   - Railway auto-detects Python apps
   - It will use the `Procfile` automatically

4. **Set Environment Variables:**
   - Go to "Variables" tab
   - Add all required environment variables

5. **Deploy:**
   - Railway automatically deploys on every push to main branch
   - Get your app URL from the "Settings" → "Domains" section

---

## Option 3: Fly.io

[Fly.io](https://fly.io) offers global deployment with a generous free tier.

### Steps:

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up and login:**
   ```bash
   fly auth signup
   fly auth login
   ```

3. **Create fly.toml** (already created if you used the template):
   ```bash
   fly launch
   ```

4. **Set secrets:**
   ```bash
   fly secrets set SUPABASE_URL=your-url
   fly secrets set SUPABASE_KEY=your-key
   fly secrets set SECRET_KEY=your-secret-key
   ```

5. **Deploy:**
   ```bash
   fly deploy
   ```

---

## Option 4: PythonAnywhere

[PythonAnywhere](https://www.pythonanywhere.com) is great for Python apps with a free tier.

### Steps:

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload your code:**
   - Use the Files tab to upload your project
   - Or clone from GitHub using Bash console

3. **Create a Web App:**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Flask" and Python 3.11

4. **Configure WSGI file:**
   - Edit the WSGI file to point to your app:
   ```python
   import sys
   path = '/home/yourusername/Spam-Email-Classification'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```

5. **Set Environment Variables:**
   - In the Web app configuration, add environment variables

6. **Reload:**
   - Click the green "Reload" button

---

## Option 5: DigitalOcean App Platform

[DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform) offers easy deployment.

### Steps:

1. **Sign up** at [digitalocean.com](https://www.digitalocean.com)

2. **Create App:**
   - Click "Create" → "Apps"
   - Connect GitHub repository

3. **Configure:**
   - **Type**: Web Service
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `gunicorn app:app`
   - **Environment Variables**: Add all required vars

4. **Deploy:**
   - Review and create
   - Your app will be available at a DigitalOcean URL

---

## Option 6: VPS (Self-Hosted)

For full control, deploy on a VPS like DigitalOcean Droplet, Linode, or AWS EC2.

### Steps:

1. **Set up server:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3-pip python3-venv nginx -y
   ```

2. **Clone and set up:**
   ```bash
   git clone your-repo-url
   cd Spam-Email-Classification
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/spam-classifier.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=Spam Email Classifier
   After=network.target
   
   [Service]
   User=your-username
   WorkingDirectory=/home/your-username/Spam-Email-Classification
   Environment="PATH=/home/your-username/Spam-Email-Classification/venv/bin"
   Environment="SUPABASE_URL=your-url"
   Environment="SUPABASE_KEY=your-key"
   Environment="SECRET_KEY=your-secret-key"
   ExecStart=/home/your-username/Spam-Email-Classification/venv/bin/gunicorn app:app
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service:**
   ```bash
   sudo systemctl start spam-classifier
   sudo systemctl enable spam-classifier
   ```

5. **Configure Nginx:**
   ```bash
   sudo nano /etc/nginx/sites-available/spam-classifier
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
   
   Enable:
   ```bash
   sudo ln -s /etc/nginx/sites-available/spam-classifier /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## Post-Deployment Checklist

- [ ] Test all routes (home, signup, signin, prediction)
- [ ] Verify Supabase connection works
- [ ] Test user registration and login
- [ ] Test email classification
- [ ] Check that static files load correctly
- [ ] Verify HTTPS is enabled (most platforms do this automatically)
- [ ] Set up custom domain (optional)

---

## Troubleshooting

### App won't start
- Check environment variables are set correctly
- Verify all dependencies are in `requirements.txt`
- Check logs on your hosting platform

### Database connection errors
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check Supabase project is active
- Ensure `users` table exists in Supabase

### Static files not loading
- Verify static folder structure is correct
- Check file paths in templates use `/static/...`
- Some platforms require specific static file configuration

### Model files not found
- Ensure `model.pkl` and `vectorizer.pkl` are committed to git
- Check file paths in `app.py` are relative

---

## Recommended: Render (Easiest)

For the easiest deployment experience, I recommend **Render**:
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Easy environment variable management
- ✅ HTTPS by default
- ✅ Simple setup process

---

## Need Help?

If you encounter issues:
1. Check the platform's documentation
2. Review application logs
3. Verify all environment variables are set
4. Ensure your code is pushed to GitHub

