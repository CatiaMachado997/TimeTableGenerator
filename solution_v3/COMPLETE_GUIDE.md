# Complete Guide: CTP Solver for New Datasets

This comprehensive guide explains how to use the CTP (Course Timetabling Problem) solver with your own dataset from scratch.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Data Format Requirements](#data-format-requirements)
3. [Complete Workflow](#complete-workflow)
4. [File Structure](#file-structure)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Usage](#advanced-usage)

## Quick Start

### Prerequisites

- **Python 3.10+** installed
- Basic command line knowledge
- Excel files with your data

### 5-Minute Setup

1. **Install dependencies**:
   ```bash
   cd solution_v3
   pip install -r requirements.txt
   ```

2. **Run the example script**:
   ```bash
   python example_run.py
   ```

3. **Follow the prompts** to create sample data or import your own

4. **View results** in the `output/` directory

## Data Format Requirements

### Required Excel Files

Place these files in a `data/` directory:

#### 1. `courses.xlsx` - Course Information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Course` | String | Course identifier | "MATH101", "PHYS101" |
| `Year` | Integer | Academic year | 1, 2, 3 |
| `Semester` | Integer | Semester number | 1, 2 |
| `Type` | String | Class type | "T" (Theory), "P" (Practice), "L" (Lab) |
| `Duration` | Integer | Number of periods needed | 1, 2, 3 |
| `Class_Group` | String | Class group identifier | "1DA", "2NB", "3DC" |
| `Professor` | String | Professor identifier | "Prof_A", "Prof_B" |
| `Value` | Integer | Course weight/priority | 1 (active), 0 (inactive) |

**Example**:
```excel
Course   | Year | Semester | Type | Duration | Class_Group | Professor | Value
---------|------|----------|------|----------|-------------|-----------|-------
MATH101  | 1    | 1        | T    | 2        | 1DA        | Prof_A    | 1
PHYS101  | 1    | 1        | T    | 2        | 1DA        | Prof_B    | 1
CHEM101  | 1    | 1        | L    | 3        | 1DB        | Prof_C    | 1
```

#### 2. `rooms.xlsx` - Room Information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Room ` | String | Room identifier | "F101", "F102" |
| `Type` | String | Room type | "Classroom", "Lab", "Computer Lab" |
| `AREA` | String | Building/area | "F", "I", "Main" |

**Example**:
```excel
Room  | Type      | AREA
------|-----------|-----
F101  | Classroom | F
F102  | Classroom | F
F103  | Lab       | F
```

#### 3. `preferences.xlsx` - Professor Preferences

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Professor` | String | Professor identifier | "Prof_A", "Prof_B" |
| `Day` | String | Day of week | "Monday", "Tuesday", "Wednesday", "Thursday", "Friday" |
| `TimeSlot` | Integer | Time slot number | 1, 2, 3, ..., 200 |
| `Available` | Integer | Availability flag | 1 (available), 0 (unavailable) |

**Example**:
```excel
Professor | Day       | TimeSlot | Available
----------|-----------|----------|----------
Prof_A    | Monday    | 1        | 1
Prof_A    | Monday    | 2        | 1
Prof_A    | Monday    | 3        | 0
Prof_B    | Monday    | 1        | 1
```

### Class Group Naming Convention

- **Day classes**: Use 'D' in the group name (e.g., "1DA", "2DB")
- **Night classes**: Use 'N' in the group name (e.g., "1NA", "2NB")
- **Other classes**: Any other naming convention

## Complete Workflow

### Option 1: Automated Workflow (Recommended)

The `example_run.py` script handles everything automatically:

```bash
python example_run.py
```

**What it does**:
1. ✅ Validates Python packages
2. ✅ Creates sample data (if needed)
3. ✅ Imports Excel files to database
4. ✅ Runs timetabling algorithm
5. ✅ Generates output files

### Option 2: Manual Workflow

If you prefer manual control:

1. **Prepare your data** according to the format above
2. **Create database**:
   ```python
   from example_run import create_database_from_excel
   create_database_from_excel("data", "uctp_database.db")
   ```
3. **Run the solution**:
   ```bash
   python main.py
   ```

## File Structure

```
solution_v3/
├── data/                    # Your Excel files go here
│   ├── courses.xlsx
│   ├── rooms.xlsx
│   └── preferences.xlsx
├── example_run.py          # Complete workflow script
├── main.py                 # Main timetabling script
├── heuristic.py            # Advanced algorithm
├── db.py                   # Database operations
├── output_writer.py        # Output generation
├── requirements.txt        # Dependencies
├── README.md              # Main documentation
├── QUICK_START.md         # Quick start guide
├── DATA_FORMAT_GUIDE.md   # Detailed data format guide
├── COMPLETE_GUIDE.md      # This comprehensive guide
└── test_example.py        # Test script for validation
```

## Period Structure

The solver uses a 200-period per day structure:

- **Morning periods (1-67)**: 8:00-12:00
- **Afternoon periods (68-133)**: 13:00-17:00  
- **Night periods (134-200)**: 18:00-22:00

### Class Group Constraints

- **Classes with 'D' in group**: Can only use morning or afternoon periods
- **Classes with 'N' in group**: Can only use night periods
- **Other classes**: Can use any period

## Constraints

### Hard Constraints (Must be satisfied)

1. **No double-booking**: A professor cannot teach multiple classes at the same time
2. **No room conflicts**: A room cannot be used for multiple classes simultaneously
3. **No class group conflicts**: A class group cannot have multiple classes at the same time
4. **Room type compatibility**: Classes must be assigned to compatible room types
5. **Consecutive periods**: Multi-period classes must be scheduled in consecutive periods

### Soft Constraints (Optimized for)

1. **Professor preferences**: Consider professor preferences for specific day/period combinations
2. **Year-based preferences**:
   - First and third years: Prefer morning periods
   - Second year: Prefer afternoon periods
   - Night classes: Use night periods only

## Output Files

After successful execution, you'll find:

### 1. `output/timetable.xlsx`
Main timetable with one sheet per class group showing:
- Rows: Periods 1-200
- Columns: Days (Monday-Friday)
- Cell content: Course name, class type, professor, and room

### 2. `output/detailed_report.xlsx`
Detailed assignment report with:
- All assignments with full details
- Professor workload analysis
- Room utilization statistics
- Constraint satisfaction report

### 3. `output/unassigned_courses.csv`
List of courses that couldn't be assigned (if any)

## Expected Performance

### Typical Results

- **Assignment rate**: 100% for well-constrained data
- **Processing time**: 0.1-0.5 seconds for small datasets
- **Memory usage**: Efficient with numpy arrays
- **Constraint satisfaction**: All hard constraints respected

### Example Output

```
============================================================
UCTP Solver - Complete Workflow Example
============================================================
Validating requirements...
  ✅ pandas
  ✅ openpyxl
  ✅ numpy
All requirements satisfied!

Creating database from Excel files in data...
  Importing courses from data/courses.xlsx
    - Imported 5 course records
  Importing rooms from data/rooms.xlsx
    - Imported 5 room records
  Importing preferences from data/preferences.xlsx
    - Imported 250 preference records
  Creating database indexes...
Database created successfully: uctp_database.db

============================================================
Running UCTP Solver...
============================================================
Loading data from database...
Found 5 courses, 5 rooms, 5 professors
Building timetable...
Assignment completed in 0.15 seconds
Assignment rate: 100% (5/5 courses)
All courses assigned successfully!
Generating output files...
Output files created successfully!

============================================================
Workflow completed successfully!
============================================================
```

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors
```bash
pip install -r requirements.txt
```

#### 2. "Database not found"
- Run `python example_run.py` to create the database
- Or ensure `uctp_database.db` exists in parent directory

#### 3. "No data imported"
- Check that Excel files exist in `data/` directory
- Verify file names: `courses.xlsx`, `rooms.xlsx`, `preferences.xlsx`
- Check `DATA_FORMAT_GUIDE.md` for correct format

#### 4. "Low assignment rate"
- Check if constraints are too restrictive
- Verify room availability and professor preferences
- Ensure sufficient time slots are available

#### 5. "Column not found" errors
- Check that column names match exactly (including spaces)
- Ensure all required columns are present
- Verify data types (numbers vs text)

### Data Quality Checks

Before running the solver:

1. **Verify all required columns** are present
2. **Check for missing or invalid data**
3. **Ensure professor names are consistent** across files
4. **Validate that class groups follow naming conventions**
5. **Check that preference time slots are within valid range** (1-200)

### Getting Help

- **Data format issues**: See `DATA_FORMAT_GUIDE.md`
- **Algorithm details**: See `README.md`
- **Quick start**: See `QUICK_START.md`
- **Code structure**: Check individual Python files

## Advanced Usage

### Customizing Constraints

Edit `heuristic.py` to modify:
- Room type compatibility rules
- Period preferences
- Assignment strategies

### Modifying Output Format

Edit `output_writer.py` to change:
- Excel sheet structure
- Report formats
- Output file names

### Adding New Data Sources

Modify `db.py` to support:
- Different database types
- Additional data formats
- Custom data validation

### Performance Optimization

The algorithm includes several optimizations:
- **Bitmask-based constraint checking**: O(1) conflict detection
- **Pre-computed period sequences**: Fast consecutive slot lookup
- **Smart room selection**: Prioritizes less-used rooms
- **Simulated annealing**: Further optimizes solutions
- **Numpy arrays**: Efficient memory usage
- **Optional parallel processing**: Faster assignment for large datasets

## Testing Your Setup

Run the test script to validate your installation:

```bash
python test_example.py
```

This will:
- Create sample data
- Run the complete workflow
- Verify output files are created
- Check for any errors

## Next Steps

Once you're comfortable with the basic workflow:

1. **Prepare your real data** according to the format guide
2. **Test with a small subset** first
3. **Adjust constraints** if needed
4. **Scale up to your full dataset**
5. **Customize the output format** for your needs

## Support

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Review the data format guide** for correct file structure
3. **Run the test script** to validate your setup
4. **Check the console output** for specific error messages

The solver is designed to be robust and provide clear feedback about any issues with your data or configuration. 