import pandas as pd
import sqlite3
import os

def import_prof_preferences():
    conn = sqlite3.connect('timetable-project.db')
    cursor = conn.cursor()
    
    file_path = 'dataset/Prof_preferences_v00.xlsx'
    if not os.path.exists(file_path):
        return
    
    try:
        excel_file = pd.ExcelFile(file_path)
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            if 'Professor' in df.columns:
                preferences_data = []
                for _, row in df.iterrows():
                    professor = row['Professor']
                    for col in row.index[1:]:
                        if col.startswith(('Mon_', 'Tue_', 'Wed_', 'Thu_', 'Fri_')):
                            day = col.split('_')[0]
                            time_slot = int(col.split('_')[1])
                            available = int(row[col]) if pd.notna(row[col]) else 0
                            preferences_data.append({
                                'Professor': professor,
                                'Day': day,
                                'TimeSlot': time_slot,
                                'Available': available
                            })
                
                df_preferences_normalized = pd.DataFrame(preferences_data)
                df_preferences_normalized.to_sql('Prof_Preferences_v00', conn, if_exists='replace', index=False)
                
                try:
                    df_preferences_normalized.to_sql('Preferences', conn, if_exists='append', index=False)
                except Exception as e:
                    pass
                
            else:
                table_name = f"Prof_Pref_{sheet_name}"
                
                columns = []
                for col in df.columns:
                    col_type = 'TEXT'
                    if df[col].dtype == 'int64':
                        col_type = 'INTEGER'
                    elif df[col].dtype == 'float64':
                        col_type = 'REAL'
                    columns.append(f"{col} {col_type}")
                
                create_sql = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        {', '.join(columns)}
                    )
                '''
                cursor.execute(create_sql)
                
                df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
    
    finally:
        conn.close()

def show_imported_data():
    conn = sqlite3.connect('timetable-project.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Prof_Pref%'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 3", conn)
    
    conn.close()

if __name__ == "__main__":
    import_prof_preferences()
    show_imported_data() 