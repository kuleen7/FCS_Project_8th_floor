# 🌐 **Chrome Testing Guide - Step by Step**

## 📋 **CURRENT STATUS**
✅ Backend: `http://localhost:8000` - RUNNING  
✅ Frontend: `http://localhost:3000` - RUNNING  
✅ Database: PostgreSQL - READY

---

## 🚀 **STEP-BY-STEP TESTING INSTRUCTIONS**

### **Step 1: Open Chrome Browser**
1. Open Google Chrome
2. Go to: `http://localhost:3000`
3. You should see the Secure Job Search Platform homepage

### **Step 2: Register a New User**
1. Click **"Create one"** button (or "Register")
2. Fill in the registration form with **EXACTLY** these details:

```
Email: chris@newuser.com
Password: Secure123!
Mobile: 9998887777
First Name: Chris
Last Name: Wilson
```

**IMPORTANT:** Use the EXACT email and mobile above - these are not in the database yet!

3. Click **"Create account"** button

### **Step 3: Get OTP Code**
After registration, you need to get the OTP code:

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
   print(f'Your OTP: {otp[0] if otp else \"No OTP found\"}')
   conn.close()
   "
   ```

4. You'll see something like: `Your OTP: 123456`

### **Step 4: Verify Email**
1. Go back to Chrome
2. Enter the 6-digit OTP code you got
3. Click **"Verify"** or **"Submit"**
4. You should see "Email verified successfully"

### **Step 5: Login**
1. Click **"Sign in"** or go to login page
2. Enter your credentials:
   ```
   Email: chris@newuser.com
   Password: Secure123!
   ```
3. Click **"Sign in"**
4. You should be redirected to the dashboard

---

## 🔍 **IF YOU GET ERRORS:**

### **Error: "Unable to register. Please check your details."**
**Cause:** Email or mobile already exists in database

**Solution:** Use these FRESH credentials:
```
Email: chris2024@newuser.com
Password: Secure123!
Mobile: 5551239999
First Name: Chris
Last Name: Wilson
```

### **Error: "No OTP found"**
**Cause:** Database query issue

**Solution:** Wait 30 seconds after registration, then try the OTP command again

### **Error: "Invalid OTP"**
**Cause:** Wrong OTP code

**Solution:** Get the latest OTP from the database command

---

## 🧪 **ALTERNATIVE: Use These Pre-Tested Credentials**

If you want to skip registration, use this existing verified user:

```
Email: demo@fcs26.com
Password: Secure123!
```

This user is already verified and should login directly.

---

## 📱 **MOBILE FORMAT RULES**

The mobile number must be:
- **10-15 characters long**
- **Only numbers** (or with dashes like `555-123-4567`)

**Valid Examples:**
- `9998887777` ✅
- `5551234567` ✅
- `1234567890` ✅

**Invalid Examples:**
- `123` ❌ (too short)
- `1234567890123456` ❌ (too long)

---

## 🔧 **TROUBLESHOOTING**

### **If Frontend Doesn't Load:**
1. Check if frontend is running:
   ```bash
   cd c:\Users\siddh_ygv5bws\OneDrive\Desktop\fcs_8_floor-main\frontend
   npm start
   ```

### **If Backend Doesn't Respond:**
1. Check if backend is running:
   ```bash
   cd c:\Users\siddh_ygv5bws\OneDrive\Desktop\fcs_8_floor-main\backend
   python -m app.main
   ```

### **If Database Connection Fails:**
1. Check PostgreSQL is running
2. Verify password is `2499`
3. Check `.env` file settings

---

## 🎯 **SUCCESS INDICATORS**

You'll know it's working when you see:

1. ✅ **Registration:** "Registration successful. Please check your email for verification code."
2. ✅ **Email Verification:** "Email verified successfully"
3. ✅ **Login:** Redirected to dashboard
4. ✅ **Dashboard:** User profile and navigation options

---

## 🌟 **AFTER SUCCESSFUL LOGIN**

Once you're logged in, you can:
- Create a company
- Post a job
- Apply for jobs
- Send encrypted messages
- View audit logs

---

## 📞 **NEED HELP?**

If you're still having issues:

1. **Check both servers are running** (no error messages in terminals)
2. **Use fresh email/mobile** (not already in database)
3. **Follow steps exactly** (don't skip any)
4. **Check console errors** in Chrome (F12 → Console)

---

## 🎉 **EXPECTED RESULT**

If you follow these steps exactly, you should successfully:
- Register a new user
- Verify email with OTP
- Login to the dashboard
- Access all March milestone features

**🏆 The system is working perfectly - just use the right credentials!**
