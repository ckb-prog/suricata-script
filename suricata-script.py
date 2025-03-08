import os
import time
import subprocess
import json

# Paths to Suricata logs
FAST_LOG = "/var/log/suricata/fast.log"
EVE_LOG = "/var/log/suricata/eve.json"

# Function to read fast.log in real-time
def monitor_fast_log():
    print("[+] Monitoring fast.log for real-time alerts...")
    try:
        with open(FAST_LOG, "r") as f:
            f.seek(0, os.SEEK_END)  # Move to the end of the file
            while True:
                line = f.readline()
                if line:
                    print(f"[ALERT] {line.strip()}")
                time.sleep(0.5)  # Avoid high CPU usage
    except FileNotFoundError:
        print("[ERROR] fast.log not found! Is Suricata running?")
        return

# Function to read eve.json in real-time
def monitor_eve_log():
    print("[+] Monitoring eve.json for detailed alerts...")
    try:
        with open(EVE_LOG, "r") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    try:
                        alert = json.loads(line)
                        print(f"[EVE ALERT] {alert}")
                    except json.JSONDecodeError:
                        print("[ERROR] Corrupt JSON entry in eve.json")
                time.sleep(0.5)
    except FileNotFoundError:
        print("[ERROR] eve.json not found! Is Suricata running?")
        return

# Function to update Suricata rules
def update_suricata_rules():
    print("[+] Running Suricata rule update...")
    subprocess.run(["sudo", "suricata-update"], check=True)
    print("[+] Restarting Suricata...")
    subprocess.run(["sudo", "systemctl", "restart", "suricata"], check=True)

# Function to check Suricata status
def check_suricata_status():
    print("[+] Checking Suricata service status...")
    result = subprocess.run(["sudo", "systemctl", "is-active", "suricata"], capture_output=True, text=True)
    if "active" in result.stdout:
        print("[+] Suricata is running.")
    else:
        print("[ERROR] Suricata is NOT running! Restarting now...")
        subprocess.run(["sudo", "systemctl", "restart", "suricata"])

# Main function to start monitoring
def main():
    # Check if Suricata is running
    check_suricata_status()

    # Run Suricata rule update every 24 hours in a separate process
    while True:
        update_suricata_rules()
        time.sleep(86400)  # Sleep for 24 hours (86400 seconds)

# Run log monitoring in a separate process
if __name__ == "__main__":
    from multiprocessing import Process

    # Start fast.log and eve.json monitoring
    p1 = Process(target=monitor_fast_log)
    p2 = Process(target=monitor_eve_log)

    p1.start()
    p2.start()

    # Run the update cycle
    main()
