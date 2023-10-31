# Login to reddit 
# Get top comments
from pathlib import Path
from praw.models import MoreComments
from praw.reddit import Reddit
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from tinydb import Query
import config
import database
import praw
import re
import sys
import time
from playwright.async_api import async_playwright  # pylint: disable=unused-import
from playwright.sync_api import ViewportSize, sync_playwright
import json

submission = Query()

class Reddit:
    reddit = None
    thread = None
    comments = None
    config = config.load_config()
    subreddit = config['Reddit']['subreddit']

    def __init__(self, oldThread):
        self.reddit = None
        self.login()
        self.get_thread(oldThread)
        self.get_comments()

    # Login to reddit 
    def login(self):
        try:
            self.reddit = praw.Reddit(client_id=self.config['RedditCredential']['client_id'],
                                 client_secret=self.config['RedditCredential']['client_secret'],
                                 user_agent=self.config['RedditCredential']['user_agent'])
            # from time import sleep
            # from selenium import webdriver
            # from selenium.webdriver.common.by import By
            # options = Options()
            # options.add_argument('--headless')
            # options.add_argument('--no-sandbox')
            # options.add_argument('--disable-dev-shm-usage')
            # options.add_argument('--force-dark-mode')
            # driver = webdriver.Chrome('chromedriver_mac64/chromedriver', options=options)
            # driver.get("https://www.reddit.com/login")
            # user = driver.find_element(By.ID, "loginUsername")
            # user.send_keys("allofthe_colors")
            # pwd = driver.find_element(By.ID, "loginPassword")
            # pwd.send_keys("yERtD7EG5#")
            # btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            # btn.click()
            # sleep(5)
            # cookie = driver.find_element(By.XPATH, '//button[text()="Accept all"]')
            # cookie.click()  # kill cookie agreement popup. Probably not needed now
            # sleep(5)

            print(f"Logged in to Reddit successfully!")
        except Exception as e:
            return e

    # ================ Get the top thread from the subreddit ================
    def get_thread(self, oldThread=None):
        subreddit_ = self.reddit.subreddit(self.subreddit)
        threads = subreddit_.top('week')
        # sort threads based on number of up-votes
        sorted_threads = sorted(threads, key=lambda x: int(x.score), reverse=True)

        # get the top most up-voted thread that is not in the database
        db = database.load_databse()
        for thread in sorted_threads:
            if oldThread and oldThread == str(thread.id):
                self.thread = thread
                print(f"Chosen thread: {thread.title} -- Score: {thread.score}")
                break
            elif not db.search(submission.id == str(thread.id)):
                db.insert({'id': thread.id, 'title': thread.title, 'time': time.time()})
                db.close()
                print(f"Chosen thread: {thread.title} -- Score: {thread.score}")
                self.thread = thread
                db.close()
                break

        if self.thread is None:
            print("No new thread found!")
            sys.exit(0)

        #create a new folder for the thread if it doesn't exist
        Path(f"./Assets/temp/{self.thread.id}").mkdir(parents=True, exist_ok=True)

    # ================ Get the top comments from the thread ================
    def get_comments(self):
        topn = self.config['Reddit']['topn_comments']
        comments = []
        for top_level_comment in self.thread.comments:
            print("===============COMMENT====================")
            c_lower = top_level_comment.body.lower()

            if len(comments) == topn:
                break
            if isinstance(top_level_comment, MoreComments) or top_level_comment.author=="AutoModerator" or c_lower in "[deleted]" or c_lower in "[removed]" or c_lower in "edit:" or len(c_lower) > 800 or c_lower in "askreddit" or c_lower in "thread" or c_lower in "http": 
                continue
            # isSure = input(f'{top_level_comment.body} (y/n): ').lower().strip() == 'y'
            # if isSure:
            #     comments.append(top_level_comment)

            comments.append(top_level_comment)
            time.sleep(0.1)
            print(top_level_comment.body)

        self.comments = comments
        if len(self.comments) == 0:
            print("No comments found!")
            sys.exit(0)

        print(f"{len(self.comments)} comments are chosen")

    # ================ Get the screenshots of the reddit posts ================
    def get_screenshots(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--force-dark-mode')

        # settings values
        W = 1080
        H = 1920

        reddit_id = re.sub(r"[^\w\s-]", "", self.thread.id)
        # ! Make sure the reddit screenshots folder exists
        Path(f"./Assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)

        print("Launching Headless Browser...")
        driver = webdriver.Chrome('chromedriver_mac64/chromedriver', options=options)
        driver.get("https://www.reddit.com" + self.thread.permalink) 
        print("Visiting Reddit...")
        driver.set_window_size(width=W, height=H)
        driver.add_cookie({"name": "USER","value": "eyJwcmVmcyI6eyJ0b3BDb250ZW50RGlzbWlzc2FsVGltZSI6MCwiZ2xvYmFsVGhlbWUiOiJSRURESVQiLCJuaWdodG1vZGUiOnRydWUsImNvbGxhcHNlZFRyYXlTZWN0aW9ucyI6eyJmYXZvcml0ZXMiOmZhbHNlLCJtdWx0aXMiOmZhbHNlLCJtb2RlcmF0aW5nIjpmYWxzZSwic3Vic2NyaXB0aW9ucyI6ZmFsc2UsInByb2ZpbGVzIjpmYWxzZX0sInRvcENvbnRlbnRUaW1lc0Rpc21pc3NlZCI6MH19","domain": ".reddit.com", "path": "/"})
        driver.add_cookie({"name": "eu_cookie", "value": "{%22opted%22:true%2C%22nonessential%22:false}", "domain": ".reddit.com","path": "/"})

        time.sleep(5)
        postcontentpath = f"./Assets/temp/{reddit_id}/png/title.png"
        try:
            # For NSFW content
            print("Checking for NSFW content...")
            button = driver.find_element(By.ID,'secondary-button')
            time.sleep(5)
            if button.is_displayed():
                button.click()
                print("Button clicked. I\'m over 18")
                time.sleep(5)
        except NoSuchElementException:
            print("No NSFW content found")
        driver.find_element(By.CSS_SELECTOR, 'shreddit-post').screenshot(filename=postcontentpath)
        print("Finding title...")

        for idx, comment in enumerate(self.comments):
            driver.get(f'https://reddit.com/comments/{self.thread.id}/comment/{comment.id}')
            print(f'https://reddit.com/comments/{self.thread.id}/comment/{comment.id}')
            print(f"Screenshotting comment {idx+1}...")
            time.sleep(5)
            try:
                driver.find_element(By.ID, f"t1_{comment.id}-comment-rtjson-content").screenshot(
                    filename=f"./Assets/temp/{reddit_id}/png/{idx}.png"
                )
            except TimeoutError:
                print("TimeoutError: Skipping screenshot...")
                continue

        # close browser instance when we are done using it
        driver.close()

        print("Screenshots downloaded Successfully.")


    def get_screenshots_using_playwright(self, theme="light"):
        # settings values
        W = 1080
        H = 1920

        reddit_id = re.sub(r"[^\w\s-]", "", self.thread.id)
        # ! Make sure the reddit screenshots folder exists
        Path(f"./Assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)

        screenshot_num: int
        with sync_playwright() as p:
            print("Launching Headless Browser...")

            browser = p.chromium.launch(headless=True)  # headless=False #to check for chrome view
            context = browser.new_context()
            my_config = config.load_config()
            # Device scale factor (or dsf for short) allows us to increase the resolution of the screenshots
            # When the dsf is 1, the width of the screenshot is 600 pixels
            # So we need a dsf such that the width of the screenshot is greater than the final resolution of the video
            dsf = (W // 600) + 1

            context = browser.new_context(
                locale="en-us",
                color_scheme="dark",
                viewport=ViewportSize(width=W, height=H),
                device_scale_factor=dsf,
            )
            # set the theme and disable non-essential cookies
            if theme == "dark":
                cookie_file = open(
                    "./Graphics/data/cookie-dark-mode.json", encoding="utf-8"
                )
                bgcolor = (33, 33, 36, 255)
                txtcolor = (240, 240, 240)
                cookies = json.load(cookie_file)
                cookie_file.close()
                context.add_cookies(cookies)  # load preference cookies

            # Get the thread screenshot
            page = context.new_page()
            # go to reddit's login page
            print("Visiting Reddit...")
            page.goto("https://www.reddit.com/login/?experiment_d2x_2020ify_buttons=enabled&use_accountmanager=true&experiment_d2x_google_sso_gis_parity=enabled&experiment_d2x_onboarding=enabled&experiment_d2x_am_modal_design_update=enabled", timeout=0)
            # fill user info
            print("Logging in...")
            page.locator("id=loginUsername").fill(self.config['RedditCredential']['client_id'])
            page.locator("id=loginPassword").fill(self.config['RedditCredential']['client_secret'])
            page.get_by_role("button", name="Log In").click()
            time.sleep(10)
            # go to the thread
            print("Visiting thread...")
            page.goto("https://www.reddit.com" + self.thread.permalink, timeout=0)
            time.sleep(10)
            page.keyboard.press("Escape")
            
            page.goto("https://www.reddit.com" + self.thread.permalink, timeout=0)
            page.set_viewport_size(ViewportSize(width=W, height=H))

            postcontentpath = f"./Assets/temp/{reddit_id}/png/title.png"
            page.locator('shreddit-post').screenshot(path=postcontentpath)
            print("Screenshot for OP completed")

            #zoom in on comments
            page.set_viewport_size(ViewportSize(width=500, height=H))
            for idx, comment in enumerate(self.comments):
                if page.locator('[data-testid="content-gate"]').is_visible():
                    print("Content gate found. Clicking...")
                    page.locator('[data-testid="content-gate"] button').click()
                print(f"Screenshotting comment {idx + 1}  {comment.permalink} ...")
                page.goto(f'https://reddit.com{comment.permalink}', timeout=0)
                try:
                    # page.locator("shreddit-comment").first.screenshot(
                    #     path=f"./Assets/temp/{reddit_id}/png/{idx}.png"
                    # )
                    page.locator(f"#t1_{comment.id}-comment-rtjson-content").screenshot(
                        path=f"./Assets/temp/{reddit_id}/png/{idx}.png"
                    )
                    print(f"Screenshot for {idx + 1} comment out of {len(self.comments)}")
                except TimeoutError:
                    print("TimeoutError: Skipping screenshot...")
                    continue

            # close browser instance when we are done using it
            browser.close()

        print("Screenshots downloaded Successfully.")