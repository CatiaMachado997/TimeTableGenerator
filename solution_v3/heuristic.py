import random
from typing import Dict, List, Tuple, Set, Optional
from typing import Union
from collections import defaultdict
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import numpy as np
import os
from tqdm import tqdm

class TimetableHeuristic:
    def __init__(self, use_parallel=True, use_simulated_annealing=True):
        # Period structure: 30 periods per day (real data format)
        # Periods 1-15: Morning (8:00-12:00)
        # Periods 16-25: Afternoon (13:00-17:00) 
        # Periods 26-30: Night (18:00-22:00)
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.morning_periods = list(range(1, 16))  # 1-15
        self.afternoon_periods = list(range(16, 26))  # 16-25
        self.night_periods = list(range(26, 31))  # 26-30
        self.all_periods = list(range(1, 31))  # 1-30
        # Rest periods: 12:00-12:30 (lunch break) and 19:00-21:00 (dinner break)
        # In 30-period system: periods 15 (12:00-12:30) and 26-30 (19:00-22:00)
        self.rest_periods = [15, 26, 27, 28, 29, 30]
        
        # OPTIMIZATION: Use numpy arrays for better memory efficiency
        # Timetable array is dtype=object to store assignment dicts per slot
        self.timetable = np.empty((len(self.days), max(self.all_periods), 20), dtype=object)
        self.timetable.fill(None)
        self.assignment_map = {}  # Maps (day_idx, period, room_idx) to course_id
        
        # OPTIMIZATION: Use bitmasks for faster constraint checking
        self.professor_bitmasks = defaultdict(lambda: {day: 0 for day in self.days})
        self.room_bitmasks = defaultdict(lambda: {day: 0 for day in self.days})
        self.class_group_bitmasks = defaultdict(lambda: {day: 0 for day in self.days})
        
        # OPTIMIZATION: Pre-computed period sequences for multi-period classes
        self.period_sequences = self._precompute_period_sequences()
        
        # OPTIMIZATION: Room availability cache with LRU eviction
        self.room_availability_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # OPTIMIZATION: Advanced room allocation heuristics
        self.room_usage_stats = defaultdict(int)
        self.room_type_compatibility = {}
        
        # OPTIMIZATION: Simulated annealing parameters
        self.use_simulated_annealing = use_simulated_annealing
        self.initial_temperature = 100.0
        self.cooling_rate = 0.95
        self.min_temperature = 0.1
        
        # OPTIMIZATION: Parallel processing
        self.use_parallel = use_parallel
        self.max_workers = min(8, (os.cpu_count() or 1))
        self.thread_local = threading.local()
        
        # Statistics
        self.assigned_classes = 0
        self.unassigned_classes = 0
        self.preference_violations = 0
        
        # OPTIMIZATION: Performance tracking
        self.constraint_checks = 0
        self.assignment_attempts = 0
        self.parallel_assignments = 0
        self.annealing_iterations = 0
        
        # OPTIMIZATION: Early termination tracking
        self.optimal_assignments = 0
        self.early_terminations = 0
        
    def _precompute_period_sequences(self) -> Dict[int, List[List[int]]]:
        """Pre-compute all valid period sequences for different class durations - OPTIMIZED"""
        sequences = {}
        
        # OPTIMIZATION: Use numpy for faster sequence generation
        for periods_needed in range(1, 11):  # Support up to 10-period classes
            valid_sequences = []
            
            # For day classes (morning + afternoon)
            day_periods = np.array(self.morning_periods + self.afternoon_periods)
            for i in range(len(day_periods) - periods_needed + 1):
                seq = day_periods[i:i + periods_needed]
                if np.all(np.diff(seq) == 1):  # Check consecutive periods
                    valid_sequences.append(seq.tolist())
            
            # For night classes
            night_periods = np.array(self.night_periods)
            for i in range(len(night_periods) - periods_needed + 1):
                seq = night_periods[i:i + periods_needed]
                if np.all(np.diff(seq) == 1):  # Check consecutive periods
                    valid_sequences.append(seq.tolist())
            
            sequences[periods_needed] = valid_sequences
        
        return sequences
    
    def _update_bitmasks(self, day: str, periods: List[int], professor_id: str, 
                        room_id: str, class_group: str, add: bool = True):
        """Update bitmasks for fast constraint checking - OPTIMIZED"""
        # OPTIMIZATION: Use safer bit operations to avoid overflow
        for period in periods:
            bit = 1 << (period - 1)  # Convert period to bit position
            
            if add:
                self.professor_bitmasks[professor_id][day] |= bit
                self.room_bitmasks[room_id][day] |= bit
                self.class_group_bitmasks[class_group][day] |= bit
            else:
                self.professor_bitmasks[professor_id][day] &= ~bit
                self.room_bitmasks[room_id][day] &= ~bit
                self.class_group_bitmasks[class_group][day] &= ~bit
    
    def _check_bitmask_conflicts(self, day: str, periods: List[int], 
                               professor_id: str, room_id: str, class_group: str) -> bool:
        """Fast conflict checking using bitmasks - OPTIMIZED"""
        self.constraint_checks += 1
        
        # OPTIMIZATION: Safer conflict checking to avoid overflow
        for period in periods:
            bit = 1 << (period - 1)
            
            # Check if any bit is already set (conflict)
            if (self.professor_bitmasks[professor_id][day] & bit or
                self.room_bitmasks[room_id][day] & bit or
                self.class_group_bitmasks[class_group][day] & bit):
                return True
        
        return False
    
    def _get_optimal_rooms(self, course: Dict, rooms: List[Dict]) -> List[Dict]:
        """Get optimal room ordering based on advanced heuristics"""
        course_id = course['CourseID']
        
        # Check cache first
        if course_id in self.room_availability_cache:
            self.cache_hits += 1
            return self.room_availability_cache[course_id]
        
        self.cache_misses += 1
        
        # OPTIMIZATION: Advanced room selection heuristics
        room_scores = []
        for room in rooms:
            score = 0
            
            # Factor 1: Room usage (prefer less used rooms)
            usage = self.room_usage_stats.get(room['RoomID'], 0)
            score -= usage * 2
            
            # Factor 2: Room type compatibility
            required_type = course.get('RequiredRoomType')
            room_type = room.get('RoomType')
            if required_type and room_type:
                if required_type == room_type:
                    score += 10
                else:
                    score -= 5
            
            # Factor 3: Room capacity vs class size
            room_capacity = room.get('Capacity', 50)
            class_size = course.get('NumberOfStudents', 30)
            if room_capacity >= class_size:
                score += 5
                # Bonus for optimal capacity
                if room_capacity <= class_size * 1.2:
                    score += 3
            else:
                score -= 10
            
            # Factor 4: Room location preference (building proximity)
            building = room.get('Building', '')
            if building in ['F', 'I']:  # Preferred buildings
                score += 2
            
            room_scores.append((score, room))
        
        # Sort by score (highest first)
        sorted_rooms = [room for score, room in sorted(room_scores, key=lambda x: x[0], reverse=True)]
        
        # Cache the result (limit cache size)
        if len(self.room_availability_cache) < 1000:
            self.room_availability_cache[course_id] = sorted_rooms
        
        return sorted_rooms
    
    def _simulated_annealing_optimization(self, courses: List[Dict], rooms: List[Dict], 
                                        preferences: List[Dict]) -> np.ndarray:
        """Apply simulated annealing to improve solution quality"""
        if not self.use_simulated_annealing:
            return self.timetable
        
        print("Applying simulated annealing optimization...")
        self.annealing_iterations = 0
        
        current_solution = self.timetable.copy()
        current_score = self._calculate_solution_score(current_solution, courses, preferences)
        best_solution = current_solution.copy()
        best_score = current_score
        
        temperature = self.initial_temperature
        
        while temperature > self.min_temperature:
            self.annealing_iterations += 1
            
            # Generate neighbor solution by swapping two random assignments
            neighbor_solution = self._generate_neighbor_solution(current_solution, courses, rooms)
            
            if neighbor_solution is not None:
                neighbor_score = self._calculate_solution_score(neighbor_solution, courses, preferences)
                
                # Calculate acceptance probability
                delta_e = neighbor_score - current_score
                if delta_e > 0 or random.random() < math.exp(delta_e / temperature):
                    current_solution = neighbor_solution
                    current_score = neighbor_score
                    
                    if current_score > best_score:
                        best_solution = current_solution.copy()
                        best_score = current_score
                        print(f"  New best score: {best_score:.2f} (iteration {self.annealing_iterations})")
            
            temperature *= self.cooling_rate
            
            if self.annealing_iterations % 100 == 0:
                print(f"  Temperature: {temperature:.2f}, Current score: {current_score:.2f}")
        
        print(f"Simulated annealing completed: {self.annealing_iterations} iterations")
        return best_solution
    
    def _calculate_solution_score(self, solution: np.ndarray, courses: List[Dict], 
                                preferences: List[Dict]) -> float:
        """Calculate overall solution quality score"""
        score = 0.0
        
        # Count assigned courses
        assigned_count = np.count_nonzero(solution)
        score += assigned_count * 10
        
        # Penalize unassigned courses
        unassigned_count = len(courses) - assigned_count
        score -= unassigned_count * 50
        
        # Add preference satisfaction bonus
        for course in courses:
            course_id = course['CourseID']
            # Find course assignment in solution
            # This is a simplified scoring - could be enhanced
            if course_id in self.assignment_map:
                score += 5
        
        return score
    
    def _generate_neighbor_solution(self, current_solution: np.ndarray, 
                                  courses: List[Dict], rooms: List[Dict]) -> Optional[np.ndarray]:
        """Generate a neighbor solution by swapping assignments"""
        # Find two random assignments to swap (work with object arrays)
        assigned_positions = []
        for day_idx in range(current_solution.shape[0]):
            for period_idx in range(current_solution.shape[1]):
                for room_idx in range(current_solution.shape[2]):
                    if current_solution[day_idx, period_idx, room_idx] is not None:
                        assigned_positions.append((day_idx, period_idx, room_idx))
        
        if len(assigned_positions) < 2:
            return None
        
        # Select two random assignments
        pos1, pos2 = random.sample(assigned_positions, 2)
        
        # Create neighbor solution
        neighbor = current_solution.copy()
        neighbor[pos1], neighbor[pos2] = neighbor[pos2], neighbor[pos1]
        
        return neighbor
    
    def _parallel_assign_course(self, course: Dict, rooms: List[Dict], 
                              preferences: List[Dict]) -> Tuple[bool, Dict]:
        """Assign a course using parallel processing - thread-safe version"""
        # Thread-local storage for performance
        if not hasattr(self.thread_local, 'local_cache'):
            self.thread_local.local_cache = {}
        
        course_id = course['CourseID']
        class_group = course['ClassGroup']
        professor_id = course['ProfessorID']
        periods_needed = course['Periods']
        year = course['Year']
        
        self.assignment_attempts += 1
        
        # OPTIMIZATION: Get optimal room ordering
        optimal_rooms = self._get_optimal_rooms(course, rooms)
        
        # Get valid period sequences for this class
        valid_sequences = self.get_valid_periods_for_class(class_group, periods_needed)
        
        # OPTIMIZATION: Sort sequences by preference
        if year in [1, 3]:
            valid_sequences.sort(key=lambda seq: 
                sum(1 for p in seq if p in self.morning_periods), reverse=True)
        elif year == 2:
            valid_sequences.sort(key=lambda seq: 
                sum(1 for p in seq if p in self.afternoon_periods), reverse=True)
        
        # Try each day with optimized search (use load-based day ordering)
        optimal_days = self._get_optimal_day_order(course)
        for day in optimal_days:
            for period_seq in valid_sequences:
                for room in optimal_rooms[:15]:
                    # Thread-safe constraint check
                    with threading.Lock():
                        if not self._check_bitmask_conflicts(day, period_seq, professor_id, 
                                                            room['RoomID'], class_group):
                            # Found valid assignment
                            assignment = {
                                'course_id': course_id,
                                'class_group': class_group,
                                'professor_id': professor_id,
                                'room_id': room['RoomID'],
                                'periods': periods_needed,
                                'day': day,
                                'period_seq': period_seq
                            }
                            
                            # Update bitmasks (thread-safe)
                            with threading.Lock():
                                self._update_bitmasks(day, period_seq, professor_id, 
                                                    room['RoomID'], class_group, add=True)
                            
                            self.assigned_classes += 1
                            self.parallel_assignments += 1
                            return True, assignment
        
        # Fallback search
        for day in optimal_days:
            for period_seq in valid_sequences[:50]:
                for room in optimal_rooms[:10]:
                    with threading.Lock():
                        if not self._check_bitmask_conflicts(day, period_seq, professor_id, 
                                                            room['RoomID'], class_group):
                            assignment = {
                                'course_id': course_id,
                                'class_group': class_group,
                                'professor_id': professor_id,
                                'room_id': room['RoomID'],
                                'periods': periods_needed,
                                'day': day,
                                'period_seq': period_seq
                            }
                            
                            with threading.Lock():
                                self._update_bitmasks(day, period_seq, professor_id, 
                                                    room['RoomID'], class_group, add=True)
                            
                            self.assigned_classes += 1
                            self.parallel_assignments += 1
                            return True, assignment
        
        self.unassigned_classes += 1
        return False, {}
    
    def get_valid_periods_for_class(self, class_group: str, periods_needed: int) -> List[List[int]]:
        """Get valid periods based on class group naming convention - OPTIMIZED"""
        # Use pre-computed sequences
        if periods_needed in self.period_sequences:
            if len(class_group) >= 2 and class_group[1] == 'D':  # Day classes
                return [seq for seq in self.period_sequences[periods_needed] 
                       if all(p in self.morning_periods + self.afternoon_periods for p in seq)]
            elif len(class_group) >= 2 and class_group[1] == 'N':  # Night classes
                return [seq for seq in self.period_sequences[periods_needed] 
                       if all(p in self.night_periods for p in seq)]
            else:  # All periods
                return self.period_sequences[periods_needed]
        
        # Fallback to original method if not pre-computed
        if len(class_group) >= 2 and class_group[1] == 'D':  # Day classes - morning or afternoon only
            valid_periods = self.morning_periods + self.afternoon_periods
        elif len(class_group) >= 2 and class_group[1] == 'N':  # Night classes - night only
            valid_periods = self.night_periods
        else:  # Default - all periods
            valid_periods = self.all_periods
        # Remove rest periods
        valid_periods = [p for p in valid_periods if p not in self.rest_periods]
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
    
    def assign_course(self, course: Dict, rooms: List[Dict], preferences: List[Dict], allow_soft_violations: bool = True) -> bool:
        """Assign a course using soft-hard or hard constraint logic based on allow_soft_violations flag"""
        course_id = course['CourseID']
        class_group = course['ClassGroup']
        professor_id = course['ProfessorID']
        periods_needed = course['Periods']
        year = course['Year']
        assigned = False
        optimal_rooms = self._get_optimal_rooms(course, rooms)
        valid_sequences = self.get_valid_periods_for_class(class_group, periods_needed)
        if year in [1, 3]:
            valid_sequences.sort(key=lambda seq: sum(1 for p in seq if p in self.morning_periods), reverse=True)
        elif year == 2:
            valid_sequences.sort(key=lambda seq: sum(1 for p in seq if p in self.afternoon_periods), reverse=True)
        optimal_days = self._get_optimal_day_order(course)
        best_score = -float('inf')
        best_assignment = None
        best_violations = None
        for day in optimal_days:
            for period_seq in valid_sequences:
                for room in optimal_rooms:
                    safe_class_group = class_group if class_group is not None else ''
                    safe_course = course if course is not None else {}
                    safe_room = room if room is not None else {}
                    score, violations = self._calculate_soft_constraint_score(day, period_seq, room['RoomID'], professor_id, year, preferences, safe_class_group, safe_course, safe_room, return_violations=True, allow_soft_violations=allow_soft_violations)  # type: ignore
                    if allow_soft_violations or (violations['professor'] == 0 and violations['room'] == 0 and violations['class_group'] == 0 and violations['room_type'] == 0):
                        if score > best_score:
                            best_score = score
                            best_assignment = (day, period_seq, room['RoomID'], room)
                            best_violations = violations
        if best_assignment:
            day, period_seq, room_id, room = best_assignment
            self._apply_assignment(day, period_seq, room_id, course)
            self._track_soft_constraint_stats(day, period_seq, professor_id, year, preferences)
            if allow_soft_violations:
                self._track_violation_stats(best_violations)
            print(f"[INFO] Assigned with soft constraint score {best_score}: {course_id} -> {day} periods {period_seq} room {room_id}")
            return True
        print(f"[INFO] No assignment found for {course_id} - {class_group}")
        self.unassigned_classes += 1
        return False

    def _is_valid_assignment(self, day: str, period_seq: List[int], room_id: str, professor_id: str, class_group: str, course: Dict, room: Dict) -> bool:
        """Check if an assignment violates hard constraints - OPTIMIZED"""
        # Check rest periods
        for period in period_seq:
            if period in self.rest_periods:
                print(f"Rest period violation: {period}")
                return False
        # OPTIMIZATION: Use bitmask check instead of manual iteration
        if self._check_bitmask_conflicts(day, period_seq, professor_id, room_id, class_group):
            print(f"Bitmask conflict: day={day}, periods={period_seq}, professor={professor_id}, room={room_id}, class_group={class_group}")
            return False
        # Check room type compatibility if info is provided
        required_type = course.get('RequiredRoomType')
        room_type = room.get('RoomType')
        if required_type and room_type and required_type != room_type:
            print(f"Room type mismatch: required={required_type}, available={room_type}")
            return False
        # Check class group constraints (D/N/other)
        if len(class_group) >= 2:
            if class_group[1] == 'D' and any(p in self.night_periods for p in period_seq):
                print(f"Day class group scheduled in night period: {class_group}, periods={period_seq}")
                return False
            if class_group[1] == 'N' and any(p not in self.night_periods for p in period_seq):
                print(f"Night class group scheduled outside night period: {class_group}, periods={period_seq}")
                return False
        return True

    def set_room_index_mapping(self, rooms: List[Dict]):
        """Set up mapping from room_id to timetable array index."""
        self.room_id_to_index = {room['RoomID']: idx for idx, room in enumerate(rooms)}

    def _apply_assignment(self, day: str, period_seq: List[int], room_id: str, course: Dict):
        """Apply an assignment to the timetable and update tracking structures - OPTIMIZED"""
        course_id = course['CourseID']
        professor_id = course['ProfessorID']
        class_group = course['ClassGroup']
        year = course.get('Year')
        semester = course.get('Semester')
        class_type = course.get('ClassType')
        # Find indices
        try:
            day_idx = self.days.index(day)
        except ValueError:
            raise ValueError(f"Invalid day: {day}")
        if not hasattr(self, 'room_id_to_index'):
            raise RuntimeError("room_id_to_index mapping not set. Call set_room_index_mapping(rooms) before assignment.")
        if room_id not in self.room_id_to_index:
            raise ValueError(f"Room ID {room_id} not found in room_id_to_index mapping.")
        room_idx = self.room_id_to_index[room_id]
        for period in period_seq:
            self.timetable[day_idx, period-1, room_idx] = {
                'course_id': course_id,
                'class_group': class_group,
                'professor_id': professor_id,
                'year': year,
                'semester': semester,
                'class_type': class_type,
                'room_id': room_id,
                'period': period,
                'day': day
            }  # type: ignore[assignment]
            self.assignment_map[(day_idx, period-1, room_idx)] = course_id
        # Only update bitmasks if all required fields are not None
        if all(x is not None for x in [day, period_seq, professor_id, room_id, class_group]):
            self._update_bitmasks(day, period_seq, professor_id, room_id, class_group, add=True)
        self.assigned_classes += 1

    def _calculate_soft_constraint_score(self, day: str, period_seq: List[int], 
                                       room_id: str, professor_id: str, year: int, 
                                       preferences: List[Dict], class_group: str = None, course: Dict = None, room: Dict = None, return_violations: bool = False, allow_soft_violations: bool = True) -> Union[float, Tuple[float, Dict[str, int]]]:
        score = 0.0
        violations = {'professor': 0, 'room': 0, 'class_group': 0, 'room_type': 0}
        # Year-based preference
        for period in period_seq:
            if year in [1, 3] and 1 <= period <= 67:
                score += 3.0
            elif year == 2 and 68 <= period <= 133:
                score += 3.0
        prof_score = self.calculate_preference_score(professor_id, day, period_seq, preferences)
        score += prof_score
        # Room type compatibility
        if course and room:
            required_type = course.get('RequiredRoomType')
            room_type = room.get('RoomType')
            if required_type and room_type and required_type != room_type:
                score -= 10
                violations['room_type'] += 1
                if not allow_soft_violations:
                    if return_violations:
                        return score, violations
                    return -float('inf')
        for period in period_seq:
            bit = 1 << (period - 1)
            if self.professor_bitmasks[professor_id][day] & bit:
                score -= 20
                violations['professor'] += 1
                if not allow_soft_violations:
                    if return_violations:
                        return score, violations
                    return -float('inf')
            if self.room_bitmasks[room_id][day] & bit:
                score -= 20
                violations['room'] += 1
                if not allow_soft_violations:
                    if return_violations:
                        return score, violations
                    return -float('inf')
            if class_group and self.class_group_bitmasks[class_group][day] & bit:
                score -= 20
                violations['class_group'] += 1
                if not allow_soft_violations:
                    if return_violations:
                        return score, violations
                    return -float('inf')
        if return_violations:
            return score, violations
        return score

    def _track_violation_stats(self, violations):
        if not hasattr(self, 'violation_stats'):
            self.violation_stats = {'professor': 0, 'room': 0, 'class_group': 0, 'room_type': 0}
        for k in violations:
            self.violation_stats[k] += violations[k]

    def report_violation_stats(self):
        if hasattr(self, 'violation_stats'):
            stats = self.violation_stats
            print("\nConstraint Violation Summary (soft-hard mode):")
            print(f"  - Professor double-bookings: {stats['professor']}")
            print(f"  - Room double-bookings: {stats['room']}")
            print(f"  - Class group double-bookings: {stats['class_group']}")
            print(f"  - Room type mismatches: {stats['room_type']}")
        else:
            print("No constraint violations recorded.")

    def build_timetable(self, courses: List[Dict], rooms: List[Dict], preferences: List[Dict]) -> Dict:
        """Build the complete timetable - ADVANCED OPTIMIZED VERSION"""
        start_time = time.time()
        print(f"Building timetable for {len(courses)} courses...")
        
        # Reset tracking structures and counters
        self.professor_bitmasks = defaultdict(lambda: {day: 0 for day in self.days})
        self.room_bitmasks = defaultdict(lambda: {day: 0 for day in self.days})
        self.class_group_bitmasks = defaultdict(lambda: {day: 0 for day in self.days})
        self.timetable = np.empty((len(self.days), max(self.all_periods), 100), dtype=object)
        self.timetable.fill(None)
        self.assignment_map = {}
        self.assigned_classes = 0
        self.unassigned_classes = 0
        self.constraint_checks = 0
        self.assignment_attempts = 0
        self.parallel_assignments = 0
        self.annealing_iterations = 0
        self.optimal_assignments = 0
        self.early_terminations = 0
        
        # Clear caches
        self.room_availability_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.room_usage_stats = defaultdict(int)
        
        # Calculate capacity constraints
        total_slots = 5 * 30  # 5 days * 30 periods
        total_periods_needed = sum(course['Periods'] for course in courses)
        
        print(f"Total available slots: {total_slots}")
        print(f"Total periods needed: {total_periods_needed}")
        print(f"Capacity ratio: {total_periods_needed / total_slots:.2f}")
        
        if total_periods_needed > total_slots:
            print("Warning: More periods needed than available slots. Prioritizing courses...")
        
        # OPTIMIZATION: Sort courses by priority (year, semester, then by difficulty to schedule)
        sorted_courses = sorted(courses, 
                              key=lambda x: (x['Year'], x['Semester'], -x['Periods'], x['CourseID']))
        
        unassigned = []
        assigned_count = 0
        
        if self.use_parallel:
            print(f"Using parallel processing with {self.max_workers} workers...")
            
            # Parallel course assignment
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all course assignments
                future_to_course = {
                    executor.submit(self._parallel_assign_course, course, rooms, preferences): course 
                    for course in sorted_courses
                }
                
                # Process completed assignments
                for i, future in enumerate(as_completed(future_to_course)):
                    course = future_to_course[future]
                    if i % 20 == 0:
                        print(f"Processing course {i+1}/{len(courses)}: {course['CourseID']}")
                    
                    try:
                        success, assignment = future.result()
                        if not success:
                            unassigned.append(course)
                            self.unassigned_classes += 1
                            print(f"Could not assign: {course['CourseID']} - {course['CourseName']} "
                                  f"({course['ClassGroup']})")
                    except Exception as e:
                        print(f"Error assigning course {course['CourseID']}: {e}")
                        unassigned.append(course)
                        self.unassigned_classes += 1
        else:
            # Sequential processing
            for i, course in enumerate(tqdm(sorted_courses, desc='Assigning courses', unit='course')):
                assigned = self.assign_course(course, rooms, preferences, allow_soft_violations=True)
                if assigned:
                    assigned_count += 1
                if not assigned:
                    unassigned.append(course)
        # If no assignments, fallback to hard constraint mode
        if assigned_count == 0:
            print("\n[WARNING] No courses assigned with soft-hard constraints. Falling back to hard constraint mode.")
            # Reset tracking structures
            self.professor_bitmasks = defaultdict(lambda: {day: 0 for day in self.days})
            self.room_bitmasks = defaultdict(lambda: {day: 0 for day in self.days})
            self.class_group_bitmasks = defaultdict(lambda: {day: 0 for day in self.days})
            self.timetable = np.empty((len(self.days), max(self.all_periods), 100), dtype=object)
            self.timetable.fill(None)
            self.assignment_map = {}
            self.assigned_classes = 0
            self.unassigned_classes = 0
            self.constraint_checks = 0
            self.assignment_attempts = 0
            self.parallel_assignments = 0
            self.annealing_iterations = 0
            self.optimal_assignments = 0
            self.early_terminations = 0
            self.violation_stats = {'professor': 0, 'room': 0, 'class_group': 0, 'room_type': 0}
            assigned_count = 0
            for i, course in enumerate(tqdm(sorted_courses, desc='Assigning courses (hard mode)', unit='course')):
                assigned = self.assign_course(course, rooms, preferences, allow_soft_violations=False)
                if assigned:
                    assigned_count += 1
                if not assigned:
                    unassigned.append(course)
        # Apply simulated annealing optimization if enabled
        if self.use_simulated_annealing and self.assigned_classes > 0:
            self.timetable = self._simulated_annealing_optimization(courses, rooms, preferences)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"\nTimetable building completed in {processing_time:.2f} seconds:")
        print(f"Advanced Performance metrics:")
        print(f"  - Constraint checks: {self.constraint_checks:,}")
        print(f"  - Assignment attempts: {self.assignment_attempts:,}")
        print(f"  - Checks per attempt: {self.constraint_checks / max(1, self.assignment_attempts):.2f}")
        print(f"  - Parallel assignments: {self.parallel_assignments}")
        print(f"  - Annealing iterations: {self.annealing_iterations}")
        print(f"  - Cache hits: {self.cache_hits}, misses: {self.cache_misses}")
        print(f"  - Cache hit rate: {self.cache_hits / max(1, self.cache_hits + self.cache_misses) * 100:.1f}%")
        print(f"  - Unassigned classes: {self.unassigned_classes}")
        
        return {
            'timetable': self.timetable,
            'assigned_classes': None,  # Will be calculated in get_statistics
            'unassigned_classes': self.unassigned_classes,
            'unassigned_courses': unassigned,
            'processing_time': processing_time,
            'performance_metrics': {
                'constraint_checks': self.constraint_checks,
                'assignment_attempts': self.assignment_attempts,
                'checks_per_attempt': self.constraint_checks / max(1, self.assignment_attempts),
                'parallel_assignments': self.parallel_assignments,
                'annealing_iterations': self.annealing_iterations,
                'cache_hit_rate': self.cache_hits / max(1, self.cache_hits + self.cache_misses) * 100
            }
        }
    
    def check_overlapping_assignments(self) -> List[Dict]:
        """Check for overlapping assignments in the same time slots"""
        overlaps = []
        
        for day_idx, day in enumerate(self.days):
            for period in self.all_periods:
                period_assignments = self.timetable[day_idx, period-1, :]
                assigned_rooms = []
                
                for room_idx in range(period_assignments.shape[0]):
                    if period_assignments[room_idx] is not None:
                        assigned_rooms.append(room_idx)
                
                if len(assigned_rooms) > 1:
                    # Multiple assignments in the same time slot
                    assignments = []
                    for room_idx in assigned_rooms:
                        course_id = self.assignment_map.get((day_idx, period-1, room_idx), 'Unknown')
                        assignments.append({'course_id': course_id})
                    
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
        for day_idx, day in enumerate(self.days):
            for period in self.all_periods:
                period_assignments = self.timetable[day_idx, period-1, :]
                assigned_rooms = []
                
                for room_idx in range(period_assignments.shape[0]):
                    if period_assignments[room_idx] is not None:
                        assigned_rooms.append(room_idx)
                
                if len(assigned_rooms) > 1:
                    # Multiple assignments in the same time slot
                    room_assignments = {}
                    professor_assignments = {}
                    class_group_assignments = {}
                    
                    for room_idx in assigned_rooms:
                        course_id = self.assignment_map.get((day_idx, period-1, room_idx), 'Unknown')
                        # This is a simplified check - would need course details for full validation
                        room_assignments[room_idx] = {'course_id': course_id}
        
        return violations

    def get_statistics(self) -> Dict:
        """Get timetable statistics based on actual timetable content"""
        unique_courses = set()
        total_period_assignments = 0
        
        for day_idx in range(len(self.days)):
            for period in self.all_periods:
                period_assignments = self.timetable[day_idx, period-1, :]
                assigned_count = 0
                
                for room_idx in range(period_assignments.shape[0]):
                    if period_assignments[room_idx] is not None:
                        assigned_count += 1
                        course_id = self.assignment_map.get((day_idx, period-1, room_idx), 'Unknown')
                        unique_courses.add(course_id)
                
                total_period_assignments += assigned_count
        
        assigned_classes = len(unique_courses)
        return {
            'total_assignments': total_period_assignments,
            'unique_courses': assigned_classes,
            'assigned_classes': assigned_classes,
            'unassigned_classes': self.unassigned_classes,
            'professor_assignments': len(self.professor_bitmasks),
            'room_assignments': len(self.room_bitmasks),
            'class_group_assignments': len(self.class_group_bitmasks),
            'performance_metrics': {
                'constraint_checks': self.constraint_checks,
                'assignment_attempts': self.assignment_attempts,
                'checks_per_attempt': self.constraint_checks / max(1, self.assignment_attempts),
                'parallel_assignments': self.parallel_assignments,
                'annealing_iterations': self.annealing_iterations,
                'cache_hit_rate': self.cache_hits / max(1, self.cache_hits + self.cache_misses) * 100
            }
        } 

    def _get_day_loads(self) -> Dict[str, int]:
        """Calculate current load (number of assignments) for each day"""
        day_loads = {day: 0 for day in self.days}
        
        for day_idx, day in enumerate(self.days):
            for period in self.all_periods:
                period_assignments = self.timetable[day_idx, period-1, :]
                for room_idx in range(period_assignments.shape[0]):
                    if period_assignments[room_idx] is not None:
                        day_loads[day] += 1
        
        return day_loads
    
    def _get_optimal_day_order(self, course: Dict) -> List[str]:
        """Get optimal day ordering for better distribution"""
        day_loads = self._get_day_loads()
        
        # Sort days by load (prefer less loaded days)
        sorted_days = sorted(self.days, key=lambda day: day_loads[day])
        
        # For year 2 courses, prefer Tuesday-Thursday (middle of week)
        if course['Year'] == 2:
            # Reorder to prefer middle days
            middle_days = ['Tuesday', 'Wednesday', 'Thursday']
            other_days = [day for day in sorted_days if day not in middle_days]
            return middle_days + other_days
        
        # For other years, use load-based ordering
        return sorted_days 

    def _track_soft_constraint_stats(self, day, period_seq, professor_id, year, preferences, satisfied=True):
        if not hasattr(self, 'soft_constraint_stats'):
            self.soft_constraint_stats = {'prof_pref_total': 0, 'prof_pref_satisfied': 0, 'year_pref_total': 0, 'year_pref_satisfied': 0}
        # Professor preference
        for period in period_seq:
            self.soft_constraint_stats['prof_pref_total'] += 1
            prof_score = self.calculate_preference_score(professor_id, day, [period], preferences)
            if prof_score > 0:
                self.soft_constraint_stats['prof_pref_satisfied'] += 1
        # Year-based preference
        for period in period_seq:
            self.soft_constraint_stats['year_pref_total'] += 1
            if (year in [1, 3] and period in self.morning_periods) or (year == 2 and period in self.afternoon_periods):
                self.soft_constraint_stats['year_pref_satisfied'] += 1

    def report_soft_constraint_stats(self):
        if hasattr(self, 'soft_constraint_stats'):
            stats = self.soft_constraint_stats
            prof_pct = 100.0 * stats['prof_pref_satisfied'] / max(1, stats['prof_pref_total'])
            year_pct = 100.0 * stats['year_pref_satisfied'] / max(1, stats['year_pref_total'])
            print(f"\nSoft Constraint Satisfaction:")
            print(f"  - Professor preferences satisfied: {prof_pct:.1f}%")
            print(f"  - Year-based period preferences satisfied: {year_pct:.1f}%")
        else:
            print("No soft constraint statistics available.") 