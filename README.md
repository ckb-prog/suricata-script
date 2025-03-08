- Monitors Suricata logs (fast.log and eve.json) in real-time.
- Runs suricata-update every 24 hours to keep rule sets fresh.
- Checks if Suricata is running and restarts it if needed.
- Removes stale PID files to prevent startup errors.
- Prevents multiple Suricata instances from running.
- Uses pgrep -x suricata for reliable process detection.
- Runs Suricata on wlan1 (Change NETWORK_INTERFACE if needed).
- Runs continuously in the background.

