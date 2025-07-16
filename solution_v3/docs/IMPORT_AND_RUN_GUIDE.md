# TimeTableGenerator - Import & Run Guide

This guide explains how to import a new dataset and run the timetable generation algorithm from scratch.

---

## 1. Prepare Your Dataset

You need two Excel files:

### Courses File (e.g., `my_courses.xlsx`)
- Columns: `Course`, `Class`, `Year`, `Semester`, `T`, `TP`, `PL`
- Each row is a course/class. T, TP, PL are the number of periods for each type (can be blank if not used).

### Preferences File (e.g., `my_preferences.xlsx`)
- Columns: `Professor`, `Mon_1`, ..., `Fri_30`
- Each row is a professor. Each cell is 1 (available) or 0 (not available) for that period.

---

## 2. Import the Dataset

Use the flexible import script:

```bash
python import_new_dataset.py path/to/my_courses.xlsx path/to/my_preferences.xlsx
```
- This will clear the database and import your new data.
- (Optional) Add a third argument for a custom database file:
  ```bash
  python import_new_dataset.py path/to/my_courses.xlsx path/to/my_preferences.xlsx my_database.db
  ```

---

## 3. Run the Algorithm

Run the main script:

```bash
python main.py
```
- The algorithm will use the imported data and generate output files in the `output/` folder.

---

## 4. Check the Output

- `output/timetable.xlsx`: Main timetable (one sheet per class group)
- `output/detailed_report.xlsx`: Detailed assignment report
- `output/unassigned_courses.csv`: List of any unassigned courses (if any)

---

## 5. Testing

- You can use the provided `test_courses.xlsx` and `test_preferences.xlsx` for a minimal test.
- For comprehensive testing, use the real dataset in the `dataset/` folder.

---

## 6. Troubleshooting

- **Missing columns**: Make sure your Excel files have the required columns.
- **No assignments**: Check that your data is not over-constrained (e.g., too few rooms or too many unavailable periods).
- **Output errors**: Ensure at least one class is assigned for each group.

---

## 7. Need Help?
If you have a new data format or need to automate batch runs, just ask for help! 