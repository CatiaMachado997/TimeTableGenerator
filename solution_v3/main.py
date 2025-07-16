#!/usr/bin/env python3
"""
University Course Timetabling Problem (UCTP) Solver
Mechanical Engineering Department (DEM) - ISEP

This script implements a heuristic approach to solve the UCTP with:
- 30 periods per day (1-10 morning, 11-20 afternoon, 21-30 night)
- Hard constraints: no double-booking, room type matching, consecutive periods
- Soft constraints: professor preferences, year-based period preferences
- Class group constraints: 'D' classes use morning/afternoon, 'N' classes use night only
"""

import os
import sys
import time
from db import DatabaseLoader
from heuristic import TimetableHeuristic
from output_writer import OutputWriter
import numpy as np

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

def main():
    """Main function to run the timetabling solution"""
    
    print("=" * 60)
    print("University Course Timetabling Problem (UCTP) Solver")
    print("Mechanical Engineering Department (DEM) - ISEP")
    print("=" * 60)
    
    # Configuration
    db_path = "uctp_database.db"  # Path to the database
    output_dir = "output"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        print("Please ensure the database file exists in the parent directory.")
        sys.exit(1)
    
    try:
        # Initialize components
        print("\n1. Initializing database connection...")
        db_loader = DatabaseLoader(db_path)
        db_loader.connect()
        
        print("2. Loading data from database...")
        courses = db_loader.load_courses()
        rooms = db_loader.load_rooms()
        professors = db_loader.load_professors()
        preferences = db_loader.load_preferences()
        class_groups = db_loader.load_class_groups()
        
        print(f"   - Loaded {len(courses)} courses")
        print(f"   - Loaded {len(rooms)} rooms")
        print(f"   - Loaded {len(professors)} professors")
        print(f"   - Loaded {len(preferences)} preferences")
        print(f"   - Loaded {len(class_groups)} class groups")
        
        # Analyze data
        print("\n3. Analyzing data...")
        total_periods_needed = sum(course['Periods'] for course in courses)
        
        # Get actual periods from heuristic
        heuristic = TimetableHeuristic()
        total_available_slots = 5 * len(heuristic.all_periods)  # 5 days * 30 periods
        
        print(f"   - Total periods needed: {total_periods_needed}")
        print(f"   - Total available slots: {total_available_slots}")
        print(f"   - Theoretical capacity: {total_periods_needed / total_available_slots:.2f} courses per slot")
        
        # Class group analysis
        print("\n4. Class group analysis:")
        for group in class_groups:
            group_courses = [c for c in courses if c['ClassGroup'] == group['ClassGroup']]
            group_periods = sum(c['Periods'] for c in group_courses)
            print(f"   - {group['ClassGroup']}: {len(group_courses)} courses, {group_periods} periods")
        
        # Period structure analysis
        print("\n5. Period structure:")
        print(f"   - Morning periods: 1-{len(heuristic.morning_periods)} (8:00-12:00)")
        print(f"   - Afternoon periods: {heuristic.afternoon_periods[0]}-{heuristic.afternoon_periods[-1]} (13:00-17:00)")
        print(f"   - Night periods: {heuristic.night_periods[0]}-{heuristic.night_periods[-1]} (18:00-22:00)")
        
        # Class type analysis
        day_classes = [c for c in courses if len(c['ClassGroup']) >= 2 and c['ClassGroup'][1] == 'D']
        night_classes = [c for c in courses if len(c['ClassGroup']) >= 2 and c['ClassGroup'][1] == 'N']
        other_classes = [c for c in courses if len(c['ClassGroup']) < 2 or (c['ClassGroup'][1] != 'D' and c['ClassGroup'][1] != 'N')]
        
        print(f"   - Day classes (D): {len(day_classes)}")
        print(f"   - Night classes (N): {len(night_classes)}")
        print(f"   - Other classes: {len(other_classes)}")
        
        # Build timetable
        print("\n6. Building timetable...")
        # OPTIMIZATION: Use advanced heuristic with optimized sequential processing and simulated annealing
        heuristic = TimetableHeuristic(use_parallel=False, use_simulated_annealing=True)
        result = heuristic.build_timetable(courses, rooms, preferences)
        
        timetable_numpy = result['timetable']
        assigned_classes = result['assigned_classes']
        unassigned_classes = result['unassigned_classes']
        unassigned_courses = result['unassigned_courses']
        
        # Convert timetable to dictionary format for output writer
        timetable_dict = convert_numpy_timetable_to_dict(
            timetable_numpy, heuristic.days, heuristic.all_periods, courses, rooms
        )
        
        # Generate output
        print("\n7. Generating output files...")
        output_writer = OutputWriter(output_dir)
        
        # Write main timetable (includes individual class group sheets)
        timetable_path = output_writer.write_timetable_to_excel(
            timetable_dict, courses, rooms, professors, "timetable.xlsx"
        )
        
        # Write unassigned courses report
        if unassigned_courses:
            unassigned_path = output_writer.write_unassigned_report(
                unassigned_courses, "unassigned_courses.csv"
            )
        
        # Write detailed report
        detailed_path = output_writer.write_detailed_report(
            timetable_dict, courses, rooms, professors, "detailed_report.xlsx"
        )
        
        # Print final statistics
        print("\n8. Final Statistics:")
        # Get heuristic statistics
        stats = heuristic.get_statistics()
        assigned_classes = stats.get('assigned_classes', 0)
        unassigned_classes = stats.get('unassigned_classes', 0)
        total_courses = assigned_classes + unassigned_classes
        assignment_rate = (assigned_classes / total_courses * 100) if total_courses > 0 else 0
        
        # Performance metrics
        perf_metrics = stats.get('performance_metrics', {})
        processing_time = result.get('processing_time', 0)
        
        print(f"   - Total period assignments: {stats['total_assignments']}")
        print(f"   - Unique courses assigned: {stats['unique_courses']}")
        print(f"   - Assigned classes: {assigned_classes}")
        print(f"   - Unassigned classes: {unassigned_classes}")
        print(f"   - Assignment rate: {assignment_rate:.2f}%")
        print(f"   - Professors with assignments: {stats['professor_assignments']}")
        print(f"   - Rooms used: {stats['room_assignments']}")
        print(f"   - Class groups scheduled: {stats['class_group_assignments']}")
        
        # Performance analysis
        print(f"\n   Performance Analysis:")
        print(f"   - Processing time: {processing_time:.2f} seconds")
        print(f"   - Constraint checks: {perf_metrics.get('constraint_checks', 0):,}")
        print(f"   - Assignment attempts: {perf_metrics.get('assignment_attempts', 0):,}")
        print(f"   - Checks per attempt: {perf_metrics.get('checks_per_attempt', 0):.2f}")
        print(f"   - Efficiency: {perf_metrics.get('assignment_attempts', 0) / max(1, processing_time):.0f} attempts/second")
        
        # Advanced optimization metrics
        print(f"\n   Advanced Optimization Metrics:")
        print(f"   - Parallel assignments: {perf_metrics.get('parallel_assignments', 0)}")
        print(f"   - Annealing iterations: {perf_metrics.get('annealing_iterations', 0)}")
        print(f"   - Cache hit rate: {perf_metrics.get('cache_hit_rate', 0):.1f}%")
        print(f"   - Memory efficiency: Using numpy arrays and bitmasks")
        print(f"   - Parallel workers: {heuristic.max_workers}")
        
        # Check for potential issues
        if stats['total_assignments'] > 150:
            print(f"   ⚠️  Warning: {stats['total_assignments']} period assignments exceed 150 available slots!")
            print(f"      This suggests multiple assignments to the same time slots.")
        
        if stats['unique_courses'] != assigned_classes:
            print(f"   ⚠️  Warning: Unique courses assigned ({stats['unique_courses']}) does not match assigned classes ({assigned_classes})!")
            
        # Validate constraints
        print("\n9. Validating hard constraints...")
        violations = heuristic.validate_constraints()
        
        # Check for overlapping assignments
        overlaps = heuristic.check_overlapping_assignments()
        
        total_violations = (len(violations['professor_conflicts']) + 
                          len(violations['room_conflicts']) + 
                          len(violations['class_group_conflicts']))
        
        if total_violations == 0 and len(overlaps) == 0:
            print("   ✅ All hard constraints are satisfied!")
        else:
            print(f"   ❌ Found constraint violations:")
            print(f"      - Professor conflicts: {len(violations['professor_conflicts'])}")
            print(f"      - Room conflicts: {len(violations['room_conflicts'])}")
            print(f"      - Class group conflicts: {len(violations['class_group_conflicts'])}")
            print(f"      - Overlapping assignments: {len(overlaps)}")
            
            if overlaps:
                print(f"\n   Example overlapping assignment:")
                overlap = overlaps[0]
                print(f"      {overlap['day']} Period {overlap['period']}: {overlap['count']} assignments")
                for i, assignment in enumerate(overlap['assignments'][:3]):  # Show first 3
                    print(f"        {i+1}. {assignment['course_name']} ({assignment['class_group']}) "
                          f"- Prof: {assignment['professor_id']}")
                if len(overlap['assignments']) > 3:
                    print(f"        ... and {len(overlap['assignments']) - 3} more")
            
            # Show first few violations
            if violations['professor_conflicts']:
                print(f"\n   Example professor conflict:")
                conflict = violations['professor_conflicts'][0]
                print(f"      {conflict['professor']} assigned to {conflict['conflict1']['course_name']} "
                      f"and {conflict['conflict2']['course_name']} at {conflict['day']} Period {conflict['period']}")
        
        print(f"\nOutput files created in: {output_dir}/")
        print(f"   - Complete timetable (all class groups): {timetable_path}")
        if unassigned_courses:
            print(f"   - Unassigned report: {unassigned_path}")
        print(f"   - Detailed report: {detailed_path}")
        
        # Close database connection
        db_loader.close()
        
        print("\n" + "=" * 60)
        print("Timetabling solution completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please check the database file and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 