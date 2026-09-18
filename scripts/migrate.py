import os
import psycopg2
from urllib.parse import urlparse

def get_dsn():
    return os.getenv("POSTGRES_DSN", "postgresql://ai_mentor:postgres@localhost:5432/ai_mentor_db")

def migrate():
    dsn = get_dsn()
    print(f"Connecting to {dsn} to run migrations...")
    
    # Extract components to connect to default 'postgres' db first to create the db if it doesn't exist
    parsed = urlparse(dsn)
    db_name = parsed.path.lstrip('/')
    
    try:
        # Connect to 'postgres' db to create target db
        conn = psycopg2.connect(
            dbname="postgres",
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not cur.fetchone():
            print(f"Creating database {db_name}...")
            cur.execute(f"CREATE DATABASE {db_name}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating db (might already exist or permission issue): {e}")

    # Now connect to target database
    try:
        conn = psycopg2.connect(dsn)
        conn.autocommit = True
        cur = conn.cursor()
        
        with open("docs/database/postgres-schema.sql", "r") as f:
            sql = f.read()
            
        print("Executing schema...")
        cur.execute(sql)
        print("Migration successful.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration failed: {e}")
        exit(1)

if __name__ == "__main__":
    migrate()
