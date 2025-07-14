# Quick Start Guide - UCTP Solver

Get up and running with the UCTP solver in 5 minutes!

## Prerequisites

- **Python 3.10+** installed on your system
- Basic familiarity with command line/terminal

## Step 1: Install Dependencies

Open your terminal/command prompt and navigate to the `solution_v3` directory:

```bash
cd solution_v3
pip install -r requirements.txt
```

## Step 2: Run the Example Script

The easiest way to get started is using the example script:

```bash
python example_run.py
```

This script will:
- ✅ Check if all required packages are installed
- ✅ Create sample data files (if needed)
- ✅ Import data to the database
- ✅ Run the timetabling algorithm
- ✅ Generate output files

## Step 3: Follow the Prompts

The script will guide you through the process:

1. **If sample data is created**: You'll see a message about creating sample files
2. **Database creation**: The script will import Excel files to create the database
3. **Algorithm execution**: The timetabling solver will run automatically
4. **Results**: Check the `output/` directory for your results

## Step 4: View Results

After successful execution, you'll find:

- `output/timetable.xlsx` - Main timetable with all class groups
- `output/detailed_report.xlsx` - Detailed assignment information
- `output/unassigned_courses.csv` - Any courses that couldn't be assigned

## Using Your Own Data

### Option A: Replace Sample Files

1. **Prepare your Excel files** according to `DATA_FORMAT_GUIDE.md`
2. **Place them in the `data/` directory**:
   - `data/courses.xlsx`
   - `data/rooms.xlsx` 
   - `data/preferences.xlsx`
3. **Run the example script again**: `python example_run.py`

### Option B: Manual Database Setup

If you already have a database:

1. **Ensure `uctp_database.db` exists** in the parent directory
2. **Run directly**: `python main.py`

## Expected Output

### Successful Run

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

Output files created in the 'output/' directory:
- timetable.xlsx: Main timetable
- detailed_report.xlsx: Detailed assignment report
- unassigned_courses.csv: Courses that couldn't be assigned (if any)
```

### Performance Metrics

- **Assignment rate**: Should be 100% for well-constrained data
- **Processing time**: Typically 0.1-0.5 seconds for small datasets
- **Memory usage**: Efficient with numpy arrays
- **Constraint satisfaction**: All hard constraints respected

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **"Database not found"**
   - Run `python example_run.py` to create the database
   - Or ensure `uctp_database.db` exists in parent directory

3. **"No data imported"**
   - Check that Excel files exist in `data/` directory
   - Verify file names: `courses.xlsx`, `rooms.xlsx`, `preferences.xlsx`
   - Check `DATA_FORMAT_GUIDE.md` for correct format

4. **"Low assignment rate"**
   - Check if constraints are too restrictive
   - Verify room availability and professor preferences
   - Ensure sufficient time slots are available

### Getting Help

- **Data format issues**: See `DATA_FORMAT_GUIDE.md`
- **Algorithm details**: See `README.md`
- **Code structure**: Check individual Python files for implementation details

## Next Steps

Once you're comfortable with the basic workflow:

1. **Customize constraints** in `heuristic.py`
2. **Modify output format** in `output_writer.py`
3. **Add new data sources** by modifying `db.py`
4. **Optimize for your specific use case**

## Example Data Structure

The sample data includes:

- **5 courses**: MATH101, PHYS101, CHEM101, ENG101, CS101
- **5 rooms**: F101-F105 (classrooms and labs)
- **5 professors**: Prof_A through Prof_E
- **250 preference records**: Full availability matrix

This provides a good starting point for understanding the system before using your own data. 