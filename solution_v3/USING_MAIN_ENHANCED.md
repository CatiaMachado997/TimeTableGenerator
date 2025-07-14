# How to Use `main_enhanced.py` to Import a New Dataset and Run the Heuristic

This guide explains how to use the enhanced main script (`main_enhanced.py`) to import a new dataset (Excel files) and generate a timetable using the advanced heuristic algorithm.

---

## 📦 **Step 1: Prepare Your Dataset**

1. **Create a `data/` directory** in the `solution_v3` folder (if it doesn't exist).
2. **Place your Excel files** in the `data/` directory:
   - `courses.xlsx` — Course information
   - `rooms.xlsx` — Room information
   - `preferences.xlsx` — Professor preferences

> **See `DATA_FORMAT_GUIDE.md` for required columns and format!**

**Example structure:**
```
solution_v3/
├── data/
│   ├── courses.xlsx
│   ├── rooms.xlsx
│   └── preferences.xlsx
```

---

## ▶️ **Step 2: Run the Enhanced Main Script**

Open a terminal in the `solution_v3` directory and run:

```bash
python main_enhanced.py
```

---

## 🧠 **What Happens Next?**

1. **Automatic Data Source Detection**
   - The script checks for Excel files in `data/` and/or an existing database.
2. **Validation**
   - Validates your Excel files for required columns and data quality.
3. **Database Creation**
   - If Excel files are found, imports them into a new SQLite database (`uctp_database.db`).
   - If both Excel files and a database exist, you will be prompted to choose which to use.
4. **Heuristic Timetabling**
   - Loads all data and runs the advanced heuristic algorithm to generate a timetable.
5. **Output Generation**
   - Attempts to write the timetable and reports to the `output/` directory (Excel output errors are handled gracefully).

---

## 📂 **Expected Output**

- `output/timetable.xlsx` — Main timetable (if Excel output succeeds)
- `output/detailed_report.xlsx` — Detailed assignment report
- `output/unassigned_courses.csv` — List of unassigned courses (if any)

> If there is an Excel output error, the script will still complete and inform you that the timetable was generated in memory.

---

## 🛠️ **Troubleshooting**

- **Missing or invalid columns:**
  - Check your Excel files against `DATA_FORMAT_GUIDE.md`.
- **Prompt: 'Use Excel files (overwrite database)?'**
  - Type `y` to use your new dataset, or `n` to use the existing database.
- **Excel output error:**
  - This does not affect the core algorithm; results are still valid.
- **No data found:**
  - Ensure your Excel files are in the correct location and named exactly as required.
- **Assignment rate is low:**
  - Check for over-constrained data or missing professor preferences.

---

## 📝 **Example Workflow**

1. **Copy your Excel files to `solution_v3/data/`**
2. **Run:**
   ```bash
   python main_enhanced.py
   ```
3. **Follow any prompts** (e.g., to overwrite the database)
4. **Check the terminal output for assignment statistics and any warnings**
5. **Review the generated files in `output/`**

---

## 📚 **Related Documentation**
- `DATA_FORMAT_GUIDE.md` — Excel file format and requirements
- `ENHANCED_FEATURES.md` — Technical details of the enhanced workflow
- `COMPLETE_GUIDE.md` — Full end-to-end workflow
- `README.md` — Project overview and quick start

---

## 💡 **Tip**
You can use the demo script to see the workflow in action with sample data:
```bash
python run_with_new_data.py
```

---

**Now you can import new datasets and generate timetables on the spot! 🚀** 