#!/usr/bin/env python3
"""
Quick Demo: Running UCTP Solver with New Datasets on the Spot

This script demonstrates how to use the enhanced main script
to handle new datasets immediately without any setup.
"""

import os
import sys
import pandas as pd

def create_demo_data():
    """Create demo Excel files to show the enhanced functionality"""
    
    print("🎯 Creating demo dataset to show enhanced functionality...")
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Demo courses data
    courses_data = {
        'Course': ['MATH101', 'PHYS101', 'CHEM101', 'ENG101', 'CS101', 'BIO101'],
        'Year': [1, 1, 1, 1, 1, 1],
        'Semester': [1, 1, 1, 1, 1, 1],
        'Type': ['T', 'T', 'L', 'P', 'T', 'L'],
        'Duration': [2, 2, 3, 2, 2, 3],
        'Class_Group': ['1DA', '1DA', '1DB', '1DB', '1DC', '1DC'],
        'Professor': ['Prof_A', 'Prof_B', 'Prof_C', 'Prof_D', 'Prof_E', 'Prof_F'],
        'Value': [1, 1, 1, 1, 1, 1]
    }
    
    courses_df = pd.DataFrame(courses_data)
    courses_df.to_excel("data/courses.xlsx", index=False)
    print("  ✅ Created data/courses.xlsx")
    
    # Demo rooms data
    rooms_data = {
        'Room ': ['F101', 'F102', 'F103', 'F104', 'F105', 'F106'],
        'Type': ['Classroom', 'Classroom', 'Lab', 'Classroom', 'Lab', 'Computer Lab'],
        'AREA': ['F', 'F', 'F', 'F', 'F', 'F']
    }
    
    rooms_df = pd.DataFrame(rooms_data)
    rooms_df.to_excel("data/rooms.xlsx", index=False)
    print("  ✅ Created data/rooms.xlsx")
    
    # Demo preferences data
    preferences_data = []
    professors = ['Prof_A', 'Prof_B', 'Prof_C', 'Prof_D', 'Prof_E', 'Prof_F']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for prof in professors:
        for day in days:
            for timeslot in range(1, 21):  # 20 time slots for demo
                preferences_data.append({
                    'Professor': prof,
                    'Day': day,
                    'TimeSlot': timeslot,
                    'Available': 1  # All available for demo
                })
    
    preferences_df = pd.DataFrame(preferences_data)
    preferences_df.to_excel("data/preferences.xlsx", index=False)
    print("  ✅ Created data/preferences.xlsx")
    
    print(f"📁 Demo dataset created with:")
    print(f"   - {len(courses_df)} courses")
    print(f"   - {len(rooms_df)} rooms")
    print(f"   - {len(preferences_df)} preference records")

def main():
    """Main demonstration function"""
    
    print("=" * 60)
    print("🚀 UCTP Solver - New Dataset Demo")
    print("=" * 60)
    
    print("\nThis demo shows how the enhanced main script can handle")
    print("new datasets on the spot without any pre-processing!")
    
    # Check if demo data exists
    if not os.path.exists("data/courses.xlsx"):
        print("\n📝 Creating demo dataset...")
        create_demo_data()
    else:
        print("\n✅ Demo dataset already exists")
    
    print("\n" + "=" * 60)
    print("🎯 Now running the enhanced main script...")
    print("=" * 60)
    
    # Import and run the enhanced main script
    try:
        from main_enhanced import main as enhanced_main
        enhanced_main()
        
    except ImportError:
        print("❌ Enhanced main script not found!")
        print("Please ensure main_enhanced.py exists in the current directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running enhanced main script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 