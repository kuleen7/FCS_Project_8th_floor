# FCS-26: Secure Job Search & Professional Networking Platform

A full-stack secure job marketplace and professional networking platform built for **CSE 345/545 (Foundations of Computer Security)** coursework. The platform implements end-to-end encryption, tamper-evident audit logging, role-based access control, and secure credential management.

**Live Demo:** https://fcs-project-8th_floor.vercel.app

## 🎯 Overview

This platform enables:
- **Job Seekers** to search jobs, apply with resumes, and communicate securely with recruiters
- **Recruiters** to post jobs, manage applications, and track candidates
- **Admins** to monitor system activity and verify audit log integrity

All sensitive communications are encrypted end-to-end, and every critical action is logged with cryptographic integrity verification.

## 🛡️ Security Features

### Message Encryption
- **Algorithm:** AES-256-GCM with PBKDF2 key derivation
- **End-to-End:** Messages encrypted on client, decrypted only by intended recipient
- **Integrity:** SHA-256 hash verification prevents tampering

### Audit Logging
- **Hash-Chained:** Each log entry contains a hash of the previous entry
- **Tamper Detection:** Any modification breaks the chain
- **Comprehensive:** Tracks authentication, data changes, admin actions

### Access Control
- **Role-Based:** User, Recruiter, Admin roles with specific permissions
- **Resource Ownership:** Users can only access their own resources
- **Company Context:** Company-based access control for jobs and applications

### Authentication
- **OTP-Based:** One-Time Password via email/SMS
- **JWT Tokens:** Stateless authentication with expiration
- **Password Policy:** Minimum requirements enforced

## 🏗️ Architecture

### Tech Stack
- **Backend:** FastAPI (Python 3.8+), PostgreSQL 12+, SQLAlchemy ORM
- **Frontend:** React 18, React Router, Tailwind CSS, crypto-js
- **Deployment:** Vercel (frontend), Render (backend)

### Directory Structure
```
backend/                 FastAPI application
├── app/
│   ├── api/            Route handlers
│   ├── models/         SQLAlchemy models
│   ├── services/       Business logic & encryption
│   ├── security/       Auth & cryptography
│   ├── schemas/        Pydantic validators
│   ├── config.py       Configuration
│   └── database.py     PostgreSQL setup
├── alembic_migrations/ Database migrations
├── requirements.txt    Dependencies
└── main.py            FastAPI entry point

frontend/              React application
├── src/
│   ├── components/    UI components
│   ├── pages/         Route pages
│   ├── services/      API clients
│   └── App.jsx        Router
├── package.json       Dependencies
└── tailwind.config.js Styling config
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your DATABASE_URL, SECRET_KEY, etc.

# Initialize database
python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('Database ready!')
"

# Start server
python -m app.main
```
Backend runs on: **http://localhost:8000**

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```
Frontend runs on: **http://localhost:3000**

## 📋 Features

### March Milestone ✅
- ✅ Company Management (create, invite members, manage roles)
- ✅ Job Postings (create, search, filter by location/type/salary)
- ✅ Application Tracking (submit, track status, recruiter notes)
- ✅ Encrypted Messaging (AES-256 end-to-end encryption)
- ✅ Audit Logging (hash-chained tamper-evident logs)

### April Milestone (In Progress)
- 🔐 PKI Integration (digital signatures, certificate-based auth)
- 🎹 Virtual Keyboard OTP (prevent keylogger attacks)
- 🛡️ Enhanced Defenses (rate limiting, IP blocking)
- ⛓️ Blockchain Audit Logs (immutable audit trail)
- 📊 Advanced Admin Dashboard

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login with OTP
- `GET /api/auth/me` - Get current user

### Companies
- `POST /api/companies/` - Create company
- `GET /api/companies/` - List user companies
- `PUT /api/companies/{id}` - Update company
- `POST /api/companies/{id}/members` - Add member
- `DELETE /api/companies/{id}/members/{user_id}` - Remove member

### Jobs
- `POST /api/jobs/` - Create job posting
- `GET /api/jobs/search` - Search jobs with filters
- `GET /api/jobs/featured` - Get featured jobs
- `PUT /api/jobs/{id}` - Update job posting

### Applications
- `POST /api/applications/` - Submit application
- `GET /api/applications/my-applications` - Get user applications
- `PUT /api/applications/{id}` - Update application status
- `GET /api/applications/job/{job_id}` - Get job applications

### Messaging
- `POST /api/messages/conversations` - Create conversation
- `POST /api/messages/conversations/{id}/messages` - Send encrypted message
- `GET /api/messages/conversations/{id}/messages` - Get messages
- `DELETE /api/messages/{id}` - Delete message

### Audit
- `GET /api/audit/logs` - Get audit logs
- `GET /api/audit/integrity` - Verify log integrity
- `GET /api/audit/summary/system` - System activity summary

**Interactive API Docs:** http://localhost:8000/api/docs (Swagger UI)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing
1. **Register & Login:** Visit http://localhost:3000, create account
2. **Create Company:** Profile → Companies → Create
3. **Post Job:** Company page → Post Job
4. **Apply:** Browse jobs → Apply → Upload resume
5. **Encrypted Message:** Messages → New conversation → Send message
6. **View Audit Logs:** Admin → Audit → View logs

### API Testing with cURL
```bash
# Health check
curl http://localhost:8000/api/health

# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123","mobile":"1234567890"}'

# Create company (after login with token)
curl -X POST http://localhost:8000/api/companies/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Acme Corp","description":"Tech company","location":"Remote"}'
```

## 🔧 Configuration

### Environment Variables (backend/.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fcs_platform

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Application
DEBUG=False
LOG_LEVEL=INFO
USE_SSL=False

# CORS (adjust for production)
CORS_ORIGINS=["http://localhost:3000"]

# Email (for OTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

### Environment Variables (frontend/.env.production)
```env
REACT_APP_API_URL=https://your-backend-url.com
```

## 📊 Database Schema

### Core Tables
- **users** - User accounts with role-based access
- **companies** - Company profiles
- **company_members** - Company membership with roles
- **jobs** - Job postings with metadata
- **applications** - Job applications with status tracking
- **conversations** - Encrypted message threads
- **messages** - Encrypted messages with integrity hashes
- **audit_logs** - Hash-chained audit trail

## 🚨 Troubleshooting

### Database Connection Error
```bash
# Verify PostgreSQL is running
pg_ctl status

# Test connection
psql -h localhost -U username -d fcs_platform
```

### Port Conflicts
```bash
# Kill processes on ports
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Module Import Errors
```bash
# Verify virtual environment
which python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### CORS Issues
- Verify frontend URL is in backend's `CORS_ORIGINS`
- Check both services are running on correct ports
- Clear browser cache

### Encryption Key Issues
```bash
# Regenerate encryption keys
rm message_encryption.key
# Restart backend to generate new key
```

## 📚 Documentation

- **Quick Start Guide:** [QUICK_START.md](QUICK_START.md)
- **March Milestone Details:** [README_MARCH_MILESTONE.md](README_MARCH_MILESTONE.md)
- **Application Tracking Guide:** [APPLICATION_TRACKING_GUIDE.md](APPLICATION_TRACKING_GUIDE.md)
- **Testing Guides:** 
  - [COMPLETE_TESTING_GUIDE.md](COMPLETE_TESTING_GUIDE.md)
  - [CHROME_TESTING_GUIDE.md](CHROME_TESTING_GUIDE.md)

## 🔐 Security Considerations

### For Production
1. **Change `SECRET_KEY`** in environment variables
2. **Enable HTTPS/SSL** - set `USE_SSL=True`
3. **Configure CORS properly** - whitelist only needed origins
4. **Use strong passwords** for database credentials
5. **Enable rate limiting** for API endpoints
6. **Regular backups** of PostgreSQL database
7. **Monitor audit logs** for suspicious activity
8. **Update dependencies** regularly

### Development vs Production
```bash
# Development
DEBUG=True
USE_SSL=False
CORS_ORIGINS=["http://localhost:3000"]

# Production
DEBUG=False
USE_SSL=True
CORS_ORIGINS=["https://yourdomain.com"]
```

## 📈 Performance

- **Database Indexes:** Optimized for search and filtering
- **Message Encryption:** Cached keys for performance
- **Connection Pooling:** SQLAlchemy session management
- **Frontend Caching:** Static assets served from CDN

---

**Last Updated:** April 2026  
**Status:** March Milestone Complete ✅ | April Milestone In Progress 🔄
