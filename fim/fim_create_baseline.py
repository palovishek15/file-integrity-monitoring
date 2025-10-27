#!/usr/bin/env python3
import os
import sqlite3
from fim_utils import hash_file, init_db, sign_baseline, DB_PATH

MONITORED_DIR = "/home/ovi/Documents/fim/monitored"

def create_baseline():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM baseline")

    for root, _, files in os.walk(MONITORED_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            file_hash = hash_file(full_path)
            c.execute("INSERT OR REPLACE INTO baseline VALUES (?, ?, ?, ?)", 
                      (full_path, file_hash, os.path.getsize(full_path), os.path.getmtime(full_path)))

    conn.commit()
    conn.close()
    sign_baseline()
    print("[+] Baseline created and digitally signed.")

if __name__ == "__main__":
    create_baseline()

