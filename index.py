import json
import os
from pathlib import Path

import csv

from io import StringIO

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


def get():
    browser_options = Options()

    # browser_options.add_argument("--headless")
    # browser_options.add_argument("--disable-gpu")
    # browser_options.add_argument("--window-size=1920x1080")
    # browser_options.add_argument('--start-maximized')
    # browser_options.add_argument("--width=1920")
    # browser_options.add_argument("--height=1080")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=browser_options)
    driver.install_addon('uBlock0@raymondhill.net.xpi', temporary=True)
    driver.maximize_window()

    delay = 20  # seconds

    url = "https://quizlet.com"
    driver.get(url)

    WebDriverWait(driver, 200).until(ec.presence_of_element_located((By.CLASS_NAME, "AssemblyAvatar")))

    url = 'https://quizlet.com/BFW_Publishers/folders/starnes-the-practice-of-statistics-6e/sets'
    driver.get(url)

    titles = WebDriverWait(driver, delay).until(
        ec.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "UIBaseCardHeader-title")]')))

    links = [title.find_element(By.TAG_NAME, 'a').get_attribute('href') for title in titles]

    data = []

    for link in links:
        driver.get(link)
        title = driver.find_element(By.CLASS_NAME, 'SetPage-titleWrapper').text

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        more = WebDriverWait(driver, delay).until(
            ec.presence_of_element_located((By.XPATH, '//button[contains(@aria-label, "more menu - horizontal")]')))
        more.click()
        export = WebDriverWait(driver, delay).until(
            ec.presence_of_element_located((By.XPATH, '//button[contains(@data-key, "Exportar")]')))
        export.click()
        export_box = WebDriverWait(driver, delay).until(
            ec.presence_of_element_located((By.ID, 'SetPageExportModal-textarea')))
        text = export_box.get_attribute('innerHTML')

        reader = csv.reader(StringIO(text), delimiter="\t")

        for row in reader:
            row.append(title)
            data.append(row)

    data.append(['front', 'back', 'tag'])
    with open('output.csv', 'w', encoding="utf-8") as csv_output:
        writer = csv.writer(csv_output, lineterminator="\n")
        writer.writerows(data)

    driver.quit()


if __name__ == '__main__':
    get()
