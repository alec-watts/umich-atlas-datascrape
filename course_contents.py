from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv
load_dotenv()

username = os.getenv("UMICH_USERNAME")
password = os.getenv("UMICH_PASSWORD")

base_url = 'https://atlas.ai.umich.edu/'
atlas_url = "https://atlas.ai.umich.edu/courses/?subject=EECS&page=1"

course_urls = []
course_content = []

# Read course urls from course_urls.txt
with open("course_urls.txt", "r") as file:
    course_urls = file.readlines()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    page.goto(atlas_url, wait_until="networkidle")
    page.fill('input#login', username)
    page.fill('input#password', password)
    page.click('input#loginSubmit')
    time.sleep(5)


    for url in course_urls:
        course_url = base_url + url
        print(course_url)
        page.goto(course_url, wait_until="networkidle")
        soup = BeautifulSoup(page.content(), 'html.parser')
        content = soup.find("div", {"class": "wrapper container app"})

        page_object = {
                'page_content': content.text,
                'metadata': { 'source': course_url }
        }
        course_content.append(page_object)


with open("contents.json", "w") as file:
    file.write(json.dumps(course_content, indent=4))
    # CLEAN UP OUTPUT?
    # YES, whitespace is taking tokens. Is there any meaning to it?

