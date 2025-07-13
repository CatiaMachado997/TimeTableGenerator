import pandas as pd
from typing import Dict, List
import os

class OutputWriter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def write_timetable_to_excel(self, timetable: Dict, courses: List[Dict], 
                                rooms: List[Dict], professors: List[Dict], 
                                filename: str = "timetable.xlsx"):
        """Write timetable to Excel with schedule grid format - all class groups in one file"""
        
        # Create a mapping for professor names
        prof_map = {p['ProfessorID']: p['ProfessorName'] for p in professors}
        room_map = {r['RoomID']: r['RoomName'] for r in rooms}
        
        # Get all class groups
        class_groups = list(set(course['ClassGroup'] for course in courses))
        class_groups.sort()
        
        # Create Excel writer
        output_path = os.path.join(self.output_dir, filename)
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            
            # Create one sheet per class group
            for class_group in class_groups:
                self._create_class_group_sheet(writer, timetable, class_group, 
                                             prof_map, room_map)
            
            # Create summary sheet
            self._create_summary_sheet(writer, timetable, courses, class_groups)
        
        print(f"Complete timetable written to: {output_path}")
        print(f"   - {len(class_groups)} class group sheets")
        print(f"   - 1 summary sheet")
        
        return output_path
    
    def _create_class_group_sheet(self, writer, timetable: Dict, class_group: str,
                                 prof_map: Dict, room_map: Dict):
        """Create a sheet for a specific class group"""
        
        # Create data structure for the grid
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        periods = list(range(1, 31))  # 1-30 periods
        
        # Initialize grid data
        grid_data = []
        
        for period in periods:
            row = [f"Period {period}"]
            
            for day in days:
                cell_content = ""
                
                # Find assignments for this day/period for this class group
                day_assignments = timetable[day][period]
                
                for room_id, assignment in day_assignments.items():
                    if assignment['class_group'] == class_group:
                        course_name = assignment['course_name']
                        class_type = assignment['class_type']
                        professor_name = prof_map.get(assignment['professor_id'], 
                                                    assignment['professor_id'])
                        room_name = room_map.get(room_id, room_id)
                        
                        cell_content = f"{course_name}\n{class_type}\n{professor_name}\n{room_name}"
                        break
                
                row.append(cell_content)
            
            grid_data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(grid_data, columns=pd.Index(['Period'] + days))
        
        # Write to Excel
        sheet_name = f"Class_{class_group.replace(' ', '_')}"
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets[sheet_name]
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _create_summary_sheet(self, writer, timetable: Dict, courses: List[Dict], 
                            class_groups: List[str]):
        """Create a summary sheet with statistics"""
        
        # Calculate statistics
        total_courses = len(courses)
        assigned_courses = 0
        unassigned_courses = 0
        
        assigned_course_ids = set()
        for day in timetable.values():
            for period in day.values():
                for assignment in period.values():
                    assigned_course_ids.add(assignment['course_id'])
        
        assigned_courses = len(assigned_course_ids)
        unassigned_courses = total_courses - assigned_courses
        
        # Create summary data
        summary_data = [
            ['Total Courses', total_courses],
            ['Assigned Courses', assigned_courses],
            ['Unassigned Courses', unassigned_courses],
            ['Assignment Rate', f"{(assigned_courses/total_courses*100):.1f}%"],
            [''],
            ['Class Groups', len(class_groups)],
            ['Days', 5],
            ['Periods per Day', 30],
            ['Total Time Slots', 150]
        ]
        
        # Add class group breakdown
        summary_data.append([''])
        summary_data.append(['Class Group Breakdown'])
        
        for class_group in class_groups:
            class_group_assignments = 0
            for day in timetable.values():
                for period in day.values():
                    for assignment in period.values():
                        if assignment['class_group'] == class_group:
                            class_group_assignments += 1
            
            summary_data.append([class_group, class_group_assignments])
        
        # Create DataFrame and write to Excel
        df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
        df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Summary']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def write_unassigned_report(self, unassigned_courses: List[Dict], 
                               filename: str = "unassigned_courses.csv"):
        """Write a report of unassigned courses"""
        if not unassigned_courses:
            print("No unassigned courses to report.")
            return
        
        output_path = os.path.join(self.output_dir, filename)
        
        # Convert to DataFrame
        df = pd.DataFrame(unassigned_courses)
        
        # Reorder columns for better readability
        column_order = ['CourseID', 'CourseName', 'ClassGroup', 'Year', 'Semester', 
                       'ClassType', 'Periods', 'ProfessorID']
        df = df[column_order]
        
        # Write to CSV
        df.to_csv(output_path, index=False)
        print(f"Unassigned courses report written to: {output_path}")
        
        # Print summary
        print(f"\nUnassigned Courses Summary:")
        print(f"Total unassigned: {len(unassigned_courses)}")
        
        # Breakdown by year
        year_counts = df['Year'].value_counts()
        print("\nBy Year:")
        for year, count in year_counts.items():
            print(f"  Year {year}: {count}")
        
        # Breakdown by class group
        group_counts = df['ClassGroup'].value_counts()
        print("\nBy Class Group:")
        for group, count in group_counts.items():
            print(f"  {group}: {count}")
        
        return output_path
    
    def write_detailed_report(self, timetable: Dict, courses: List[Dict], 
                            rooms: List[Dict], professors: List[Dict],
                            filename: str = "detailed_report.xlsx"):
        """Write a detailed report with all assignments"""
        
        output_path = os.path.join(self.output_dir, filename)
        
        # Create detailed data
        detailed_data = []
        
        for day in timetable:
            for period in timetable[day]:
                for room_id, assignment in timetable[day][period].items():
                    detailed_data.append({
                        'Day': day,
                        'Period': period,
                        'Room': room_id,
                        'CourseID': assignment['course_id'],
                        'CourseName': assignment['course_name'],
                        'ClassType': assignment['class_type'],
                        'ClassGroup': assignment['class_group'],
                        'ProfessorID': assignment['professor_id']
                    })
        
        # Create DataFrame
        df = pd.DataFrame(detailed_data)
        
        # Sort by day, period, room
        df = df.sort_values(['Day', 'Period', 'Room'])
        
        # Write to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detailed_Assignments', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Detailed_Assignments']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Detailed report written to: {output_path}")
        return output_path 