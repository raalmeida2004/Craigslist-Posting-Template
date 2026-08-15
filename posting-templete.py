import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. Define your marketplace item data structure
item_data = {
    "city_url": "https://craigslist.org", # Use your local Craigslist URL
    "title": "Minimalist Wooden Coffee Table",
    "price": "120",
    "postal_code": "01701",
    "description": "Excellent condition solid wood coffee table. Moving sale.\n\nPick up only.",
    "email": "your_email@example.com",
    "phone": "555-123-4567"
}

def start_craigslist_post(data):
    # Initialize the Chrome browser automatically
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Uncomment to run in the background
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(10) # Wait up to 10 seconds for elements to appear
    
    try:
        print("Opening Craigslist...")
        driver.get(data["city_url"])
        
        # Click "create a posting"
        print("Starting new post...")
        driver.find_element(By.ID, "post").click()
        
        # Select "for sale by owner" (typically the 3rd radio option, varies by region)
        # Note: You may need to adjust these selectors based on your specific location's workflow
        driver.find_element(By.XPATH, "//input[@value='fso']").click() 
        
        # Select category: "furniture - by owner" as an example
        driver.find_element(By.XPATH, "//input[@value='fsa']").click()
        
        print("Filling out form data...")
        # Fill out Title
        driver.find_element(By.ID, "PostingTitle").send_keys(data["title"])
        
        # Fill out Price
        driver.find_element(By.NAME, "price").send_keys(data["price"])
        
        # Fill out Postal Code
        driver.find_element(By.ID, "postal_code").send_keys(data["postal_code"])
        
        # Fill out Description
        driver.find_element(By.ID, "PostingBody").send_keys(data["description"])
        
        # Fill out Contact Info
        driver.find_element(By.NAME, "FromEMail").send_keys(data["email"])
        driver.find_element(By.NAME, "ConfirmEMail").send_keys(data["email"])
        driver.find_element(By.NAME, "contact_phone").send_keys(data["phone"])
        
        # Click Continue to go to the map/image upload step
        print("Form filled. Moving to next step...")
        driver.find_element(By.NAME, "go").click()
        
        # Pause to let you review or manually complete images/publishing
        print("Template complete. Script holding open for 60 seconds for manual review.")
        time.sleep(60)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    start_craigslist_post(item_data)
