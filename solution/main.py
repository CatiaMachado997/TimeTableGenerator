from db import load_all_data
from heuristic import build_timetable
from output_writer import write_output

def main():
    data = load_all_data()
    timetable = build_timetable(data)
    write_output(timetable)

if __name__ == "__main__":
    main() 