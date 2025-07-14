import sqlite3

def create_tables():
    conn = sqlite3.connect('uctp_database.db')
    cursor = conn.cursor()
    
    try:
        with open('create_tables.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)
    except Exception as e:
        pass
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables() 