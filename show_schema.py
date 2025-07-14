import sqlite3
import pandas as pd

def show_database_info():
    conn = sqlite3.connect('uctp_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    tables = cursor.fetchall()
    
    print("Database Schema:")
    print("=" * 50)
    
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        print("-" * 30)
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            pk_str = " (PRIMARY KEY)" if pk else ""
            not_null_str = " NOT NULL" if not_null else ""
            print(f"  {col_name}: {col_type}{not_null_str}{pk_str}")
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Rows: {count}")
    
    conn.close()

if __name__ == "__main__":
    show_database_info() 