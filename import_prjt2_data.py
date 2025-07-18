import pandas as pd
import sqlite3
import os

def import_prjt2_data():
    print("Starting PRJT2 data import...")
    conn = sqlite3.connect('uctp_database.db')
    cursor = conn.cursor()
    
    file_path = 'dataset/PRJT2_Support_Data_V3.xlsx'
    print(f"Looking for file: {file_path}")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    print(f"File found, proceeding with import...")
    
    try:
        excel_file = pd.ExcelFile(file_path)
        print(f"Excel file sheets: {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            print(f"Processing sheet: {sheet_name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"  Sheet shape: {df.shape}")
            
            table_name = f"PRJT2_{sheet_name.replace(' ', '_').replace('-', '_')}"
            
            if sheet_name == 'CoursePlan':
                print(f"  Importing to PRJT2_CoursePlan...")
                df.to_sql('PRJT2_CoursePlan', conn, if_exists='replace', index=False)
                print(f"  Imported {len(df)} rows to PRJT2_CoursePlan")
                
            elif sheet_name == 'Rooms':
                print(f"  Importing to PRJT2_Rooms...")
                df.to_sql('PRJT2_Rooms', conn, if_exists='replace', index=False)
                print(f"  Imported {len(df)} rows to PRJT2_Rooms")
                
            elif sheet_name == 'UC_Rooms':
                print(f"  Importing to PRJT2_UC_Rooms...")
                df = df.rename(columns={'Unnamed: 0': 'Class'})
                df.to_sql('PRJT2_UC_Rooms', conn, if_exists='replace', index=False)
                print(f"  Imported {len(df)} rows to PRJT2_UC_Rooms")
                
            elif sheet_name == 'Preferences':
                print(f"  Processing preferences...")
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
                df_preferences_normalized.to_sql('PRJT2_Preferences', conn, if_exists='replace', index=False)
                print(f"  Imported {len(df_preferences_normalized)} preference rows")
                
            elif sheet_name == 'Week_Frame':
                print(f"  Processing week frame...")
                df_clean = df.dropna()
                if len(df_clean) > 0:
                    data_row = df_clean.iloc[0]
                    if 'Period' in str(data_row.iloc[0]):
                        df_clean = df_clean.iloc[1:].reset_index(drop=True)
                    
                    df_clean.columns = ['Period', 'Start_Time', 'End_Time'] + [f'Col_{i}' for i in range(len(df_clean.columns)-3)]
                    df_clean = df_clean[['Period', 'Start_Time', 'End_Time']]
                    df_clean.to_sql('PRJT2_Week_Frame', conn, if_exists='replace', index=False)
                    print(f"  Imported {len(df_clean)} week frame rows")
                    
            elif sheet_name == 'Service':
                print(f"  Importing to PRJT2_Service...")
                df.to_sql('PRJT2_Service', conn, if_exists='replace', index=False)
                print(f"  Imported {len(df)} rows to PRJT2_Service")
                
            elif sheet_name.startswith('L-'):
                print(f"  Processing class data from {sheet_name}...")
                class_data = []
                for _, row in df.iterrows():
                    base_data = {
                        'Degree': row['Degree'],
                        'Year': row['Year'],
                        'Semester': row['Semester'],
                        'Course': row['Course'],
                        'Regime': row['Regime'],
                        'Language': row['Language'],
                        'Type': row['Type'],
                        'Duration': row['Duration'],
                        'Professor': row['Professor']
                    }
                    
                    for col in row.index[9:]:
                        if pd.notna(row[col]) and row[col] is not None:
                            class_data.append({
                                **base_data,
                                'Class_Group': col,
                                'Value': float(row[col]) if pd.notna(row[col]) else None
                            })
                
                if class_data:
                    df_class = pd.DataFrame(class_data)
                    df_class.to_sql('Class', conn, if_exists='append', index=False)
                    print(f"  Imported {len(df_class)} class rows")
                else:
                    print(f"  No class data found in {sheet_name}")
                
            elif sheet_name in ['Output Example', 'Output Template']:
                print(f"  Importing to {table_name}...")
                df.to_sql(f'PRJT2_{sheet_name.replace(" ", "_")}', conn, if_exists='replace', index=False)
                print(f"  Imported {len(df)} rows to {table_name}")
                
            else:
                print(f"  Importing to generic table {table_name}...")
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
                print(f"  Imported {len(df)} rows to {table_name}")
        
        conn.commit()
        print("Import completed successfully!")
        
    except Exception as e:
        print(f"Error during import: {e}")
        conn.rollback()
    
    finally:
        conn.close()

def show_imported_data():
    conn = sqlite3.connect('uctp_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'PRJT2%'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 3", conn)
    
    cursor.execute("SELECT COUNT(*) FROM Class")
    class_count = cursor.fetchone()[0]
    
    conn.close()

if __name__ == "__main__":
    import_prjt2_data()
    show_imported_data() 