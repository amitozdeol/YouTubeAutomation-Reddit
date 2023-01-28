# import json
# import re
# from pathlib import Path
# from typing import Dict, Final

# from playwright.async_api import async_playwright  # pylint: disable=unused-import
# from playwright.sync_api import ViewportSize, sync_playwright


# #from utils.imagenarator import imagemaker


# def get_screenshots_of_reddit_posts(reddit_thread, reddit_comments, screenshot_num: int, theme="dark"):

#     # settings values
#     W = 1080
#     H = 1920
#     # W = 1200
#     # H = 2133

#     reddit_id = re.sub(r"[^\w\s-]", "", reddit_thread.id)
#     # ! Make sure the reddit screenshots folder exists
#     Path(f"./Assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)

#     screenshot_num: int
#     with sync_playwright() as p:
#         print("Launching Headless Browser...")

#         browser = p.chromium.launch(headless=True)  # headless=False #to check for chrome view
#         context = browser.new_context()
#         # Device scale factor (or dsf for short) allows us to increase the resolution of the screenshots
#         # When the dsf is 1, the width of the screenshot is 600 pixels
#         # So we need a dsf such that the width of the screenshot is greater than the final resolution of the video
#         dsf = (W // 600) + 1

#         context = browser.new_context(
#             locale="en-us",
#             color_scheme="dark",
#             viewport=ViewportSize(width=W, height=H),
#             device_scale_factor=dsf,
#         )
#         # set the theme and disable non-essential cookies
#         if theme == "dark":
#             cookie_file = open(
#                 "./Graphics/data/cookie-dark-mode.json", encoding="utf-8"
#             )
#             bgcolor = (33, 33, 36, 255)
#             txtcolor = (240, 240, 240)


#         cookies = json.load(cookie_file)
#         cookie_file.close()

#         context.add_cookies(cookies)  # load preference cookies

#         # Get the thread screenshot
#         page = context.new_page()
#         page.goto("https://www.reddit.com" + reddit_thread.permalink, timeout=0)
#         page.set_viewport_size(ViewportSize(width=W, height=H))

#         postcontentpath = f"./Assets/temp/{reddit_id}/png/title.png"
#         page.is_visible('[data-test-id="post-content"]')
#         page.locator('[data-test-id="post-content"]').screenshot(path=postcontentpath)



#         for idx, comment in enumerate(reddit_comments):


#             if page.locator('[data-testid="content-gate"]').is_visible():
#                 page.locator('[data-testid="content-gate"] button').click()

#             page.goto(f'https://reddit.com{comment.permalink}', timeout=0)

#             try:
#                 page.locator(f"#t1_{comment.id}").screenshot(
#                     path=f"./Assets/temp/{reddit_id}/png/{idx}.png"
#                 )
#             except TimeoutError:
#                 print("TimeoutError: Skipping screenshot...")
#                 continue

#         # close browser instance when we are done using it
#         browser.close()

#     print("Screenshots downloaded Successfully.")


import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

import json
import re
from pathlib import Path

def get_screenshots_of_reddit_posts(reddit_thread, reddit_comments, screenshot_num: int, theme="dark"):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--force-dark-mode')

    # settings values
    W = 1080
    H = 1920

    reddit_id = re.sub(r"[^\w\s-]", "", reddit_thread.id)
    # ! Make sure the reddit screenshots folder exists
    Path(f"./Assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)

    screenshot_num: int

    print("Launching Headless Browser...")
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=options)

    dsf = (W // 600) + 1

    # set the theme and disable non-essential cookies

    driver.get("https://www.reddit.com" + reddit_thread.permalink)
    driver.set_window_size(width=W, height=H)
    driver.add_cookie({"name": "USER",
                       "value": "eyJwcmVmcyI6eyJ0b3BDb250ZW50RGlzbWlzc2FsVGltZSI6MCwiZ2xvYmFsVGhlbWUiOiJSRURESVQiLCJuaWdodG1vZGUiOnRydWUsImNvbGxhcHNlZFRyYXlTZWN0aW9ucyI6eyJmYXZvcml0ZXMiOmZhbHNlLCJtdWx0aXMiOmZhbHNlLCJtb2RlcmF0aW5nIjpmYWxzZSwic3Vic2NyaXB0aW9ucyI6ZmFsc2UsInByb2ZpbGVzIjpmYWxzZX0sInRvcENvbnRlbnRUaW1lc0Rpc21pc3NlZCI6MH19",
                       "domain": ".reddit.com", "path": "/"})
    driver.add_cookie(
        {"name": "eu_cookie", "value": "{%22opted%22:true%2C%22nonessential%22:false}", "domain": ".reddit.com","path": "/"})

    time.sleep(5)
    postcontentpath = f"./Assets/temp/{reddit_id}/png/title.png"
    try:
        # For NSFW content
        button = driver.find_element(By.XPATH,'//button[text()="I\'m over 18"]')
        time.sleep(5)
        if button.is_displayed():
            button.click()
            print("Button clicked. I\'m over 18")
    except NoSuchElementException:
        print("...")
    
    driver.find_element(By.CSS_SELECTOR, '[data-test-id="post-content"]').screenshot(filename=postcontentpath)

    for idx, comment in enumerate(reddit_comments):

        # if driver.find_element(By.CSS_SELECTOR, '[data-testid="content-gate"]').is_displayed():
        #     driver.find_element(By.CSS_SELECTOR, '[data-testid="content-gate"] button').click()

        driver.get(f'https://reddit.com{comment.permalink}')

        try:
            driver.find_element(By.CSS_SELECTOR, f"#t1_{comment.id}").screenshot(
                filename=f"./Assets/temp/{reddit_id}/png/{idx}.png"
            )
        except TimeoutError:
            print("TimeoutError: Skipping screenshot...")
            continue

    # close browser instance when we are done using it
    driver.close()

    print("Screenshots downloaded Successfully.")
