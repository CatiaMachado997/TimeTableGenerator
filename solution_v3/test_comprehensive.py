#!/usr/bin/env python3
"""
Comprehensive test script for the UCTP solver
Tests all aspects: data loading, timetable generation, constraint validation, and output generation
"""

import os
import sys
import pandas as pd
import sqlite3
from pathlib import Path
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import DatabaseLoader
from heuristic import TimetableHeuristic
from output_writer import OutputWriter

def create_realistic_test_database():
    """Create a realistic test database with more courses and better distribution"""
    print("Creating realistic test database...")
    
    # Connect to SQLite database
    conn = sqlite3.connect("test_realistic.db")
    
    try:
        # Create realistic course data with better distribution
        courses_data = {
            'Course': ['MATH101', 'PHYS101', 'CHEM101', 'ENG101', 'CS101', 'MATH201', 'PHYS201', 'ENG201'],
            'Year': [1, 1, 1, 1, 1, 2, 2, 2],
            'Semester': [1, 1, 1, 1, 1, 1, 1, 1],
            'Type': ['T', 'T', 'T', 'T', 'T', 'T', 'T', 'T'],
            'Duration': [2, 2, 2, 2, 2, 2, 2, 2],
            'Class_Group': ['1DA', '1DA', '1DB', '1DB', '1DC', '2DA', '2DA', '2DB'],
            'Professor': ['Prof_A', 'Prof_B', 'Prof_C', 'Prof_D', 'Prof_E', 'Prof_F', 'Prof_G', 'Prof_H'],
            'Value': [1, 1, 1, 1, 1, 1, 1, 1]
        }
        
        rooms_data = {
            'Room ': ['F101', 'F102', 'F103', 'F104', 'F105', 'F106', 'F107', 'F108'],
            'Type': ['Classroom', 'Classroom', 'Lab', 'Classroom', 'Lab', 'Classroom', 'Classroom', 'Lab'],
            'AREA': ['F', 'F', 'F', 'F', 'F', 'F', 'F', 'F']
        }
        
        preferences_data = []
        professors = ['Prof_A', 'Prof_B', 'Prof_C', 'Prof_D', 'Prof_E', 'Prof_F', 'Prof_G', 'Prof_H']
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        for prof in professors:
            for day in days:
                for timeslot in range(1, 21):  # 20 time slots
                    # Create some preference patterns
                    available = 1
                    if day == 'Friday' and timeslot > 15:  # Friday afternoon less preferred
                        available = 0
                    elif day == 'Monday' and timeslot < 5:  # Monday morning preferred
                        available = 1
                    
                    preferences_data.append({
                        'Professor': prof,
                        'Day': day,
                        'TimeSlot': timeslot,
                        'Available': available
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
        print("Realistic test database created successfully")
        
    except Exception as e:
        print(f"Error creating realistic test database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def convert_numpy_timetable_to_dict(timetable_numpy, days, all_periods, courses, rooms):
    """Convert numpy timetable to dictionary format with proper course information"""
    timetable_dict = {}
    
    # Create course lookup
    course_lookup = {course['CourseID']: course for course in courses}
    room_lookup = {room['RoomID']: room for room in rooms}
    
    for day_idx, day in enumerate(days):
        timetable_dict[day] = {}
        for period in all_periods:
            timetable_dict[day][period] = {}
            
            period_assignments = timetable_numpy[day_idx, period-1, :]
            assigned_rooms = []
            for room_idx, course_id in enumerate(period_assignments):
                if course_id is not None:
                    assigned_rooms.append(room_idx)
            
            for room_idx in assigned_rooms:
                course_id = period_assignments[room_idx]
                if course_id is not None:
                    # Find the actual course and room information
                    course = course_lookup.get(str(course_id), {})
                    room = room_lookup.get(f"Room_{room_idx}", {})
                    
                    timetable_dict[day][period][f"Room_{room_idx}"] = {
                        'Day': day,
                        'Period': period,
                        'Room': f"Room_{room_idx}",
                        'course_id': str(course_id),
                        'course_name': course.get('CourseName', f"Course_{course_id}"),
                        'class_type': course.get('ClassType', 'T'),
                        'class_group': course.get('ClassGroup', 'Unknown'),
                        'professor_id': course.get('ProfessorID', f"Prof_{course_id}")
                    }
    
    return timetable_dict

def test_constraint_validation(heuristic, timetable_dict):
    """Test that all hard constraints are being respected"""
    print("\n" + "="*50)
    print("Testing Constraint Validation")
    print("="*50)
    
    # Test 1: No professor conflicts
    professor_assignments = {}
    for day in timetable_dict:
        for period in timetable_dict[day]:
            for room, assignment in timetable_dict[day][period].items():
                prof = assignment['professor_id']
                key = (day, period)
                if key in professor_assignments:
                    if prof in professor_assignments[key]:
                        print(f"❌ Professor conflict: {prof} assigned twice at {day} period {period}")
                        return False
                else:
                    professor_assignments[key] = []
                professor_assignments[key].append(prof)
    
    # Test 2: No room conflicts
    room_assignments = {}
    for day in timetable_dict:
        for period in timetable_dict[day]:
            for room, assignment in timetable_dict[day][period].items():
                key = (day, period)
                if key in room_assignments:
                    if room in room_assignments[key]:
                        print(f"❌ Room conflict: {room} used twice at {day} period {period}")
                        return False
                else:
                    room_assignments[key] = []
                room_assignments[key].append(room)
    
    # Test 3: No class group conflicts
    class_group_assignments = {}
    for day in timetable_dict:
        for period in timetable_dict[day]:
            for room, assignment in timetable_dict[day][period].items():
                class_group = assignment['class_group']
                key = (day, period)
                if key in class_group_assignments:
                    if class_group in class_group_assignments[key]:
                        print(f"❌ Class group conflict: {class_group} has two classes at {day} period {period}")
                        return False
                else:
                    class_group_assignments[key] = []
                class_group_assignments[key].append(class_group)
    
    print("✅ All hard constraints validated successfully!")
    return True

def test_distribution_across_days(timetable_dict):
    """Test that classes are distributed across the week, not just Monday"""
    print("\n" + "="*50)
    print("Testing Distribution Across Days")
    print("="*50)
    
    day_counts = {}
    for day in timetable_dict:
        day_counts[day] = 0
        for period in timetable_dict[day]:
            day_counts[day] += len(timetable_dict[day][period])
    
    print("Assignments per day:")
    for day, count in day_counts.items():
        print(f"  {day}: {count} assignments")
    
    # Check if Monday is overloaded
    monday_count = day_counts.get('Monday', 0)
    total_assignments = sum(day_counts.values())
    
    if total_assignments == 0:
        print("❌ No assignments found!")
        return False
    
    monday_percentage = (monday_count / total_assignments) * 100
    print(f"Monday has {monday_percentage:.1f}% of all assignments")
    
    if monday_percentage > 80:
        print("❌ Monday is overloaded (>80% of assignments)")
        return False
    elif monday_percentage > 60:
        print("⚠️  Monday has high load (>60% of assignments)")
    else:
        print("✅ Good distribution across days")
    
    return True

def test_rest_periods(timetable_dict):
    """Test that rest periods are respected (12:00-12:30 and 19:00-21:00)"""
    print("\n" + "="*50)
    print("Testing Rest Periods")
    print("="*50)
    
    # Define rest periods (these would be periods 9-10 and 19-20 in the 200-period system)
    # For now, let's check if there are any assignments in early periods that might conflict
    rest_period_violations = []
    
    for day in timetable_dict:
        for period in timetable_dict[day]:
            # Check if this period is in a rest period
            if period in [9, 10, 19, 20]:  # Example rest periods
                for room, assignment in timetable_dict[day][period].items():
                    rest_period_violations.append({
                        'day': day,
                        'period': period,
                        'course': assignment['course_name']
                    })
    
    if rest_period_violations:
        print("❌ Rest period violations found:")
        for violation in rest_period_violations:
            print(f"  {violation['course']} assigned to {violation['day']} period {violation['period']}")
        return False
    else:
        print("✅ No rest period violations found")
        return True

def test_output_generation(timetable_dict, courses, rooms, professors):
    """Test that output files can be generated correctly"""
    print("\n" + "="*50)
    print("Testing Output Generation")
    print("="*50)
    
    output_writer = OutputWriter("test_output_comprehensive")
    
    try:
        # Test detailed report
        detailed_path = output_writer.write_detailed_report(
            timetable_dict, courses, rooms, professors, "test_detailed_comprehensive.xlsx"
        )
        print(f"✅ Detailed report created: {detailed_path}")
        
        # Test main timetable
        timetable_path = output_writer.write_timetable_to_excel(
            timetable_dict, courses, rooms, professors, "test_timetable_comprehensive.xlsx"
        )
        print(f"✅ Main timetable created: {timetable_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Output generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all comprehensive tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE UCTP SOLVER TEST")
    print("="*60)
    
    # Create realistic test database
    create_realistic_test_database()
    
    # Load data
    db_loader = DatabaseLoader("test_realistic.db")
    db_loader.connect()
    
    courses = db_loader.load_courses()
    rooms = db_loader.load_rooms()
    professors = db_loader.load_professors()
    preferences = db_loader.load_preferences()
    
    print(f"\nLoaded {len(courses)} courses, {len(rooms)} rooms, {len(professors)} professors")
    
    # Test timetable generation
    print("\n" + "="*50)
    print("Testing Timetable Generation")
    print("="*50)
    
    heuristic = TimetableHeuristic(use_parallel=False, use_simulated_annealing=True)
    result = heuristic.build_timetable(courses, rooms, preferences)
    
    print(f"Timetable built successfully!")
    print(f"Assigned classes: {heuristic.assigned_classes}")
    print(f"Unassigned classes: {heuristic.unassigned_classes}")
    
    # Convert timetable format
    timetable_dict = convert_numpy_timetable_to_dict(
        result['timetable'], 
        heuristic.days, 
        heuristic.all_periods,
        courses,
        rooms
    )
    
    # Debug timetable structure
    print(f"\nTimetable structure:")
    total_assignments = sum(len(period) for day in timetable_dict.values() for period in day.values())
    print(f"Total assignments found: {total_assignments}")
    
    # Run all tests
    tests_passed = 0
    total_tests = 4
    
    if test_constraint_validation(heuristic, timetable_dict):
        tests_passed += 1
    
    if test_distribution_across_days(timetable_dict):
        tests_passed += 1
    
    if test_rest_periods(timetable_dict):
        tests_passed += 1
    
    if test_output_generation(timetable_dict, courses, rooms, professors):
        tests_passed += 1
    
    # Cleanup
    db_loader.close()
    
    # Remove test files
    if os.path.exists("test_realistic.db"):
        os.remove("test_realistic.db")
    
    # Final results
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST RESULTS")
    print("="*60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 