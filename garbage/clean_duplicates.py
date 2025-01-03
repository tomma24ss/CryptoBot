import csv, os
from datetime import datetime, timezone

CSV_FILE = "./data/BTCUSD.csv"

def clean_duplicates():
    """Remove duplicates from the BTCUSD CSV file based on minute-level timestamps."""
    if not os.path.isfile(CSV_FILE):
        print("CSV file does not exist.")
        return

    cleaned_data = {}
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            timestamp = datetime.fromisoformat(row['timestamp']).replace(second=0, microsecond=0, tzinfo=timezone.utc)
            cleaned_data[timestamp] = row  # Overwrite duplicates with the latest entry

    sorted_data = sorted(cleaned_data.values(), key=lambda x: x['timestamp'])

    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "timestamp", "symbol", "price", "open", "high", "low", "volume", "quoteVolume", "openTime", "closeTime"
        ])
        writer.writeheader()
        for row in sorted_data:
            writer.writerow(row)

    print("Duplicates removed successfully. CSV file cleaned.")

if __name__ == "__main__":
    clean_duplicates()
