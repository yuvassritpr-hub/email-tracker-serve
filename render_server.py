from flask import Flask, request, send_file, jsonify
import sqlite3, io, os
from datetime import datetime

app = Flask(__name__)
DB  = '/tmp/tracker.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id   TEXT,
        recipient  TEXT,
        event_type TEXT,
        ip         TEXT,
        timestamp  TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return '<html><body style="font-family:Arial;text-align:center;padding:60px"><h2 style="color:#0078d4">&#10003; Email Tracker Server Running!</h2><p>Tracking server is active.</p></body></html>'

@app.route('/logo/<email_id>/<recipient>')
def track_logo(email_id, recipient):
    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Only count once per email_id+recipient
    c.execute("SELECT id FROM events WHERE email_id=? AND recipient=? AND event_type='open'",
              (email_id, recipient))
    if not c.fetchone():
        c.execute("INSERT INTO events (email_id,recipient,event_type,ip,timestamp) VALUES (?,?,?,?,?)",
                  (email_id, recipient, 'open', request.remote_addr, now))
    else:
        c.execute("UPDATE events SET timestamp=? WHERE email_id=? AND recipient=? AND event_type='open'",
                  (now, email_id, recipient))
    conn.commit()
    conn.close()
    px = bytes([71,73,70,56,57,97,1,0,1,0,128,0,0,255,255,255,0,0,0,
                33,249,4,0,0,0,0,0,44,0,0,0,0,1,0,1,0,0,2,2,68,1,0,59])
    return send_file(io.BytesIO(px), mimetype='image/gif')

@app.route('/click/<email_id>/<recipient>')
def track_click(email_id, recipient):
    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("SELECT id FROM events WHERE email_id=? AND recipient=? AND event_type='click'",
              (email_id, recipient))
    if not c.fetchone():
        c.execute("INSERT INTO events (email_id,recipient,event_type,ip,timestamp) VALUES (?,?,?,?,?)",
                  (email_id, recipient, 'click', request.remote_addr, now))
    conn.commit()
    conn.close()
    return '''<html><body style="font-family:Arial;text-align:center;padding:60px;background:#f0f8ff">
    <div style="background:white;border-radius:12px;padding:40px;display:inline-block;box-shadow:0 4px 20px rgba(0,0,0,.1)">
    <h2 style="color:#0078d4">&#10003; Email Received!</h2>
    <p style="color:#666">Thank you. You may close this page.</p>
    </div></body></html>'''

@app.route('/api/events')
def get_events():
    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    c.execute("SELECT email_id,recipient,event_type,ip,timestamp FROM events ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"email_id":r[0],"recipient":r[1],
                     "type":r[2],"ip":r[3],"time":r[4]} for r in rows])

@app.route('/api/ping')
def ping():
    return jsonify({"status":"ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
