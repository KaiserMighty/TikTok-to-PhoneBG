from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

def populate_links(creator_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    current_directory = os.path.dirname(os.path.realpath(__file__))
    chromedriver_path = os.path.join(current_directory, 'chromedriver.exe')
    service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(creator_url)
        time.sleep(2)

        # Hit "Something Went Wrong" button if it exists
        while True:
            try:
                button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "emuynwa3.css-tlik2g-Button-StyledButton.ehk74z00"))
                )
                button.click()
                print("Refresh")
            except Exception as e:
                break

        # Scroll down to load all content
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Find and Save links
        wait = WebDriverWait(driver, 10)
        div_elements = wait.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "css-at0k0c-DivWrapper.e1cg0wnj1")))

        content_links = []
        for div in div_elements:
            try:
                a_tag = div.find_element(By.TAG_NAME, 'a')
                href = a_tag.get_attribute('href')
                if href:
                    content_links.append(href)
            except Exception as e:
                print(f"Error extracting link")

        with open("links.txt", "w") as file:
            for link in content_links:
                file.write(link + "\n")

        print(f"Found and saved {len(content_links)} URLs to links.txt")

    finally:
        driver.quit()

creator_url = 'https://www.tiktok.com/@incme4life'
populate_links(creator_url)
