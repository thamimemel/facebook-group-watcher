from feedgen.feed import FeedGenerator

class Feed():
    def __init__(self):
        self.fg = FeedGenerator()
        self.fg.id("1")
        self.fg.title("Facebook Group Watcher")
        self.fg.link(href="http://localhost:8888", rel="alternate")
        self.fg.logo("https://image.similarpng.com/very-thumbnail/2020/04/Facebook-logo-3d-button-social-media-png-3.png")
        self.fg.subtitle("Cool facebook watcher for groups")
        self.fg.link(href="http://localhost:8888/rss.atom", rel="self")
        self.fg.language("en")

    def add_entry(self, post):
        fe = self.fg.add_entry()
        fe.id(str(post[0]))
        fe.link(href=post[1])
        fe.title(post[3])
        fe.content(content=post[4])
        fe.summary(summary=post[2])
    
    def gen_feed(self):
        atomfeed = self.fg.atom_str(pretty=True)
        f = open("feed.xml", "wb")
        f.write(atomfeed)
        f.close()
        self.__init__() # reset