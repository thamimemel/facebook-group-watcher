import sqlite3 

class Database():
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()

        # Init settings table if not yet inited
        self.c.execute("CREATE TABLE IF NOT EXISTS Settings (name text, val text)")
        self.c.execute("select * from Settings")
        if (len(self.c.fetchall()) == 0):
            self.init_settings()
        self.setting_parser()


        #Init Posts table if not yet inited
        self.c.execute("CREATE TABLE IF NOT EXISTS Posts (url text, keys text, title text, content text)")

    
    # Init Settings table
    def init_settings(self):
        settings = [('scroll_nbr', '3'),('scroll_timer', '5'),]
        self.c.executemany('INSERT INTO Settings VALUES (?,?);', settings)
        self.conn.commit()

    # settings
    def setting_parser(self):
        settings = {}
        self.c.execute("select * from Settings")
        for e in self.c.fetchall():
            settings[e[0]] = e[1]
        self.settings = settings

    def get_post(self, url):
        self.c.execute("SELECT * FROM Posts WHERE url=?", (url,))
        return self.c.fetchone()
    
    def insert_post(self, post):
        data = (post["url"], post["key"], post["title"], post["content"])
        self.c.execute("INSERT INTO Posts VALUES (?,?,?,?)", data)
    
    def update_post(self, url, keys):
        self.c.execute("""
        UPDATE Posts
        SET keys=?
        WHERE url=?
        """, (keys, url))