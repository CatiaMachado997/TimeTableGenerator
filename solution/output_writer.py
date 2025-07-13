import pandas as pd

def write_output(timetable, filename="output_solution.xlsx"):
    # Output columns as in the Output Template
    columns = [
        'Degree', 'Year', 'Semester', 'Class_Group', 'Course', 'Type', 'Professor', 'Room', 'Day', 'Period'
    ]
    timetable = timetable[columns]
    timetable.to_excel(filename, index=False)

    # --- Schedule format ---
    # Create a schedule grid for each class group
    week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    periods = list(range(1, 9))
    class_groups = timetable['Class_Group'].unique()

    with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        for group in class_groups:
            group_df = timetable[timetable['Class_Group'] == group]
            # Create empty grid
            grid = pd.DataFrame('', index=week_days, columns=periods)
            for _, row in group_df.iterrows():
                day = row['Day']
                period = row['Period']
                value = f"{row['Course']} {row['Type']}\n{row['Room']}\n{row['Professor']}"
                # If cell already filled (multi-period class), append
                if grid.at[day, period]:
                    grid.at[day, period] += f"; {value}"
                else:
                    grid.at[day, period] = value
            # Write each group as a separate sheet
            grid.to_excel(writer, sheet_name=f"Schedule_{group}")
        # Optionally, write a summary sheet with all class groups
        # timetable.to_excel(writer, sheet_name="FlatTimetable", index=False) 