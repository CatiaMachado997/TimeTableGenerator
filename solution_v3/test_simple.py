#!/usr/bin/env python3
"""
Simple test script to debug the output writer issue
"""

import os
import sys
import pandas as pd
import sqlite3
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import DatabaseLoader
from heuristic import TimetableHeuristic
from output_writer import OutputWriter

def create_test_database():
    """Create a simple test database"""
    print("Creating test database...")
    
    # Connect to SQLite database
    conn = sqlite3.connect("test_database.db")
    
    try:
        # Create simple test data matching the expected schema
        courses_data = {
            'Course': ['MATH101', 'PHYS101'],
            'Year': [1, 1],
            'Semester': [1, 1],
            'Type': ['T', 'T'],
            'Duration': [2, 2],
            'Class_Group': ['1DA', '1DA'],
            'Professor': ['Prof_A', 'Prof_B'],
            'Value': [1, 1]
        }
        
        rooms_data = {
            'Room ': ['F101', 'F102'],
            'Type': ['Classroom', 'Classroom'],
            'AREA': ['F', 'F']
        }
        
        preferences_data = []
        for prof in ['Prof_A', 'Prof_B']:
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                for timeslot in range(1, 11):
                    preferences_data.append({
                        'Professor': prof,
                        'Day': day,
                        'TimeSlot': timeslot,
                        'Available': 1
                    })
        
        # Create tables
        courses_df = pd.DataFrame(courses_data)
        rooms_df = pd.DataFrame(rooms_data)
        preferences_df = pd.DataFrame(preferences_data)
        preferences_df = preferences_df[['Professor', 'Day', 'TimeSlot', 'Available']]
        
        courses_df.to_sql('Class', conn, if_exists='replace', index=False)
        rooms_df.to_sql('Rooms', conn, if_exists='replace', index=False)
        preferences_df.to_sql('Preferences', conn, if_exists='replace', index=False)
        
        conn.commit()
        print("Test database created successfully")
        
    except Exception as e:
        print(f"Error creating test database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def convert_numpy_timetable_to_dict(timetable_numpy, days, all_periods):
    """Convert numpy timetable to dictionary format expected by output writer, with correct keys."""
    timetable_dict = {}
    for day_idx, day in enumerate(days):
        timetable_dict[day] = {}
        for period in all_periods:
            timetable_dict[day][period] = {}
            period_assignments = timetable_numpy[day_idx, period-1, :]
            assigned_rooms = np.where(period_assignments > 0)[0]
            for room_idx in assigned_rooms:
                course_id = period_assignments[room_idx]
                if course_id > 0:
                    timetable_dict[day][period][f"Room_{room_idx}"] = {
                        'Day': day,
                        'Period': period,
                        'Room': f"Room_{room_idx}",
                        'course_id': str(course_id),
                        'course_name': f"Course_{course_id}",
                        'class_type': 'T',
                        'class_group': '1DA',
                        'professor_id': f"Prof_{course_id}"
                    }
    return timetable_dict

def test_basic_functionality():
    """Test basic functionality"""
    print("\n" + "="*50)
    print("Testing Basic Functionality")
    print("="*50)
    
    # Create test database
    create_test_database()
    
    # Load data
    db_loader = DatabaseLoader("test_database.db")
    db_loader.connect()
    
    courses = db_loader.load_courses()
    rooms = db_loader.load_rooms()
    professors = db_loader.load_professors()
    preferences = db_loader.load_preferences()
    
    print(f"Loaded {len(courses)} courses, {len(rooms)} rooms, {len(professors)} professors")
    
    # Test heuristic
    heuristic = TimetableHeuristic(use_parallel=False, use_simulated_annealing=False)
    result = heuristic.build_timetable(courses, rooms, preferences)
    
    print(f"Timetable built successfully!")
    print(f"Assigned classes: {heuristic.assigned_classes}")
    print(f"Unassigned classes: {heuristic.unassigned_classes}")
    
    # Convert timetable format
    timetable_dict = convert_numpy_timetable_to_dict(
        result['timetable'], 
        heuristic.days, 
        heuristic.all_periods
    )
    
    # Debug: Print timetable structure
    print(f"\nTimetable structure debug:")
    print(f"Days: {list(timetable_dict.keys())}")
    print(f"Periods for Monday: {list(timetable_dict['Monday'].keys())[:5]}...")
    print(f"Assignments for Monday period 1: {timetable_dict['Monday'][1]}")
    print(f"Total assignments found: {sum(len(period) for day in timetable_dict.values() for period in day.values())}")
    
    # Test output writer
    print("\nTesting output writer...")
    output_writer = OutputWriter("test_output")
    
    try:
        # Test detailed report first (simpler)
        detailed_path = output_writer.write_detailed_report(
            timetable_dict, courses, rooms, professors, "test_detailed.xlsx"
        )
        print(f"✅ Detailed report created: {detailed_path}")
        
        # Test main timetable
        timetable_path = output_writer.write_timetable_to_excel(
            timetable_dict, courses, rooms, professors, "test_timetable.xlsx"
        )
        print(f"✅ Main timetable created: {timetable_path}")
        
    except Exception as e:
        print(f"❌ Output writer error: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    db_loader.close()
    
    # Remove test files
    if os.path.exists("test_database.db"):
        os.remove("test_database.db")
    
    print("\nTest completed!")

if __name__ == "__main__":
    import numpy as np
    test_basic_functionality() 