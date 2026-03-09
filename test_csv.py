
import tablib
from import_export.formats import base_formats

class SaneCSV(base_formats.CSV):
    def create_dataset(self, in_stream, **kwargs):
        if isinstance(in_stream, bytes):
            raw_bytes = in_stream
        elif hasattr(in_stream, 'read'):
            raw_bytes = in_stream.read()
            if hasattr(in_stream, 'seek'):
                in_stream.seek(0)
        else:
            print(f"DEBUG: Not bytes/stream: {type(in_stream)}")
            return super().create_dataset(in_stream, **kwargs)

        results = []
        for encoding in ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1'):
            try:
                decoded = raw_bytes.decode(encoding)
                print(f"TEST: Decoded with {encoding}")
                dataset = tablib.Dataset()
                dataset.csv = decoded
                return dataset
            except Exception as e:
                print(f"TEST: Failed {encoding}: {e}")
                continue
        return None

if __name__ == "__main__":
    import os
    file_path = '/tmp/repro.csv'
    if not os.path.exists(file_path):
        print("FAIL: /tmp/repro.csv not found")
        exit(1)
        
    with open(file_path, 'rb') as f:
        data = f.read()
        
    fmt = SaneCSV()
    ds = fmt.create_dataset(data)
    if ds:
        print(f"SUCCESS: Loaded {len(ds)} rows")
        print(f"Headers: {ds.headers}")
    else:
        print("FAIL: All encodings failed")
