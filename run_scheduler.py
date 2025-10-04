#!/usr/bin/env python3
"""
Scheduler wrapper for Railway - runs check_appointments.py every 5 minutes
"""
import time
import subprocess
import datetime
import sys

# Interval in seconds (5 minutes = 300 seconds)
CHECK_INTERVAL = 300

def run_check():
    """Run the appointment checker script"""
    try:
        print(f"\n{'='*60}")
        print(f"Running check at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        result = subprocess.run(
            [sys.executable, "check_appointments.py"],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✅ Check completed successfully")
        else:
            print(f"\n⚠️  Check completed with exit code: {result.returncode}")
            
    except Exception as e:
        print(f"\n❌ Error running check: {e}")

def main():
    print("🚀 Rotterdam Appointment Scheduler Started!")
    print(f"⏰ Will check every {CHECK_INTERVAL} seconds ({CHECK_INTERVAL//60} minutes)")
    print(f"🕐 First check starting now...\n")
    
    while True:
        run_check()
        
        next_run = datetime.datetime.now() + datetime.timedelta(seconds=CHECK_INTERVAL)
        print(f"\n💤 Sleeping until {next_run.strftime('%H:%M:%S')}")
        print(f"{'='*60}\n")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Scheduler stopped by user")
        sys.exit(0)

