# Login to reddit 
# Get top comments
import praw
from praw.reddit import Reddit
from praw.models import MoreComments
from tinydb import Query

import time
import re
import sys
import config
import database
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from imgur_downloader import ImgurDownloader
import os

submission = Query()

#create a simple python class to login to reddit
class Reddit:
    reddit = None
    thread = None
    comments = None
    config = config.load_config()

    def __init__(self, oldThread):
        self.reddit = None
        self.login()
        self.get_thread(oldThread)
        self.get_comments()

    def login(self):
        try:
            self.reddit = praw.Reddit(client_id=self.config['RedditCredential']['client_id'],
                                 client_secret=self.config['RedditCredential']['client_secret'],
                                 user_agent=self.config['RedditCredential']['user_agent'])
            print(f"Logged in to Reddit successfully!")
        except Exception as e:
            return e

    def get_thread(self, oldThread=None):
        subreddit_ = self.reddit.subreddit("photoshopbattles")
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
        Path(f"./Assets/{self.thread.id}").mkdir(parents=True, exist_ok=True)

        self.download_image(self.thread.url, self.thread._url_parts(self.thread.url)[1])
        db.close()

    # get top n comments
    def get_comments(self):
        topn = self.config['Reddit']['topn_comments']
        comments = []
        for c in self.thread.comments:
            print("===================================")
            if len(comments) == topn:
                break
            if isinstance(c, MoreComments) or c.author=="AutoModerator":
                continue
            isSure = input(f'{c.body} (y/n): ').lower().strip() == 'y'
            if isSure:
                #visit a url in the comment
                soup = BeautifulSoup(c.body_html)
                i=0
                for a in soup.find_all('a', href=True):
                    if a['href'].endswith(('jpg', 'jpeg', 'png')):
                        url = a['href']
                        self.download_image(url, self.thread._url_parts(self.thread.url)[1])
                        #download the image from the url and save it to the temp folder
                        os.system(f"wget -O ./Assets/{self.thread.id}/{c.id}{i}.jpg {url}")
                        comments.append(url)
                        print("Found the URL:", url)
                        i+=1

        self.comments = comments
        if len(self.comments) == 0:
            print("No comments found!")
            sys.exit(0)

        print(f"{len(self.comments)} comments are chosen")

    # Function to download image from url
    def download_image(self, url, filename):
        os.system(f"wget -O ./Assets/{self.thread.id}/{filename} {url}")

    def get_screenshots_of_reddit_posts(self, reddit_thread, reddit_comments):
        options = Options()
        options.add_argument('--headless')
