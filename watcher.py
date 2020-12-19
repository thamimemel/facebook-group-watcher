from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from time import sleep
import re
LOGIN_URL = 'https://www.facebook.com/login.php'

class FacebookGroupWatcher():
    def __init__(self, email, password, database, browser='Chrome'):
        # Get Entries from entries.txt
        self.getEntries()
        # Get settings from DB
        self.settings = database.settings

        # Store credentials for login
        self.email = email
        self.password = password
        if browser == 'Chrome':
            # Use chrome
            self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
        elif browser == 'Firefox':
            # Set it to Firefox
            options = Options()
            options.set_preference("dom.disable_open_during_load", False)
            options.set_preference('dom.popup_maximum', -1)
            #options.set_headless(True)
            self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
        sleep(1)
        self.init_tabs()

    def init_tabs(self):
        # open new tab for mobile facebook
        self.driver.execute_script("window.open('', '_blank');")
        sleep(1)
        # return to web tab
        self.driver.switch_to_window(self.driver.window_handles[0])

    def login(self):
        self.driver.get(LOGIN_URL)
        email_element = self.driver.find_element_by_id('email')
        email_element.send_keys(self.email) # Give keyboard input
 
        password_element = self.driver.find_element_by_id('pass')
        password_element.send_keys(self.password) # Give password as input too
 
        login_button = self.driver.find_element_by_class_name('_xkt')
        login_button.click() # Send mouse click
 
        sleep(5)
    
    def getEntries(self):
        self.entries = []
        with open("entries.txt", "r") as f:
            for line in f:
                self.entries.append(line.strip())
        f.close()
    
    def getGroupe(self, entry):
        return entry.split("|")[0].strip()

    def getKeywords(self, entry):
        return entry.split("|")[1].strip().split(" ")
    
    # Takes a page (group) url and returns a list of latest posts urls
    def getPostsUrls(self):
        for entry in self.entries:
            group = self.getGroupe(entry)
            for key in self.getKeywords(entry):
                self.driver.get(group + "search?q="+ key + "&filters=eyJycF9jaHJvbm9fc29ydDowIjoie1wibmFtZVwiOlwiY2hyb25vc29ydFwiLFwiYXJnc1wiOlwiXCJ9In0%3D")
                print("Current group: " + group + " " + key)
                for _ in range(1): #int(self.settings["scroll_nbr"])
                    sleep(int(self.settings["scroll_timer"]))
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)") 
                sleep(int(self.settings["scroll_timer"]))
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, "lxml")
                links = soup.findAll("a")
                # switch to mobile tab
                self.driver.switch_to_window(self.driver.window_handles[1])
                #loop over soup and find links for posts                
                for link in links:
                    href = link.get('href')
                    if "/permalink/" in href and "comment" not in href:
                        # open post in m.facebook.com to get post info
                        self.driver.get(href.replace("www", "m"))
                        post = {"link": href}
                        try:
                            post["content"] = self.driver.find_element_by_css_selector("._5rgt._5nk5").text
                        except Exception:
                            post["content"] = ""
                        post["title"] = " ".join(re.compile(r"\s+").split(post["content"]))[0:80]

                        print(post)
                #return to web tab
                self.driver.switch_to_window(self.driver.window_handles[0])
        
    def close(self):
        for tab in self.driver.window_handles:
            self.driver.switch_to_window(tab)
            self.driver.close()