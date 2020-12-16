from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from time import sleep
import sqlite3 

LOGIN_URL = 'https://www.facebook.com/login.php'


class Database():
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        # Init settings if not yet inited
        self.c.execute("CREATE TABLE IF NOT EXISTS Settings (name text, val text)")
        self.c.execute("select * from Settings")
        if (not self.c.fetchall()):
            self.init_settings()
            print("reach")
        self.c.execute("select * from Settings")
        print(self.c.fetchall())
    
    # Init Settings table
    def init_settings(self):
        settings = [('scroll_nbr', '3'),('scroll_timer', '5'),]
        self.c.executemany('INSERT INTO Settings VALUES (?,?);', settings)
        self.conn.commit()


class FacebookGroupWatcher():
    def __init__(self, email, password, browser='Chrome'):
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
        for _ in range(3):
            sleep(5)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)") 
        sleep(5)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "lxml")
        for link in soup.findAll('a'):
            href = link.get('href')
            if "/permalink/" in href and "comment" not in href:
                print(href)

if __name__ == '__main__':
    # init databases
    db = Database()
    # Init watchers
    watcher = FacebookGroupWatcher(email='memelthami', password='hp811998aZ-xyznew', browser='Firefox')
    watcher.login()
    for i in range(1):
        watcher.getGroup()
    watcher.driver.close()
