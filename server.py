'''
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
'''
import flask
import sqlite3

app = flask.Flask(__name__)

@app.route("/", methods=["GET"])
def gethome():
    return flask.render_template("index.html")

@app.route("/feed.xml", methods=["GET"])
def feed():
    return flask.send_from_directory(".", "feed.xml")

@app.route("/getgroups", methods=["GET"])
def getgroups():
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Groups")
        return flask.jsonify(cur.fetchall())
app.run(host= "127.0.0.1", port=8888, debug=True)