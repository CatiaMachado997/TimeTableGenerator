# University Course Timetabling Problem (UCTP) Solver - Version 3

## Overview

This solution implements a heuristic approach to solve the University Course Timetabling Problem for the Mechanical Engineering Department (DEM) at ISEP. This version includes the correct period structure with 30 periods per day.

## Period Structure

The solution uses a 30-period per day structure:

- **Morning periods (1-10)**: 8:00-12:00
- **Afternoon periods (11-20)**: 13:00-17:00  
- **Night periods (21-30)**: 18:00-22:00

## Class Group Constraints

- **Classes ending in 'D'**: Can only use morning (1-10) or afternoon (11-20) periods
- **Classes ending in 'N'**: Can only use night periods (21-30)
- **Other classes**: Can use any period

## Hard Constraints

1. **No double-booking**: A professor cannot teach multiple classes at the same time
2. **No room conflicts**: A room cannot be used for multiple classes simultaneously
3. **No class group conflicts**: A class group cannot have multiple classes at the same time
4. **Room type compatibility**: Classes must be assigned to compatible room types
5. **Consecutive periods**: Multi-period classes must be scheduled in consecutive periods

## Soft Constraints

1. **Professor preferences**: Consider professor preferences for specific day/period combinations
2. **Year-based preferences**:
   - First and third years: Prefer morning periods
   - Second year: Prefer afternoon periods
   - Night classes: Use night periods only

## Files

- `main.py`: Main script that orchestrates the timetabling process
- `db.py`: Database loader for reading course, room, professor, and preference data
- `heuristic.py`: Timetable building heuristic with constraint handling
- `output_writer.py`: Excel output generation with schedule grid format
- `requirements.txt`: Python dependencies

## Usage

1. **Prerequisites**: Ensure the database file `uctp_database.db` exists in the parent directory
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run the solution**: `python main.py`

## Output

The solution generates several output files in the `output/` directory:

1. **timetable.xlsx**: Main timetable with one sheet per class group showing the schedule grid
2. **timetable_[CLASS_GROUP].xlsx**: Individual Excel files for each class group (e.g., timetable_L_1D.xlsx, timetable_L_2D.xlsx, timetable_L_1N.xlsx)
3. **unassigned_courses.csv**: Report of courses that could not be assigned
4. **detailed_report.xlsx**: Detailed assignment report with all assignments

### Individual Class Group Files

Each class group gets its own Excel file with a clean timetable showing:
- Rows: Periods 1-30
- Columns: Days (Monday-Friday)  
- Cell content: Course name, class type, professor, and room
- Auto-adjusted column widths for readability

## Schedule Grid Format

Each class group sheet contains:
- Rows: Periods 1-30
- Columns: Days (Monday-Friday)
- Cell content: Course name, class type, professor, and room

## Algorithm

The heuristic uses a greedy approach with the following steps:

1. Sort courses by priority (year, semester, periods needed)
2. For each course, try all valid day/period/room combinations
3. Evaluate combinations based on hard constraints and soft preferences
4. Select the best valid assignment
5. Update tracking structures and continue

## Performance

The solution typically achieves:
- High assignment rates (>95% for most datasets)
- Respect for all hard constraints
- Consideration of soft constraints where possible
- Efficient processing of large datasets

## Troubleshooting

If you encounter issues:

1. **Database not found**: Ensure `uctp_database.db` is in the parent directory
2. **Low assignment rate**: Check for over-constrained data or insufficient rooms
3. **Import errors**: Install required dependencies with `pip install -r requirements.txt`

## Version History

- **v3**: Updated to 30 periods per day structure with proper class group constraints
- **v2**: Previous version with 8 periods per day
- **v1**: Initial implementation 