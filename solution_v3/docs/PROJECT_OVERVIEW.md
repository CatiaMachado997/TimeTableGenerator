# TimeTableGenerator - Project Overview

## Project Summary
This project is a University Course Timetabling Problem (UCTP) solver for the Mechanical Engineering Department (DEM) at ISEP. It generates valid, constraint-respecting timetables for university courses, professors, and rooms, and outputs professional Excel reports.

## Key Features
- **Heuristic-based scheduling algorithm** with simulated annealing optimization
- **Flexible data import**: Supports any dataset with the required structure
- **Constraint validation**: No double-booking, room/class group/professor conflicts, or rest period violations
- **Rest period support**: Lunch and dinner breaks are respected
- **Professional output**: Excel timetable and detailed report for all class groups
- **Performance**: Schedules 60+ courses in under a second

## Major Improvements
- Switched from a 200-period to a 30-period per day system to match real university data
- Added robust data import scripts for real and test datasets
- Created flexible import for new datasets with the same structure
- Added comprehensive constraint validation and reporting
- Improved day distribution and assignment rate
- Added rest period constraints (lunch/dinner breaks)
- Simplified database setup with a single SQL file and setup script
- Created minimal and comprehensive test datasets for validation

## Testing & Validation
- **Minimal test**: 3 courses, 3 professors, 100% assignment rate
- **Real data test**: 66 courses, 66 professors, 91% assignment rate, all constraints respected
- **Comprehensive test script**: Validates constraints, distribution, rest periods, and output generation
- **Output**: All tests generate Excel files with correct assignments and statistics

## Output Files
- `output/timetable.xlsx`: Main timetable with one sheet per class group
- `output/detailed_report.xlsx`: Detailed assignment report
- `output/unassigned_courses.csv`: List of any unassigned courses (if any)

## Ready for Production
- The system is now production-ready and can be used for real university scheduling or further research/automation. 