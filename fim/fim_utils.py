import hashlib
import sqlite3
import os
import json
import hmac

DB_PATH = "/home/ovi/Documents/fim/fim.db"
SECRET_KEY = b"MyStrongSecretKey"  # Change this for real use
BASELINE_SIG = "/home/ovi/Documents/fim/fim_baseline.sig"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS baseline (
            path TEXT PRIMARY KEY,
            hash TEXT,
            size INTEGER,
            mtime REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            new_files TEXT,
            deleted_files TEXT,
            modified_files TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_file(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()

def sign_baseline():
    """Generate digital signature for baseline table"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT path, hash FROM baseline ORDER BY path")
    data = json.dumps(c.fetchall()).encode()
    conn.close()

    sig = hmac.new(SECRET_KEY, data, hashlib.sha256).hexdigest()
    with open(BASELINE_SIG, "w") as f:
        f.write(sig)

def verify_signature():
    """Verify that the baseline hasn't been modified"""
    if not os.path.exists(BASELINE_SIG):
        print("[!] No baseline signature found.")
        return False

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT path, hash FROM baseline ORDER BY path")
    data = json.dumps(c.fetchall()).encode()
    conn.close()

    with open(BASELINE_SIG) as f:
        stored_sig = f.read().strip()
    current_sig = hmac.new(SECRET_KEY, data, hashlib.sha256).hexdigest()

    return hmac.compare_digest(stored_sig, current_sig)

