from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup 
import time 
import requests 
import urllib.parse 
import datetime
import os
import atexit

# Global WebDriver instance (singleton pattern to reuse browser)
_driver_instance = None

def get_driver():
    """Get or create a singleton WebDriver instance"""
    global _driver_instance
    
    if _driver_instance is None:
        print("Creating new Chrome WebDriver instance...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        # Add memory optimization flags
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-default-apps")
        
        _driver_instance = webdriver.Chrome(options=chrome_options)
        print("Chrome WebDriver instance created successfully")
        
        # Register cleanup on exit
        atexit.register(cleanup_driver)
    
    return _driver_instance

def cleanup_driver():
    """Clean up the WebDriver instance"""
    global _driver_instance
    if _driver_instance is not None:
        try:
            print("Cleaning up Chrome WebDriver...")
            _driver_instance.quit()
            _driver_instance = None
            print("Chrome WebDriver cleaned up successfully")
        except Exception as e:
            print(f"Error cleaning up driver: {e}")

def reset_driver():
    """Reset the driver if it's in a bad state"""
    global _driver_instance
    if _driver_instance is not None:
        cleanup_driver()
    return get_driver()

# Function to send a push notification via ntfy.sh with priority
def send_notification_with_priority(message, title, priority="default"):
    # Get the ntfy topic from environment variable (or use default)
    ntfy_topic = os.environ.get('NTFY_TOPIC', 'rotterdam-appointments-default')
    ntfy_url = f'https://ntfy.sh/{ntfy_topic}'
    
    # Set tags based on priority
    if priority == "urgent":
        tags = "tada,rotating_light,calendar"
        priority_val = "urgent"
    else:
        tags = "clipboard,calendar"
        priority_val = "default"
    
    try:
        # Use query parameters for better emoji support
        params = {
            'title': title,
            'priority': priority_val,
            'tags': tags
        }
        
        response = requests.post(
            ntfy_url,
            data=message.encode('utf-8'),
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"Notification sent successfully to ntfy topic: {ntfy_topic}")
        else:
            print(f"Failed to send notification. Status code: {response.status_code}, response: {response.text}")
    except Exception as e:
        print(f"Error sending notification: {e}")


def main():
    """Main function to check appointments"""
    # Get the reusable driver instance
    try:
        driver = get_driver()
    except Exception as e:
        print(f"Failed to get driver, attempting reset: {e}")
        driver = reset_driver()
    
    # Open the URL
    driver.get("https://concern.ir.rotterdam.nl/afspraak/maken/product/indienen-naturalisatieverzoek") 

    try:
        # Get the current date and time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Script started at: {current_time}")

        time.sleep(2)  # Wait for page to fully load
        
        # Wait for the dropdown to be present and select "2" (value="1" means 2 people)
        print("Waiting for dropdown to be present...")
        dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id3"))
        )
        
        # Select the option for 2 people (value="1")
        select = Select(dropdown)
        select.select_by_value("1")  # This selects "2" from the dropdown
        print("Selected 2 people from dropdown")
        
        # Wait a bit for the page to react to the selection
        time.sleep(1)
        
        # Wait for the "Verder" button to be clickable and click it
        print("Waiting for 'Verder' button...")
        # Re-find the button to avoid stale element
        verder_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "id5"))
        )
        # Use JavaScript click to avoid interception issues
        driver.execute_script("arguments[0].click();", verder_button)
        print("Clicked 'Verder' button")

        # Wait for results page to load completely
        print("Waiting for results to load...")
        time.sleep(3)

        # Parse the updated HTML content with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Look for all buttons with class 'list-group-item-action' and not disabled
        available_dates = soup.find_all('button', class_='list-group-item-action')

        # Check for alert warning (no dates available)
        alert_no_dates = soup.find_all('div', class_='alert-warning')

        if alert_no_dates:
            message_first_part = "No available dates alert found."
            print(message_first_part)
        else:
            message_first_part = "Found something."
            print(message_first_part)

        # Filter out "Wachtrij beschikbaar" (waiting list) entries
        actual_available_slots = []
        
        if available_dates:
            for date_button in available_dates:
                if date_button.get('disabled') is None:
                    location = date_button.find('h3').text.strip() if date_button.find('h3') else ""
                    date_time = date_button.find('p').text.strip() if date_button.find('p') else ""
                    
                    # Skip if it's a waiting list entry
                    if "Wachtrij beschikbaar" in date_time or "wachtrij" in date_time.lower():
                        print(f"Skipping waiting list entry: {location} - {date_time}")
                        continue
                    
                    # This is an actual available slot!
                    actual_available_slots.append(f"{location}: {date_time}")

        if actual_available_slots:
            # We found actual appointment slots (not waiting list)!
            date_info = "\n".join(actual_available_slots)
            message = f"🎉🎉🎉 APPOINTMENT SLOTS AVAILABLE! 🎉🎉🎉\n\n{date_info}\n\nCheck immediately:\nhttps://concern.ir.rotterdam.nl/afspraak/maken/product/indienen-naturalisatieverzoek\n\nMessage Sent at: {current_time}"
            print(message)
            
            # Send the notification with high priority and special title
            send_notification_with_priority(message, "🎉 SLOTS AVAILABLE!", "urgent")
        else:
            print("No actual appointment slots found (only waiting list or nothing).")
            print(f"Check completed at: {current_time} - No notification sent")

    except Exception as e:
        error_message = f"❌ ERROR: Script failed with exception: {str(e)}\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(error_message)
        send_notification_with_priority(error_message, "❌ Script Error", "high")
        
        # Reset driver on error
        print("Resetting driver due to error...")
        reset_driver()
    
    finally:
        # Don't close the driver - reuse it for next run
        # Just navigate away to clear state
        try:
            driver.get("about:blank")
        except:
            pass
        print("Check completed, driver ready for next run")

if __name__ == "__main__":
    main()
