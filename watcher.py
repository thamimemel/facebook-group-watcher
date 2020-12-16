from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from time import sleep

LOGIN_URL = 'https://www.facebook.com/login.php'

class FacebookGroupWatcher():
    def __init__(self, email, password, settings, browser='Chrome'):
        # Store credentials for login
        self.settings = settings
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
        self.driver.get(LOGIN_URL)
        sleep(1)
 
 
 
    def login(self):
        email_element = self.driver.find_element_by_id('email')
        email_element.send_keys(self.email) # Give keyboard input
 
        password_element = self.driver.find_element_by_id('pass')
        password_element.send_keys(self.password) # Give password as input too
 
        login_button = self.driver.find_element_by_class_name('_xkt')
        login_button.click() # Send mouse click
 
        sleep(5)
    
    def getGroup(self):
        #https://m.facebook.com/abdelilah.memel.5
        self.getPostsUrls("https://www.facebook.com/groups/1408001826007480/search?q=emploi&filters=eyJycF9jaHJvbm9fc29ydDowIjoie1wibmFtZVwiOlwiY2hyb25vc29ydFwiLFwiYXJnc1wiOlwiXCJ9In0%3D")

    # Takes a page (group) url and returns a list of latest posts urls
    def getPostsUrls(self, page):
        self.driver.get(page)
        for _ in range(self.settings["scroll_nbr"]):
            sleep(self.settings["scroll_timer"])
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)") 
        sleep(self.settings["scroll_timer"])
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "lxml")
        for link in soup.findAll('a'):
            href = link.get('href')
            if "/permalink/" in href and "comment" not in href:
                print(href)