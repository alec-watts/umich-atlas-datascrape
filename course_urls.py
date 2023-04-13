from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('UMICH_USERNAME')
password = os.getenv('UMICH_PASSWORD')
atlas_url = 'https://atlas.ai.umich.edu/courses/?subject=EECS&page=1'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()

    # Login to Atlas
    page.goto(atlas_url)
    page.fill('input#login', username)
    page.fill('input#password', password)
    page.click('input#loginSubmit')

    # Load 'Browse Courses'
    page.goto(atlas_url, wait_until='networkidle')

    # Change page size to 64 courses
    page.select_option('select#page-size-selector', '32')
    time.sleep(5)

    # Extract the href attributes from the anchor elements
    page_links = ['?subject=EECS&page=1',
                  '?subject=EECS&page=2', 
                  '?subject=EECS&page=3',
                  '?subject=EECS&page=4',
                  '?subject=EECS&page=5',
                  '?subject=EECS&page=6',
                  '?subject=EECS&page=7']
    # anchor_elements = page.query_selector_all('div.pagination > span > a')
    # for anchor in anchor_elements:
    #     href = anchor.get_attribute('href')
    #     page_links.append(href)
    course_links = []

    base_link = 'https://atlas.ai.umich.edu/courses/'
    # Loop through each page and extract the course links
    for page_link in page_links:
        link = base_link + page_link
        page.goto(link, wait_until='networkidle')
        # time.sleep(5)
            
        # Extract the course links
        soup = BeautifulSoup(page.content(), 'html.parser')
        course_cards = soup.find_all('div', class_='course-card')

        for course_card in course_cards:
            link = course_card.find('a', class_='text-small')
            if link:
                href = link.get('href')
                href = urllib.parse.quote(href)
                course_links.append(href)

    # Write each element in the list to a separate line in the file
    with open('course_urls.txt', 'w') as file:
        for link in course_links:
            file.write(link + '\n')

# https://www.youtube.com/watch?v=H2-5ecFwHHQ&ab_channel=JohnWatsonRooney
