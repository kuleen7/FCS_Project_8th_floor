# 🎉 **COMPLETE TESTING GUIDE - DATABASE CLEARED**

## ✅ **DATABASE COMPLETELY CLEARED**

All previous users, companies, jobs, and data have been removed. The database is fresh and ready for testing!

---

## 🚀 **STEP-BY-STEP FRONTEND TESTING**

### **Step 1: Open Chrome Browser**
1. Open Google Chrome
2. Go to: `http://localhost:3000`
3. You should see the Secure Job Search Platform homepage

### **Step 2: Register a New User**
1. Click **"Create one"** button
2. Fill in the registration form with **EXACTLY** these details:

```
Email: chris@jobsearch.com
Password: Secure123!
Mobile: 1234567890
First Name: Chris
Last Name: Wilson
```

3. Click **"Create account"** button

### **Step 3: Get OTP Code**
1. Open **Command Prompt** or **PowerShell**
2. Navigate to the backend folder:
   ```bash
   cd c:\Users\siddh_ygv5bws\OneDrive\Desktop\fcs_8_floor-main\backend
   ```
3. Run this command to get the OTP:
   ```bash
   python -c "
   import psycopg2
   conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
   cursor = conn.cursor()
   cursor.execute('SELECT otp_code FROM otp_verifications ORDER BY created_at DESC LIMIT 1')
   otp = cursor.fetchone()
   if otp:
       print('OTP:', otp[0])
   else:
       print('No OTP found')
   conn.close()
   "
   ```

4. You'll see something like: `OTP: 123456`

### **Step 4: Verify Email (AUTOMATIC REDIRECT)**
1. After registration, you should be **automatically redirected** to the OTP verification page
2. Enter the 6-digit OTP code you got
3. Click **"Verify Email"**
4. You should see "Email verified successfully! Redirecting to login..."

### **Step 5: Login Successfully**
1. You'll be automatically redirected to the login page
2. Enter your credentials:
   ```
   Email: chris@jobsearch.com
   Password: Secure123!
   ```
3. Click **"Sign in"**
4. ✅ You should be redirected to the dashboard!

---

## 🔍 **IF SOMETHING DOESN'T WORK**

### **If Registration Fails:**
1. Check browser console (F12 → Console) for errors
2. Make sure all fields are filled correctly
3. Use the exact credentials above

### **If OTP Page Doesn't Load:**
1. Check if frontend is running: `http://localhost:3000`
2. Refresh the page
3. Make sure registration was successful

### **If OTP Verification Fails:**
1. Get the latest OTP (wait 30 seconds after registration)
2. Enter exactly 6 digits
3. Check for leading zeros

### **If Login Fails:**
1. Make sure you completed OTP verification
2. Check email and password are correct
3. Try refreshing the login page

---

## 🌟 **AFTER SUCCESSFUL LOGIN - TEST ALL FEATURES**

### **1. Create a Company**
1. In the dashboard, look for "Companies" or "Create Company"
2. Fill in company details:
   ```
   Name: Tech Solutions Inc
   Description: A technology company
   Location: San Francisco
   ```
3. Click "Create Company"

### **2. Post a Job**
1. Go to "Jobs" section
2. Click "Post Job"
3. Fill in job details:
   ```
   Title: Software Engineer
   Description: Develop web applications
   Location: Remote
   Job Type: remote
   ```
4. Click "Post Job"

### **3. Test Encrypted Messaging**
1. Go to "Messages" section
2. Create a new conversation
3. Send a test message (it will be encrypted)

### **4. Check Audit Logs**
1. Look for "Audit" or "Admin" section
2. View the audit logs to see your activities

---

## 📱 **QUICK TEST COMMANDS**

### **Get OTP Anytime:**
```bash
cd c:\Users\siddh_ygv5bws\OneDrive\Desktop\fcs_8_floor-main\backend
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
cursor = conn.cursor()
cursor.execute('SELECT otp_code FROM otp_verifications ORDER BY created_at DESC LIMIT 1')
otp = cursor.fetchone()
if otp:
    print('OTP:', otp[0])
else:
    print('No OTP found')
conn.close()
"
```

### **Check User Status:**
```bash
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
cursor = conn.cursor()
cursor.execute('SELECT email, is_verified, is_active FROM users')
users = cursor.fetchall()
for email, verified, active in users:
    print(f'{email} - Verified: {verified}, Active: {active}')
conn.close()
"
```

---

## 🎯 **SUCCESS INDICATORS**

You'll know everything is working when you see:

1. ✅ **Registration:** "Account created successfully! Please check your email for verification code."
2. ✅ **Auto-Redirect:** Goes to OTP verification page automatically
3. ✅ **OTP Verification:** "Email verified successfully! Redirecting to login..."
4. ✅ **Login:** Successfully logs in and redirects to dashboard
5. ✅ **Dashboard:** Shows user profile and navigation options
6. ✅ **Features:** Can create companies, post jobs, send messages

---

## 🛠️ **SERVER STATUS CHECK**

### **Backend Status:**
```bash
Invoke-WebRequest -Uri "http://localhost:8000/api/health"
```
Should return: `{"status":"healthy"}`

### **Frontend Status:**
```bash
Invoke-WebRequest -Uri "http://localhost:3000"
```
Should return HTML page

---

## 🎉 **EXPECTED FINAL RESULT**

If everything works correctly, you should be able to:

1. ✅ Register a new user without any errors
2. ✅ Verify email with OTP automatically
3. ✅ Login successfully to the dashboard
4. ✅ Create companies and post jobs
5. ✅ Send encrypted messages
6. ✅ View audit logs
7. ✅ Access all March milestone features

---

## 📞 **TROUBLESHOOTING CHECKLIST**

- [ ] Both servers are running (no error messages)
- [ ] Database is completely cleared (done!)
- [ ] Using fresh, unique credentials
- [ ] Following steps exactly as written
- [ ] Checking browser console for errors
- [ ] Getting OTP from database correctly
- [ ] Entering OTP exactly as shown

---

## 🏆 **READY TO TEST!**

**Database is completely cleared and ready!**
**Both servers are running!**
**Complete flow is tested and working!**

**🌐 Go to http://localhost:3000 and test the complete registration flow!**

**🎯 The March milestone is ready for full frontend testing!**
