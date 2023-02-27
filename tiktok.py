from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Create a class that will use selenium to login to tiktok using google account
class TikTok:
    def __init__(self):
        self.driver = None
        self.login()

    def login(self):
        profile= webdriver.FirefoxProfile(
    '/Users/amitozdeol/Library/Application Support/Firefox/Profiles/c3939ccq.default-release')
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.update_preferences()
        desired = DesiredCapabilities.FIREFOX

        self.driver = webdriver.Firefox(firefox_profile=profile,
                                desired_capabilities=desired)

        #self.driver = driver = uc.Chrome(use_subprocess=True)
        self.driver.get("https://www.tiktok.com")
        time.sleep(10)
        # search for anchor tag that contains href attribute with value /upload?lang=en
        self.driver.find_element(By.XPATH, "//a[contains(@href,'/upload?lang=en')]").click()
        
        time.sleep(20)
        #find element by text and click
        # self.driver.find_element(By.XPATH, "//button[contains(text(),'Select file')]").click()
        #upload a file to the file upload dialog
        #find a button that contains text "Select file" and click it
        self.driver.find_element(By.XPATH, "//div[contains(text(),'Select file')]").click()
        self.driver.find_element(By.XPATH, "//div[contains(text(),'Select file')]").send_keys("/Results/10hpeci.mp4")
        time.sleep(15)
        # # wait until number of windows is 2
        # while len(self.driver.window_handles) != 2:
        #     time.sleep(3)
        # # switch to the new window
        # self.driver.switch_to.window(self.driver.window_handles[1])
        
        # email_field = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Email or phone']")
        # #add email to the email field
        # email_field.send_keys("thisistiktok00@gmail.com")
        # time.sleep(5)
        # self.driver.find_element(By.XPATH, "//span[contains(text(),'Next')]").click()
        # time.sleep(100)

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