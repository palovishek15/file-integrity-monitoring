#!/usr/bin/env python3
import os
import hashlib
import json
import requests
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

# Directory to monitor
MONITORED_DIR = Path("/home/ovi/Documents/fim/monitored")
BASELINE_FILE = Path("baseline.json")
SIGNATURE_FILE = Path("baseline_signature.sig")
PRIVATE_KEY_FILE = "private_key.pem"
SERVER_URL = "http://127.0.0.1:5000/report"

def hash_file(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def load_baseline():
    if BASELINE_FILE.exists():
        with open(BASELINE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_baseline(data):
    with open(BASELINE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    # Sign the baseline after saving
    sign_baseline()

def sign_baseline():
    """Sign the baseline.json with the private key."""
    if BASELINE_FILE.exists():
        # Load the private key
        with open(PRIVATE_KEY_FILE, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(), password=None
            )
        
        # Hash the baseline file (create a hash of its contents)
        with open(BASELINE_FILE, "rb") as f:
            baseline_data = f.read()
        
        # Create a signature of the baseline data
        signature = private_key.sign(
            baseline_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Save the signature to a file
        with open(SIGNATURE_FILE, "wb") as sig_file:
            sig_file.write(signature)

def verify_baseline():
    """Verify the baseline file using the public key."""
    if not SIGNATURE_FILE.exists():
        print("No signature found, baseline may have been tampered with.")
        return False
    
    with open(SIGNATURE_FILE, "rb") as sig_file:
        signature = sig_file.read()

    # Load the public key
    with open("public_key.pem", "rb") as pub_key_file:
        public_key = serialization.load_pem_public_key(pub_key_file.read())

    # Load the baseline file and verify the signature
    with open(BASELINE_FILE, "rb") as f:
        baseline_data = f.read()

    try:
        # Verify the signature
        public_key.verify(
            signature,
            baseline_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print("Baseline verification successful!")
        return True
    except Exception as e:
        print(f"Error verifying baseline: {e}")
        return False

def send_notification(title, message):
    """Send desktop notification."""
    import notify2
    notify2.init("FIM Alert")
    n = notify2.Notification(title, message)
    n.set_urgency(notify2.URGENCY_NORMAL)
    n.show()

def main():
    baseline = load_baseline()
    current = {}

    new_files = []
    deleted_files = []
    modified_files = []

    # Verify the baseline file before using it
    if not verify_baseline():
        print("Warning: Baseline file has been tampered with!")
        return

    for f in MONITORED_DIR.iterdir():
        if f.is_file():
            current[f.name] = hash_file(f)
            if f.name not in baseline:
                new_files.append(f.name)
            elif baseline[f.name] != current[f.name]:
                modified_files.append(f.name)

    for f in baseline:
        if f not in current:
            deleted_files.append(f)

    report = {
        "new": new_files,
        "deleted": deleted_files,
        "changed": modified_files
    }

    # Send report to server
    if new_files or deleted_files or modified_files:
        try:
            requests.post(SERVER_URL, json=report)
        except Exception as e:
            print(f"Error sending report: {e}")

    # Save new baseline after the changes
    save_baseline(current)

if __name__ == "__main__":
    main()

