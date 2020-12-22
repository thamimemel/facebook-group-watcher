from database import Database
from watcher import FacebookGroupWatcher
from feed import Feed
from multiprocessing import Process
from termcolor import colored

if __name__ == '__main__':
    # init databases
    db = Database()
    print(colored("SUCCESS> Database Initialized", "green"))
    # init Feed
    feed = Feed()
    print(colored("SUCCESS> Feed Initialized", "green"))
    # Init watchers
    watcher = FacebookGroupWatcher(email='memelthami', password='hp811998aZ-xyznew', database=db, feed=feed, browser='Firefox')
    print(colored("SUCCESS> Watcher Initialized", "green"))

    def watch():
        watcher.login()
        watcher.drive()
    try:
        p1 = Process(target=watch)
        p1.start()
        print(colored("SUCCESS> Watcher Started Successfully", "green"))

    except Exception:
        watcher.close()
        print(colored("ERROR> unexpected error, closing", "red"))
