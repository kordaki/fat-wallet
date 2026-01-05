# Deploy to Render.com - Step-by-Step Guide

## Prerequisites
- GitHub account
- Render.com account (free)
- Your code pushed to GitHub

## Step 1: Push Code to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/fat-wallet.git
git branch -M main
git push -u origin main
```

## Step 2: Create Background Worker on Render

1. Go to https://render.com
2. Click **"New +"** → **"Background Worker"**
3. Connect your GitHub repository
4. Configure the worker:

### Build Settings:
- **Name**: `fat-wallet-bot`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python market_bot_v2.py`

### Environment Variables:
Click **"Add Environment Variable"** for each:

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | `8573028822:AAGLvpsvmNUGcuOGZ7QL8ui5UlV7Ks7luOg` |
| `TELEGRAM_CHAT_ID` | `-1003544900612` |

### Plan:
- Select **"Free"** plan

## Step 3: Deploy

1. Click **"Create Background Worker"**
2. Render will automatically:
   - Clone your repo
   - Install dependencies
   - Start your bot
3. Monitor the logs to verify it started

## Step 4: Verify Deployment

You should see in the logs:
```
============================================================
Fat Wallet Market Bot Started
============================================================
Watchlist: 8 stocks
Check interval: 15 minutes
============================================================
```

And your Telegram channel should receive the startup message!

## Step 5: Test Admin Commands

Send to your bot on Telegram:
```
/start
/watchlist
/settings
```

## Troubleshooting

### Bot not starting?
- Check logs in Render dashboard
- Verify environment variables are set correctly
- Make sure `.env` file is in `.gitignore` (don't commit secrets!)

### Database not working?
- Render workers have persistent disk storage
- Database will be created automatically on first run

### Need to restart?
- Go to Render dashboard
- Click "Manual Deploy" → "Clear build cache & deploy"

## Updating Your Bot

After making code changes:

```bash
git add .
git commit -m "Update bot"
git push
```

Render will automatically redeploy! 🚀

## Free Tier Limits

- 750 hours/month (enough for 24/7 operation)
- 512MB RAM (plenty for your bot)
- 0.1 CPU (sufficient for light tasks)

## Cost

**$0/month** - Completely free! 🎉
