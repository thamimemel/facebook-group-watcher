import http.server
import socketserver

class Server():
    def __init__(self):
        self.PORT = 8888
        self.handler = http.server.SimpleHTTPRequestHandler

    def serve(self):
        with socketserver.TCPServer(("", self.PORT), self.handler) as httpd:
            print("Server started at localhost:" + str(self.PORT))
            httpd.serve_forever()
