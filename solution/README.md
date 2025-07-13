# DEM-ISEP Timetabling Solution

This folder contains a Python solution for the University Course Timetabling Problem (UCTP) for the Mechanical Engineering Department (DEM) at ISEP.

## Structure
- `main.py`: Entry point. Runs the full pipeline.
- `db.py`: Database access and data loading from SQLite.
- `heuristic.py`: Constructive heuristic for timetable generation.
- `metaheuristic.py`: (Optional) Metaheuristic for solution improvement.
- `output_writer.py`: Writes the solution to the required Excel format.
- `requirements.txt`: Python dependencies.

## Algorithm Explanation

### Overview
The solution implements a **constructive greedy heuristic** that builds a feasible timetable by assigning classes to time slots and rooms while respecting all hard constraints and optimizing for soft constraints.

### Hard Constraints (Must be satisfied)
1. **Professor Uniqueness**: No professor can teach more than one class at the same time
2. **Room Uniqueness**: No room can be assigned to more than one class at the same time
3. **Class Group Uniqueness**: No class group can attend more than one class at the same time
4. **Room Type Matching**: Classes must be assigned to rooms of the appropriate type:
   - **T (Theoretical)**: Assigned to T-type rooms
   - **TP (Theoretical-Practical)**: Assigned to TP-type rooms
   - **PL (Laboratory)**: Assigned to L-type rooms with matching knowledge area
5. **Consecutive Periods**: Multi-period classes must be scheduled in consecutive time slots
6. **Duration Compliance**: All classes must be scheduled for their required number of periods

### Soft Constraints (Preferences)
1. **Year-based Period Prioritization**:
   - **First and Third Years (L-1*, L-3*)**: Prioritized for morning periods (1-4) in day regime
   - **Second Year (L-2*)**: Prioritized for afternoon periods (5-8) in day regime
   - **Night Regime**: All periods are equally available
2. **Professor Preferences**: Consider individual professor preferences for specific time slots
3. **Priority-based Assignment**: First/third year classes are assigned before second year classes

### Algorithm Steps

#### 1. Data Preparation
- Load all data from SQLite database (courses, rooms, preferences, class assignments)
- Parse class durations from UC_Rooms table (e.g., "T(1h+1h)" → 2 periods)
- Determine room type and knowledge area requirements

#### 2. Class Prioritization
- Sort classes by priority: First/third years (priority 1) before second years (priority 2)
- This ensures preferred time slots are allocated to higher priority classes

#### 3. Greedy Assignment Process
For each class in priority order:

1. **Calculate Requirements**:
   - Determine class duration from UC_Rooms table
   - Identify valid room types and knowledge areas
   - Get preferred periods based on year and regime

2. **Period Selection**:
   - Try preferred periods first (morning for 1st/3rd years, afternoon for 2nd year)
   - Check if consecutive periods fit within the day (8 periods max)

3. **Constraint Validation**:
   - Verify no professor conflicts for all required periods
   - Verify no class group conflicts for all required periods
   - Check room availability for all required periods

4. **Room Optimization**:
   - For each valid time slot, evaluate all available rooms
   - Calculate preference score based on professor preferences
   - Select room with highest preference score

5. **Assignment**:
   - Assign all consecutive periods to the selected room
   - Update tracking sets (used_prof, used_room, used_group)
   - Add assignment to timetable

#### 4. Output Generation
- Convert assignments to DataFrame format
- Write to Excel file matching the Output Template structure

### Key Features

#### Smart Room Selection
The algorithm doesn't just pick the first available room. Instead, it:
- Evaluates all valid rooms for each time slot
- Calculates a preference score based on professor preferences
- Selects the room that maximizes professor satisfaction

#### Preference Integration
Professor preferences are integrated as follows:
- Each professor has preferences for specific day-period combinations
- Preferences are weighted in room selection decisions
- Higher preference scores lead to better assignments

#### Flexible Period Assignment
- Classes can be assigned to any valid period if preferred periods are unavailable
- The algorithm gracefully degrades from optimal to feasible assignments
- All hard constraints are always maintained

### Performance Characteristics

- **Time Complexity**: O(n × d × p × r) where n=classes, d=days, p=periods, r=rooms
- **Space Complexity**: O(n × d × p) for tracking assignments
- **Solution Quality**: Feasible solution that respects all hard constraints
- **Scalability**: Can handle the DEM-ISEP dataset efficiently

### Limitations and Future Improvements

1. **Greedy Nature**: The algorithm makes locally optimal choices, which may not lead to globally optimal solutions
2. **No Backtracking**: Once a class is assigned, it's not reconsidered
3. **Simple Preference Model**: Uses additive preference scores

**Potential Improvements**:
- Implement metaheuristics (simulated annealing, genetic algorithm)
- Add backtracking for better solution quality
- Consider more sophisticated preference models
- Add optimization for minimizing gaps between classes

## How to Run
1. Ensure you have Python 3.9+ and the required packages (see `requirements.txt`).
2. Make sure the SQLite database (`timetable-project.db`) is in the project root.
3. Run:
   ```bash
   python main.py
   ```
4. The output will be written in the format required by the Output Template.

## Notes
- The solution uses a constructive heuristic that respects all hard constraints.
- Professor preferences and year-based period prioritization are implemented as soft constraints.
- The algorithm is deterministic and will produce the same result for the same input.
- All code is modular and can be extended for additional constraints or optimization objectives. 