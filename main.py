# requirements: selenium
import sys
import logging
import csv

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ROOT_URL = "https://congbobanan.toaan.gov.vn/0tat1cvn/ban-an-quyet-dinh/"
COURT = "TAND tỉnh An Giang"

# KEYWORD1 = "trọng tài"
# KEYWORD2 = "PQTT"
# KEYWORD3 = "nước ngoài"
KEYWORDS = ["trọng tài", "PQTT", "nước ngoài"]

# LEVEL = "TW"
LEVEL = "CW"
# LEVEL = "T"

START_AT_PAGE = 1


def extract_info(element):
    title = element.text.split("\n")[0]
    link = element.find_element(By.CLASS_NAME, "echo_id_pub").get_attribute("href")
    return title, link


def main(args):
    opts = FirefoxOptions()
    opts.add_argument("--headless")

    browser = Firefox(options=opts)
    browser.get(ROOT_URL)

    other_radio_button = browser.find_element(By.XPATH, "//*[@type='radio'][@value=13]")
    other_radio_button.click()

    confirm_button = browser.find_element(
        By.XPATH, "//*[@type='submit'][@value='Xác nhận']"
    )
    confirm_button.click()

    cap_toa_an_options = browser.find_element(
        By.ID, "ctl00_Content_home_Public_ctl00_Drop_Levels_top"
    )
    cap_toa_an_options.click()
    cap_toa_an_dropdown = Select(cap_toa_an_options)
    cap_toa_an_dropdown.select_by_value(LEVEL)

    # banan_quyetdinh_options = browser.find_element(
    #     By.ID, "ctl00_Content_home_Public_ctl00_Drop_STATUS_JUDGMENT_SEARCH_top"
    # )
    # banan_quyetdinh_options.click()
    # banan_quyetdinh_dropdown = Select(banan_quyetdinh_options)
    # banan_quyetdinh_dropdown.select_by_value("0")  # Ban an
    # banan_quyetdinh_dropdown.select_by_value("1")  # Quyet dinh

    """
    toaan_options = browser.find_element(
        By.ID, "ctl00_Content_home_Public_ctl00_Ra_Drop_Courts_top_chosen"
    )
    toaan_options.click()

    toaan_input = browser.find_element(
        By.XPATH,
        "//*[@class='chosen-search-input'][@type='text'][@autocomplete='off']",
    )

    toaan_input.send_keys(COURT)
    toaan_input.send_keys(Keys.ENTER)
    """

    search_button = browser.find_element(
        By.ID, "ctl00_Content_home_Public_ctl00_cmd_search_banner"
    )
    search_button.click()

    pagenum_button = browser.find_element(
        By.ID, "ctl00_Content_home_Public_ctl00_DropPages"
    )
    # pagenum_button.click()
    pagenum_dropdown = Select(pagenum_button)
    num_pages = len(pagenum_dropdown.options)
    logging.info(f"Num pages: {num_pages}")

    pagenum_dropdown.select_by_value(str(START_AT_PAGE))

    logging.info(f"Start at page {START_AT_PAGE}")
    for i in range(START_AT_PAGE, num_pages + 2):
        current_page = str(i)
        logging.info(f"Page: {current_page}")
        result_list = browser.find_element(By.ID, "List_group_pub")
        results = result_list.find_elements(By.CLASS_NAME, "list-group-item")

        found = []
        for res in results:
            # extract info here
            try:
                if not any(kw in res.text for kw in KEYWORDS):
                    continue

                matches = ",".join(kw for kw in KEYWORDS if kw in res.text)
                title, link = extract_info(res)
                print(",".join([matches, title, link]))
                found.append([matches, title, link])

            except StaleElementReferenceException:
                logging.debug("stale!!!")

        with open(f"{LEVEL}.csv", "a") as f:
            writer = csv.writer(f)
            for row in found:
                writer.writerow(row)

        try:
            wait = WebDriverWait(browser, 5)
            _ = wait.until(
                EC.text_to_be_present_in_element_value(
                    (By.ID, "ctl00_Content_home_Public_ctl00_DropPages"),
                    current_page,
                )
            )
        except TimeoutException:
            pass

        wait2 = WebDriverWait(browser, 5)
        for _ in range(3):
            done = wait2.until(
                EC.element_to_be_clickable(
                    (By.ID, "ctl00_Content_home_Public_ctl00_cmdnext")
                )
            )
            if done:
                break

        nextpage_button = browser.find_element(
            By.ID, "ctl00_Content_home_Public_ctl00_cmdnext"
        )
        nextpage_button.click()
        browser.implicitly_wait(5)

    browser.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv)
