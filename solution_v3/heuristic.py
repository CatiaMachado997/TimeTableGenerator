import random
from typing import Dict, List, Tuple, Set
from collections import defaultdict

class TimetableHeuristic:
    def __init__(self):
        # Period structure: 30 periods per day
        # Periods 1-10: Morning (8:00-12:00)
        # Periods 11-20: Afternoon (13:00-17:00) 
        # Periods 21-30: Night (18:00-22:00)
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.morning_periods = list(range(1, 11))  # 1-10
        self.afternoon_periods = list(range(11, 21))  # 11-20
        self.night_periods = list(range(21, 31))  # 21-30
        self.all_periods = list(range(1, 31))  # 1-30
        
        # Timetable structure: {day: {period: {room_id: assignment}}}
        self.timetable = {day: {period: {} for period in self.all_periods} for day in self.days}
        
        # Tracking structures
        self.professor_assignments = defaultdict(set)  # professor -> set of (day, period)
        self.room_assignments = defaultdict(set)  # room -> set of (day, period)
        self.class_group_assignments = defaultdict(set)  # class_group -> set of (day, period)
        
        # Statistics
        self.assigned_classes = 0
        self.unassigned_classes = 0
        self.preference_violations = 0
        
    def get_valid_periods_for_class(self, class_group: str, periods_needed: int) -> List[List[int]]:
        """Get valid periods based on class group naming convention"""
        if len(class_group) >= 2 and class_group[1] == 'D':  # Day classes - morning or afternoon only
            valid_periods = self.morning_periods + self.afternoon_periods
        elif len(class_group) >= 2 and class_group[1] == 'N':  # Night classes - night only
            valid_periods = self.night_periods
        else:  # Default - all periods
            valid_periods = self.all_periods
            
        # For multi-period classes, ensure consecutive periods
        if periods_needed > 1:
            consecutive_periods = []
            for i in range(len(valid_periods) - periods_needed + 1):
                period_sequence = valid_periods[i:i + periods_needed]
                # Check if periods are consecutive
                if all(period_sequence[j] + 1 == period_sequence[j+1] 
                      for j in range(len(period_sequence) - 1)):
                    consecutive_periods.append(period_sequence)
            return consecutive_periods
        else:
            return [[period] for period in valid_periods]
    
    def get_priority_periods(self, year: int, class_group: str) -> List[int]:
        """Get priority periods based on year and class group"""
        if len(class_group) >= 2 and class_group[1] == 'N':  # Night classes
            return self.night_periods
        elif year == 1 or year == 3:  # First and third years prefer morning
            return self.morning_periods + self.afternoon_periods
        elif year == 2:  # Second year prefers afternoon
            return self.afternoon_periods + self.morning_periods
        else:  # Default
            return self.all_periods
    
    def check_hard_constraints(self, course: Dict, day: str, periods: List[int], 
                             room_id: str, professor_id: str) -> bool:
        """Check if assignment violates hard constraints"""
        class_group = course['ClassGroup']
        
        # Check professor availability
        for period in periods:
            if (day, period) in self.professor_assignments[professor_id]:
                return False
        
        # Check room availability
        for period in periods:
            if (day, period) in self.room_assignments[room_id]:
                return False
        
        # Check class group availability
        for period in periods:
            if (day, period) in self.class_group_assignments[class_group]:
                return False
        
        # Check room type compatibility
        room_type = course.get('RequiredRoomType')
        if room_type:
            # This would need to be checked against the actual room type
            # For now, we'll assume all rooms are compatible
            pass
        
        return True
    
    def calculate_preference_score(self, professor_id: str, day: str, 
                                 periods: List[int], preferences: List[Dict]) -> int:
        """Calculate preference score for assignment"""
        score = 0
        
        # Build professor preferences dictionary
        prof_preferences = {}
        for preference in preferences:
            if preference['ProfessorID'] == professor_id:
                day_of_week = preference['DayOfWeek']
                period = preference['Period']
                pref_value = preference['Preference']
                
                if day_of_week not in prof_preferences:
                    prof_preferences[day_of_week] = {}
                prof_preferences[day_of_week][period] = pref_value
        
        for period in periods:
            if day in prof_preferences and period in prof_preferences[day]:
                preference = prof_preferences[day][period]
                if preference == 'Preferred':
                    score += 2
                elif preference == 'Acceptable':
                    score += 1
                elif preference == 'Unwanted':
                    score -= 2
                elif preference == 'Forbidden':
                    score -= 10  # Heavy penalty but not impossible
        
        return score
    
    def assign_course(self, course: Dict, rooms: List[Dict], preferences: List[Dict]) -> bool:
        """Assign a course using hard constraints and soft constraints (year/professor preferences)"""
        course_id = course['CourseID']
        professor_id = course['ProfessorID']
        class_group = course['ClassGroup']
        periods_needed = course['Periods']
        year = course['Year']

        valid_period_sequences = self.get_valid_periods_for_class(class_group, periods_needed)
        if not valid_period_sequences:
            print(f"[DEBUG] No valid period sequences for {course_id} ({class_group})")
            return False

        # First, try to find assignments with both year-based and professor preferences
        best_score = float('-inf')
        best_assignment = None
        
        # Try all possible combinations to find the best preferred assignment
        for day in self.days:
            for period_seq in valid_period_sequences:
                for room in rooms:
                    room_id = room['RoomID']
                    
                    # Check if this assignment is valid (hard constraints)
                    if self._is_valid_assignment(day, period_seq, room_id, professor_id, class_group):
                        # Calculate soft constraint score (both year and professor preferences)
                        score = self._calculate_soft_constraint_score(
                            day, period_seq, room_id, professor_id, year, preferences
                        )
                        
                        if score > best_score:
                            best_score = score
                            best_assignment = (day, period_seq, room_id)

        # If we found a preferred assignment (score > 0), use it
        if best_assignment and best_score > 0:
            day, period_seq, room_id = best_assignment
            self._apply_assignment(day, period_seq, room_id, course)
            print(f"[DEBUG] Assigned {course_id} to {day} periods {period_seq} room {room_id} (preferred score: {best_score})")
            return True
        
        # If no preferred assignment found, try any available assignment (ignore all soft constraints)
        print(f"[DEBUG] No preferred assignment found for {course_id}, trying any available slot...")
        
        for day in self.days:
            for period_seq in valid_period_sequences:
                for room in rooms:
                    room_id = room['RoomID']
                    
                    # Check if this assignment is valid (hard constraints only)
                    if self._is_valid_assignment(day, period_seq, room_id, professor_id, class_group):
                        # Apply assignment without considering any soft constraints
                        self._apply_assignment(day, period_seq, room_id, course)
                        print(f"[DEBUG] Assigned {course_id} to {day} periods {period_seq} room {room_id} (fallback - no preferences)")
                        return True
        
        print(f"[DEBUG] No valid assignment found for {course_id}")
        return False

    def _is_valid_assignment(self, day: str, period_seq: List[int], room_id: str, 
                             professor_id: str, class_group: str) -> bool:
        """Check if an assignment violates hard constraints"""
        for period in period_seq:
            if (room_id in self.timetable[day][period] or
                professor_id in [a['professor_id'] for a in self.timetable[day][period].values()] or
                class_group in [a['class_group'] for a in self.timetable[day][period].values()]):
                return False
        return True

    def _apply_assignment(self, day: str, period_seq: List[int], room_id: str, course: Dict):
        """Apply an assignment to the timetable and update tracking structures"""
        course_id = course['CourseID']
        professor_id = course['ProfessorID']
        class_group = course['ClassGroup']
        
        for period in period_seq:
            self.timetable[day][period][room_id] = {
                'course_id': course_id,
                'course_name': course['CourseName'],
                'class_type': course['ClassType'],
                'professor_id': professor_id,
                'class_group': class_group
            }
        for period in period_seq:
            self.professor_assignments[professor_id].add((day, period))
            self.room_assignments[room_id].add((day, period))
            self.class_group_assignments[class_group].add((day, period))
        self.assigned_classes += 1
    
    def _calculate_soft_constraint_score(self, day: str, period_seq: List[int], 
                                       room_id: str, professor_id: str, year: int, 
                                       preferences: List[Dict]) -> float:
        """Calculate soft constraint score for an assignment"""
        score = 0.0
        
        # Year-based preference (1st/3rd year prefer morning, 2nd year prefers afternoon)
        # Weight: 3.0 per period to make year preferences significant
        for period in period_seq:
            if year in [1, 3] and 1 <= period <= 10:  # Morning periods
                score += 3.0
            elif year == 2 and 11 <= period <= 20:  # Afternoon periods  
                score += 3.0
        
        # Professor preference (use existing method)
        # This already has its own weighting system (2 for Preferred, 1 for Acceptable, etc.)
        prof_score = self.calculate_preference_score(professor_id, day, period_seq, preferences)
        score += prof_score
        
        return score

    def build_timetable(self, courses: List[Dict], rooms: List[Dict], 
                       preferences: List[Dict]) -> Dict:
        """Build the complete timetable"""
        print(f"Building timetable for {len(courses)} courses...")
        
        # Reset tracking structures and counters
        self.professor_assignments = defaultdict(set)
        self.room_assignments = defaultdict(set)
        self.class_group_assignments = defaultdict(set)
        self.timetable = {day: {period: {} for period in self.all_periods} for day in self.days}
        self.assigned_classes = 0
        self.unassigned_classes = 0
        
        # Calculate capacity constraints
        total_slots = 5 * 30  # 5 days * 30 periods
        total_periods_needed = sum(course['Periods'] for course in courses)
        
        print(f"Total available slots: {total_slots}")
        print(f"Total periods needed: {total_periods_needed}")
        print(f"Capacity ratio: {total_periods_needed / total_slots:.2f}")
        
        if total_periods_needed > total_slots:
            print("Warning: More periods needed than available slots. Prioritizing courses...")
        
        sorted_courses = sorted(courses, 
                              key=lambda x: (x['Year'], x['Semester'], x['Periods']))
        
        unassigned = []
        
        for i, course in enumerate(sorted_courses):
            if i % 20 == 0:
                print(f"Processing course {i+1}/{len(courses)}: {course['CourseID']}")
            
            assigned = self.assign_course(course, rooms, preferences)
            if not assigned:
                unassigned.append(course)
                self.unassigned_classes += 1
                print(f"Could not assign: {course['CourseID']} - {course['CourseName']} "
                      f"({course['ClassGroup']})")
        
        print(f"\nTimetable building completed:")
        # Assigned classes will be recalculated in get_statistics
        print(f"Unassigned classes: {self.unassigned_classes}")
        return {
            'timetable': self.timetable,
            'assigned_classes': None,  # Will be calculated in get_statistics
            'unassigned_classes': self.unassigned_classes,
            'unassigned_courses': unassigned
        }
    
    def check_overlapping_assignments(self) -> List[Dict]:
        """Check for overlapping assignments in the same time slots"""
        overlaps = []
        
        for day in self.days:
            for period in self.all_periods:
                period_assignments = self.timetable[day][period]
                
                if len(period_assignments) > 1:
                    # Multiple assignments in the same time slot
                    assignments = list(period_assignments.values())
                    overlaps.append({
                        'day': day,
                        'period': period,
                        'assignments': assignments,
                        'count': len(assignments)
                    })
        
        return overlaps

    def validate_constraints(self) -> Dict:
        """Validate that all hard constraints are being respected"""
        violations = {
            'professor_conflicts': [],
            'room_conflicts': [],
            'class_group_conflicts': [],
            'period_violations': []
        }
        
        # Check for conflicts in the timetable
        for day in self.days:
            for period in self.all_periods:
                period_assignments = self.timetable[day][period]
                
                # Check for room conflicts (multiple assignments to same room)
                room_assignments = {}
                for room_id, assignment in period_assignments.items():
                    if room_id in room_assignments:
                        violations['room_conflicts'].append({
                            'day': day, 'period': period, 'room': room_id,
                            'conflict1': room_assignments[room_id],
                            'conflict2': assignment
                        })
                    else:
                        room_assignments[room_id] = assignment
                
                # Check for professor conflicts
                professor_assignments = {}
                for room_id, assignment in period_assignments.items():
                    prof_id = assignment['professor_id']
                    if prof_id in professor_assignments:
                        violations['professor_conflicts'].append({
                            'day': day, 'period': period, 'professor': prof_id,
                            'conflict1': professor_assignments[prof_id],
                            'conflict2': assignment
                        })
                    else:
                        professor_assignments[prof_id] = assignment
                
                # Check for class group conflicts
                class_group_assignments = {}
                for room_id, assignment in period_assignments.items():
                    class_group = assignment['class_group']
                    if class_group in class_group_assignments:
                        violations['class_group_conflicts'].append({
                            'day': day, 'period': period, 'class_group': class_group,
                            'conflict1': class_group_assignments[class_group],
                            'conflict2': assignment
                        })
                    else:
                        class_group_assignments[class_group] = assignment
        
        return violations

    def get_statistics(self) -> Dict:
        """Get timetable statistics based on actual timetable content"""
        unique_courses = set()
        total_period_assignments = 0
        for day in self.timetable.values():
            for period in day.values():
                total_period_assignments += len(period)
                for assignment in period.values():
                    unique_courses.add(assignment['course_id'])
        assigned_classes = len(unique_courses)
        return {
            'total_assignments': total_period_assignments,
            'unique_courses': assigned_classes,
            'assigned_classes': assigned_classes,
            'unassigned_classes': self.unassigned_classes,
            'professor_assignments': len(self.professor_assignments),
            'room_assignments': len(self.room_assignments),
            'class_group_assignments': len(self.class_group_assignments)
        } 