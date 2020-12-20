import http.server
import socketserver
from termcolor import colored

class quitHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

class Server():
    def __init__(self):
        self.PORT = 8888
        self.handler = quitHandler

    def serve(self):
        with socketserver.TCPServer(("", self.PORT), self.handler) as httpd:
            print(colored("SUCESS> Server started at http://localhost:" + str(self.PORT), "green"))
            print(colored("INFO> RSS Feeds Will be Available at http://localhost:" + str(self.PORT) + "/feed.xml", "yellow"))
            httpd.serve_forever()
