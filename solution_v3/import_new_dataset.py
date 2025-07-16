#!/usr/bin/env python3
"""
Import New Dataset Script
TimeTableGenerator - University Course Timetabling Problem (UCTP) Solver

This script imports a new dataset with the same structure as the original
but different data. You can specify custom file paths for courses and preferences.
"""

import pandas as pd
import sqlite3
import os
import sys
from typing import Dict, List

def import_new_dataset(courses_file: str, preferences_file: str, db_path: str = "uctp_database.db"):
    """Import new dataset into the database"""
    
    print("=" * 60)
    print("TimeTableGenerator - New Dataset Import")
    print("University Course Timetabling Problem (UCTP) Solver")
    print("=" * 60)
    
    # Check if dataset files exist
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
        
        # Validate course data structure
        required_columns = ['Course', 'Class', 'Year', 'Semester', 'T', 'TP', 'PL']
        missing_columns = [col for col in required_columns if col not in courses_df.columns]
        if missing_columns:
            print(f"❌ Error: Missing required columns in courses file: {missing_columns}")
            return False
        
        # Process courses and create individual class records
        class_records = []
        for _, row in courses_df.iterrows():
            course = row['Course']
            class_name = row['Class']
            year = row['Year']
            semester = row['Semester']
            
            # Create records for each class type (T, TP, PL)
            if pd.notna(row['T']) and float(row['T']) > 0:
                class_records.append({
                    'Degree': 'MEGI',
                    'Year': year,
                    'Semester': semester,
                    'Course': f"{course}_{class_name}_T",
                    'Regime': 'D',
                    'Language': 'PT',
                    'Type': 'T',
                    'Duration': int(row['T']),
                    'Professor': f"Prof_{course}_{class_name}_T",
                    'Class_Group': f"{year}D{chr(65 + len([r for r in class_records if r['Year'] == year and r['Type'] == 'T']))}",
                    'Value': 1.0
                })
            
            if pd.notna(row['TP']) and float(row['TP']) > 0:
                class_records.append({
                    'Degree': 'MEGI',
                    'Year': year,
                    'Semester': semester,
                    'Course': f"{course}_{class_name}_TP",
                    'Regime': 'D',
                    'Language': 'PT',
                    'Type': 'TP',
                    'Duration': int(row['TP']),
                    'Professor': f"Prof_{course}_{class_name}_TP",
                    'Class_Group': f"{year}D{chr(65 + len([r for r in class_records if r['Year'] == year and r['Type'] == 'TP']))}",
                    'Value': 1.0
                })
            
            if pd.notna(row['PL']) and float(row['PL']) > 0:
                class_records.append({
                    'Degree': 'MEGI',
                    'Year': year,
                    'Semester': semester,
                    'Course': f"{course}_{class_name}_PL",
                    'Regime': 'D',
                    'Language': 'PT',
                    'Type': 'PL',
                    'Duration': int(row['PL']),
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
        
        # Validate preferences data structure
        if 'Professor' not in preferences_df.columns:
            print("❌ Error: Missing 'Professor' column in preferences file")
            return False
        
        # Check for day_period columns
        expected_columns = ['Professor']
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
            for period in range(1, 31):
                expected_columns.append(f"{day}_{period}")
        
        missing_pref_columns = [col for col in expected_columns if col not in preferences_df.columns]
        if len(missing_pref_columns) > 1:  # Allow missing some columns
            print(f"⚠️  Warning: Some preference columns missing: {missing_pref_columns[:5]}...")
        
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
                        available = int(row[column]) if pd.notna(row[column]) and row[column] is not None else 0
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
        
        # Show year distribution
        cursor.execute("SELECT Year, COUNT(*) as courses, SUM(Duration) as periods FROM Class WHERE Value > 0 GROUP BY Year ORDER BY Year")
        year_stats = cursor.fetchall()
        print(f"\n   📊 Year Distribution:")
        for year, courses, periods in year_stats:
            print(f"      Year {year}: {courses} courses, {periods} periods")
        
        conn.close()
        
        print(f"\n✅ New dataset import completed successfully!")
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
    if len(sys.argv) < 3:
        print("Usage: python import_new_dataset.py <courses_file> <preferences_file> [database_file]")
        print("\nExample:")
        print("  python import_new_dataset.py ../dataset/new_courses.xlsx ../dataset/new_preferences.xlsx")
        print("  python import_new_dataset.py ../dataset/new_courses.xlsx ../dataset/new_preferences.xlsx new_database.db")
        sys.exit(1)
    
    courses_file = sys.argv[1]
    preferences_file = sys.argv[2]
    db_path = sys.argv[3] if len(sys.argv) > 3 else "uctp_database.db"
    
    success = import_new_dataset(courses_file, preferences_file, db_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 