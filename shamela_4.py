from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import google.generativeai as genai

# Configure the Gemini API
api_key = 'AIzaSyANaYZ8rmgmGJrTIQYUTECoVvQYXc0Gbyo'
genai.configure(api_key=api_key)

# Initialize the Gemini model
model_1 = genai.GenerativeModel(
    "gemini-1.5-flash", 
    system_instruction="Translate the English text into Arabic. Give output only the Arabic text"
)

# Function to set up the Selenium WebDriver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to perform the search and scrape the contents
def scrape_shamela(search_text):
    url = "https://shamela.ws/search"

    # Initialize the WebDriver
    driver = setup_driver()
    driver.get(url)

    try:
        # Wait for the search input box to appear
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='بحث في كل الكتب']"))
        )

        # Enter the search text
        search_box.send_keys(search_text)

        # Click the search button
        search_button = driver.find_element(By.XPATH, "//button[contains(text(), 'بحث')]")
        search_button.click()

        # Wait for search results to load
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[@class='card']")))

        # Get the first 5 search result links
        result_links = driver.find_elements(By.XPATH, "//a[@class='card']")[:5]
        contents = []

        for link in result_links:
            # Open the link in a new tab
            href = link.get_attribute("href")
            driver.execute_script(f"window.open('{href}', '_blank');")

        # Switch to each tab, extract contents, and close the tab
        for i in range(1, len(driver.window_handles)):
            driver.switch_to.window(driver.window_handles[i])
            time.sleep(2)  # Wait for page to load

            # Extract page content
            body_content = driver.find_element(By.TAG_NAME, "body").text
            contents.append(body_content)

            # Close the tab
            driver.close()

        # Switch back to the main tab
        driver.switch_to.window(driver.window_handles[0])

        return contents

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        driver.quit()

# Main function
if __name__ == "__main__":
    search_query = input("Enter the text to search: ")
    response_1 = model_1.generate_content(search_query)
    prompt_1 = response_1.text
    print(f"Translation: {prompt_1}")

    results = scrape_shamela(search_query)

    if results:
        print("\nExtracted Contents:")
        for idx, content in enumerate(results):
            print(f"\nResult {idx + 1}:")
            print(content)
    else:
        print("No results found or an error occurred.")
