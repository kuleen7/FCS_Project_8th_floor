#!/usr/bin/env python3
"""
Quick OTP Retrieval Script
Run this after registration to get the latest OTP code
"""
import psycopg2
import sys

def get_latest_otp():
    try:
        conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
        cursor = conn.cursor()
        cursor.execute('SELECT otp_code FROM otp_verifications ORDER BY created_at DESC LIMIT 1')
        otp = cursor.fetchone()
        conn.close()
        
        if otp:
            print(f"🔐 LATEST OTP: {otp[0]}")
            print("✅ Copy this code and enter it in the frontend OTP verification page")
            return otp[0]
        else:
            print("❌ No OTP found. Make sure you've registered a user first.")
            return None
            
    except Exception as e:
        print(f"❌ Error getting OTP: {e}")
        print("Make sure the backend is running and database is accessible.")
        return None

def check_users():
    """Check current users in database"""
    try:
        conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
        cursor = conn.cursor()
        cursor.execute('SELECT email, is_verified, is_active FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        
        if users:
            print("\n📋 Current Users:")
            for email, verified, active in users:
                status = "✅ Verified" if verified else "❌ Not Verified"
                print(f"  • {email} - {status}")
        else:
            print("\n📋 No users in database")
            
    except Exception as e:
        print(f"❌ Error checking users: {e}")

if __name__ == "__main__":
    print("🔍 OTP Retrieval Tool")
    print("=" * 40)
    
    # Check users first
    check_users()
    
    # Get latest OTP
    print("\n🔐 Getting Latest OTP...")
    otp = get_latest_otp()
    
    if otp:
        print(f"\n🎯 Next Steps:")
        print(f"1. Go to http://localhost:3000/verify-otp")
        print(f"2. Enter OTP: {otp}")
        print(f"3. Click 'Verify Email'")
        print(f"4. Login with your credentials")
    else:
        print(f"\n📝 To get an OTP:")
        print(f"1. Register a new user at http://localhost:3000")
        print(f"2. Run this script again to get the OTP")
