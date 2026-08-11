from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "traffic.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT NOT NULL,
        status TEXT NOT NULL,
        vehicles INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT NOT NULL,
        type TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_no TEXT NOT NULL,
        violation TEXT NOT NULL,
        fine INTEGER NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    if conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO signals(location,status,vehicles) VALUES(?,?,?)",
            [
                ("Rajiv Gandhi Chowk", "GREEN", 42),
                ("Gandhi Chowk", "RED", 68),
                ("Main Bus Stand", "YELLOW", 31),
                ("Shivaji Chowk", "GREEN", 24),
            ],
        )
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.get("/api/dashboard")
def dashboard():
    conn = get_db()
    signals = [dict(r) for r in conn.execute("SELECT * FROM signals ORDER BY id")]
    incidents = [dict(r) for r in conn.execute(
        "SELECT * FROM incidents ORDER BY id DESC LIMIT 5"
    )]
    violations = [dict(r) for r in conn.execute(
        "SELECT * FROM violations ORDER BY id DESC LIMIT 5"
    )]
    stats = {
        "signals": len(signals),
        "vehicles": sum(r["vehicles"] for r in signals),
        "incidents": conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0],
        "violations": conn.execute("SELECT COUNT(*) FROM violations").fetchone()[0],
    }
    conn.close()
    return jsonify({"stats": stats, "signals": signals,
                    "incidents": incidents, "violations": violations})

@app.post("/api/signals/<int:sid>/toggle")
def toggle_signal(sid):
    conn = get_db()
    row = conn.execute("SELECT status FROM signals WHERE id=?", (sid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Signal not found"}), 404
    cycle = {"RED": "GREEN", "GREEN": "YELLOW", "YELLOW": "RED"}
    new_status = cycle[row["status"]]
    conn.execute("UPDATE signals SET status=? WHERE id=?", (new_status, sid))
    conn.commit()
    conn.close()
    return jsonify({"status": new_status})

@app.post("/api/incidents")
def add_incident():
    data = request.get_json()
    if not data.get("location") or not data.get("type"):
        return jsonify({"error": "Location and type are required"}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO incidents(location,type,description,created_at) VALUES(?,?,?,?)",
        (data["location"], data["type"], data.get("description",""),
         datetime.now().strftime("%d-%m-%Y %H:%M"))
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Incident reported successfully"})

@app.post("/api/violations")
def add_violation():
    data = request.get_json()
    if not data.get("vehicle_no") or not data.get("violation"):
        return jsonify({"error": "Vehicle number and violation are required"}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO violations(vehicle_no,violation,fine,created_at) VALUES(?,?,?,?)",
        (data["vehicle_no"].upper(), data["violation"],
         int(data.get("fine", 500)),
         datetime.now().strftime("%d-%m-%Y %H:%M"))
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Violation added successfully"})

if __name__ == "__main__":
    app.run(debug=True)


