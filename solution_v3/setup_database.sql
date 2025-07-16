-- =====================================================
-- TimeTableGenerator Database Setup
-- University Course Timetabling Problem (UCTP) Solver
-- Mechanical Engineering Department (DEM) - ISEP
-- =====================================================

-- Drop existing tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS Preferences;
DROP TABLE IF EXISTS Rooms;
DROP TABLE IF EXISTS Class;

-- =====================================================
-- Core Tables for TimeTableGenerator
-- =====================================================

-- Main courses table
CREATE TABLE IF NOT EXISTS Class (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Degree TEXT NOT NULL DEFAULT 'MEGI',
    Year INTEGER NOT NULL,
    Semester INTEGER NOT NULL,
    Course TEXT NOT NULL,
    Regime TEXT NOT NULL DEFAULT 'D',
    Language TEXT NOT NULL DEFAULT 'PT',
    Type TEXT NOT NULL,
    Duration INTEGER NOT NULL,
    Professor TEXT NOT NULL,
    Class_Group TEXT NOT NULL,
    Value REAL NOT NULL DEFAULT 1.0
);

-- Rooms information
CREATE TABLE IF NOT EXISTS Rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    "Room " TEXT NOT NULL,
    "Type" TEXT NOT NULL,
    "AREA" TEXT NOT NULL
);

-- Professor preferences
CREATE TABLE IF NOT EXISTS Preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Professor TEXT NOT NULL,
    Day TEXT NOT NULL,
    TimeSlot INTEGER NOT NULL,
    Available INTEGER NOT NULL DEFAULT 1,
    UNIQUE(Professor, Day, TimeSlot)
);

-- =====================================================
-- Indexes for Performance
-- =====================================================

-- Indexes for Class table
CREATE INDEX IF NOT EXISTS idx_class_course ON Class(Course);
CREATE INDEX IF NOT EXISTS idx_class_professor ON Class(Professor);
CREATE INDEX IF NOT EXISTS idx_class_group ON Class(Class_Group);
CREATE INDEX IF NOT EXISTS idx_class_year_semester ON Class(Year, Semester);
CREATE INDEX IF NOT EXISTS idx_class_value ON Class(Value);

-- Indexes for Rooms table
CREATE INDEX IF NOT EXISTS idx_rooms_room ON Rooms("Room ");
CREATE INDEX IF NOT EXISTS idx_rooms_type ON Rooms("Type");

-- Indexes for Preferences table
CREATE INDEX IF NOT EXISTS idx_preferences_professor ON Preferences(Professor);
CREATE INDEX IF NOT EXISTS idx_preferences_day ON Preferences(Day);
CREATE INDEX IF NOT EXISTS idx_preferences_timeslot ON Preferences(TimeSlot);

-- =====================================================
-- Sample Data (Optional - for testing)
-- =====================================================

-- Sample courses (uncomment to add test data)
/*
INSERT INTO Class (Year, Semester, Course, Type, Duration, Professor, Class_Group, Value) VALUES
(1, 1, 'CHEM101', 'T', 2, 'Prof1', '1DA', 1.0),
(1, 1, 'CS101', 'T', 2, 'Prof2', '1DB', 1.0),
(1, 1, 'ENG101', 'T', 2, 'Prof3', '1DC', 1.0),
(1, 1, 'MATH101', 'T', 2, 'Prof4', '1DA', 1.0),
(1, 1, 'PHYS101', 'T', 2, 'Prof5', '1DB', 1.0);

-- Sample rooms (uncomment to add test data)
INSERT INTO Rooms ("Room ", "Type", "AREA") VALUES
('F101', 'Classroom', 'F'),
('F102', 'Classroom', 'F'),
('F103', 'Classroom', 'F'),
('F104', 'Classroom', 'F'),
('F105', 'Classroom', 'F');

-- Sample preferences (uncomment to add test data)
INSERT INTO Preferences (Professor, Day, TimeSlot, Available) VALUES
('Prof1', 'Monday', 1, 1),
('Prof1', 'Monday', 2, 1),
('Prof2', 'Tuesday', 1, 1),
('Prof2', 'Tuesday', 2, 1),
('Prof3', 'Wednesday', 1, 1),
('Prof3', 'Wednesday', 2, 1),
('Prof4', 'Thursday', 1, 1),
('Prof4', 'Thursday', 2, 1),
('Prof5', 'Friday', 1, 1),
('Prof5', 'Friday', 2, 1);
*/

-- =====================================================
-- Database Setup Complete
-- =====================================================

-- Verify tables were created
SELECT 'Database setup completed successfully!' as status;
SELECT 'Tables created:' as info;
SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Class', 'Rooms', 'Preferences'); 