from database import Database
from watcher import FacebookGroupWatcher
from Feed import Feed

if __name__ == '__main__':
    # init databases
    db = Database()
    # init Feed
    feed = Feed()
    # Init watchers
    watcher = FacebookGroupWatcher(email='memelthami', password='hp811998aZ-xyznew', database=db, feed=feed, browser='Firefox')
    try:
        watcher.login()
        watcher.drive()
    except Exception:
        watcher.close()
        print("unexpected error, closing")
