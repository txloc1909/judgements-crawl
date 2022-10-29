import sys
import os
import logging
import csv
from argparse import ArgumentParser

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import ElementNotSelectableException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ROOT_URL = "https://congbobanan.toaan.gov.vn/0tat1cvn/ban-an-quyet-dinh/"


def load_keywords(keyword_file):
    with open(keyword_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        return [line.strip() for line in lines]


def load_court_name(court_file):
    with open(court_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) == 0:
            raise RuntimeError("No court name found")
        elif len(lines) > 1:
            raise RuntimeError("More than 1 court specified")

        return lines[0].strip()


def get_pass_survey(browser):
    other_radio_button = browser.find_element(By.XPATH, "//*[@type='radio'][@value=13]")
    other_radio_button.click()

    confirm_button = browser.find_element(
        By.XPATH, "//*[@type='submit'][@value='Xác nhận']"
    )
    confirm_button.click()


def choose_court_level(browser, level):
    cap_toa_an_options = browser.find_element(
        By.ID, "ctl00_Content_home_Public_ctl00_Drop_Levels_top"
    )
    cap_toa_an_options.click()
    cap_toa_an_dropdown = Select(cap_toa_an_options)
    cap_toa_an_dropdown.select_by_value(level)


def choose_judgement_type(browser, judgement):
    banan_quyetdinh_options = browser.find_element(
        By.ID,
        "ctl00_Content_home_Public_ctl00_Drop_STATUS_JUDGMENT_SEARCH_top",
    )
    banan_quyetdinh_options.click()
    banan_quyetdinh_dropdown = Select(banan_quyetdinh_options)
    banan_quyetdinh_dropdown.select_by_value(judgement)


def extract_info(element):
    title = element.text.split("\n")[0]
    link = element.find_element(By.CLASS_NAME, "echo_id_pub").get_attribute("href")
    return title, link


def main(args):
    if not args.level and args.court:
        raise Exception("Not specify court level but specify court name")

    if os.path.exists(args.keyword_file):
        keywords = load_keywords(args.keyword_file)
    else:
        raise Exception("Keyword file not found")

    if args.court:
        if os.path.exists(args.court):
            court_name = load_court_name(args.court)
        else:
            raise Exception("Court file not found")

    output_file = ""
    if args.level:
        output_file += args.level
    if args.judgement:
        output_file += args.judgement
    if args.court:
        output_file += args.court.split(".")[0]
    if args.type:
        output_file += str(args.type)

    output_file += args.keyword_file.split(".")[0]
    output_file += ".csv"

    opts = FirefoxOptions()
    opts.add_argument("--headless")

    with Firefox(options=opts) as browser:
        browser.get(ROOT_URL)

        get_pass_survey(browser)

        if args.level:
            choose_court_level(browser, args.level)

        if args.judgement:
            choose_judgement_type(browser, args.judgement)

        if args.court:
            toaan_options = browser.find_element(
                By.ID, "ctl00_Content_home_Public_ctl00_Ra_Drop_Courts_top_chosen"
            )
            toaan_options.click()
            toaan_input = browser.find_element(
                By.XPATH,
                "//*[@class='chosen-search-input'][@type='text'][@autocomplete='off']",
            )
            toaan_input.send_keys(court_name)
            toaan_input.send_keys(Keys.ENTER)

        if args.type:
            for attempt in range(3):
                try:
                    loaivuviec_options = browser.find_element(
                        By.ID,
                        "ctl00_Content_home_Public_ctl00_Drop_CASES_STYLES_SEARCH_top",
                    )
                    loaivuviec_options.click()
                    loaivuviec_dropdown = Select(loaivuviec_options)
                    loaivuviec_dropdown.select_by_value(str(args.type))
                except StaleElementReferenceException:
                    continue
                else:
                    break
            else:  # no break
                raise RuntimeError("Cannot select")

        search_button = browser.find_element(
            By.ID, "ctl00_Content_home_Public_ctl00_cmd_search_banner"
        )
        search_button.click()

        pagenum_button = browser.find_element(
            By.ID, "ctl00_Content_home_Public_ctl00_DropPages"
        )
        pagenum_dropdown = Select(pagenum_button)
        num_pages = len(pagenum_dropdown.options)
        logging.info(f"Num pages: {num_pages}")

        if args.start_from > num_pages:
            raise RuntimeError("Invalid start page")

        pagenum_dropdown.select_by_value(str(args.start_from))

        logging.info(f"Start at page {args.start_from}")
        try:
            for i in range(args.start_from, num_pages + 1):
                current_page = str(i)
                logging.info(f"Page: {current_page}")
                result_list = browser.find_element(By.ID, "List_group_pub")
                results = result_list.find_elements(By.CLASS_NAME, "list-group-item")

                found = []
                for res in results:
                    # extract info here
                    try:
                        if not any(kw in res.text for kw in keywords):
                            continue

                        matches = ",".join(kw for kw in keywords if kw in res.text)
                        title, link = extract_info(res)
                        print(",".join([matches, title, link]))
                        found.append([matches, title, link])

                    except StaleElementReferenceException:
                        logging.debug("stale!!!")

                with open(output_file, "a", encoding="utf-8") as f:
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
                try:
                    nextpage_button = wait2.until(
                        EC.element_to_be_clickable(
                            (By.ID, "ctl00_Content_home_Public_ctl00_cmdnext")
                        )
                    )
                except TimeoutException:
                    if num_pages > 1:
                        raise RuntimeError("Cannot press next page")
                    else:
                        nextpage_button = None

                # close an unexpected backdrop covering the entire page
                try:
                    close_backdrop_button = browser.find_element(
                        By.CLASS_NAME, "backdrop-close"
                    )
                    close_backdrop_button.click()
                    logging.info("Successfully close backdrop")
                except (
                    NoSuchElementException,
                    ElementNotVisibleException,
                    ElementNotSelectableException,
                    ElementNotInteractableException,
                ):
                    logging.info("No backdrop appeared")
                except Exception as e:
                    logging.info(f"Cannot close backdrop due to unknown exception: {e}")
                    print(type(e))

                if nextpage_button:
                    nextpage_button.click()

                browser.implicitly_wait(5)
        except KeyboardInterrupt:
            logging.info("Interrupted!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = ArgumentParser()
    parser.add_argument(
        "-l",
        "--level",
        type=str,
        default="",
        choices=["TW", "CW", "T", "H"],
        required=False,
        help="Court level",
    )
    parser.add_argument(
        "-j",
        "--judgement",
        type=str,
        default="",
        choices=["0", "1"],
        required=False,
        help="Judgement or Decision",
    )
    parser.add_argument(
        "-c",
        "--court",
        default=None,
        required=False,
        help="Path to file specify court name",
    )
    parser.add_argument(
        "-t",
        "--type",
        default=None,
        type=int,
        choices=[50, 0, 1, 2, 3, 4, 5, 11],
        required=False,
        help="Case type",
    )
    parser.add_argument(
        "--keyword_file",
        required=True,
    )
    parser.add_argument(
        "--start_from",
        default=1,
        type=int,
        required=False,
        help="Start from page",
    )
    args = parser.parse_args()
    main(args)
