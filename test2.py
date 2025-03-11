from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# Configure Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-popup-blocking")
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)

# Create DataFrame to store scraped data
dff = pd.DataFrame(columns=['Job Title', 'Description', 'Location', 'Company'])

# Loop through pages 0 to 200
for page in range(0, 200):
    url = f"https://www.remotejobs.io/search?searchkeyword=ai&page={page}"
    driver.get(url)

   
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'job-card-wrapper-1')))
    except:
        print(f"Skipping page {page} (No job listings found).")
        continue

    soup = BeautifulSoup(driver.page_source, 'html5lib')
    
    for i in range(1, 51):  
        job_card = soup.find('div', id=f'job-card-wrapper-{i}')
        if not job_card:
            continue

        Title = job_card.find('h3', class_='sc-jv5lm6-11 cUEXgX')
        Title = Title.text.strip() if Title else "Not Available"

        Description = job_card.find('p')
        Description = Description.text.strip() if Description else "Not Available"

        Location = job_card.find('span', class_='sc-jv5lm6-8 fxYdFy')
        Location = Location.text.strip() if Location else "Not Available"

        Company = "RemoteJobs.io"  

        dff = pd.concat([dff, pd.DataFrame([[Title, Description, Location, Company]],
                                           columns=['Job Title', 'Description', 'Location', 'Company'])],
                        ignore_index=True)

    print(f"Scraped Page {page}")

# Save scraped data to Excel
os.makedirs("data", exist_ok=True)
file_name = f"data/RemoteJobs_{datetime.today().date()}.xlsx"
dff.to_excel(file_name, index=False)

print(f"Scraping completed. Data saved to {file_name}")

# Close the browser
driver.quit()
