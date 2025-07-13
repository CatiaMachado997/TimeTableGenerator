import pandas as pd
import sqlite3
import os

def create_database():
    conn = sqlite3.connect('timetable-project.db')
    cursor = conn.cursor()
    
    try:
        with open('create_tables.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)
    except Exception as e:
        pass
    
    try:
        df_courseplan = pd.read_excel('dataset/PRJT2_Support_Data_V3.xlsx', sheet_name='CoursePlan')
        df_courseplan.to_sql('CoursePlan', conn, if_exists='replace', index=False)
    except Exception as e:
        pass
    
    try:
        df_rooms = pd.read_excel('dataset/PRJT2_Support_Data_V3.xlsx', sheet_name='Rooms')
        df_rooms.to_sql('Rooms', conn, if_exists='replace', index=False)
    except Exception as e:
        pass
    
    try:
        df_uc_rooms = pd.read_excel('dataset/PRJT2_Support_Data_V3.xlsx', sheet_name='UC_Rooms')
        df_uc_rooms = df_uc_rooms.rename(columns={'Unnamed: 0': 'Class'})
        df_uc_rooms.to_sql('UC_Rooms', conn, if_exists='replace', index=False)
    except Exception as e:
        pass
    
    try:
        df_preferences = pd.read_excel('dataset/PRJT2_Support_Data_V3.xlsx', sheet_name='Preferences')
        preferences_data = []
        for _, row in df_preferences.iterrows():
            professor = row['Professor']
            for col in row.index[1:]:
                if col.startswith(('Mon_', 'Tue_', 'Wed_', 'Thu_', 'Fri_')):
                    day = col.split('_')[0]
                    time_slot = int(col.split('_')[1])
                    available = int(row[col])
                    preferences_data.append({
                        'Professor': professor,
                        'Day': day,
                        'TimeSlot': time_slot,
                        'Available': available
                    })
        df_preferences_normalized = pd.DataFrame(preferences_data)
        df_preferences_normalized.to_sql('Preferences', conn, if_exists='replace', index=False)
    except Exception as e:
        pass
    
    try:
        df_week_frame = pd.read_excel('dataset/PRJT2_Support_Data_V3.xlsx', sheet_name='Week_Frame')
        df_week_frame = df_week_frame.dropna()
        if len(df_week_frame) > 0:
            data_row = df_week_frame.iloc[0]
            if 'Period' in str(data_row.iloc[0]):
                df_week_frame = df_week_frame.iloc[1:].reset_index(drop=True)
            df_week_frame.columns = ['Period', 'Start_Time', 'End_Time'] + [f'Col_{i}' for i in range(len(df_week_frame.columns)-3)]
            df_week_frame = df_week_frame[['Period', 'Start_Time', 'End_Time']]
            df_week_frame.to_sql('Week_Frame', conn, if_exists='replace', index=False)
    except Exception as e:
        pass
    
    try:
        df_service = pd.read_excel('dataset/PRJT2_Support_Data_V3.xlsx', sheet_name='Service')
        df_service.to_sql('Service', conn, if_exists='replace', index=False)
    except Exception as e:
        pass
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database() 