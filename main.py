from database import Database
from watcher import FacebookGroupWatcher
if __name__ == '__main__':
    # init databases
    db = Database()
    # Init watchers
    watcher = FacebookGroupWatcher(email='memelthami', password='hp811998aZ-xyznew', settings=db.settings, browser='Firefox')
    print(watcher.keywords)
    watcher.login()
    watcher.getPostsUrls()
    watcher.driver.close()
