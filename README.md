# Secure Job Search and Professional Networking Platform

A full-stack job marketplace and professional networking platform with end-to-end encryption and tamper-evident audit logging, developed for CSE 345/545 (Foundations of Computer Security) coursework.

**Live Deployment:** https://fcs-project-8th_floor.vercel.app

## Overview

This platform provides three user roles with distinct workflows:

- **Job Seekers:** Search and apply to positions, upload resumes, and communicate securely with recruiters
- **Recruiters:** Post job listings, manage incoming applications, and track candidate progress
- **Administrators:** Monitor system activity, verify audit log integrity, and generate activity reports

All sensitive data exchanges utilize end-to-end encryption with cryptographic integrity verification. Critical system actions are logged to a hash-chained audit trail that detects any tampering or modification.

## Technical Architecture

### Backend Stack
- **Framework:** FastAPI (Python 3.8+)
- **Database:** PostgreSQL 12+
- **ORM:** SQLAlchemy
- **Deployment:** Render

### Frontend Stack
- **Framework:** React 18
- **Routing:** React Router
- **Styling:** Tailwind CSS
- **Cryptography:** crypto-js
- **Deployment:** Vercel

### Language Composition
- Python: 62.5%
- JavaScript: 32.6%
- Shell: 4.8%
- Other: 0.1%

## Security Architecture

### Encryption

**Message Encryption:**
- Algorithm: AES-256-GCM with PBKDF2 key derivation
- Scope: End-to-end encryption between client and intended recipient
- Integrity: SHA-256 hash verification prevents message tampering

**Audit Trail:**
- Hash-chained design: Each log entry contains SHA-256 hash of previous entry
- Tamper detection: Any modification breaks the cryptographic chain
- Coverage: Authentication events, data modifications, administrative actions

### Access Control

**Authorization Model:**
- Role-based access control (RBAC) with User, Recruiter, and Admin roles
- Resource ownership restrictions: Users access only their own data
- Company-level context: Job listings and applications scoped to company membership
- Granular permissions enforced at API endpoint level

**Authentication Mechanism:**
- OTP-based registration and login (email/SMS delivery)
- JWT token issuance with configurable expiration
- Password policy enforcement with minimum complexity requirements
- Session management via stateless token validation

## Project Structure

```
backend/
├── app/
│   ├── api/                Route handlers and endpoint definitions
│   ├── models/             SQLAlchemy ORM model definitions
│   ├── services/           Business logic and encryption operations
│   ├── security/           Authentication and cryptographic utilities
│   ├── schemas/            Pydantic validation schemas
│   ├── config.py           Application configuration
│   └── database.py         PostgreSQL connection setup
├── alembic_migrations/     Database schema versioning
├── requirements.txt        Python dependencies
└── main.py                FastAPI application entrypoint

frontend/
├── src/
│   ├── components/        Reusable React components
│   ├── pages/             Route page components
│   ├── services/          API client modules
│   └── App.jsx            Router configuration
├── package.json           npm dependencies
└── tailwind.config.js     Tailwind CSS configuration
```

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- PostgreSQL 12 or higher
- Git

### Backend Installation

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with DATABASE_URL, SECRET_KEY, and other required variables

# Initialize database schema
python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('Database schema initialized')
"

