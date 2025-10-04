# Rotterdam Appointment Checker

Automated Python script that checks for available naturalization appointment slots in Rotterdam and sends push notifications when slots become available.

## Features

- 🤖 Runs automatically every 15 minutes via GitHub Actions
- 📱 Sends push notifications via ntfy.sh (zero setup required!)
- 🎯 Filters out waiting list entries (only notifies for actual appointments)
- ☁️ Completely cloud-based (no local machine needed)
- 🔄 Can be triggered manually from GitHub Actions UI

## Setup Instructions

### 1. Fork/Clone this Repository

```bash
git clone https://github.com/YOUR_USERNAME/rotterdam-appointment-checker.git
cd rotterdam-appointment-checker
```

### 2. Choose Your Notification Topic

Pick a unique topic name (e.g., `rotterdam-appt-yourname-2025`)

**Subscribe to notifications:**
- **On your phone:** Download the [ntfy app](https://ntfy.sh/) (iOS/Android) and subscribe to your topic
- **On desktop:** Visit https://ntfy.sh/your-topic-name and bookmark it
- **No account or API key needed!**

### 3. Configure GitHub Secret

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add one secret:

**NTFY_TOPIC**
- Value: Your unique topic name (e.g., `rotterdam-appt-nadir-2025`)
- Note: If you skip this, it will use a default topic (not recommended)

### 4. Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. Click "I understand my workflows, go ahead and enable them"
3. The workflow will now run automatically every 15 minutes

### 5. Manual Trigger (Optional)

To test immediately:
1. Go to **Actions** tab
2. Click "Check Rotterdam Appointments" workflow
3. Click "Run workflow" → "Run workflow"

## How It Works

1. The script opens the Rotterdam appointment website
2. Selects "2 people" from the dropdown
3. Checks for available appointment slots
4. Filters out "waiting list" entries
5. Sends a push notification via ntfy.sh if actual slots are found
6. Runs every 15 minutes automatically

## Local Development

### Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -r requirements.txt

# Set environment variable
export NTFY_TOPIC="your-topic-name"

# Run the script
python check_appointments.py
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export NTFY_TOPIC="your-topic-name"

# Run the script
python check_appointments.py
```

## Customization

### Change Schedule Frequency

Edit `.github/workflows/check-appointments.yml`:

```yaml
schedule:
  - cron: '*/15 * * * *'  # Every 15 minutes
  # - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '0 * * * *'     # Every hour
  # - cron: '0 9-17 * * *'  # Every hour from 9 AM to 5 PM
```

### Change Number of People

Edit `check_appointments.py` line 71:

```python
select.select_by_value("1")  # 2 people (value "1" = 2 people)
# select.select_by_value("0")  # 1 person
# select.select_by_value("2")  # 3 people
```

### Receive Notifications on Multiple Devices

Simply subscribe to the same topic on all your devices:
- Phone: ntfy app
- Desktop: https://ntfy.sh/your-topic-name
- All devices will receive notifications simultaneously!

## Troubleshooting

### No notifications received

1. Check GitHub Actions logs:
   - Go to **Actions** tab → Select latest run → View logs
2. Verify your ntfy topic name is correct in GitHub Secrets
3. Make sure you're subscribed to the correct topic on ntfy.sh

### Script failing

- Check the Actions logs for error messages
- The script includes error reporting via push notifications
- Failed runs automatically upload logs as artifacts

## Notes

- GitHub Actions has usage limits on free accounts (2,000 minutes/month for free tier)
- This script respects the website by adding delays between actions
- The script runs in headless mode (no visible browser)

## License

MIT License - Feel free to use and modify as needed!

## Disclaimer

This script is for personal use only. Please respect the website's terms of service and don't abuse the automated checking functionality.

