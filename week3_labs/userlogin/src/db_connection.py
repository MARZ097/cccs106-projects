import mysql.connector

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin123",  # 🔑 change this to your MySQL root password
            database="fletapp"
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return None
