# 📱 Mobile Phone Format Guide

## **Required Format:**
- **Minimum:** 10 characters
- **Maximum:** 15 characters
- **Characters allowed:** Numbers and basic symbols (+ - ( ) )

---

## ✅ **Valid Examples:**

### **Simple Numbers (10 digits):**
```
1234567890
9876543210
5551234567
```

### **With Country Code (11-15 digits):**
```
12345678901    (11 digits - with country code)
123456789012   (12 digits)
1234567890123  (13 digits)
12345678901234 (14 digits)
123456789012345 (15 digits)
```

### **With Formatting (10-15 characters total):**
```
555-123-4567   (12 characters)
(555)1234567   (12 characters)
+15551234567   (12 characters)
(555) 123-4567 (14 characters)
```

---

## ❌ **Invalid Examples:**

### **Too Short (under 10 characters):**
```
123          (3 characters) ❌
1234567      (7 characters) ❌
123456789    (9 characters) ❌
```

### **Too Long (over 15 characters):**
```
1234567890123456 (16 characters) ❌
+1-555-123-4567  (16 characters) ❌
```

---

## 🎯 **Recommended Formats:**

### **For Testing:**
```
1234567890      (Simple 10-digit)
5551234567      (10-digit US format)
12345678901     (11-digit with country code)
```

### **For Production:**
```
+15551234567    (International format)
555-123-4567    (US format with dashes)
(555)123-4567   (US format with parentheses)
```

---

## 🔍 **Error Messages:**

If you enter an invalid mobile number, you'll see:

### **Too Short:**
```
String should have at least 10 characters
```

### **Too Long:**
```
String should have at most 15 characters
```

---

## 📝 **Frontend Validation:**

The frontend should validate:
- ✅ Minimum 10 characters
- ✅ Maximum 15 characters
- ✅ Only numbers and basic formatting symbols

---

## 🧪 **Test These Formats:**

### **Working Examples:**
```bash
# Test in frontend or API:
"1234567890"     ✅ (10 digits)
"5551234567"     ✅ (10 digits)  
"555-123-4567"   ✅ (12 chars with dashes)
"+15551234567"   ✅ (12 chars with country code)
"(555)1234567"   ✅ (12 chars with parentheses)
```

### **Failing Examples:**
```bash
"123"            ❌ (too short)
"123456789"      ❌ (too short)
"1234567890123456" ❌ (too long)
```

---

## 🚀 **Quick Fix:**

If you're getting the "check your details" error for mobile, use one of these:

```
1234567890
5551234567
555-123-4567
```

**🎯 Any 10-15 character combination of numbers will work!**
