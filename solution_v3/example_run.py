#!/usr/bin/env python3
"""
Example: How to Run UCTP Solver on a New Dataset from Scratch

This script demonstrates the complete workflow for setting up and running
the University Course Timetabling Problem (UCTP) solver on a new dataset.

Prerequisites:
- Python 3.10+
- Required packages: pandas, openpyxl, numpy
- Excel files with course data, room data, and professor preferences

File Structure Expected:
├── data/
│   ├── courses.xlsx          # Course information
│   ├── rooms.xlsx            # Room information  
│   ├── professors.xlsx       # Professor information
│   └── preferences.xlsx      # Professor preferences
├── example_run.py           # This script
├── main.py                  # Main timetabling script
├── db.py                    # Database operations
├── heuristic.py             # Timetabling algorithm
└── output_writer.py         # Output generation
"""

import os
import sys
import pandas as pd
import sqlite3
from pathlib import Path

def create_database_from_excel(data_dir: str, db_path: str = "uctp_database.db"):
    """
    Create SQLite database from Excel files.
    
    Args:
        data_dir: Directory containing Excel files
        db_path: Path for the output SQLite database
    """
    print(f"Creating database from Excel files in {data_dir}...")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    
    try:
        # Read and import course data
        courses_file = os.path.join(data_dir, "courses.xlsx")
        if os.path.exists(courses_file):
            print(f"  Importing courses from {courses_file}")
            courses_df = pd.read_excel(courses_file)
            courses_df.to_sql('Class', conn, if_exists='replace', index=False)
            print(f"    - Imported {len(courses_df)} course records")
        else:
            print(f"  Warning: {courses_file} not found")
        
        # Read and import room data
        rooms_file = os.path.join(data_dir, "rooms.xlsx")
        if os.path.exists(rooms_file):
            print(f"  Importing rooms from {rooms_file}")
            rooms_df = pd.read_excel(rooms_file)
            rooms_df.to_sql('Rooms', conn, if_exists='replace', index=False)
            print(f"    - Imported {len(rooms_df)} room records")
        else:
            print(f"  Warning: {rooms_file} not found")
        
        # Read and import professor preferences
        preferences_file = os.path.join(data_dir, "preferences.xlsx")
        if os.path.exists(preferences_file):
            print(f"  Importing preferences from {preferences_file}")
            preferences_df = pd.read_excel(preferences_file)
            preferences_df.to_sql('Preferences', conn, if_exists='replace', index=False)
            print(f"    - Imported {len(preferences_df)} preference records")
        else:
            print(f"  Warning: {preferences_file} not found")
        
        # Create indexes for better performance
        print("  Creating database indexes...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_class_course ON Class(Course)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_class_professor ON Class(Professor)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_preferences_professor ON Preferences(Professor)")
        
        conn.commit()
        print(f"Database created successfully: {db_path}")
        
    except Exception as e:
        print(f"Error creating database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def create_sample_data(data_dir: str):
    """
    Create sample Excel files for demonstration.
    
    Args:
        data_dir: Directory to create sample files
    """
    print(f"Creating sample data files in {data_dir}...")
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Sample courses data
    courses_data = {
        'Course': ['MATH101', 'PHYS101', 'CHEM101', 'ENG101', 'CS101'],
        'Year': [1, 1, 1, 1, 1],
        'Semester': [1, 1, 1, 1, 1],
        'Type': ['T', 'T', 'T', 'T', 'T'],
        'Duration': [2, 2, 2, 2, 2],
        'Class_Group': ['1DA', '1DA', '1DB', '1DB', '1DC'],
        'Professor': ['Prof_A', 'Prof_B', 'Prof_C', 'Prof_D', 'Prof_E'],
        'Value': [1, 1, 1, 1, 1]
    }
    
    courses_df = pd.DataFrame(courses_data)
    courses_df.to_excel(os.path.join(data_dir, "courses.xlsx"), index=False)
    print(f"  Created courses.xlsx with {len(courses_df)} courses")
    
    # Sample rooms data
    rooms_data = {
        'Room ': ['F101', 'F102', 'F103', 'F104', 'F105'],
        'Type': ['Classroom', 'Classroom', 'Lab', 'Classroom', 'Lab'],
        'AREA': ['F', 'F', 'F', 'F', 'F']
    }
    
    rooms_df = pd.DataFrame(rooms_data)
    rooms_df.to_excel(os.path.join(data_dir, "rooms.xlsx"), index=False)
    print(f"  Created rooms.xlsx with {len(rooms_df)} rooms")
    
    # Sample preferences data
    preferences_data = []
    professors = ['Prof_A', 'Prof_B', 'Prof_C', 'Prof_D', 'Prof_E']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for prof in professors:
        for day in days:
            for timeslot in range(1, 11):  # 10 time slots
                preferences_data.append({
                    'Professor': prof,
                    'Day': day,
                    'TimeSlot': timeslot,
                    'Available': 1  # 1 for available, 0 for unavailable
                })
    
    preferences_df = pd.DataFrame(preferences_data)
    preferences_df.to_excel(os.path.join(data_dir, "preferences.xlsx"), index=False)
    print(f"  Created preferences.xlsx with {len(preferences_df)} preference records")

def validate_data_requirements():
    """
    Validate that all required packages are installed.
    """
    print("Validating requirements...")
    
    required_packages = ['pandas', 'openpyxl', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} (missing)")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("All requirements satisfied!")
    return True

def run_timetabling_solution():
    """
    Run the main timetabling solution.
    """
    print("\n" + "="*60)
    print("Running UCTP Solver...")
    print("="*60)
    
    # Import and run main script
    try:
        # Use subprocess to run main.py to avoid import conflicts
        import subprocess
        import sys
        
        result = subprocess.run([sys.executable, "main.py"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error running main.py: {result.stderr}")
            raise Exception(f"Main script failed with return code {result.returncode}")
            
    except Exception as e:
        print(f"Error running timetabling solution: {e}")
        raise

def main():
    """
    Main function demonstrating the complete workflow.
    """
    print("="*60)
    print("UCTP Solver - Complete Workflow Example")
    print("="*60)
    
    # Step 1: Validate requirements
    if not validate_data_requirements():
        sys.exit(1)
    
    # Step 2: Check if sample data should be created
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"\nData directory '{data_dir}' not found.")
        create_sample = input("Create sample data files? (y/n): ").lower().strip()
        if create_sample == 'y':
            create_sample_data(data_dir)
        else:
            print("Please create your data files manually and run again.")
            sys.exit(1)
    
    # Step 3: Create database from Excel files
    db_path = "uctp_database.db"
    if not os.path.exists(db_path):
        create_database_from_excel(data_dir, db_path)
    else:
        print(f"Database {db_path} already exists.")
        overwrite = input("Overwrite existing database? (y/n): ").lower().strip()
        if overwrite == 'y':
            create_database_from_excel(data_dir, db_path)
    
    # Step 4: Run timetabling solution
    run_timetabling_solution()
    
    print("\n" + "="*60)
    print("Workflow completed successfully!")
    print("="*60)
    print("\nOutput files created in the 'output/' directory:")
    print("- timetable.xlsx: Main timetable")
    print("- detailed_report.xlsx: Detailed assignment report")
    print("- unassigned_courses.csv: Courses that couldn't be assigned (if any)")

if __name__ == "__main__":
    main() 