# Railway.app Setup Guide

## Why Railway?

- ✅ $5/month free credit (enough for ~300,000 executions!)
- ✅ Persistent containers (no Chrome reinstall overhead)
- ✅ ~5 second execution time (vs 33s on GitHub Actions)
- ✅ Super simple setup
- ✅ Built-in cron scheduling

## Setup Steps (5 minutes)

### 1. Create Railway Account

Go to [Railway.app](https://railway.app/) and sign up with GitHub

### 2. Deploy Your Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose `rotterdam-appointment-checker`
4. Railway will automatically detect the Dockerfile and deploy!

### 3. How It Works

Railway runs the container continuously, and `run_scheduler.py` handles the scheduling internally:
- Runs the check immediately on startup
- Waits 5 minutes
- Runs again
- Repeats forever

No cron configuration needed - it's all built into the container!

### 4. Add Environment Variable

1. In your project, go to **"Variables"** tab
2. Click **"Add Variable"**
3. Add:
   - **Name:** `NTFY_TOPIC`
   - **Value:** `your-unique-topic-name` (e.g., `rotterdam-appt-nadir-2025`)
4. Click **"Save"**

### 5. Subscribe to Notifications

- **On phone:** Download [ntfy app](https://ntfy.sh/) and subscribe to your topic
- **On desktop:** Visit https://ntfy.sh/your-topic-name

### 6. Deploy!

Click **"Deploy"** and you're done! 🎉

## Monitoring

- **View logs:** Click on your service → "Logs" tab
- **Check runs:** See execution history in the logs
- **Test manually:** Click "Redeploy" to trigger immediately

## Cost Calculation

**At 5-minute intervals:**
- 8,640 runs/month × 5 seconds = 43,200 seconds = 12 hours compute/month
- Railway charges ~$0.000463/minute
- **Total: ~$0.33/month** (well under $5 free credit!)

You could run this for **15 months** on the free tier alone!

## Advantages over GitHub Actions

| Feature | Railway | GitHub Actions |
|---------|---------|----------------|
| Execution time | ~5 seconds | ~33 seconds |
| Free tier | $5/month (~300k runs) | 2000 minutes |
| Setup complexity | Very Easy | Medium |
| Container persistence | Yes | No (fresh every time) |
| Chrome install time | Once | Every run |

## Troubleshooting

### Logs show Chrome errors
Make sure the Dockerfile is building correctly. Check the build logs.

### No notifications received
1. Verify `NTFY_TOPIC` environment variable is set
2. Make sure you're subscribed to the correct topic
3. Check the logs to see if the script is running

### Want to change frequency?

Add a `CRON_SCHEDULE` environment variable in Railway (default: `*/5 * * * *`):

**Common patterns:**
- Every 5 minutes: `*/5 * * * *` (default, 24/7)
- Every 10 minutes: `*/10 * * * *`
- Every 5 min, 8 AM - 10 PM: `*/5 8-22 * * *` (saves money!)
- Every 15 minutes: `*/15 * * * *`
- Every hour: `0 * * * *`
- Business hours only: `*/5 9-17 * * 1-5` (9 AM-5 PM, Mon-Fri)

**Format:** `minute hour day month day_of_week`

No code changes needed - just update the env variable in Railway!

## Support

Railway Discord: https://discord.gg/railway
Railway Docs: https://docs.railway.app/

