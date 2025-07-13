import sqlite3
import pandas as pd

def load_all_data(db_path="timetable-project.db"):
    conn = sqlite3.connect(db_path)
    data = {}
    data['courseplan'] = pd.read_sql_query("SELECT * FROM CoursePlan", conn)
    data['rooms'] = pd.read_sql_query("SELECT * FROM Rooms", conn)
    data['uc_rooms'] = pd.read_sql_query("SELECT * FROM UC_Rooms", conn)
    data['preferences'] = pd.read_sql_query("SELECT * FROM Preferences", conn)
    data['service'] = pd.read_sql_query("SELECT * FROM Service", conn)
    data['class'] = pd.read_sql_query("SELECT * FROM Class", conn)
    data['week_frame'] = pd.read_sql_query("SELECT * FROM Week_Frame", conn)
    
    # Remove duplicates from preferences table
    data['preferences'] = data['preferences'].drop_duplicates()
    print(f"Removed {63772 - len(data['preferences'])} duplicate preference entries")
    
    conn.close()
    return data 