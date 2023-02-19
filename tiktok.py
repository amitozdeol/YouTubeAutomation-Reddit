from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Create a class that will use selenium to login to tiktok using google account
class TikTok:
    def __init__(self):
        self.driver = None
        self.login()

    def login(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.tiktok.com/login")
        time.sleep(1)
        #find element by text and click
        self.driver.find_element(By.XPATH, "//p[contains(text(),'Continue with Google')]").click()
        # wait until number of windows is 2
        while len(self.driver.window_handles) != 2:
            time.sleep(1)
        # switch to the new window
        self.driver.switch_to.window(self.driver.window_handles[1])
        
        email_field = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Email or phone']")
        #add email to the email field
        email_field.send_keys("thisistiktok00@gmail.com")
        time.sleep(100)
        self.driver.find_element(By.XPATH, "//span[contains(text(),'Next')]").click()
        

        # self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Email or phone']").click()
        # self.driver.find_element_by_id("identifierId").send_keys("your_email")
        # self.driver.find_element_by_id("identifierNext").click()
        # time.sleep(5)
        # self.driver.find_element_by_name("password").send_keys("your_password")
        # self.driver.find_element_by_id("passwordNext").click()
        # time.sleep(5)

    def get_trending_videos(self):
        self.driver.get("https://www.tiktok.com/trending")
        time.sleep(5)
        # get the trending videos
        trending_videos = self.driver.find_elements_by_class_name("jsx-4273615897")
        for video in trending_videos:
            print(video.get_attribute("href"))
        self.driver.close()