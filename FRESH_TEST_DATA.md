# 🧪 Fresh Test Data for Registration

## 🎯 **SOLUTION: Use Unique Email and Mobile**

The "unable to register" error happens because the email or mobile number is already in the database. Use these fresh test accounts:

---

## ✅ **Working Test Accounts:**

### **Test User 1:**
```
Email: alice@jobsearch.com
Password: Secure123!
Mobile: 1112223333
First Name: Alice
Last Name: Johnson
```

### **Test User 2:**
```
Email: bob@jobsearch.com
Password: Secure123!
Mobile: 4445556666
First Name: Bob
Last Name: Smith
```

### **Test User 3:**
```
Email: charlie@jobsearch.com
Password: Secure123!
Mobile: 7778889999
First Name: Charlie
Last Name: Brown
```

---

## 📱 **Mobile Format Rules:**

✅ **Valid Mobile Formats:**
- `1112223333` (10 digits)
- `555-123-4567` (with dashes)
- `(555)1234567` (with parentheses)
- `+15551234567` (with country code)

❌ **Invalid Mobile Formats:**
- `123` (too short)
- `1234567890123456` (too long)

---

## 🚀 **Step-by-Step Test:**

### **1. Register Alice:**
1. Go to `http://localhost:3000`
2. Click "Create one"
3. Enter:
   - Email: `alice@jobsearch.com`
   - Password: `Secure123!`
   - Mobile: `1112223333`
   - First Name: `Alice`
   - Last Name: `Johnson`
4. Click "Create account"

### **2. Get OTP for Alice:**
```bash
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
cursor = conn.cursor()
cursor.execute('SELECT otp_code FROM otp_verifications ORDER BY created_at DESC LIMIT 1')
otp = cursor.fetchone()
print(f'Alice OTP: {otp[0] if otp else \"No OTP found\"}')
conn.close()
"
```

### **3. Verify Alice's Email:**
- Enter the OTP code in the frontend
- Should see "Email verified successfully"

### **4. Login Alice:**
- Email: `alice@jobsearch.com`
- Password: `Secure123!`
- Should redirect to dashboard

### **5. Register Bob (repeat steps):**
- Use Bob's details above
- Get new OTP for Bob
- Verify and login

---

## 🔍 **Why This Works:**

1. **Unique Emails:** No duplicates in database
2. **Unique Mobiles:** No duplicates in database  
3. **Valid Format:** 10-digit mobile numbers
4. **Strong Password:** Meets all requirements

---

## 📞 **If You Still Get Errors:**

### **Check These:**
1. **Email is completely unique** (not in the list above)
2. **Mobile is 10 digits** (like `1234567890`)
3. **Password has:** uppercase, lowercase, digit, special character
4. **All fields are filled**

### **Quick Test Format:**
```
Email: mytest123@example.com
Password: Secure123!
Mobile: 1234567890
First Name: Test
Last Name: User
```

---

## 🎉 **Expected Result:**

If you use the fresh test data above, you should see:
- ✅ "Registration successful. Please check your email for verification code."
- ✅ OTP verification works
- ✅ Login redirects to dashboard
- ✅ No more "check your details" error

**🏆 The system works perfectly with unique data!**
