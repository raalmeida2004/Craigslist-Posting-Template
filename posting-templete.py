from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Framingham, MA is served by Boston's Craigslist region.
item_data = {
    "city_url": "https://boston.craigslist.org/",
    "sub_area": "metro west",  # matches "choose the location that fits best" options
    "category": "general for sale",  # matches an "option-label" on the category picker
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


def click_when_ready(driver, locator, timeout=15, retries=3):
    """Wait for an element to be clickable and click it, re-locating on
    StaleElementReferenceException (Craigslist's pages re-render their DOM
    right after load, which can invalidate the element between find and click)."""
    for attempt in range(retries):
        try:
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            ).click()
            return
        except StaleElementReferenceException:
            if attempt == retries - 1:
                raise


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
        click_when_ready(
            driver,
            (By.CSS_SELECTOR, "a[href*='/post/'], a[href*='post.craigslist.org']"),
        )

        # Craigslist embeds the whole posting flow in an iframe on the /post
        # landing page; switch into it before looking for any form elements.
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe.cl-framed-application-iframe")
            )
        )

        # Some metro areas (like Boston) ask you to narrow down to a
        # sub-region before showing the category picker.
        if data.get("sub_area"):
            try:
                click_when_ready(
                    driver,
                    (By.XPATH, f"//label[contains(., '{data['sub_area']}')]"),
                    timeout=10,
                )
                click_when_ready(
                    driver,
                    (By.XPATH, "//button[contains(., 'continue')] | //input[@value='continue']"),
                )
            except TimeoutException:
                pass  # this metro area didn't ask for a sub-region

        # Select "for sale by owner" (typically the 3rd radio option, varies by region)
        # Note: You may need to adjust these selectors based on your specific location's workflow
        click_when_ready(driver, (By.XPATH, "//input[@value='fso']"))

        # Select the category. Craigslist's category ids are numeric and vary
        # by region, so match on the visible option-label text instead.
        click_when_ready(
            driver,
            (
                By.XPATH,
                f"//label[contains(@class, 'radio-option')]"
                f"[.//span[normalize-space(text())='{data['category']}']]",
            ),
        )
        click_when_ready(driver, (By.NAME, "go"))

        print("Filling out form data...")
        # Fill out Title
        driver.find_element(By.ID, "PostingTitle").send_keys(data["title"])

        # Fill out Price
        driver.find_element(By.NAME, "price").send_keys(data["price"])

        # Fill out Postal Code
        driver.find_element(By.ID, "postal_code").send_keys(data["postal_code"])

        # Fill out Description
        driver.find_element(By.ID, "PostingBody").send_keys(data["description"])

        # Fill out Contact Info (Craigslist dropped the "confirm email" field;
        # the phone input is disabled until "publish phone number" is checked)
        driver.find_element(By.NAME, "FromEMail").send_keys(data["email"])
        if data.get("phone"):
            click_when_ready(driver, (By.NAME, "show_phone_ok"))
            driver.find_element(By.NAME, "contact_phone").send_keys(data["phone"])

        # Click Continue to go to the map/image upload step
        print("Form filled. Moving to next step...")
        click_when_ready(driver, (By.NAME, "go"))

        # Hold the browser open until you're done adding photos and publishing,
        # instead of a fixed sleep that can close it out from under you mid-action.
        print("Template complete. Add photos and finish publishing in the browser window.")
        input("Press Enter here once you're done (this keeps the browser open until then)...")

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
