import pandas as pd
import sqlite3
import os
from typing import Dict, List, Tuple

class DatabaseLoader:
    def __init__(self, db_path: str = "uctp_database.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        return self.conn
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
    
    def load_courses(self) -> List[Dict]:
        """Load all courses from the database"""
        query = """
        SELECT DISTINCT 
               Course as CourseID,
               Course as CourseName,
               0 as Credits,
               Year,
               Semester,
               Type as ClassType,
               Duration as Periods,
               Class_Group as ClassGroup,
               Professor as ProfessorID
        FROM Class
        ORDER BY Year, Semester, Course, Class_Group
        """
        df = pd.read_sql_query(query, self.conn)
        return df.to_dict('records')
    
    def load_rooms(self) -> List[Dict]:
        """Load all rooms from the database"""
        query = """
        SELECT 
               "Room " as RoomID,
               "Room " as RoomName,
               50 as Capacity,
               "Type" as RoomType,
               "AREA" as Building
        FROM Rooms
        ORDER BY "Room "
        """
        df = pd.read_sql_query(query, self.conn)
        return df.to_dict('records')
    
    def load_professors(self) -> List[Dict]:
        """Load all professors from the database"""
        query = """
        SELECT DISTINCT 
               Professor as ProfessorID,
               Professor as ProfessorName,
               'DEM' as Department
        FROM Class
        ORDER BY Professor
        """
        df = pd.read_sql_query(query, self.conn)
        return df.to_dict('records')
    
    def load_preferences(self) -> List[Dict]:
        """Load professor preferences from the database"""
        query = """
        SELECT DISTINCT 
               Professor as ProfessorID,
               Day as DayOfWeek,
               TimeSlot as Period,
               CASE 
                   WHEN Available = 1 THEN 'Preferred'
                   WHEN Available = 0 THEN 'Forbidden'
                   ELSE 'Acceptable'
               END as Preference
        FROM Preferences
        ORDER BY Professor, Day, TimeSlot
        """
        df = pd.read_sql_query(query, self.conn)
        return df.to_dict('records')
    
    def load_class_groups(self) -> List[Dict]:
        """Load class groups from the database"""
        query = """
        SELECT DISTINCT 
               Class_Group as ClassGroup,
               Year,
               30 as NumberOfStudents
        FROM Class
        ORDER BY Year, Class_Group
        """
        df = pd.read_sql_query(query, self.conn)
        return df.to_dict('records')
    
    def get_course_requirements(self, course_id: str) -> Dict:
        """Get specific requirements for a course"""
        query = """
        SELECT 
               Course as CourseID,
               Course as CourseName,
               0 as Credits,
               Year,
               Semester,
               Type as ClassType,
               Duration as Periods,
               Class_Group as ClassGroup,
               Professor as ProfessorID,
               'General' as RequiredRoomType
        FROM Class
        WHERE Course = ?
        """
        df = pd.read_sql_query(query, self.conn, params=[course_id])
        if not df.empty:
            return df.iloc[0].to_dict()
        return {}
    
    def get_professor_preferences(self, professor_id: str) -> List[Dict]:
        """Get preferences for a specific professor"""
        query = """
        SELECT 
               Day as DayOfWeek,
               TimeSlot as Period,
               CASE 
                   WHEN Available = 1 THEN 'Preferred'
                   WHEN Available = 0 THEN 'Forbidden'
                   ELSE 'Acceptable'
               END as Preference
        FROM Preferences
        WHERE Professor = ?
        ORDER BY Day, TimeSlot
        """
        df = pd.read_sql_query(query, self.conn, params=[professor_id])
        return df.to_dict('records')
    
    def get_available_rooms(self, room_type: str = None) -> List[Dict]:
        """Get available rooms, optionally filtered by type"""
        if room_type:
            query = """
            SELECT 
                   "Room " as RoomID,
                   "Room " as RoomName,
                   50 as Capacity,
                   "Type" as RoomType,
                   "AREA" as Building
            FROM Rooms
            WHERE "Type" = ?
            ORDER BY "Room "
            """
            df = pd.read_sql_query(query, self.conn, params=[room_type])
        else:
            query = """
            SELECT 
                   "Room " as RoomID,
                   "Room " as RoomName,
                   50 as Capacity,
                   "Type" as RoomType,
                   "AREA" as Building
            FROM Rooms
            ORDER BY "Room "
            """
            df = pd.read_sql_query(query, self.conn)
        return df.to_dict('records')
    
    def get_courses_by_year(self, year: int) -> List[Dict]:
        """Get all courses for a specific year"""
        query = """
        SELECT DISTINCT 
               Course as CourseID,
               Course as CourseName,
               0 as Credits,
               Year,
               Semester,
               Type as ClassType,
               Duration as Periods,
               Class_Group as ClassGroup,
               Professor as ProfessorID
        FROM Class
        WHERE Year = ?
        ORDER BY Semester, Course, Class_Group
        """
        df = pd.read_sql_query(query, self.conn, params=[year])
        return df.to_dict('records')
    
    def get_courses_by_class_group(self, class_group: str) -> List[Dict]:
        """Get all courses for a specific class group"""
        query = """
        SELECT DISTINCT 
               Course as CourseID,
               Course as CourseName,
               0 as Credits,
               Year,
               Semester,
               Type as ClassType,
               Duration as Periods,
               Class_Group as ClassGroup,
               Professor as ProfessorID
        FROM Class
        WHERE Class_Group = ?
        ORDER BY Year, Semester, Course
        """
        df = pd.read_sql_query(query, self.conn, params=[class_group])
        return df.to_dict('records') 