# Start FastAPI server
python -m app.main
```

Backend API runs on: http://localhost:8000

### Frontend Installation

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend application runs on: http://localhost:3000

## API Reference

### Authentication Endpoints
- `POST /api/auth/register` - Create user account
- `POST /api/auth/login` - Authenticate with OTP
- `GET /api/auth/me` - Retrieve current user information

### Company Management
- `POST /api/companies/` - Create company
- `GET /api/companies/` - List user companies
- `PUT /api/companies/{id}` - Modify company information
- `POST /api/companies/{id}/members` - Add company member
- `DELETE /api/companies/{id}/members/{user_id}` - Remove company member

### Job Postings
- `POST /api/jobs/` - Create job listing
- `GET /api/jobs/search` - Query jobs with filters
- `GET /api/jobs/featured` - Retrieve featured listings
- `PUT /api/jobs/{id}` - Update job posting

### Applications
- `POST /api/applications/` - Submit job application
- `GET /api/applications/my-applications` - Get user applications
- `PUT /api/applications/{id}` - Update application status
- `GET /api/applications/job/{job_id}` - Get job applications list

### Messaging
- `POST /api/messages/conversations` - Create conversation thread
- `POST /api/messages/conversations/{id}/messages` - Send encrypted message
- `GET /api/messages/conversations/{id}/messages` - Retrieve conversation messages
- `DELETE /api/messages/{id}` - Delete message

### Audit and Compliance
- `GET /api/audit/logs` - Retrieve audit log entries
- `GET /api/audit/integrity` - Verify hash chain integrity
- `GET /api/audit/summary/system` - Generate system activity summary

Full API documentation available at: http://localhost:8000/api/docs (Swagger UI)

## Database Schema

### Core Tables
- **users:** User account records with role assignments
- **companies:** Company profile information
- **company_members:** Membership records with role assignments
- **jobs:** Job listing records with metadata
- **applications:** Application submission records with status tracking
- **conversations:** Message thread records
- **messages:** Encrypted message records with integrity hashes
- **audit_logs:** Hash-chained audit trail entries

## Testing

### Backend Test Suite
```bash
cd backend
pytest tests/ -v
```

### Frontend Test Suite
```bash
cd frontend
npm test
```

### Manual Workflow Testing
1. Create account and authenticate at http://localhost:3000
2. Create company via Profile → Companies
3. Post job listing from company dashboard
4. Submit application and upload resume
5. Exchange encrypted messages via messaging system
6. View audit logs from admin interface

### cURL API Examples
```bash
# Health check
curl http://localhost:8000/api/health

# User registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123","mobile":"1234567890"}'

# Create company (requires valid JWT token)
curl -X POST http://localhost:8000/api/companies/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"name":"Company Name","description":"Description","location":"City"}'
```

## Configuration

### Backend Environment Variables (.env)
```env
# Database connectivity
DATABASE_URL=postgresql://user:password@localhost:5432/fcs_platform

# Cryptographic settings
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Application settings
DEBUG=False
LOG_LEVEL=INFO
USE_SSL=False

# CORS configuration (adjust for production)
CORS_ORIGINS=["http://localhost:3000"]

# Email provider (for OTP delivery)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS provider (Twilio)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
```

### Frontend Environment Variables (.env.production)
```env
REACT_APP_API_URL=https://your-backend-url.com
```

## Troubleshooting

### Database Connectivity Issues
```bash
# Verify PostgreSQL daemon status
pg_ctl status

# Test database connection
psql -h localhost -U username -d fcs_platform
```

### Port Conflicts

On Windows:
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

On Linux/macOS:
```bash
lsof -i :8000
kill -9 <PID>
```

### Python Module Import Errors
```bash
# Verify virtual environment activation
which python

# Force reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### CORS Configuration Problems
- Verify frontend origin is in backend's CORS_ORIGINS list
- Confirm both services running on correct ports
- Clear browser cache and session storage

### Encryption Key Issues
```bash
# Regenerate keys (data will be unrecoverable)
rm message_encryption.key
# Restart backend to initialize new key
```

## Production Deployment

### Security Requirements
1. Replace `SECRET_KEY` with cryptographically secure random value
2. Enable HTTPS: Set `USE_SSL=True` and configure TLS certificates
3. Restrict CORS origins to approved domains only
4. Use strong, randomly-generated database credentials
5. Implement rate limiting on API endpoints
6. Configure automated database backups
7. Monitor audit logs for suspicious patterns
8. Maintain regular security updates for all dependencies

### Development vs Production Configuration
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

## Performance Considerations

- Database queries optimized with strategic indexes for search and filtering
- Message encryption key caching to reduce cryptographic operations
- SQLAlchemy connection pooling for database resource management
- Frontend static assets served via CDN for reduced latency

## Additional Documentation

- [QUICK_START.md](QUICK_START.md) - Rapid setup guide
- [README_MARCH_MILESTONE.md](README_MARCH_MILESTONE.md) - Milestone objectives and features
- [APPLICATION_TRACKING_GUIDE.md](APPLICATION_TRACKING_GUIDE.md) - Application workflow documentation
- [COMPLETE_TESTING_GUIDE.md](COMPLETE_TESTING_GUIDE.md) - Comprehensive testing procedures
- [CHROME_TESTING_GUIDE.md](CHROME_TESTING_GUIDE.md) - Browser-specific testing guide
