import os
import psycopg2

try:
    conn = psycopg2.connect(
        dbname='db_gfa',
        user='spmo_admin',
        password='secret_password',
        host='127.0.0.1',
        port='5432'
    )
    print("SUCCESS: Connected to db_gfa")
    conn.close()
except Exception as e:
    print(f"FAILURE: {e}")
