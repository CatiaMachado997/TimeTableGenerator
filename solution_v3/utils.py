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