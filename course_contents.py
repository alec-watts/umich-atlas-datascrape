from playwright.async_api import async_playwright
import asyncio
from asyncio import as_completed
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv
from tqdm.auto import tqdm

load_dotenv()

username = os.getenv('UMICH_USERNAME')
password = os.getenv('UMICH_PASSWORD')

base_url = 'https://atlas.ai.umich.edu'
atlas_url = 'https://atlas.ai.umich.edu/courses/?subject=EECS&page=1'

course_urls = []
course_content = []

# Read course urls from course_urls.txt
with open('course_urls.txt', 'r') as file:
    course_urls = file.readlines()


async def fetch_course_content(url, context, semaphore):
    async with semaphore:
        page = await context.new_page()
        await page.goto(url, wait_until='networkidle')
        soup = BeautifulSoup(await page.content(), 'html.parser')
        content = soup.find('div', {'class': 'wrapper container app'})

        page_content = ''
        if content is not None:
            page_content = content.text

        page_object = {
            'page_content': page_content,
            'metadata': {'source': url}
        }
        await page.close()
        return page_object


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        # browser = await p.chromium.launch()
        context = await browser.new_context()

        page = await context.new_page()
        await page.goto(atlas_url, wait_until='networkidle')
        await page.fill('input#login', username)
        await page.fill('input#password', password)
        await page.click('input#loginSubmit')
        await asyncio.sleep(15)

        # Set a limit on the number of concurrent tasks.
        concurrent_limit = 4
        semaphore = asyncio.Semaphore(concurrent_limit)

        tasks = []
        for url in course_urls:
            course_url = base_url + url.strip()
            task = asyncio.create_task(
                fetch_course_content(course_url, context, semaphore))
            tasks.append(task)

        # course_content.extend(await asyncio.gather(*tasks))
        with tqdm(total=len(tasks), desc='Fetching course content') as pbar:
            for task in asyncio.as_completed(tasks):
                content = await task
                course_content.append(content)
                pbar.update(1)

        await browser.close()

asyncio.run(main())

with open('course_contents.json', 'w') as file:
    file.write(json.dumps(course_content, indent=4))
