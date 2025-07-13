import pandas as pd
import numpy as np
from collections import defaultdict

def build_timetable(data):
    week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    periods = list(range(1, 9))  # 8 periods per day
    rooms = data['rooms']
    uc_rooms = data['uc_rooms']
    preferences = data['preferences']
    
    # Global state for backtracking
    used_prof = set()  # (day, period, professor)
    used_room = set()  # (day, period, room)
    used_group = set()  # (day, period, class_group)
    timetable = []
    
    # Helper: get valid rooms for a class type and area
    def get_valid_rooms(class_type, area=None):
        if class_type == 'T':
            return rooms[rooms['Type'].str.strip() == 'T']['Room '].tolist()
        elif class_type == 'TP':
            return rooms[rooms['Type'].str.strip() == 'TP']['Room '].tolist()
        elif class_type == 'PL':
            if area:
                return rooms[(rooms['Type'].str.strip() == 'L') & (rooms['AREA'].str.strip() == area)]['Room '].tolist()
            else:
                return rooms[rooms['Type'].str.strip() == 'L']['Room '].tolist()
        else:
            return rooms['Room '].tolist()

    # Helper: get duration for a class
    def get_duration(course, class_type):
        row = uc_rooms[uc_rooms['Class'] == course]
        if row.empty:
            return 1
        if class_type == 'T':
            val = row['T'].values[0]
        elif class_type == 'TP':
            val = row['TP'].values[0]
        elif class_type == 'PL':
            val = row['PL'].values[0]
        else:
            return 1
        if pd.isna(val):
            return 1
        import re
        m = re.search(r'(\d+)h', str(val))
        if m:
            return int(m.group(1))
        return 1

    # Helper: get area for PL class
    def get_area(course):
        row = uc_rooms[uc_rooms['Class'] == course]
        if row.empty:
            return None
        return row['Type Laboratory'].values[0] if 'Type Laboratory' in row else None

    # Helper: get professor preference
    def get_professor_preference(professor, day, period):
        pref_row = preferences[(preferences['Professor'] == professor) & 
                              (preferences['Day'] == day) & 
                              (preferences['TimeSlot'] == period)]
        if not pref_row.empty:
            return pref_row['Available'].iloc[0]
        return 0

    # Helper: check if assignment is valid
    def is_valid_assignment(day, periods_needed, professor, class_group, room):
        for p in periods_needed:
            if (day, p, professor) in used_prof:
                return False
            if (day, p, class_group) in used_group:
                return False
            if (day, p, room) in used_room:
                return False
        return True

    # Helper: make assignment
    def make_assignment(day, periods_needed, professor, class_group, room):
        for p in periods_needed:
            used_prof.add((day, p, professor))
            used_room.add((day, p, room))
            used_group.add((day, p, class_group))
            timetable.append({
                'Degree': row['Degree'],
                'Year': row['Year'],
                'Semester': row['Semester'],
                'Course': row['Course'],
                'Type': row['Type'],
                'Professor': professor,
                'Class_Group': class_group,
                'Room': room,
                'Day': day,
                'Period': p
            })

    # Helper: get preferred periods based on year and regime
    def get_preferred_periods(class_group, regime):
        if class_group.startswith('1') or class_group.startswith('3'):
            if regime == 'D':
                return [1, 2, 3, 4, 5, 6, 7, 8]
            else:
                return [1, 2, 3, 4, 5, 6, 7, 8]
        elif class_group.startswith('2'):
            if regime == 'D':
                return [5, 6, 7, 8, 1, 2, 3, 4]
            else:
                return [1, 2, 3, 4, 5, 6, 7, 8]
        else:
            return [1, 2, 3, 4, 5, 6, 7, 8]

    # Sort classes by priority and complexity
    class_data = data['class'].copy()
    class_data['duration'] = class_data.apply(lambda x: get_duration(x['Course'], x['Type']), axis=1)
    class_data['priority'] = class_data['Class_Group'].apply(
        lambda x: 1 if x.startswith(('1', '3')) else 2
    )
    # Sort by priority first, then by duration (longer classes first)
    class_data = class_data.sort_values(['priority', 'duration'], ascending=[True, False])

    # Phase 1: Try to assign all classes with strict constraints
    unassigned_classes = []
    
    for idx, row in class_data.iterrows():
        assigned = False
        duration = get_duration(row['Course'], row['Type'])
        area = get_area(row['Course']) if row['Type'] == 'PL' else None
        valid_rooms = get_valid_rooms(row['Type'], area)
        preferred_periods = get_preferred_periods(row['Class_Group'], row['Regime'])
        
        # Try all possible combinations systematically
        for day in week_days:
            for period_start in preferred_periods:
                if period_start + duration - 1 > 8:
                    continue
                    
                periods_needed = list(range(period_start, period_start + duration))
                
                # Try each valid room
                for room in valid_rooms:
                    if is_valid_assignment(day, periods_needed, row['Professor'], row['Class_Group'], room):
                        make_assignment(day, periods_needed, row['Professor'], row['Class_Group'], room)
                        assigned = True
                        break
                if assigned:
                    break
            if assigned:
                break
        
        # If still not assigned, try non-preferred periods
        if not assigned:
            non_preferred = [p for p in periods if p not in preferred_periods]
            for day in week_days:
                for period_start in non_preferred:
                    if period_start + duration - 1 > 8:
                        continue
                        
                    periods_needed = list(range(period_start, period_start + duration))
                    
                    for room in valid_rooms:
                        if is_valid_assignment(day, periods_needed, row['Professor'], row['Class_Group'], room):
                            make_assignment(day, periods_needed, row['Professor'], row['Class_Group'], room)
                            assigned = True
                            break
                    if assigned:
                        break
                if assigned:
                    break
        
        if not assigned:
            unassigned_classes.append(row)
    
    print(f"Phase 1 completed: {len(timetable)} classes assigned, {len(unassigned_classes)} remaining")
    
    # Phase 2: Try to assign remaining classes by relaxing room constraints
    still_unassigned = []
    
    for row in unassigned_classes:
        assigned = False
        duration = get_duration(row['Course'], row['Type'])
        all_rooms = rooms['Room '].tolist()
        
        for day in week_days:
            for period_start in periods:
                if period_start + duration - 1 > 8:
                    continue
                    
                periods_needed = list(range(period_start, period_start + duration))
                
                for room in all_rooms:
                    if is_valid_assignment(day, periods_needed, row['Professor'], row['Class_Group'], room):
                        make_assignment(day, periods_needed, row['Professor'], row['Class_Group'], room)
                        assigned = True
                        break
                if assigned:
                    break
            if assigned:
                break
        
        if not assigned:
            still_unassigned.append(row)
    
    print(f"Phase 2 completed: {len(timetable)} classes assigned, {len(still_unassigned)} remaining")
    
    # Phase 3: Final attempt - relax professor conflicts for remaining classes
    for row in still_unassigned:
        assigned = False
        duration = get_duration(row['Course'], row['Type'])
        all_rooms = rooms['Room '].tolist()
        
        for day in week_days:
            for period_start in periods:
                if period_start + duration - 1 > 8:
                    continue
                    
                periods_needed = list(range(period_start, period_start + duration))
                
                # Check only room and group conflicts, ignore professor conflicts
                conflict = False
                for p in periods_needed:
                    if (day, p, row['Class_Group']) in used_group:
                        conflict = True
                        break
                    if (day, p, room) in used_room:
                        conflict = True
                        break
                
                if not conflict:
                    for room in all_rooms:
                        room_available = True
                        for p in periods_needed:
                            if (day, p, room) in used_room:
                                room_available = False
                                break
                        if room_available:
                            make_assignment(day, periods_needed, row['Professor'], row['Class_Group'], room)
                            assigned = True
                            break
                if assigned:
                    break
            if assigned:
                break
        
        if not assigned:
            print(f"WARNING: Could not assign class {row['Course']} {row['Class_Group']} {row['Type']} {row['Professor']}")
    
    print(f"Final result: {len(timetable)} classes assigned out of {len(class_data)}")

    # Output unassigned classes to CSV for reporting
    if len(still_unassigned) > 0:
        pd.DataFrame(still_unassigned).to_csv('unassigned_classes.csv', index=False)
        print(f"Unassigned classes written to unassigned_classes.csv")
    
    return pd.DataFrame(timetable) 