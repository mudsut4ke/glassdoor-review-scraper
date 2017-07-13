import time
import json
import config as cfg

from review_model import Review
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

username = cfg.USERNAME
password = cfg.PASSWORD
companyURL = cfg.PAGE_URL
limit_page = cfg.LIMIT_PAGE
page_count = 1


def json_export(raw_data):
    json_file = open("data.json", "w")
    json_file.write(json.dumps(raw_data))
    json_file.close()


def init_driver():
    chrome_driver = webdriver.Chrome(executable_path="./chromedriver")
    chrome_driver.wait = WebDriverWait(chrome_driver, 5)
    return chrome_driver


def login(chrome_driver, user_username, user_password):
    chrome_driver.get("http://www.glassdoor.com/profile/login_input.htm")
    try:
        user_field = chrome_driver.wait.until(ec.presence_of_element_located(
            (By.NAME, "username")))
        pw_field = chrome_driver.find_element_by_class_name("signin-password")
        login_button = chrome_driver.find_element_by_id("signInBtn")
        user_field.send_keys(user_username)
        user_field.send_keys(Keys.TAB)
        time.sleep(1)
        pw_field.send_keys(user_password)
        time.sleep(1)
        login_button.click()
    except TimeoutException:
        print("TimeoutException!")


def parse_reviews_html(reviews, raw_data):
    for review in reviews:
        recommends = ""
        outlook = ""
        approves_of_ceo = ""

        date = review.find("time", {"class": "date"}).getText().strip()
        title = review.find("span", {"class": "summary"}).getText().strip()
        reviewer = review.find("span", {"class": "authorJobTitle"}).getText().strip()
        work_location = review.find("span", {"class": "authorLocation"}).getText().strip() if review.find("span", {
            "class": "authorLocation"}) else ""
        rec = review.find_all("div", {"class": "tightLt col span-1-3"})
        if len(rec) > 0:
            recommends = rec[0].find("span", {"class": "middle"}).getText().strip()
        if len(rec) > 1:
            outlook = rec[1].find("span", {"class": "middle"}).getText().strip()
        if len(rec) > 2:
            approves_of_ceo = rec[2].find("span", {"class": "middle"}).getText().strip()

        review_text = review.find("p", {"class": "tightBot"}).getText() if review.find("p", {
            "class": "tightBot"}) else ""
        pros = review.find("p", {"class": "pros"}).getText() if review.find("p", {
            "class": "pros"}) else ""
        con = review.find("p", {"class": "cons"}).getText() if review.find("p", {
            "class": "cons"}) else ""
        advice = review.find("p", {"class": "adviceMgmt"}).getText() if review.find("p", {
            "class": "adviceMgmt"}) else ""

        r = Review(date, title, reviewer, work_location, recommends, outlook, approves_of_ceo, review_text, pros,
                   con,
                   advice)
        raw_data.append(r.as_json())

    return raw_data


def get_data(chrome_driver, current_url, raw_data, refresh):
    global page_count
    if page_count > limit_page:
        return raw_data

    time.sleep(2)
    if refresh:
        chrome_driver.get(current_url)
        print ("Getting page:" + current_url)
    time.sleep(2)
    html_source = chrome_driver.page_source
    soup = BeautifulSoup(html_source, "html.parser")
    next_page_url = get_next_page(soup)

    if not next_page_url:
        return raw_data

    reviews = soup.find_all("li", {"class": ["empReview", "padVert"]})
    if reviews:
        raw_data = parse_reviews_html(reviews, raw_data)
        print ("Page " + str(page_count) + " scraped.")
        page_count += 1
        get_data(chrome_driver, next_page_url, raw_data, True)
    else:
        print("Retry....")
        time.sleep(3)
        get_data(chrome_driver, next_page_url, raw_data, False)
    return raw_data


def get_next_page(soup):
    nextpage = soup.find('li', {'class': 'next'})
    if nextpage.find('a'):
        next_page_url = 'http://glassdoor.com' + nextpage.find('a').get('href')
        return next_page_url
    else:
        return None


if __name__ == "__main__":
    browser_driver = init_driver()
    time.sleep(5)
    print ("Logging into account ...")
    login(browser_driver, username, password)
    time.sleep(5)

    print ("Starting data scraping ...")
    data = get_data(browser_driver, companyURL, [], True)
    print ("Exporting data to data.json")

    json_export(data)
    browser_driver.quit()
    print ("Done scraped " + str(len(data)) + " review from " + str(page_count-1) + " page")
