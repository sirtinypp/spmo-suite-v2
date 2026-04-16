import os
import psycopg2
import sqlite3
from pathlib import Path

# --- Configuration ---
# Source: Postgres (Shared DB)
PG_DB = os.environ.get('DB_NAME', 'db_store')
PG_USER = os.environ.get('DB_USER', 'spmo_admin')
PG_PASS = os.environ.get('DB_PASSWORD', 'secret_password')
PG_HOST = os.environ.get('DB_HOST', 'db')

# Destination: SQLite (Local Branch)
BASE_DIR = Path(__file__).resolve().parent
SQLITE_PATH = BASE_DIR / 'db_expansion.sqlite3'

def bridge():
    print(f"Connecting to Source: {PG_HOST} (Postgres)...")
    pg_conn = psycopg2.connect(dbname=PG_DB, user=PG_USER, password=PG_PASS, host=PG_HOST)
    pg_cur = pg_conn.cursor()

    print(f"Connecting to Destination: {SQLITE_PATH} (SQLite)...")
    sl_conn = sqlite3.connect(SQLITE_PATH)
    sl_cur = sl_conn.cursor()

    # Tables to sync with their expanded field mapping
    tables = [
        ('auth_user', ['id', 'password', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined'], []),
        ('supplies_userprofile', ['id', 'user_id', 'department_id', 'role'], []),
        ('supplies_category', ['id', 'name', 'description'], []),
        ('supplies_department', ['id', 'name', 'description'], []),
        ('supplies_supplier', ['id', 'name', 'contact_person', 'email'], [('is_ps_dbm', 0)]),
        ('supplies_product', ['id', 'name', 'brand', 'item_code', 'supplier_id', 'description', 'price', 'category_id', 'stock', 'unit', 'reorder_point', 'image', 'created_at'], []),
        ('supplies_order', ['id', 'user_id', 'employee_name', 'department_id', 'total_amount', 'remarks', 'created_at', 'approved_at', 'completed_at', 'status'], [('admin_validated', 0), ('chief_approved', 0)]),
    ]

    for table, columns, new_fields in tables:
        print(f"Syncing table: {table}...")
        col_list = ", ".join(columns)
        pg_cur.execute(f"SELECT {col_list} FROM {table}")
        rows = pg_cur.fetchall()
        
        # Prepare the data with new field defaults and type conversion
        final_rows = []
        for row in rows:
            new_row = []
            for val in row:
                # Convert Decimals for SQLite
                if hasattr(val, '__float__') and not isinstance(val, (int, float)):
                    new_row.append(float(val))
                else:
                    new_row.append(val)
            
            for _, default_val in new_fields:
                new_row.append(default_val)
            final_rows.append(tuple(new_row))

        # Update column list for SQLite
        all_cols = columns + [f[0] for f in new_fields]
        all_col_str = ", ".join(all_cols)
        placeholders = ", ".join(["?"] * len(all_cols))
        
        # Clear target (Surgical)
        sl_cur.execute(f"DELETE FROM {table}")
        
        # Insert
        sl_cur.executemany(f"INSERT INTO {table} ({all_col_str}) VALUES ({placeholders})", final_rows)
        print(f"  -> {len(rows)} records synced.")

    sl_conn.commit()
    pg_conn.close()
    sl_conn.close()
    print("Surgical Data Bridge Complete.")

if __name__ == "__main__":
    bridge()
