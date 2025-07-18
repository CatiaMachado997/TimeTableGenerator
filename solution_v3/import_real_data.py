#!/usr/bin/env python3
"""
Import Real Dataset Script
TimeTableGenerator - University Course Timetabling Problem (UCTP) Solver

This script imports the real dataset from the dataset folder into the database
with the correct format for the TimeTableGenerator algorithm.
"""

import pandas as pd
import sqlite3
import os
import sys
from typing import Dict, List

def import_real_data(db_path: str = "uctp_database.db"):
    """Import real dataset into the database"""
    
    print("=" * 60)
    print("TimeTableGenerator - Real Data Import")
    print("University Course Timetabling Problem (UCTP) Solver")
    print("=" * 60)
    
    # Check if dataset files exist
    courses_file = "../dataset/PRJT2_Support_Data_V3.xlsx"
    preferences_file = "../dataset/Prof_preferences_v00.xlsx"
    
    if not os.path.exists(courses_file):
        print(f"❌ Error: Course data file not found: {courses_file}")
        return False
    
    if not os.path.exists(preferences_file):
        print(f"❌ Error: Preferences file not found: {preferences_file}")
        return False
    
    try:
        # Connect to database
        print(f"\n1. Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        print("2. Clearing existing data...")
        cursor.execute("DELETE FROM Class")
        cursor.execute("DELETE FROM Preferences")
        cursor.execute("DELETE FROM Rooms")
        
        # Import course data
        print("3. Importing course data...")
        courses_df = pd.read_excel(courses_file)
        print(f"   - Loaded {len(courses_df)} course records")
        
        # Process courses and create individual class records
        class_records = []
        for _, row in courses_df.iterrows():
            course = row['Course']
            class_name = row['Class']
            year = row['Year']
            semester = row['Semester']
            
            # Create records for each class type (T, TP, PL)
            t_value = row.get('T', None)
            if t_value is not None and pd.notna(t_value) and float(t_value) > 0:
                class_records.append({
                    'Degree': 'MEGI',
                    'Year': year,
                    'Semester': semester,
                    'Course': f"{course}_{class_name}_T",
                    'Regime': 'D',
                    'Language': 'PT',
                    'Type': 'T',
                    'Duration': int(t_value),
                    'Professor': f"Prof_{course}_{class_name}_T",
                    'Class_Group': f"{year}D{chr(65 + len([r for r in class_records if r['Year'] == year and r['Type'] == 'T']))}",
                    'Value': 1.0
                })
            
            tp_value = row.get('TP', None)
            if tp_value is not None and pd.notna(tp_value) and float(tp_value) > 0:
                class_records.append({
                    'Degree': 'MEGI',
                    'Year': year,
                    'Semester': semester,
                    'Course': f"{course}_{class_name}_TP",
                    'Regime': 'D',
                    'Language': 'PT',
                    'Type': 'TP',
                    'Duration': int(tp_value),
                    'Professor': f"Prof_{course}_{class_name}_TP",
                    'Class_Group': f"{year}D{chr(65 + len([r for r in class_records if r['Year'] == year and r['Type'] == 'TP']))}",
                    'Value': 1.0
                })
            
            pl_value = row.get('PL', None)
            if pl_value is not None and pd.notna(pl_value) and float(pl_value) > 0:
                class_records.append({
                    'Degree': 'MEGI',
                    'Year': year,
                    'Semester': semester,
                    'Course': f"{course}_{class_name}_PL",
                    'Regime': 'D',
                    'Language': 'PT',
                    'Type': 'PL',
                    'Duration': int(pl_value),
                    'Professor': f"Prof_{course}_{class_name}_PL",
                    'Class_Group': f"{year}D{chr(65 + len([r for r in class_records if r['Year'] == year and r['Type'] == 'PL']))}",
                    'Value': 1.0
                })
        
        print(f"   - Created {len(class_records)} class records")
        
        # Insert class records
        for record in class_records:
            cursor.execute("""
                INSERT INTO Class (Degree, Year, Semester, Course, Regime, Language, Type, Duration, Professor, Class_Group, Value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (record['Degree'], record['Year'], record['Semester'], record['Course'], 
                  record['Regime'], record['Language'], record['Type'], record['Duration'], 
                  record['Professor'], record['Class_Group'], record['Value']))
        
        # Import preferences data
        print("4. Importing professor preferences...")
        preferences_df = pd.read_excel(preferences_file)
        print(f"   - Loaded {len(preferences_df)} professor records")
        
        # Convert wide format to long format
        preference_records = []
        for _, row in preferences_df.iterrows():
            professor = row['Professor']
            
            # Process each day
            for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
                day_name = {'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 
                           'Thu': 'Thursday', 'Fri': 'Friday'}[day]
                
                # Process each period (1-30)
                for period in range(1, 31):
                    column = f"{day}_{period}"
                    if column in row:
                        cell_value = row.get(column, None)
                        if cell_value is not None and pd.notna(cell_value):
                            available = int(cell_value)
                        else:
                            available = 0
                        preference_records.append({
                            'Professor': professor,
                            'Day': day_name,
                            'TimeSlot': period,
                            'Available': available
                        })
        
        print(f"   - Created {len(preference_records)} preference records")
        
        # Insert preference records
        for record in preference_records:
            cursor.execute("""
                INSERT INTO Preferences (Professor, Day, TimeSlot, Available)
                VALUES (?, ?, ?, ?)
            """, (record['Professor'], record['Day'], record['TimeSlot'], record['Available']))
        
        # Create room data (since it's not in the dataset, create default rooms)
        print("5. Creating room data...")
        rooms = []
        for i in range(1, 21):  # Create 20 rooms
            rooms.append({
                'Room': f'F{i:02d}',
                'Type': 'Classroom',
                'AREA': 'F'
            })
        
        for room in rooms:
            cursor.execute("""
                INSERT INTO Rooms (Room, Type, AREA)
                VALUES (?, ?, ?)
            """, (room['Room'], room['Type'], room['AREA']))
        
        print(f"   - Created {len(rooms)} room records")
        
        # Commit and close
        conn.commit()
        conn.close()
        
        # Verify import
        print("\n6. Verifying import...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Class WHERE Value > 0")
        class_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Preferences")
        pref_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Rooms")
        room_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT Professor) FROM Class WHERE Value > 0")
        prof_count = cursor.fetchone()[0]
        
        print(f"   ✅ Classes imported: {class_count}")
        print(f"   ✅ Preferences imported: {pref_count}")
        print(f"   ✅ Rooms created: {room_count}")
        print(f"   ✅ Professors: {prof_count}")
        
        conn.close()
        
        print(f"\n✅ Real data import completed successfully!")
        print(f"\nNext steps:")
        print(f"1. Run the timetabling solution: python main.py")
        print(f"2. Check the generated output files in output/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print('[DEBUG] ENTERED main()')
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "uctp_database.db"
    
    success = import_real_data(db_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 