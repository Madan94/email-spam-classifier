# Render Deployment Fix

## Issue
`gunicorn: command not found` error during deployment.

## Solution

### Option 1: Update Render Dashboard Settings (Recommended)

1. Go to your Render dashboard → Your Web Service → Settings

2. Update the **Build Command**:
   ```
   pip install --upgrade pip && pip install -r requirements.txt
   ```

3. Update the **Start Command**:
   ```
   python -m gunicorn app:app --bind 0.0.0.0:$PORT
   ```

4. Make sure **Python Version** is set to `3.11.9` (or `3.11`)

5. Click **Save Changes** and **Manual Deploy** → **Deploy latest commit**

### Option 2: Use the build.sh script

1. In Render dashboard, set **Build Command** to:
   ```
   chmod +x build.sh && ./build.sh
   ```

2. Set **Start Command** to:
   ```
   python -m gunicorn app:app --bind 0.0.0.0:$PORT
   ```

### Option 3: Use render.yaml (Auto-deploy)

If you're using `render.yaml`, make sure it's committed to your repo and Render will use it automatically.

## Verify Environment Variables

Make sure these are set in Render dashboard → Environment:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `FLASK_ENV=production`

## After Fix

Once deployed successfully, your app will be available at:
`https://your-app-name.onrender.com`

## Troubleshooting

If still having issues:
1. Check the **Logs** tab in Render dashboard
2. Verify `gunicorn==21.2.0` is in `requirements.txt`
3. Try clearing build cache: Settings → Clear build cache → Deploy

