import sqlite3
import pandas as pd

def show_class_table():
    conn = sqlite3.connect('timetable-project.db')
    
    print("=== CLASS TABLE STRUCTURE ===")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Class)")
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        pk_str = " (PRIMARY KEY)" if pk else ""
        not_null_str = " NOT NULL" if not_null else ""
        print(f"  - {col_name}: {col_type}{not_null_str}{pk_str}")
    
    print(f"\nTotal records: {pd.read_sql_query('SELECT COUNT(*) as count FROM Class', conn).iloc[0]['count']}")
    
    print("\n=== SAMPLE DATA ===")
    df = pd.read_sql_query("SELECT * FROM Class LIMIT 10", conn)
    print(df.to_string(index=False))
    
    print("\n=== CLASS GROUPS ===")
    df_groups = pd.read_sql_query("SELECT DISTINCT Class_Group FROM Class ORDER BY Class_Group", conn)
    print(df_groups.to_string(index=False))
    
    print("\n=== YEARS AND REGIMES ===")
    df_summary = pd.read_sql_query("""
        SELECT Year, Regime, COUNT(*) as count 
        FROM Class 
        GROUP BY Year, Regime 
        ORDER BY Year, Regime
    """, conn)
    print(df_summary.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    show_class_table() 