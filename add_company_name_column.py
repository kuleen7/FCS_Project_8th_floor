"""
Add company_name column to users table
"""
import psycopg2

def add_company_name_column():
    """Add company_name column to users table"""
    
    try:
        conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
        cursor = conn.cursor()
        
        # Add company_name column if it doesn't exist
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS company_name VARCHAR(255)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ company_name column added successfully")
        
    except Exception as e:
        print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    add_company_name_column()
