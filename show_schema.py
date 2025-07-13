import sqlite3
import pandas as pd

def show_database_info():
    conn = sqlite3.connect('timetable-project.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            pk_str = " (PRIMARY KEY)" if pk else ""
            not_null_str = " NOT NULL" if not_null else ""
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 3", conn)
    
    conn.close()

if __name__ == "__main__":
    show_database_info() 