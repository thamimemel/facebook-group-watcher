from flask import Flask, request, render_template, send_from_directory, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/", methods=["GET"])
def gethome():
    return render_template("index.html")

@app.route("/feed.xml", methods=["GET"])
def feed():
    return send_from_directory(".", "feed.xml")

@app.route("/getgroups", methods=["GET"])
def getgroups():
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Groups")
        return jsonify(cur.fetchall())

@app.route("/addgroup", methods=["POST"])
def addgroup():
    req_data = request.get_json()   
    url = req_data["url"]
    keywords = req_data["keywords"]
    try:
        with sqlite3.connect("database.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Groups VALUES (?, ?)", (url, keywords))
            return jsonify({"success": "ok"})
    except Exception:
        return jsonify({"failed": "error connecting to database"})
app.run(host= "127.0.0.1", port=8888, debug=True)