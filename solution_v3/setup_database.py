#!/usr/bin/env python3
"""
TimeTableGenerator Database Setup Script
University Course Timetabling Problem (UCTP) Solver
Mechanical Engineering Department (DEM)

This script creates a simplified database with only the essential tables
needed for the TimeTableGenerator solution.
"""

import sqlite3
import os
import sys

def setup_database(db_path: str = "uctp_database.db"):
    """Set up the database with essential tables"""
    
    print("=" * 60)
    print("TimeTableGenerator Database Setup")
    print("University Course Timetabling Problem (UCTP) Solver")
    print("Mechanical Engineering Department (DEM)")
    print("=" * 60)
    
    # Check if database already exists
    if os.path.exists(db_path):
        print(f"\n⚠️  Database '{db_path}' already exists!")
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response != 'y':
            print("Database setup cancelled.")
            return False
        else:
            print(f"Removing existing database '{db_path}'...")
            os.remove(db_path)
    
    try:
        # Create database connection
        print(f"\n1. Creating database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute SQL file
        print("2. Reading setup SQL file...")
        sql_file = "setup_database.sql"
        
        if not os.path.exists(sql_file):
            print(f"❌ Error: SQL file '{sql_file}' not found!")
            print("Please ensure 'setup_database.sql' is in the same directory.")
            return False
        
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        print("3. Executing SQL script...")
        cursor.executescript(sql_script)
        
        # Verify tables were created
        print("4. Verifying database setup...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['Class', 'Rooms', 'Preferences']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Error: Missing tables: {missing_tables}")
            return False
        
        print(f"✅ Database setup completed successfully!")
        print(f"   - Created {len(tables)} tables")
        print(f"   - Required tables: {', '.join(required_tables)}")
        
        # Show table schemas
        print("\n5. Table schemas:")
        for table in required_tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"\n   {table}:")
            for col in columns:
                col_name, col_type, not_null, default_val, pk = col[1:6]
                pk_str = " (PK)" if pk else ""
                print(f"     - {col_name}: {col_type}{pk_str}")
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print(f"\n✅ Database '{db_path}' is ready for use!")
        print("\nNext steps:")
        print("1. Import your course data into the 'Class' table")
        print("2. Import your room data into the 'Rooms' table") 
        print("3. Import professor preferences into the 'Preferences' table")
        print("4. Run the timetabling solution: python main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "uctp_database.db"
    
    success = setup_database(db_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 