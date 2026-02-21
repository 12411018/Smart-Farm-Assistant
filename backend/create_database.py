"""Create the smart_irrigation database if it doesn't exist"""

import psycopg2
from psycopg2 import sql

# Connect to default 'postgres' database first
try:
    # Connect to the default postgres database
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='Parth@2006',
        host='localhost',
        port=5432
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='smart_irrigation'")
    exists = cursor.fetchone()
    
    if exists:
        print("✅ Database 'smart_irrigation' already exists!")
    else:
        # Create the database
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier('smart_irrigation')
        ))
        print("✅ Database 'smart_irrigation' created successfully!")
    
    cursor.close()
    conn.close()
    
except psycopg2.Error as e:
    print(f"❌ Error: {e}")
    print("\nMake sure:")
    print("1. PostgreSQL is running")
    print("2. Password is correct (Parth@2006)")
    print("3. User 'postgres' has database creation permissions")
