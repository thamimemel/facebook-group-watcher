from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from time import sleep
import re
from sys import exit
from termcolor import colored

LOGIN_URL = 'https://www.facebook.com/login.php'

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
            options = Options()
            # Disable images and notifications popups
            prefs = {'profile.managed_default_content_settings.images':2, "profile.default_content_setting_values.notifications" : 2,}
            options.add_experimental_option("prefs", prefs)
            # Prevent detection (hopefully ?)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_argument('--disable-blink-features=AutomationControlled')
            # Maximize
            options.add_argument("--start-maximized")
            # Headless
            options.set_headless(True)
            # Disable GPU
            options.add_argument("--disable-gpu")
            # Start Browser
            self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
            # Hide webdriver usage
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        sleep(1)

    def login(self):
        print(colored("INFO> Getting Login Page", "yellow"))
        self.driver.get(LOGIN_URL)
        email_element = self.driver.find_element_by_id('email')
        email_element.send_keys(self.email) # Give keyboard input
 
        password_element = self.driver.find_element_by_id('pass')
        password_element.send_keys(self.password) # Give password as input too
 
        login_button = self.driver.find_element_by_class_name('_xkt')
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
        return entry[1].strip().split(",")
    
    # Takes a page (group) url and returns a list of latest posts urls
    def drive(self):
        while True:
            self.getEntries()
            for entry in self.entries:
                group = self.getGroupe(entry)
                keywords = self.getKeywords(entry)
                # Go to mobile group
                self.driver.get(group+"?sorting_setting=CHRONOLOGICAL")
                sleep(5)
                for _ in range(5):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)") 
                    sleep(3)
                
                # find all "See More" buttons
                more_btns = self.driver.find_elements_by_css_selector("div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.oo9gr5id.gpro0wi8.lrazzd5p")

                # find all post links
                links = self.driver.find_elements_by_css_selector(".oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.gpro0wi8.b1v8xokw")

                # simulate mouse over to activate links
                action = ActionChains(self.driver)
                for link in links:
                    action.move_to_element(link).perform()
                    sleep(0.3)
                
                # Click all more buttons if there is any
                if more_btns:
                    for btn in more_btns:
                        self.driver.execute_script("arguments[0].click()", btn)
                        sleep(1)
                
                # make soup
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, "lxml")

                # find all posts
                articles = soup.find_all("div", class_=['du4w35lb k4urcfbm l9j0dhe7 sjgh65i0'])
                
                # loop over posts
                for index, article in enumerate(articles):
                    href = self.clean_post_link(links[index].get_attribute("href"))    # post link
                    text = self.get_clean_post_text(article) # post content
                    if text:
                        matched_keys = self.fing_matching_keywords(text, keywords)
                        if (matched_keys):
                            print(index)
                            print(matched_keys)

                import sys
                self.driver.quit()
                sys.exit()
                sleep(120)
                """
                for key in self.getKeywords(entry):
                    self.driver.get(group + "search?q="+ key + "&filters=eyJycF9jaHJvbm9fc29ydDowIjoie1wibmFtZVwiOlwiY2hyb25vc29ydFwiLFwiYXJnc1wiOlwiXCJ9In0%3D")
                    print(colored("INFO> Driving to Group: " + group + " With keyword " + key, "yellow"))
                    for _ in range(int(self.settings["scroll_nbr"])):
                        sleep(int(self.settings["scroll_timer"]))
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)") 
                    sleep(int(self.settings["scroll_timer"]))
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, "lxml")
                    links = soup.findAll("a")
                    # switch to mobile tab
                    self.driver.switch_to_window(self.driver.window_handles[1])
                    #loop over soup and find links for posts      
                    print(colored(">>>>>>Scanning Matched Posts from " + group + " for keyword " + key, "yellow"))          
                    for link in links:
                        href = link.get('href')
                        if "/permalink/" in href and "comment" not in href:
                            # open post in m.facebook.com to get post info
                            self.driver.get(href.replace("www", "m"))
                            post = {"url": href, "key": key}
                            if (self.driver.find_element_by_css_selector("._5rgt._5nk5").text):
                                post["content"] = self.driver.find_element_by_css_selector("._5rgt._5nk5").text
                            else:
                                post["content"] = "NO TEXT CONTENT"
                            post["title"] = " ".join(re.compile(r"\s+").split(post["content"]))[0:80]
                            # Inserting or updating entry in database
                            post_query = self.database.get_post(post["url"])
                            if (not post_query):
                                self.database.insert_post(post)
                            elif (post_query and key not in post_query[1]):
                                new_key = "%s,%s" % (post_query[1], key)
                                self.database.update_post(post["url"], new_key)
                    try:
                        self.database.conn.commit()
                        print(colored("SUCCESS> New Posts Saved to Database", "green"))
                    except Exception:
                        print(colored("ERROR> Error Saving to Database, Exiting", "red"))
                        exit(1)
                    try:
                        print(colored("INFO> Generating New RSS Feed", "yellow"))
                        self.generate_feed()
                        print(colored("SUCCESS> RSS Updated Successfully", "green"))
                    except Exception:
                        print(colored("ERROR> Error Generating Feed, Exiting", "red"))
                        exit(1)
                    #return to web tab
                    self.driver.switch_to_window(self.driver.window_handles[0])
                    """
    def fing_matching_keywords(self, text, keywords):
        text_set = set(text.split(" "))
        return ",".join(list(text_set.intersection(keywords)))
    
    def get_clean_post_text(self, post):
        long = post.find("span", class_=['d2edcug0 hpfvmrgz qv66sw1b c1et5uql gk29lw5a a8c37x1j keod5gw0 nxhoafnm aigsh9s9 d9wwppkn fe6kdd0r mau55g9w c8b282yb hrzyx87i jq4qci2q a3bd9o3v knj5qynh oo9gr5id hzawbc8m'])
        short = post.find("div", class_=['qt6c0cv9 hv4rvrfc dati1w0a jb3vyjys'])
        if long:
            return long.text
        
        if short:
            return short.text
    
    def clean_post_link(self, link):
        if "?__cft" in link:
            return link[0: link.index("?__cft")]
        return "NULL"
    
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
