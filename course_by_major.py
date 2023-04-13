from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('UMICH_USERNAME')
password = os.getenv('UMICH_PASSWORD')
major_url = 'https://atlas.ai.umich.edu/major/Computer%20Science%20BS/'


def click_buttons(elements):
    for element in elements:
        element.click()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()

    # Login to Atlas
    page.goto(major_url)
    page.fill('input#login', username)
    page.fill('input#password', password)
    page.click('input#loginSubmit')

    # Load 'Browse Courses'
    page.goto(major_url, wait_until='networkidle')
    time.sleep(15)

    load_more_buttons = page.query_selector_all('.load-more-major-link')
    for button in load_more_buttons:
        button.click()
    
    time.sleep(5)

    course_links = []

    soup = BeautifulSoup(page.content(), 'html.parser')
    course_cards = soup.find_all('div', class_='course-card-bottom')

    for course_card in course_cards:
        link = course_card.find('a', href=True)
        href = urllib.parse.quote(link['href'])
        course_links.append(href)


    # Write each element in the list to a separate line in the file
    with open('course_urls.txt', 'w') as file:
        for link in course_links:
            file.write(link + '\n')

# https://www.youtube.com/watch?v=H2-5ecFwHHQ&ab_channel=JohnWatsonRooney
