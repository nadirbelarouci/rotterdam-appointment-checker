#!/usr/bin/env python3
"""
Scheduler wrapper for Railway - runs check_appointments.py using cron expressions
Uses APScheduler for production-grade scheduling with proper cron support
"""
import os
import sys
import subprocess
import datetime
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from datetime import timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cron expression: every 5 minutes
# Format: minute hour day month day_of_week
# Examples:
#   "*/5 * * * *"        - Every 5 minutes (24/7)
#   "*/5 8-22 * * *"     - Every 5 minutes, 8 AM - 10 PM
#   "*/10 * * * *"       - Every 10 minutes
#   "0 * * * *"          - Every hour on the hour
#   "0 9-17 * * 1-5"     - Every hour 9 AM-5 PM, Mon-Fri
CRON_SCHEDULE = os.getenv("CRON_SCHEDULE", "*/5 * * * *")

# Statistics
job_stats = {
    "total_runs": 0,
    "successful_runs": 0,
    "failed_runs": 0,
    "last_run_time": None,
    "last_run_status": None
}

def run_check():
    """Run the appointment checker script"""
    job_stats["total_runs"] += 1
    job_stats["last_run_time"] = datetime.datetime.now(timezone.utc)
    
    try:
        logger.info("="*70)
        logger.info(f"🔍 Starting appointment check #{job_stats['total_runs']}")
        logger.info("="*70)
        
        result = subprocess.run(
            [sys.executable, "check_appointments.py"],
            capture_output=False,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            job_stats["successful_runs"] += 1
            job_stats["last_run_status"] = "success"
            logger.info("✅ Check completed successfully")
        else:
            job_stats["failed_runs"] += 1
            job_stats["last_run_status"] = "failed"
            logger.warning(f"⚠️  Check completed with exit code: {result.returncode}")
        
        # Print statistics
        success_rate = (job_stats["successful_runs"] / job_stats["total_runs"] * 100) if job_stats["total_runs"] > 0 else 0
        logger.info(f"📊 Stats: {job_stats['total_runs']} runs | "
                   f"{job_stats['successful_runs']} ✅ | "
                   f"{job_stats['failed_runs']} ❌ | "
                   f"Success rate: {success_rate:.1f}%")
        logger.info("="*70 + "\n")
            
    except subprocess.TimeoutExpired:
        job_stats["failed_runs"] += 1
        job_stats["last_run_status"] = "timeout"
        logger.error("⏱️  Check timed out after 2 minutes")
    except Exception as e:
        job_stats["failed_runs"] += 1
        job_stats["last_run_status"] = "error"
        logger.error(f"❌ Error running check: {e}", exc_info=True)

def job_listener(event):
    """Listen to job events for logging"""
    if event.exception:
        logger.error(f"Job crashed with exception: {event.exception}")
    else:
        logger.debug(f"Job executed successfully")

def main():
    """Main scheduler loop"""
    logger.info("="*70)
    logger.info("🚀 Rotterdam Appointment Scheduler Starting...")
    logger.info("="*70)
    logger.info(f"📅 Schedule: {CRON_SCHEDULE}")
    logger.info(f"🌍 Timezone: UTC")
    logger.info(f"🐍 Python: {sys.version.split()[0]}")
    logger.info(f"🕐 Current time: {datetime.datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Parse cron expression to show next run (use UTC timezone)
    trigger = CronTrigger.from_crontab(CRON_SCHEDULE, timezone='UTC')
    logger.info("="*70)
    logger.info("✨ Scheduler ready! Waiting for first scheduled run...")
    logger.info("="*70 + "\n")
    
    # Create scheduler with UTC timezone
    scheduler = BlockingScheduler(timezone='UTC')
    
    # Add the job with cron expression
    scheduler.add_job(
        run_check,
        trigger=trigger,
        id='appointment_checker',
        name='Check Rotterdam Appointments',
        misfire_grace_time=60,  # Allow 60s grace if a job is missed
        max_instances=1,  # Only one instance at a time
        coalesce=True  # If multiple runs are pending, only run once
    )
    
    # Add listener for job events
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    
    # Print next run times
    job = scheduler.get_job('appointment_checker')
    logger.info(f"⏰ Next 5 scheduled runs:")
    next_runs = []
    test_time = datetime.datetime.now(timezone.utc)
    for i in range(5):
        next_run = trigger.get_next_fire_time(next_runs[-1] if next_runs else test_time, test_time)
        if next_run:
            next_runs.append(next_run)
            logger.info(f"   {i+1}. {next_run.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("")
    
    try:
        # Start the scheduler
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n👋 Scheduler stopped by user")
        scheduler.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()

