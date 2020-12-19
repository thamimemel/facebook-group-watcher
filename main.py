from database import Database
from watcher import FacebookGroupWatcher
from feed import Feed
from server import Server
from multiprocessing import Process

if __name__ == '__main__':
    # init databases
    db = Database()
    # init Feed
    feed = Feed()
    # init server
    server = Server()
    # Init watchers
    watcher = FacebookGroupWatcher(email='memelthami', password='hp811998aZ-xyznew', database=db, feed=feed, browser='Firefox')

    def watch():
        watcher.login()
        watcher.drive()
    try:
        p1 = Process(target=watch)
        p1.start()
        p2 = Process(target=server.serve)
        p2.start()


    except Exception:
        watcher.close()
        print("unexpected error, closing")
