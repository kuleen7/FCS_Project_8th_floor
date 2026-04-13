"""
Add privacy_level column to users table
"""
import psycopg2

def add_privacy_level_column():
    """Add privacy_level column to users table"""
    
    try:
        conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
        cursor = conn.cursor()
        
        # Add privacy_level column if it doesn't exist
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS privacy_level VARCHAR(20) DEFAULT 'public'
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ privacy_level column added successfully")
        
    except Exception as e:
        print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    add_privacy_level_column()
