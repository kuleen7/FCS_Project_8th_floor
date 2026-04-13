# 🚀 Quick Start Guide - FCS-26 March Milestone

## ⚡ 5-Minute Setup

### 1. Clone and Navigate
```bash
cd fcs_8_floor-main
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Create .env file
echo DATABASE_URL=postgresql://localhost:5432/fcs_platform > .env
echo SECRET_KEY=dev-secret-key-change-in-production >> .env
echo DEBUG=True >> .env

# Create database tables
python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('Database ready!')
"
```

### 4. Start Backend
```bash
python -m app.main
```
Backend runs on: `http://localhost:8000`

### 5. Frontend Setup
```bash
cd ../frontend
npm install
npm start
```
Frontend runs on: `http://localhost:3000`

## 🎯 Test the Features

### 1. Register & Login
- Visit `http://localhost:3000`
- Create account
- Login with OTP

### 2. Create Company
- Go to profile → companies
- Click "Create Company"
- Fill company details

### 3. Post a Job
- Navigate to company page
- Click "Post Job"
- Fill job details and submit

### 4. Apply to Job
- Browse jobs
- Click "Apply" on any job
- Upload resume and submit

### 5. Send Encrypted Message
- Go to messages
- Start new conversation
- Send message (automatically encrypted)

### 6. Check Audit Logs (Admin)
- Login as admin user
- Visit audit section
- View tamper-evident logs

## 🔍 API Testing

Use these quick curl commands to test APIs:

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123","mobile":"1234567890"}'
```

### Create Company (after login)
```bash
curl -X POST http://localhost:8000/api/companies/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Test Company","description":"A test company","location":"Remote"}'
```

### Post Job
```bash
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"company_id":1,"title":"Software Engineer","description":"Develop secure software","location":"Remote"}'
```

## 🛠️ Common Fixes

### Database Issues
```bash
# Reset database
python -c "
from app.database import engine, Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
"
```

### Port Conflicts
```bash
# Kill processes on ports 8000 and 3000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Permission Issues
```bash
# Run as administrator (Windows)
# or use sudo (Linux/Mac)
```

## 📚 Documentation

- Full documentation: `README_MARCH_MILESTONE.md`
- API docs: `http://localhost:8000/api/docs`
- Project plan: `.windsurf/plans/fcs-26-march-milestone-e942e8.md`

## ✅ Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can register new user
- [ ] Can create company
- [ ] Can post job
- [ ] Can apply to job
- [ ] Can send encrypted message
- [ ] Can view audit logs (admin)

## 🚨 Need Help?

1. Check both terminals for errors
2. Verify PostgreSQL is installed and running
3. Ensure all dependencies are installed
4. Check environment variables in `.env`

**🎉 You're ready to explore the March Milestone features!**
