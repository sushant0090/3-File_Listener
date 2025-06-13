import os
import time
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

FOLDER = "log_input"

def setup_db():
    conn = sqlite3.connect("log_uploads.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fname TEXT,
        level TEXT,
        msg TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_logs(path):
    try:
        fname = os.path.basename(path)
        with open(path, 'r') as f:
            lines = f.readlines()

        data = []
        for line in lines:
            if ':' in line:
                part1, part2 = line.strip().split(':', 1)
                data.append((fname, part1.strip(), part2.strip()))

        conn = sqlite3.connect("log_uploads.db")
        cur = conn.cursor()
        cur.executemany("INSERT INTO entries (fname, level, msg) VALUES (?, ?, ?)", data)
        conn.commit()
        conn.close()
        print(f"Inserted: {fname}")
    except Exception as e:
        print(f"Error: {e}")

class WatchHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".log"):
            print(f"Detected: {event.src_path}")
            time.sleep(1)
            save_logs(event.src_path)

def run_monitor():
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    setup_db()
    obs = Observer()
    obs.schedule(WatchHandler(), FOLDER, recursive=False)
    obs.start()
    print(f"Watching: {FOLDER}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

if __name__ == "__main__":
    run_monitor()
