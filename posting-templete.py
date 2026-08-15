import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Framingham, MA is served by Boston's Craigslist region.
item_data = {
    "city_url": "https://boston.craigslist.org/",
    "title": "2026 Vtr tank pro *elite*",
    "price": "1850",
    "postal_code": "01702",
    "description": (
        "2026 keyless star, usb/12v port, 2 keys, Alarm, Bluetooth speaker, "
        "come check one out, Well assembled no bolts missing or scratched up. "
        "0 miles, clean title, Perfect for saving Money on gas"
    ),
    "email": "REPLACE_WITH_YOUR_EMAIL",
    "phone": "REPLACE_WITH_YOUR_PHONE",
}


def start_craigslist_post(data):
    # Initialize Chrome Options
    options = webdriver.ChromeOptions()

    # --- CRITICAL FIXES FOR HEADLESS / LINUX ENVIRONMENTS ---
    options.add_argument("--headless=new")       # Run without a GUI (mandatory for servers)
    options.add_argument("--no-sandbox")          # Bypass OS security model (fixes system bus errors)
    options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems in Docker/VPS
    options.add_argument("--disable-gpu")          # Disables hardware acceleration
    options.add_argument("--remote-debugging-port=9222") # Avoids port allocation crashes
    options.add_argument("--window-size=1920,1080") # Forces the desktop layout instead of Craigslist's mobile UI

    # Initialize the driver with the new options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(10) # Wait up to 10 seconds for elements to appear

    try:
        print("Opening Craigslist...")
        driver.get(data["city_url"])

        # Click "post to classifieds" (matched by the link's href pattern since
        # Craigslist's ids/visible text for this link vary by layout)
        print("Starting new post...")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[href*='/post/'], a[href*='post.craigslist.org']")
            )
        ).click()

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
        driver.save_screenshot("error_screenshot.png")
        with open("error_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved error_screenshot.png and error_page.html for debugging.")

    finally:
        driver.quit()


if __name__ == "__main__":
    start_craigslist_post(item_data)
