from selenium import webdriver
import undetected_chromedriver as uc
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
from time import sleep
import re
from termcolor import colored
from random import uniform

LOGIN_URL = 'https://m.facebook.com/login.php'

class FacebookGroupWatcher():
    def __init__(self, email, password, database, feed, browser='Chrome'):
        # set self feed and database
        self.feed = feed
        self.database = database

        # Get Entries from entries.txt
        self.getEntries()

        # Get settings from DB
        self.settings = database.settings

        # Store credentials for login
        self.email = email
        self.password = password
        if browser == 'Chrome':
            # Use chrome
            options = ChromeOptions()
            # Disable images and notifications popups
            prefs = {'profile.managed_default_content_settings.images':2, "profile.default_content_setting_values.notifications" : 2,}
            options.add_experimental_option("prefs", prefs)
            # Prevent detection (hopefully ?)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_argument('--disable-blink-features=AutomationControlled')
            # Maximize
            options.add_argument("--start-maximized")
            # Headless
            #options.set_headless(True)
            # Disable GPU
            options.add_argument("--disable-gpu")
            # Start Browser
            self.driver = uc.Chrome(options=options)
            # Hide webdriver usage
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        elif browser == 'Firefox':
            # Set it to Firefox
            options = FirefoxOptions()
            options.set_preference("dom.disable_open_during_load", False)
            options.set_preference('dom.popup_maximum', -1)
            options.set_headless(True)
            self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
        sleep(1)


    def login(self):
        print(colored("INFO> Getting Login Page", "yellow"))
        self.driver.get(LOGIN_URL)
        email_element = self.driver.find_element_by_id('m_login_email')
        email_element.send_keys(self.email) # Give keyboard input

        password_element = self.driver.find_element_by_id('m_login_password')
        password_element.send_keys(self.password) # Give password as input too
 
        login_button = self.driver.find_element_by_id('u_0_4')
        login_button.click() # Send mouse click
        print(colored("INFO> Logging IN", "yellow"))
        sleep(5)
    
    def getEntries(self):
        self.entries = []
        self.database.c.execute("SELECT * from Groups")
        self.entries = self.database.c.fetchall()
    
    def getGroupe(self, entry):
        return entry[0]

    def getKeywords(self, entry):
        return entry[1].lower().strip().split(",")
    
    # Takes a page (group) url and returns a list of latest posts urls
    def drive(self):
        while True:
            self.getEntries()
            if not self.entries:
                print(colored("ALERT> No groups added yet, waiting ...", "yellow"))
                sleep(3)
                continue
            for entry in self.entries:
                group = self.getGroupe(entry)
                keywords = self.getKeywords(entry)
                self.driver.get(group.replace("www", "m") + "?ref=group_browse")
                print(colored("INFO> Driving to group %s" % group, "green"))
                # scroll down to get more posts
                for _ in range(15):
                    sleep(round(uniform(1,3), 2))
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                # Click all read more buttons
                more_btns = self.driver.find_elements_by_css_selector("span[data-sigil='more']")
                for btn in more_btns:
                    try:
                        btn.click()
                    except Exception:
                        pass
                # Make the soup
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, "lxml")

                # Get all posts
                posts = soup.find_all("article")
                # Filter posts older than 24h
                posts = [p for p in posts if re.search(r"hr|min|now", self.get_post_date(p))]
                
                for p in posts:
                    content = self.get_post_content(p)
                    if not content:
                        continue
                    href = self.get_post_link(p)
                    matches = self.find_matching_keywords(content, keywords)
                    if not matches:
                        continue
                    post = {"url": href, "keys": matches, "content": content}
                    post["title"] = " ".join(re.compile(r"\s+").split(post["content"]))[0:80]
                    
                    # Inserting entry in database if it doesn't exist
                    post_query = self.database.get_post(post["url"])
                    if (not post_query):
                        self.database.insert_post(post)

                try:
                    self.database.conn.commit()
                    print(colored("SUCCESS> New Posts Saved to Database", "green"))
                except Exception:
                    print(colored("ERROR> Error Saving to Database, Exiting", "red"))
                
                self.generate_feed()
                sleep(round(uniform(10, 20), 2))

    def get_post_date(self, post):
        link_el = post.find("div", class_=["_52jc _5qc4 _78cz _24u0 _36xo"])
        return link_el.getText()
    
    def get_post_link(self, post):
        link = post.find("div", class_=["_52jc _5qc4 _78cz _24u0 _36xo"]).find("a")["href"]
        if "?refid" in link:
            return link[0: link.index("?refid")].replace("://m", "://www")
        return "NULL"

    def get_post_content(self, post):
        # Posts with background and text
        content1 = post.find("span", class_=["_1-sk _2z7e"])
        # Only text posts
        content2 = post.find("div", class_=["_5rgt _5nk5 _5msi"])

        if content1:
            return content1.getText()
        elif content2:
            return content2.getText()
    
    def find_matching_keywords(self, text, keywords):
        # Turn content into a list
        text_set = text.lower().split(" ")
        # Clean up the words, remove empty strings and turn it into a set of unique words
        text_set = set(filter(bool, [e if e.isalnum() else "".join(filter(str.isalnum, e)) for e in text_set]))
        print(text_set)
        return ",".join(list(text_set.intersection(keywords)))
    
    def generate_feed(self):
        self.database.c.execute("SELECT rowid, * FROM Posts")
        posts = self.database.c.fetchall()
        for post in posts:
            self.feed.add_entry(post)
        self.feed.gen_feed()
    
    def close(self):
        for tab in self.driver.window_handles:
            self.driver.switch_to_window(tab)
            self.driver.close()