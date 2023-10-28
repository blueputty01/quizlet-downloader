import csv
import os
import time
from io import StringIO

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


FOLDER_LOCATION = os.getenv("FOLDER_LOCATION")

def get():
    options = webdriver.ChromeOptions()
    # bot block workaround
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    # driver.install_addon('uBlock0@raymondhill.net.xpi', temporary=True)
    # bot block workaround
    driver.maximize_window()
    # https://stackoverflow.com/questions/51770608/selenium-does-not-work-with-a-chromedriver-modified-to-avoid-detection/75776883#75776883
    driver.execute_cdp_cmd("Page.removeScriptToEvaluateOnNewDocument", {"identifier":"1"})

    delay = 20

    # must first navigate to homepage to allow for user to login 
    # as quizlet only allows full views for authenticated users
    driver.get("https://www.quizlet.com/")
    WebDriverWait(driver, 200).until(ec.presence_of_element_located((By.CLASS_NAME, "AssemblyAvatar")))

    driver.get(FOLDER_LOCATION)

    titles = WebDriverWait(driver, delay).until(
        ec.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "UIBaseCardHeader-title")]')))

    links = [title.find_element(By.TAG_NAME, 'a').get_attribute('href') for title in titles]

    data = []

    # for set in folder
    for link in links:
        driver.get(link)
        title = driver.find_element(By.CLASS_NAME, 'SetPage-breadcrumbTitleWrapper').text

        # ensure entire page is scrolled to view
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # get all terms
        terms = WebDriverWait(driver, delay).until(
            ec.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "TermText")]')))

        term_iterator = iter(terms)

        for span in term_iterator:
            
            data.append([span.text, next(term_iterator).text, title])


    data.append(['front', 'back', 'tag'])
    with open('output.csv', 'w', encoding="utf-8") as csv_output:
        writer = csv.writer(csv_output, lineterminator="\n")
        writer.writerows(data)

    driver.quit()


if __name__ == '__main__':
    get()
