from flask import Flask, request, render_template, send_from_directory, jsonify
import sqlite3

app = Flask(__name__)

sqlite3.connect("database.db").cursor().execute("CREATE TABLE IF NOT EXISTS Groups (url text, keywords text)")
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
            if (not cur.execute("SELECT * FROM Groups WHERE url = ?", (url,)).fetchone()):
                cur.execute("INSERT INTO Groups VALUES (?, ?)", (url, keywords))
                return jsonify({"success": "ok"})
            return jsonify({"failed": "group already exists, are you trying to update an existing goup"})
    except Exception:
        return jsonify({"failed": "error connecting to database"})
app.run(host= "127.0.0.1", port=8888, debug=True)