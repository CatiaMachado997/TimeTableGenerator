# Data Format Guide for UCTP Solver

This guide explains the expected format for Excel files that can be imported into the UCTP solver.

## File Structure

Place your Excel files in a `data/` directory:

```
data/
├── courses.xlsx          # Course information
├── rooms.xlsx            # Room information  
└── preferences.xlsx      # Professor preferences
```

## 1. Courses Data (`courses.xlsx`)

### Required Columns:

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

### Example Data:

```excel
Course   | Year | Semester | Type | Duration | Class_Group | Professor | Value
---------|------|----------|------|----------|-------------|-----------|-------
MATH101  | 1    | 1        | T    | 2        | 1DA        | Prof_A    | 1
PHYS101  | 1    | 1        | T    | 2        | 1DA        | Prof_B    | 1
CHEM101  | 1    | 1        | L    | 3        | 1DB        | Prof_C    | 1
ENG101   | 1    | 1        | P    | 2        | 1DB        | Prof_D    | 1
CS101    | 1    | 1        | T    | 2        | 1DC        | Prof_E    | 1
```

### Class Group Naming Convention:

- **Day classes**: Use 'D' in the group name (e.g., "1DA", "2DB")
- **Night classes**: Use 'N' in the group name (e.g., "1NA", "2NB")
- **Other classes**: Any other naming convention

## 2. Rooms Data (`rooms.xlsx`)

### Required Columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Room ` | String | Room identifier | "F101", "F102" |
| `Type` | String | Room type | "Classroom", "Lab", "Computer Lab" |
| `AREA` | String | Building/area | "F", "I", "Main" |

### Example Data:

```excel
Room  | Type      | AREA
------|-----------|-----
F101  | Classroom | F
F102  | Classroom | F
F103  | Lab       | F
F104  | Classroom | F
F105  | Lab       | F
```

## 3. Preferences Data (`preferences.xlsx`)

### Required Columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Professor` | String | Professor identifier | "Prof_A", "Prof_B" |
| `Day` | String | Day of week | "Monday", "Tuesday", "Wednesday", "Thursday", "Friday" |
| `TimeSlot` | Integer | Time slot number | 1, 2, 3, ..., 200 |
| `Available` | Integer | Availability flag | 1 (available), 0 (unavailable) |

### Example Data:

```excel
Professor | Day       | TimeSlot | Available
----------|-----------|----------|----------
Prof_A    | Monday    | 1        | 1
Prof_A    | Monday    | 2        | 1
Prof_A    | Monday    | 3        | 0
Prof_A    | Tuesday   | 1        | 1
Prof_B    | Monday    | 1        | 1
Prof_B    | Monday    | 2        | 0
```

## Data Validation Rules

### Courses:
- `Year` must be 1, 2, or 3
- `Semester` must be 1 or 2
- `Duration` must be positive integer
- `Value` should be 1 for active courses, 0 for inactive
- `Class_Group` should follow naming convention for day/night classes

### Rooms:
- `Room ` column name must include a space at the end
- Room identifiers should be unique
- Room types are used for compatibility checking

### Preferences:
- `Day` must be one of: "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
- `TimeSlot` must be between 1 and 200 (for 200-period structure)
- `Available` must be 0 or 1

## Period Structure

The solver uses a 200-period per day structure:

- **Morning periods (1-67)**: 8:00-12:00
- **Afternoon periods (68-133)**: 13:00-17:00  
- **Night periods (134-200)**: 18:00-22:00

## Class Group Constraints

- **Classes with 'D' in group**: Can only use morning or afternoon periods
- **Classes with 'N' in group**: Can only use night periods
- **Other classes**: Can use any period

## Tips for Data Preparation

1. **Ensure data consistency**: All professor names in courses must exist in preferences
2. **Check for duplicates**: Avoid duplicate course-class-group combinations
3. **Validate periods**: Make sure preference time slots are within valid range
4. **Room capacity**: Consider adding room capacity if needed for large classes
5. **Backup your data**: Always keep backups of your original Excel files

## Running with Your Data

1. Prepare your Excel files according to the format above
2. Place them in a `data/` directory
3. Run: `python example_run.py`
4. The script will guide you through the import process

## Troubleshooting

### Common Issues:

1. **"Column not found"**: Check that column names match exactly (including spaces)
2. **"Invalid data type"**: Ensure numeric columns contain only numbers
3. **"Professor not found"**: All professors in courses must have preference records
4. **"No valid assignments"**: Check if constraints are too restrictive

### Data Quality Checks:

- Verify all required columns are present
- Check for missing or invalid data
- Ensure professor names are consistent across files
- Validate that class groups follow naming conventions 