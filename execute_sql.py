import sqlite3
import sys

def execute_sql_file(sql_file_path):
    conn = sqlite3.connect('timetable-project.db')
    cursor = conn.cursor()
    
    try:
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)
        conn.commit()
    except Exception as e:
        pass
    
    conn.close()

def execute_sql_query(sql_query):
    conn = sqlite3.connect('timetable-project.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.commit()
        return results
    except Exception as e:
        pass
    
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].endswith('.sql'):
            execute_sql_file(sys.argv[1])
        else:
            query = ' '.join(sys.argv[1:])
            results = execute_sql_query(query)
            if results:
                for row in results:
                    print(row) 