import sys
import os
import re
import time
from pathlib import Path

import PyPDF2
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException


DOWNLOAD_DIR = Path.home() / "Downloads"


def download_article(url):
    """Download the article to user's download directory"""
    opts = FirefoxOptions()
    # opts.add_argument("--headless")
    with Firefox(options=opts) as browser:
        browser.get(url)
        pdf_url = browser.find_element(By.TAG_NAME, "iframe").get_attribute("src")
        browser.get(pdf_url)

        wait = WebDriverWait(browser, 10)
        download = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="download"]'))
        )
        download.click()

        # wait for download to complete
        while any(filename.endswith(".part") for filename in os.listdir(DOWNLOAD_DIR)):
            time.sleep(0.5)


def check_if_file_is_downloaded():
    """Check for an existing file `document.pdf` in Download directory"""
    file_ = DOWNLOAD_DIR / "document.pdf"
    return file_.is_file() and file_.exists()


def search_inside_judgement(url, search_terms):
    document_id = url.split("/")[3]
    NUM_TRY_DOWNLOAD = 5
    for _ in range(NUM_TRY_DOWNLOAD):
        download_article(url)
        if check_if_file_is_downloaded():
            break
    else:  # no break
        print(f"CANNOT DOWNLOAD FROM {url}")
        return

    downloaded_file = DOWNLOAD_DIR / "document.pdf"
    new_file = DOWNLOAD_DIR / "laws" / (document_id + ".pdf")
    downloaded_file.rename(new_file)

    assert new_file.is_file() and new_file.exists()
    reader = PyPDF2.PdfFileReader(new_file)
    num_pages = reader.getNumPages()
    for i in range(num_pages):
        page = reader.getPage(i)
        text = page.extractText()
        found = any(term in text for term in search_terms)
        if found:
            return True
    else:  # no break
        return False


def main():
    # search_term = "phúc thẩm"
    search_terms = ["phúc thẩm", "tòa"]
    url1 = "https://congbobanan.toaan.gov.vn/2ta984325t1cvn/chi-tiet-ban-an"
    url2 = "https://congbobanan.toaan.gov.vn/2ta984343t1cvn/chi-tiet-ban-an"
    url3 = "https://congbobanan.toaan.gov.vn/2ta800934t1cvn/chi-tiet-ban-an"

    URLs = [url1, url2, url3]

    for url in URLs:
        print(f"Start with: {url}")
        print(search_inside_judgement(url, search_terms))


if __name__ == "__main__":
    main()
