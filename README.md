# File Integrity Monitoring System (FIM)

A **File Integrity Monitoring (FIM)** system that tracks and reports changes to files in a specified directory. The system uses **digital signatures** to protect the baseline file from tampering. It uses **Flask** for the server and **SQLite** for storing the reports, while client-side scripts monitor the filesystem, create file integrity reports, and sign baseline files.

## Features

- **Monitors directory** for file changes (new, deleted, modified files).
- **Digital signature protection** to prevent tampering with the baseline.
- **Flask-based web dashboard** to display the integrity reports in real-time.
- **SQLite database** to store file integrity reports.
- **Client-server architecture** where the client sends reports to the server.
- **Desktop notifications** when changes occur (optional).

## Project Structure

```plaintext
fim_system/
├── fim_server.py                # Flask server code (handles report receiving, DB, dashboard)
├── fim_check.py                 # Client-side script (hashes files, signs baseline, sends report)
├── monitored/                   # Directory being monitored for file changes
│   ├── important.conf           # Example file to be monitored (you can add more)
│   └── script.sh                # Another file to monitor
├── baseline.json                # Stores the hash of baseline files (sent by the client)
├── baseline_signature.sig       # Signature of baseline.json (signed by the client)
├── private_key.pem              # Private key for signing the baseline (client side)
├── public_key.pem               # Public key for verifying the baseline (client side)
├── fim.db                       # SQLite database to store file integrity reports
├── reports.log                  # Log file to store incoming reports (optional for debugging)
├── requirements.txt             # List of Python dependencies
└── README.md                    # Project documentation (explains the project)
````

## Prerequisites

Before running the project, make sure you have the following installed on your machine:

* **Python 3.x**
* **pip** (Python package installer)

You also need to install the required Python packages:

```bash
pip install -r requirements.txt
```

## Installation & Setup

1. **Clone the repository**:

   Clone the GitHub repository to your local machine.

   ```bash
   git clone https://github.com/palovishek/file-integrity-monitoring.git
   cd file-integrity-monitoring
   ```

2. **Install the dependencies**:

   Install all required Python packages listed in `requirements.txt`.

   ```bash
   pip install -r requirements.txt
   ```

3. **Generate RSA Keys** (if not already provided):

   If you don't have the `private_key.pem` and `public_key.pem` files, you can generate them using the following Python code:

   ```python
   from cryptography.hazmat.primitives.asymmetric import rsa
   from cryptography.hazmat.primitives import serialization

   # Generate private key
   private_key = rsa.generate_private_key(
       public_exponent=65537,
       key_size=2048
   )

   # Save private key to file
   with open("private_key.pem", "wb") as private_key_file:
       private_key_file.write(
           private_key.private_bytes(
               encoding=serialization.Encoding.PEM,
               format=serialization.PrivateFormat.PKCS8,
               encryption_algorithm=serialization.NoEncryption()
           )
       )

   # Generate public key
   public_key = private_key.public_key()

   # Save public key to file
   with open("public_key.pem", "wb") as public_key_file:
       public_key_file.write(
           public_key.public_bytes(
               encoding=serialization.Encoding.PEM,
               format=serialization.PublicFormat.SubjectPublicKeyInfo
           )
       )
   ```

4. **Start the Flask Server**:

   Run the Flask server (`fim_server.py`) to handle incoming reports from the client:

   ```bash
   python3 fim_server.py
   ```

   The server will run on `http://127.0.0.1:5000` and listen for incoming reports from the client.

5. **Run the Client Script**:

   The client script (`fim_check.py`) will monitor the directory specified in the `MONITORED_DIR` variable for file changes and send reports to the Flask server.

   ```bash
   python3 fim_check.py
   ```

   This script will:

   * Hash the files in the `monitored/` directory.
   * Compare the hashes to the **baseline**.
   * Detect changes and send reports to the server.
   * Sign the **baseline.json** file and protect it with the private key.

## How It Works

### Server-Side:

* **Flask Server (`fim_server.py`)**:

  * Handles incoming file integrity reports via the `/report` route.
  * Stores reports in an **SQLite** database (`fim.db`).
  * Provides a **real-time dashboard** of the last 20 reports via the `/` route.

### Client-Side:

* **File Monitoring**:

  * Monitors the `monitored/` directory for changes (new, modified, deleted files).
  * Computes file hashes using **SHA-256**.

* **Digital Signatures**:

  * **Signs** the `baseline.json` file with the **private key**.
  * Verifies the **integrity** of the `baseline.json` using the **public key** before sending reports to the server.

* **File Integrity Report**:

  * Sends a report containing the list of **new**, **deleted**, and **modified** files to the Flask server.

* **Notifications** (optional):

  * Desktop notifications alert the user when files are modified.

### Digital Signatures:

* **Private Key** (`private_key.pem`) is used to sign the `baseline.json` file on the client-side.
* **Public Key** (`public_key.pem`) is used to verify the integrity of the baseline file before sending the report.

## Dashboard

The Flask server provides a simple dashboard at `http://127.0.0.1:5000` that shows the last 20 integrity reports. The reports are updated every 5 seconds.

---

## Example Output:

When running the client, it will monitor the `monitored/` directory. For example:

```bash
New file detected: important.conf
File modified: script.sh
File deleted: old_file.txt
```

If a report is sent to the server, it will be stored in the SQLite database and can be viewed on the Flask dashboard.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

* **Flask**: For creating the web server.
* **SQLite**: For storing integrity reports.
* **Cryptography**: For signing and verifying the baseline files.


### Key Sections of the README:

- **Project Overview**: Provides a brief summary of the project’s goals and what it does.
- **Project Structure**: Explains the directory layout.
- **Installation Instructions**: Steps for installing dependencies, generating keys, and running both the server and client.
- **How It Works**: A description of how the client and server interact, how files are monitored, and how digital signatures are used.
- **Dashboard Info**: Provides info on how to access the real-time dashboard that shows integrity reports.
- **License & Acknowledgements**: Credits the libraries used and provides licensing info.
