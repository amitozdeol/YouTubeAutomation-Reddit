# Login to reddit 
# Get top comments
import praw
from praw.reddit import Reddit
from praw.models import MoreComments
from tinydb import Query

import time
import re
import config
import database
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import sys

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
        self.get_screenshots()

    # Login to reddit 
    def login(self):
        try:
            self.reddit = praw.Reddit(client_id=self.config['RedditCredential']['client_id'],
                                 client_secret=self.config['RedditCredential']['client_secret'],
                                 user_agent=self.config['RedditCredential']['user_agent'])
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
            if isinstance(top_level_comment, MoreComments) or top_level_comment.author=="AutoModerator" or c_lower in "[deleted]" or c_lower in "[removed]" or c_lower in "edit:" or len(c_lower) > 800 or c_lower in "askreddit" or c_lower in "http": 
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
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=options)
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
            button = driver.find_element(By.XPATH,'//button[text()="I\'m over 18"]')
            time.sleep(5)
            if button.is_displayed():
                button.click()
                print("Button clicked. I\'m over 18")
        except NoSuchElementException:
            print("No NSFW content found")
        
        driver.find_element(By.CSS_SELECTOR, '[data-test-id="post-content"]').screenshot(filename=postcontentpath)
        print("Finding title...")

        for idx, comment in enumerate(self.comments):
            driver.get(f'https://reddit.com{comment.permalink}')
            print(f"Screenshotting comment {idx+1}...")

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
