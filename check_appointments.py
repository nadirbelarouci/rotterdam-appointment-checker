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


# Set up Chrome options for headless mode (required for GitHub Actions)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Required for running in containers
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--window-size=1920,1080")  # Set window size

# Initialize WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

# Open the URL
driver.get("https://concern.ir.rotterdam.nl/afspraak/maken/product/indienen-naturalisatieverzoek") 

try:
    # Get the current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Script started at: {current_time}")

    time.sleep(3)  # Reduced from 5 to 3 seconds
    
    # Wait for the dropdown to be present and select "2" (value="1" means 2 people)
    print("Waiting for dropdown to be present...")
    dropdown = WebDriverWait(driver, 8).until(  # Reduced from 10 to 8
        EC.presence_of_element_located((By.ID, "id3"))
    )
    
    # Select the option for 2 people (value="1")
    select = Select(dropdown)
    select.select_by_value("1")  # This selects "2" from the dropdown
    print("Selected 2 people from dropdown")
    
    time.sleep(1)  # Reduced from 2 to 1 second
    
    # Wait for the "Verder" button to be clickable and click it
    print("Waiting for 'Verder' button...")
    verder_button = WebDriverWait(driver, 8).until(  # Reduced from 10 to 8
        EC.element_to_be_clickable((By.ID, "id5"))
    )
    verder_button.click()
    print("Clicked 'Verder' button")

    # Wait for the page to load and the dates to appear
    time.sleep(3)  # Reduced from 5 to 3 seconds

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
        
        # Send a simple status notification
        message = f"📋 Status Check\n\nNo appointment slots available (only waiting list).\n\nChecked at: {current_time}"
        send_notification_with_priority(message, "📋 Rotterdam Check", "default")

except Exception as e:
    error_message = f"❌ ERROR: Script failed with exception: {str(e)}\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(error_message)
    send_notification_with_priority(error_message, "❌ Script Error", "high")

finally:
    # Close the WebDriver
    driver.quit()
    print("WebDriver closed")
