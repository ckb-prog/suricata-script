import os
import time
import subprocess
import json

# Configuration
SURICATA_CONFIG = "/usr/local/etc/suricata/suricata.yaml"
NETWORK_INTERFACE = "wlan1"  # Change interface if needed
FAST_LOG = "/var/log/suricata/fast.log"
EVE_LOG = "/var/log/suricata/eve.json"
PID_FILE = "/usr/local/var/run/suricata.pid"

# Function to check if Suricata is running
def check_suricata_status():
    print("[+] Checking Suricata service status...")
    
    # Check if Suricata is running using pgrep
    result = subprocess.run(["pgrep", "-x", "suricata"], capture_output=True, text=True)
    
    if result.stdout.strip():
        print("[+] Suricata is running.")
    else:
        print("[ERROR] Suricata is NOT running! Restarting now...")

        # Remove old PID file if it exists
        if os.path.exists(PID_FILE):
            print("[+] Removing stale PID file...")
            os.remove(PID_FILE)

        # Restart Suricata manually
        subprocess.run(["sudo", "pkill", "suricata"], check=False)  # Kill any existing Suricata processes
        subprocess.run(["sudo", "suricata", "-c", SURICATA_CONFIG, "-i", NETWORK_INTERFACE, "-D"], check=True)  # Start Suricata in background

# Function to update Suricata rules and restart if needed
def update_suricata_rules():
    print("[+] Running Suricata rule update...")
    subprocess.run(["sudo", "suricata-update"], check=True)
    
    print("[+] Restarting Suricata manually after rule update...")
    check_suricata_status()

# Function to monitor fast.log in real-time
def monitor_fast_log():
    print("[+] Monitoring fast.log for real-time alerts...")
    try:
        with open(FAST_LOG, "r") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    print(f"[ALERT] {line.strip()}")
                time.sleep(0.5)  # Reduce CPU usage
    except FileNotFoundError:
        print("[ERROR] fast.log not found! Is Suricata running?")

# Function to monitor eve.json in real-time
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
                        print(f"[EVE ALERT] {json.dumps(alert, indent=2)}")
                    except json.JSONDecodeError:
                        print("[ERROR] Corrupt JSON entry in eve.json")
                time.sleep(0.5)
    except FileNotFoundError:
        print("[ERROR] eve.json not found! Is Suricata running?")

# Main function to start monitoring and rule updates
def main():
    check_suricata_status()  # Ensure Suricata is running

    while True:
        update_suricata_rules()  # Run updates every 24 hours
        time.sleep(86400)  # Sleep for 24 hours (86400 seconds)

# Run log monitoring in separate processes
if __name__ == "__main__":
    from multiprocessing import Process

    p1 = Process(target=monitor_fast_log)
    p2 = Process(target=monitor_eve_log)

    p1.start()
    p2.start()

    main()
