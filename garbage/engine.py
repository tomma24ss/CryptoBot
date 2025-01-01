# engine.py

import time
import subprocess
from datetime import datetime

def run_script():
    """Run the BTCUSD data scraping script."""
    print(f"[{datetime.now()}] Running BTCUSD.py...")
    subprocess.run(["python", "BTCUSD.py"])

def main():
    """Schedule the BTCUSD.py script every minute."""
    try:
        while True:
            run_script()
            time.sleep(60)  # Wait for 60 seconds before running again
    except KeyboardInterrupt:
        print("\nScheduler stopped manually.")

if __name__ == "__main__":
    main()
