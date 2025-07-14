# TimeTableGenerator

A comprehensive University Course Timetabling Problem (UCTP) solver with advanced optimization algorithms and support for new datasets.

## 🎯 Overview

This project implements an advanced, highly-optimized heuristic approach to solve the University Course Timetabling Problem for the Mechanical Engineering Department (DEM) at ISEP. The solution features:

- **200-period per day structure** for maximum flexibility
- **Advanced optimizations** including bitmask-based constraint checking, numpy arrays, and simulated annealing
- **New dataset support** - can import Excel files on the spot
- **100% assignment rate** for well-constrained data
- **Sub-second processing** for typical datasets

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (recommended for best compatibility)
- **pandas**, **openpyxl**, **numpy**

### Installation
```bash
# Clone the repository
git clone https://github.com/CatiaMachado997/TimeTableGenerator.git
cd TimeTableGenerator

# Navigate to the solution directory
cd solution_v3

# Install dependencies
pip install -r requirements.txt
```

### For New Datasets (Recommended)
```bash
# Place your Excel files in data/ directory, then run:
python main_enhanced.py

# Or use the demo script to see it in action:
python run_with_new_data.py
```

### For Existing Users
```bash
# If you have an existing database:
python main.py
```

## 📁 Project Structure

```
TimeTableGenerator/
├── solution_v3/                    # Main solution directory
│   ├── main_enhanced.py           # Enhanced script (new dataset support)
│   ├── main.py                    # Original script (existing database only)
│   ├── run_with_new_data.py       # Demo script
│   ├── example_run.py             # Complete workflow script
│   ├── heuristic.py               # Advanced timetabling algorithm
│   ├── db.py                      # Database operations
│   ├── output_writer.py           # Output generation
│   ├── requirements.txt           # Python dependencies
│   ├── data/                      # Excel files directory
│   │   ├── courses.xlsx           # Course information
│   │   ├── rooms.xlsx             # Room information
│   │   └── preferences.xlsx       # Professor preferences
│   └── Documentation/
│       ├── README.md              # Main documentation
│       ├── QUICK_START.md         # 5-minute setup guide
│       ├── COMPLETE_GUIDE.md      # Comprehensive user guide
│       ├── DATA_FORMAT_GUIDE.md   # Excel format specifications
│       ├── ENHANCED_FEATURES.md   # Technical enhancement details
│       ├── USING_MAIN_ENHANCED.md # How to use enhanced script
│       └── COMMIT_SUMMARY.md      # Development summary
└── .gitignore                     # Git ignore rules
```

## 🔧 Key Features

### **Advanced Algorithm**
- **Bitmask-based constraint checking**: O(1) conflict detection
- **Pre-computed period sequences**: Fast consecutive slot lookup
- **Smart room selection**: Prioritizes less-used and compatible rooms
- **Simulated annealing**: Further optimizes solutions after greedy assignment
- **Numpy arrays**: Efficient memory usage and fast operations
- **Optional parallel processing**: Faster assignment for large datasets

### **New Dataset Support**
- **Automatic Excel file detection** and import
- **Data validation** with comprehensive error checking
- **Smart conflict resolution** between Excel files and existing databases
- **Graceful error handling** for all scenarios

### **Period Structure**
- **Morning periods (1-67)**: 8:00-12:00
- **Afternoon periods (68-133)**: 13:00-17:00
- **Night periods (134-200)**: 18:00-22:00

### **Constraints**
**Hard Constraints (Must be satisfied):**
- No double-booking of professors, rooms, or class groups
- Room type compatibility
- Consecutive periods for multi-period classes

**Soft Constraints (Optimized for):**
- Professor preferences for specific day/period combinations
- Year-based period preferences
- Class group constraints (day vs night classes)

## 📊 Expected Performance

- **Assignment rate**: 100% for well-constrained data
- **Processing time**: 0.1-0.5 seconds for typical datasets
- **Memory usage**: Efficient with numpy arrays
- **Constraint satisfaction**: All hard constraints respected

## 📚 Documentation

### **For New Users**
- **[QUICK_START.md](solution_v3/QUICK_START.md)** - Get up and running in 5 minutes
- **[USING_MAIN_ENHANCED.md](solution_v3/USING_MAIN_ENHANCED.md)** - How to use the enhanced script
- **[DATA_FORMAT_GUIDE.md](solution_v3/DATA_FORMAT_GUIDE.md)** - Excel file format requirements

### **For Advanced Users**
- **[COMPLETE_GUIDE.md](solution_v3/COMPLETE_GUIDE.md)** - Comprehensive workflow guide
- **[ENHANCED_FEATURES.md](solution_v3/ENHANCED_FEATURES.md)** - Technical implementation details

### **For Developers**
- **[COMMIT_SUMMARY.md](solution_v3/COMMIT_SUMMARY.md)** - Development history and changes

## 🎯 Usage Examples

### **Scenario 1: New Dataset**
1. Place Excel files in `solution_v3/data/`
2. Run: `python main_enhanced.py`
3. Follow prompts and view results in `output/`

### **Scenario 2: Demo**
```bash
python run_with_new_data.py
```

### **Scenario 3: Existing Database**
```bash
python main.py
```

## 🛠️ Troubleshooting

### **Common Issues**
1. **"Module not found"**: Run `pip install -r requirements.txt`
2. **"Database not found"**: Use `python main_enhanced.py` for new datasets
3. **"No data imported"**: Check Excel files in `data/` directory
4. **"Low assignment rate"**: Check constraints and room availability
5. **Excel output errors**: Core algorithm still works; check console output

### **Getting Help**
- Check the troubleshooting sections in the documentation
- Review `DATA_FORMAT_GUIDE.md` for correct file formats
- Run the demo script to validate your setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ISEP Mechanical Engineering Department (DEM)** for the original problem specification
- **Advanced optimization techniques** including bitmask operations and simulated annealing
- **Python ecosystem** for pandas, numpy, and openpyxl libraries

---

**Ready to generate optimal timetables? Start with the [Quick Start Guide](solution_v3/QUICK_START.md)! 🚀**