# TimeTableGenerator - University Course Timetabling Problem (UCTP) Solver

---

**Documentation Map:**
- [Quick Start Guide](QUICK_START.md)
- [Complete Guide](COMPLETE_GUIDE.md)
- [Data Format Guide](DATA_FORMAT_GUIDE.md)
- [Enhanced Features](ENHANCED_FEATURES.md)
- [How to Use main_enhanced.py](USING_MAIN_ENHANCED.md)

---

## Overview
This project generates optimized university course timetables from real datasets. It supports direct Excel import, robust data validation, and produces output files for review and analysis.

---

## Installation
1. **Clone the repository** (if needed):
   ```bash
   git clone <repo-url>
   cd solution_v3
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run the Main Script
1. **Navigate to the solution_v3 directory:**
   ```bash
   cd solution_v3
   ```
2. **Run the main script:**
   ```bash
   python main_enhanced.py
   ```
   - The script will detect your data and prompt you if both Excel files and a database exist.
   - Type `y` to use the Excel files and regenerate the database.

---

## How to Import a New Dataset and Run the Workflow
1. **Prepare your new dataset:**
   - Place your new Excel files in the `dataset/` directory:
     - `PRJT2_Support_Data_V3.xlsx` (with a `CoursePlan` sheet)
     - `Prof_preferences_v00.xlsx`
2. **Delete or move any old files in `data/` if you want them to be regenerated.**
3. **Run the script:**
   ```bash
   python main_enhanced.py
   ```
   - The script will automatically transform your dataset into the required format, create the database, and generate the timetable.
4. **Check the output:**
   - Output files will be in the `output/` directory:
     - `timetable.xlsx` (main timetable)
     - `detailed_report.xlsx` (detailed assignments)
     - `unassigned_courses.csv` (if any)

---

## Data Format Requirements
- **courses.xlsx**: Must have columns: `Course`, `Year`, `Semester`, `Type`, `Duration`, `Class_Group`, `Professor`, `Value`
- **rooms.xlsx**: Must have columns: `Room ` (with a space), `Type`, `AREA`
- **preferences.xlsx**: Must have columns: `Professor`, `Day`, `TimeSlot`, `Available`

See [DATA_FORMAT_GUIDE.md](DATA_FORMAT_GUIDE.md) for detailed examples.

---

## Dynamic Path Handling

This project uses dynamic path resolution for all key directories:

- **Data and Dataset Folders:**
  - The script automatically searches for the `data/` and `dataset/` directories, starting from the script location and current working directory, and walking up the directory tree.
  - As long as the required files (`courses.xlsx`, `rooms.xlsx`, `preferences.xlsx`) are present in `data/`, the script will find and use them.
  - You can move the `solution_v3` folder, and the script will still work as long as the folder structure is preserved.

- **Output Folder:**
  - All generated files (e.g., `timetable.xlsx`, `detailed_report.xlsx`, `unassigned_courses.csv`) are written to the `output/` directory inside `solution_v3`.
  - Check this folder after running the script for your results.

## Workflow Summary

1. Place your Excel data files in the `data/` directory.
2. Run the main script:
   ```bash
   python main_enhanced.py
   ```
3. The script will:
   - Dynamically find the data and dataset directories
   - Validate and import your data
   - Build the timetable
   - Write all outputs to the `output/` directory

## Troubleshooting
- If you do not see output files, check the terminal for errors or warnings.
- Ensure your data files are named and formatted correctly (see [DATA_FORMAT_GUIDE.md](DATA_FORMAT_GUIDE.md)).
- If you move the project, keep the folder structure intact.
- For further help, see the in-code debug prints or contact the maintainer.

---

## Constraints & Troubleshooting

### Enforced Hard Constraints
1. **No double-booking:** Professors cannot teach multiple classes at the same time.
2. **No room conflicts:** Rooms cannot be used for multiple classes simultaneously.
3. **No class group conflicts:** Class groups cannot have multiple classes at the same time.
4. **Room type compatibility:** Classes are assigned only to compatible room types.
5. **Consecutive periods:** Multi-period classes are scheduled in consecutive periods.
6. **Class group period constraints:**
   - 'D' in group: only morning/afternoon periods
   - 'N' in group: only night periods
   - Others: any period

### Enforced Soft Constraints
- **Professor preferences:** Tries to schedule classes in preferred periods.
- **Year-based preferences:**
  - 1st/3rd year: prefer morning
  - 2nd year: prefer afternoon
  - Night classes: night periods only

### Debug Output for Troubleshooting
- The script prints detailed debug lines for every failed assignment, showing which constraint was violated:
  - `[DEBUG] Rest period violation: ...`
  - `[DEBUG] Bitmask conflict: ...`
  - `[DEBUG] Room type mismatch: ...`
  - `[DEBUG] Day class group scheduled in night period: ...`
  - `[DEBUG] Night class group scheduled outside night period: ...`
- Use these lines to adjust your data or constraints as needed.

---

## Deployment/Production Use

- The code is robust, all constraints are enforced, and the output is correct (see below for troubleshooting blank timetables).
- Dynamic path handling means you can move the project or data folders as needed.
- All documentation is cross-linked for easy navigation.
- For best results, always validate your input data with the provided guides before running in production.
- For automation or integration, use the main_enhanced.py script as the entry point.

---

## FAQ / Common Pitfalls

**Q: Why is my timetable blank (empty output in timetable.xlsx)?**
- A blank timetable means the scheduling algorithm could not assign any courses for your data. This is usually due to:
  - Overly restrictive constraints (e.g., not enough available periods, rooms, or professor availability)
  - Data errors (e.g., missing or mismatched professor names, class groups, or room types)
  - All courses set to inactive (`Value` column not 1)
- **Troubleshooting steps:**
  1. Check the terminal/debug output for lines like `[DEBUG] Assignment failed: ...` or constraint violation messages.
  2. Review your input data for missing or inconsistent values (see [DATA_FORMAT_GUIDE.md](DATA_FORMAT_GUIDE.md)).
  3. Try relaxing constraints or adding more availability in your data.
  4. Ensure all required columns are present and correctly named.
  5. If only one class group is filled, check that all courses have the correct `Class_Group` and `Value` set to 1.

**Q: Where are my output files?**
- All output files are written to the `output/` directory inside `solution_v3`.

**Q: How do I use my own data?**
- See the [Data Format Guide](DATA_FORMAT_GUIDE.md) and [How to Use main_enhanced.py](USING_MAIN_ENHANCED.md).

**Q: What if I get an Excel output error?**
- The script will still complete and print a warning. Check the debug output and try again after fixing any data issues.

---

## Example Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run the main script
python main_enhanced.py
```

---

## Contact
For questions or issues, contact the project maintainer.

---

**See also:** [Quick Start Guide](QUICK_START.md) | [Complete Guide](COMPLETE_GUIDE.md) | [Data Format Guide](DATA_FORMAT_GUIDE.md) | [Enhanced Features](ENHANCED_FEATURES.md) | [How to Use main_enhanced.py](USING_MAIN_ENHANCED.md) 