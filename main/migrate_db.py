"""
Database migration script to add medical_conditions column
"""
import pymysql
from config import DB_CONFIG

try:
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Check if column already exists
    cur.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME='users' AND COLUMN_NAME='medical_conditions'
    """)
    
    if cur.fetchone():
        print("✅ Column 'medical_conditions' already exists")
    else:
        # Add the column
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN medical_conditions TEXT NULL DEFAULT NULL
        """)
        conn.commit()
        print("✅ Added 'medical_conditions' column to users table")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
