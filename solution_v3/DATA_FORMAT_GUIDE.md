# Data Format Guide for CTP Solver

This guide explains the expected format for Excel files that can be imported into the CTP solver.

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