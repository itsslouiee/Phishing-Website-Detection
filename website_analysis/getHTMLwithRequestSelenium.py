import os
import requests
import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Dataset path
datasetpath = "DatasetCreator"  # needs to changed as per user's file locations

# Logging
logging.basicConfig(
    filename='HTML_script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/58.0.3029.110 Safari/537.3"
)

def is_url_accessible(url, timeout=10):
    try:
        resp = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT}
        )

        if resp.status_code < 400:
            return True

        resp = requests.get(
            url,
            timeout=timeout,
            stream=True,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT}
        )

        return resp.status_code < 400

    except Exception as e:
        logging.info(f"URL check failed for {url}: {e}")
        return False


def fetch_static_html(url, timeout=10):
    """
    Try to retrieve static HTML using Requests.
    Return HTML if meaningful content is found.
    Otherwise return None.
    """
    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT}
        )

        response.raise_for_status()

        html = response.text

        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        text_content = soup.get_text(strip=True)

        # Basic validation
        if (
            "<html" in html.lower()
            and len(html) > 500
            and len(text_content) > 100
        ):
            logging.info(f"Static HTML successfully retrieved for {url}")
            return html

        logging.info(f"Static HTML appears incomplete for {url}")
        return None

    except Exception as e:
        logging.info(f"Static HTML retrieval failed for {url}: {e}")
        return None


def save_html_to_file(filename, html_content):
    if html_content.strip():
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(html_content)

        logging.info(f"HTML saved to {filename}")
        print(f"HTML saved to {filename}")
    else:
        logging.info(f"Skipped saving {filename} (empty HTML)")


def parsingURL(url, key, temp):

    logging.info(f"Opening URL: {url}")

    if temp == 1:
        file_name = os.path.join("All_HTML", f"{key}.txt")

    # --------------------------------------------------
    # STEP 1 : Check accessibility
    # --------------------------------------------------
    if not is_url_accessible(url):
        logging.info(f"URL not accessible, skipping: {url}")
        return

    # --------------------------------------------------
    # STEP 2 : Try Requests first
    # --------------------------------------------------
    html_content = fetch_static_html(url)

    if html_content:
        logging.info(
            f"Static HTML used successfully for {url}"
        )
        save_html_to_file(file_name, html_content)
        return

    logging.info(
        f"Static HTML unavailable. Switching to Selenium for {url}"
    )

    # --------------------------------------------------
    # STEP 3 : Selenium fallback
    # --------------------------------------------------

    driver = None

    try:
        options = Options()

        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument('--start-maximized')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--use_subprocess')
        options.add_argument('--allow-insecure-localhost')

        options.add_argument(
            f'user-agent={USER_AGENT}'
        )

        driver = webdriver.Chrome(options=options)

        driver.set_page_load_timeout(15)

        driver.get(url)

        time.sleep(2)

        page_title = driver.title or ""

        if any(
            err in page_title.lower()
            for err in [
                "not found",
                "404",
                "error",
                "can't be reached",
                "temporarily down"
            ]
        ):
            logging.info(
                f"Page not accessible, skipping save: {page_title}"
            )
            return

        if "Suspected phishing site" in page_title:
            try:
                proceed_button = driver.find_element(
                    By.CLASS_NAME,
                    "cf-btn-danger"
                )
                proceed_button.click()
                time.sleep(3)

            except Exception as e:
                logging.error(
                    f"Failed to bypass phishing warning: {e}"
                )
                return

        html_content = driver.page_source

        save_html_to_file(file_name, html_content)

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        if driver:
            driver.quit()

        logging.info("Browser closed.")


def main(url, key):
    parsingURL(url, key, 1)