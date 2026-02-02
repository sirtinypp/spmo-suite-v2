
try:
    with open(r"C:\Users\Aaron\Downloads\SPMO APPCSE (1).csv", "rb") as f:
        raw_data = f.read(500)
        print(f"Raw Bytes Sample: {raw_data[:50]}")
        
    try:
        print("\nTrying UTF-8:")
        print(raw_data.decode('utf-8'))
    except Exception as e:
        print(f"UTF-8 Failed: {e}")

    try:
        print("\nTrying ISO-8859-1:")
        print(raw_data.decode('iso-8859-1'))
    except Exception as e:
        print(f"ISO-8859-1 Failed: {e}")
        
    try:
        print("\nTrying CP1252:")
        print(raw_data.decode('cp1252'))
    except Exception as e:
        print(f"CP1252 Failed: {e}")

except FileNotFoundError:
    print("File not found.")
