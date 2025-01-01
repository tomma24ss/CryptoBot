import os
import csv
import time
import requests
import logging
from datetime import datetime, timezone, timedelta

# ======= CONFIGURATION =======
CSV_FILE = "./data/BTCUSD.csv"
LOG_FILE = "./data/logs/BTCUSD.log"
HISTORICAL_API_URL = "https://api.binance.com/api/v3/klines"
REALTIME_API_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
START_DATE = "2022-01-01"
BATCH_LIMIT = 1000  # Binance API max batch size

# ======= LOGGING CONFIGURATION =======
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def log_and_print(message):
    print(message)
    logging.info(message)

# ======= DATA FETCHING =======

def fetch_with_retries(url, params, max_retries=5):
    """Fetch data from Binance API with retries and exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            log_and_print(f"Attempt {attempt + 1} failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            log_and_print(f"Request failed: {e}")
        time.sleep(2 ** attempt)  # Exponential backoff
    raise Exception("Failed after maximum retries.")

def fetch_historical_data(start_time):
    """Fetch historical BTCUSD data from Binance API in batches."""
    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "startTime": int(start_time.timestamp() * 1000),
        "limit": BATCH_LIMIT
    }
    return fetch_with_retries(HISTORICAL_API_URL, params)

def fetch_current_data():
    """Fetch current BTCUSD real-time data."""
    data = fetch_with_retries(REALTIME_API_URL, {})
    now = datetime.now(timezone.utc)
    return {
        "timestamp": now.replace(microsecond=0).isoformat(),
        "symbol": data.get("symbol", "BTCUSDT"),
        "price": data.get("lastPrice"),
        "open": data.get("openPrice"),
        "high": data.get("highPrice"),
        "low": data.get("lowPrice"),
        "volume": data.get("volume"),
        "quoteVolume": data.get("quoteVolume"),
        "openTime": datetime.fromtimestamp(data.get("openTime", 0) / 1000, tz=timezone.utc).isoformat(),
        "closeTime": datetime.fromtimestamp(data.get("closeTime", 0) / 1000, tz=timezone.utc).isoformat()
    }

# ======= DATA MANAGEMENT =======

def load_existing_data():
    """Load existing data from CSV into a list."""
    data = []
    if not os.path.isfile(CSV_FILE):
        return data
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['timestamp'] = datetime.fromisoformat(row['timestamp']).replace(tzinfo=timezone.utc)
            data.append(row)
    return data

def write_sorted_data(data):
    """Write sorted data back to the CSV."""
    data.sort(key=lambda x: x['timestamp'])
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "timestamp", "symbol", "price", "open", "high", "low", "volume", "quoteVolume", "openTime", "closeTime"
        ])
        writer.writeheader()
        for row in data:
            row['timestamp'] = row['timestamp'].isoformat()
            writer.writerow(row)

def append_realtime_data():
    """Append real-time data directly to CSV."""
    current_data = fetch_current_data()
    if current_data:
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=[
                "timestamp", "symbol", "price", "open", "high", "low", "volume", "quoteVolume", "openTime", "closeTime"
            ])
            if os.stat(CSV_FILE).st_size == 0:  # Write header if file is empty
                writer.writeheader()
            writer.writerow(current_data)
        log_and_print(f"[{datetime.now(timezone.utc).replace(microsecond=0)}] Real-time Data Appended.")

# ======= GAP DETECTION =======

def detect_gaps(data):
    """Detect gaps in the timestamp sequence."""
    gaps = []
    if not data:
        start_time = datetime.fromisoformat(START_DATE).replace(tzinfo=timezone.utc)
        return [(start_time, start_time + timedelta(minutes=BATCH_LIMIT))]

    timestamps = [row['timestamp'] for row in data]
    for i in range(1, len(timestamps)):
        expected_next = timestamps[i - 1] + timedelta(minutes=1)
        if timestamps[i] > expected_next:
            gap_start = expected_next
            gap_end = min(gap_start + timedelta(minutes=BATCH_LIMIT), timestamps[i])
            gaps.append((gap_start, gap_end))
    
    last_timestamp = timestamps[-1]
    now = datetime.now(timezone.utc)
    if last_timestamp + timedelta(minutes=1) < now:
        gap_start = last_timestamp + timedelta(minutes=1)
        gap_end = min(gap_start + timedelta(minutes=BATCH_LIMIT), now)
        gaps.append((gap_start, gap_end))
    
    return gaps

def fill_gaps():
    """Fill detected gaps in historical data."""
    data = load_existing_data()
    gaps = detect_gaps(data)
    
    if not gaps:
        log_and_print("No gaps detected. Historical data is up-to-date.")
        return
    
    for gap_start, gap_end in gaps:
        log_and_print(f"Filling gap: {gap_start} to {gap_end}")
        historical_data = fetch_historical_data(gap_start)
        if historical_data:
            for entry in historical_data:
                data.append({
                    "timestamp": datetime.fromtimestamp(int(entry[0]) / 1000, tz=timezone.utc),
                    "symbol": "BTCUSDT",
                    "price": entry[4],
                    "open": entry[1],
                    "high": entry[2],
                    "low": entry[3],
                    "volume": entry[5],
                    "quoteVolume": entry[7],
                    "openTime": datetime.fromtimestamp(int(entry[0]) / 1000, tz=timezone.utc).isoformat(),
                    "closeTime": datetime.fromtimestamp(int(entry[6]) / 1000, tz=timezone.utc).isoformat()
                })
        else:
            log_and_print(f"Failed to fill gap: {gap_start} to {gap_end}")
    write_sorted_data(data)

# ======= MAIN SCRIPT =======

def main():
    if not os.path.exists(os.path.dirname(CSV_FILE)):
        os.makedirs(os.path.dirname(CSV_FILE))
    fill_gaps()
    append_realtime_data()

def main_scheduler():
    """Schedule BTCUSD data fetching every minute."""
    while True:
        try:
            main()
            time.sleep(60)
        except KeyboardInterrupt:
            log_and_print("Scheduler stopped manually.")
            break
        except Exception as e:
            log_and_print(f"Unexpected error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main_scheduler()
