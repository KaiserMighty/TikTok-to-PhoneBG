from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import os
import time
import requests

def download_image(image_url, folder_name, image_name):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(os.path.join(folder_name, image_name), 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {image_name}")
    else:
        print(f"Failed to download {image_name}")

def download_slideshows(file_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    current_directory = os.path.dirname(os.path.realpath(__file__))
    chromedriver_path = os.path.join(current_directory, 'chromedriver.exe')
    service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        with open(file_path, 'r') as file:
            urls = file.readlines()

        for url in urls:
            url = url.strip()
            if not url:
                continue

            driver.get(url)
            time.sleep(5)

            try:
                image_elements = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "css-brxox6-ImgPhotoSlide.e10jea832"))
                )
            except Exception as e:
                print(f"Failed to find images for URL {url}: {e}")
                continue

            if not image_elements:
                print(f"No images found for URL: {url}")
                continue

            # Folder for each link
            folder_name = url.split('/')[-1]
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            # Save each image of the slideshow
            for idx, img_element in enumerate(image_elements):
                img_url = img_element.get_attribute('src')
                img_name = f"slide_{idx + 1}.jpg"
                download_image(img_url, folder_name, img_name)

    finally:
        driver.quit()

def populate_links(creator_url):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tiktok_scraper.py <TikTok page URL>")
        sys.exit(1)

    creator_url = sys.argv[1]
    populate_links(creator_url)
    download_slideshows("links.txt")