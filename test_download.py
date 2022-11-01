from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By

URL = "https://congbobanan.toaan.gov.vn/2ta1066628t1cvn/chi-tiet-ban-an"
opts = FirefoxOptions()
# opts.add_argument("--headless")
with Firefox(options=opts) as browser:
    browser.get(URL)
    pdf_url = browser.find_element(By.TAG_NAME, "iframe").get_attribute("src")
    print(pdf_url)
    browser.get(pdf_url)
    download = browser.find_element(By.XPATH, '//*[@id="download"]')
    download.click()
    print("after download click")
    input("Pause:")
