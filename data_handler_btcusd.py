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
def fetch_with_retries(url, params=None, max_retries=5):
    """Fetch data from Binance API with retries."""
    params = params or {}
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            log_and_print(f"Attempt {attempt + 1} failed with status {response.status_code}")
        except requests.exceptions.RequestException as e:
            log_and_print(f"Request failed: {e}")
        time.sleep(2 ** attempt)
    raise Exception("Failed after maximum retries.")


def fetch_historical_data(start_time):
    """Fetch historical BTCUSD data from Binance API."""
    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "startTime": int(start_time.timestamp() * 1000),
        "limit": BATCH_LIMIT
    }
    return fetch_with_retries(HISTORICAL_API_URL, params)


def fetch_current_data():
    """Fetch real-time BTCUSD data."""
    data = fetch_with_retries(REALTIME_API_URL)
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)  # Minute-level precision
    return {
        "timestamp": now.isoformat(),
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
    """Load existing data from CSV."""
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
    """Write sorted, deduplicated data to CSV."""
    unique_data = {row['timestamp']: row for row in data}  # Deduplicate by timestamp
    sorted_data = sorted(unique_data.values(), key=lambda x: x['timestamp'])
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "timestamp", "symbol", "price", "open", "high", "low", "volume", "quoteVolume", "openTime", "closeTime"
        ])
        writer.writeheader()
        for row in sorted_data:
            row['timestamp'] = row['timestamp'].isoformat()
            writer.writerow(row)


def get_existing_timestamps():
    """Get a set of existing minute-level timestamps from CSV."""
    if not os.path.isfile(CSV_FILE):
        return set()
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        return {datetime.fromisoformat(row['timestamp']).replace(second=0, microsecond=0) for row in reader}


def append_realtime_data():
    """Append real-time data if it's not a duplicate minute-level entry."""
    current_data = fetch_current_data()
    current_timestamp = datetime.fromisoformat(current_data['timestamp']).replace(tzinfo=timezone.utc)

    existing_timestamps = get_existing_timestamps()

    if current_timestamp in existing_timestamps:
        log_and_print(f"Duplicate detected for minute: {current_timestamp}. Skipping.")
        return

    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "timestamp", "symbol", "price", "open", "high", "low", "volume", "quoteVolume", "openTime", "closeTime"
        ])
        if os.stat(CSV_FILE).st_size == 0:
            writer.writeheader()
        writer.writerow(current_data)

    log_and_print(f"Real-time Data Appended: {current_data['timestamp']}")


# ======= GAP DETECTION AND FILLING =======
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
    return gaps


def fill_gaps():
    """Fill detected gaps in historical data in batches."""
    data = load_existing_data()
    gaps = detect_gaps(data)

    for gap_start, gap_end in gaps:
        current_start = gap_start
        while current_start < gap_end:
            batch_end = min(current_start + timedelta(minutes=BATCH_LIMIT), gap_end)
            log_and_print(f"Fetching batch: {current_start} to {batch_end}")
            historical_data = fetch_historical_data(current_start)
            for entry in historical_data:
                timestamp = datetime.fromtimestamp(int(entry[0]) / 1000, tz=timezone.utc).replace(second=0)
                if timestamp not in [row['timestamp'] for row in data]:
                    data.append({
                        "timestamp": timestamp,
                        "symbol": "BTCUSDT",
                        "price": entry[4],
                        "open": entry[1],
                        "high": entry[2],
                        "low": entry[3],
                        "volume": entry[5],
                        "quoteVolume": entry[7],
                    })
            current_start = batch_end

    write_sorted_data(data)
    log_and_print("Gap filling completed successfully.")


def remove_duplicates():
    """Remove existing duplicates in CSV."""
    data = load_existing_data()
    write_sorted_data(data)
    log_and_print("Duplicates removed successfully.")


# ======= MAIN SCRIPT =======
def main():
    remove_duplicates()
    fill_gaps()
    append_realtime_data()


def main_scheduler():
    while True:
        try:
            main()
            time.sleep(60)
        except KeyboardInterrupt:
            log_and_print("Scheduler stopped manually.")
            break


if __name__ == "__main__":
    main_scheduler()
