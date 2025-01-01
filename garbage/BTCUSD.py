import csv
import os
import requests
from datetime import datetime, timezone, timedelta

# Constants
CSV_FILE = "data/BTCUSD.csv"
HISTORICAL_API_URL = "https://api.binance.com/api/v3/klines"
REALTIME_API_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
START_DATE = "2022-01-01"  # Start date for historical data
BATCH_LIMIT = 1000  # Binance API max batch size


def fetch_historical_data(start_time):
    """Fetch historical BTCUSD data from Binance API in batches."""
    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "startTime": int(start_time.timestamp() * 1000),
        "limit": BATCH_LIMIT
    }
    response = requests.get(HISTORICAL_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch historical data starting from {start_time}.")
        return None


def fetch_current_data():
    """Fetch current BTCUSD detailed data."""
    response = requests.get(REALTIME_API_URL)
    if response.status_code == 200:
        data = response.json()
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
            "openTime": datetime.fromtimestamp(data.get("openTime", 0) / 1000, tz=timezone.utc).replace(microsecond=0).isoformat(),
            "closeTime": datetime.fromtimestamp(data.get("closeTime", 0) / 1000, tz=timezone.utc).replace(microsecond=0).isoformat()
        }
    else:
        print("Failed to fetch real-time data.")
        return None


def load_existing_data():
    """Load existing data from CSV and return all rows as a list of dictionaries."""
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
            break
    
    if not gaps:
        last_timestamp = timestamps[-1]
        now = datetime.now(timezone.utc)
        if last_timestamp + timedelta(minutes=1) < now:
            gap_start = last_timestamp + timedelta(minutes=1)
            gap_end = min(gap_start + timedelta(minutes=BATCH_LIMIT), now)
            gaps.append((gap_start, gap_end))
    
    return gaps


def fill_gaps():
    """Fill detected gaps in historical data and maintain order."""
    data = load_existing_data()
    gaps = detect_gaps(data)
    
    if not gaps:
        print("No gaps detected. Historical data is up-to-date.")
        return
    
    gap_start, gap_end = gaps[0]
    print(f"Filling historical data gap from {gap_start} to {gap_end}.")
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
        write_sorted_data(data)
        print(f"Filled historical data up to: {gap_end}")
    else:
        print("Failed to fill historical gap. Retrying in the next run.")


def update_realtime_data():
    data = load_existing_data()
    current_data = fetch_current_data()
    if current_data:
        current_data['timestamp'] = datetime.fromisoformat(current_data['timestamp'])
        data.append(current_data)
        write_sorted_data(data)
        print(f"[{datetime.now(timezone.utc).replace(microsecond=0)}] Real-time Data Written: {current_data}")


def main():
    if not os.path.exists(os.path.dirname(CSV_FILE)):
        os.makedirs(os.path.dirname(CSV_FILE))
    fill_gaps()
    update_realtime_data()


if __name__ == "__main__":
    main()
