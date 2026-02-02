import csv

csv_path = r"C:\Users\Aaron\Downloads\SPMO APPCSE (1).csv"

try:
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 60: # Target the line with MULTIMEDIA PROJECTOR
                print(f"Row {i} Data:")
                for idx, val in enumerate(row):
                    print(f"[{idx}] {val}")
                break
except Exception as e:
    print(f"Error: {e}")
