import sqlite3
import pandas as pd

def show_all_tables():
    conn = sqlite3.connect('timetable-project.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    tables = cursor.fetchall()
    
    total_records = 0
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        total_records += count
    
    original_tables = ['CoursePlan', 'Rooms', 'UC_Rooms', 'Preferences', 'Week_Frame', 'Service']
    prof_pref_tables = [t[0] for t in tables if t[0].startswith('Prof_')]
    prjt2_tables = [t[0] for t in tables if t[0].startswith('PRJT2_')]
    
    for table in original_tables:
        if table in [t[0] for t in tables]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
    
    for table in prof_pref_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
    
    for table in prjt2_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
    
    conn.close()

def show_sample_data():
    conn = sqlite3.connect('timetable-project.db')
    
    key_tables = [
        'CoursePlan',
        'Rooms', 
        'UC_Rooms',
        'Preferences',
        'Service',
        'Prof_Preferences_v00',
        'PRJT2_CoursePlan',
        'PRJT2_Rooms',
        'PRJT2_Preferences'
    ]
    
    for table in key_tables:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 2", conn)
        except Exception as e:
            pass
    
    conn.close()

if __name__ == "__main__":
    show_all_tables()
    show_sample_data() 