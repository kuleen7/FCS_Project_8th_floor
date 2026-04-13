# FCS-26 Secure Job Search Platform - March Milestone Implementation

## Overview

This document provides comprehensive instructions for running and testing the March milestone implementation of the Secure Job Search & Professional Networking Platform. The March milestone adds company management, job postings, application tracking, encrypted messaging, and comprehensive audit logging.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/fcs_platform
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   LOG_LEVEL=INFO
   USE_SSL=False
   ```

5. **Initialize database**
   ```bash
   # Run database migrations
   python -m alembic upgrade head
   
   # Or create tables manually (if no migrations)
   python -c "
   from app.database import engine, Base
   from app.models import *
   Base.metadata.create_all(bind=engine)
   print('Database tables created successfully')
   "
   ```

6. **Start the backend server**
   ```bash
   python -m app.main
   ```
   
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the frontend server**
   ```bash
   npm start
   ```
   
   The frontend will be available at `http://localhost:3000`

## 📋 March Milestone Features

### 1. Company Management
- **Company Creation**: Users can create and manage company pages
- **Member Management**: Add/remove company members with role-based permissions
- **Company Profiles**: Complete company information with verification status

**API Endpoints:**
- `POST /api/companies/` - Create company
- `GET /api/companies/` - Get user companies
- `PUT /api/companies/{id}` - Update company
- `POST /api/companies/{id}/members` - Add member
- `DELETE /api/companies/{id}/members/{user_id}` - Remove member

### 2. Job Postings
- **Job Creation**: Company admins/recruiters can post jobs
- **Advanced Search**: Filter by keywords, location, job type, salary
- **Job Management**: Update, deactivate, or delete job postings

**API Endpoints:**
- `POST /api/jobs/` - Create job posting
- `GET /api/jobs/search` - Search jobs with filters
- `GET /api/jobs/featured` - Get featured jobs
- `PUT /api/jobs/{id}` - Update job posting

### 3. Application Tracking
- **Application Submission**: Users can apply with resumes and cover notes
- **Status Management**: Track applications through the recruitment pipeline
- **Recruiter Tools**: Shortlist candidates and add notes

**API Endpoints:**
- `POST /api/applications/` - Submit application
- `GET /api/applications/my-applications` - Get user applications
- `PUT /api/applications/{id}` - Update application status
- `GET /api/applications/job/{job_id}` - Get job applications

### 4. Encrypted Messaging
- **End-to-End Encryption**: All messages are encrypted using AES-256
- **Conversation Management**: Create one-to-one and group conversations
- **Message Security**: Hash-based integrity verification

**API Endpoints:**
- `POST /api/messages/conversations` - Create conversation
- `POST /api/messages/conversations/{id}/messages` - Send message
- `GET /api/messages/conversations/{id}/messages` - Get messages
- `DELETE /api/messages/{id}` - Delete message

### 5. Audit Logging
- **Tamper-Evident Logs**: Hash-chained audit trail
- **Comprehensive Tracking**: All critical actions are logged
- **Admin Dashboard**: View system activity and integrity reports

**API Endpoints:**
- `GET /api/audit/logs` - Get audit logs
- `GET /api/audit/integrity` - Verify log integrity
- `GET /api/audit/summary/system` - System activity summary

## 🔐 Security Features

### Message Encryption
- **Algorithm**: AES-256 with PBKDF2 key derivation
- **Key Management**: Per-conversation keys derived from master key
- **Integrity**: SHA-256 hash verification for all messages

### Audit Logging
- **Hash Chaining**: Each log entry contains hash of previous entry
- **Tamper Detection**: Any modification breaks the chain
- **Comprehensive Coverage**: Authentication, data changes, admin actions

### Access Control
- **Role-Based Permissions**: User, Recruiter, Admin roles
- **Resource Ownership**: Users can only access their own resources
- **Company Permissions**: Company-based access control for jobs and applications

## 🧪 Testing

### Backend Testing

1. **Run unit tests**
   ```bash
   cd backend
   pytest tests/ -v
   ```

2. **Test API endpoints**
   ```bash
   # Health check
   curl http://localhost:8000/api/health
   
   # Register user
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"SecurePass123","mobile":"1234567890"}'
   
   # Login
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"SecurePass123"}'
   ```

3. **Test message encryption**
   ```python
   # Test script for message encryption
   import requests
   
   # Create conversation
   conv_data = {
     "type": "one_to_one",
     "participant_ids": [2]  # Another user ID
   }
   response = requests.post(
     "http://localhost:8000/api/messages/conversations",
     json=conv_data,
     headers={"Authorization": "Bearer YOUR_TOKEN"}
   )
   ```

### Frontend Testing

1. **Run React tests**
   ```bash
   cd frontend
   npm test
   ```

2. **Test user flows**
   - Register new account
   - Create company
   - Post job
   - Apply to job
   - Send encrypted message

### Security Testing

1. **Test audit log integrity**
   ```bash
   curl -X GET "http://localhost:8000/api/audit/integrity" \
     -H "Authorization: Bearer ADMIN_TOKEN"
   ```

2. **Test encryption verification**
   ```python
   # Verify message encryption
   from app.services.message_service import message_service
   
   # Test encryption/decryption
   encrypted, hash_val = message_service._encrypt_message("Hello", 1, 1)
   decrypted = message_service._decrypt_message(encrypted, 1, 1)
   assert decrypted == "Hello"
   ```

## 📊 Database Schema

### New Tables Added

1. **companies** - Company information
2. **company_members** - Company membership
3. **jobs** - Job postings
4. **applications** - Job applications
5. **conversations** - Message conversations
6. **conversation_participants** - Conversation members
7. **messages** - Encrypted messages

### Key Relationships

- Companies → Jobs (one-to-many)
- Companies → Company Members (one-to-many)
- Jobs → Applications (one-to-many)
- Conversations → Messages (one-to-many)
- Users → Applications (one-to-many)
- Users → Messages (one-to-many)

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Application
DEBUG=False
LOG_LEVEL=INFO
USE_SSL=False

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Email (for OTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS (for OTP) - Twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL is running
   pg_ctl status
   
   # Check connection
   psql -h localhost -U username -d dbname
   ```

2. **Module Import Errors**
   ```bash
   # Install missing dependencies
   pip install -r requirements.txt
   
   # Check virtual environment
   which python
   ```

3. **Encryption Key Issues**
   ```bash
   # Remove existing key file to regenerate
   rm message_encryption.key
   ```

4. **CORS Issues**
   - Ensure frontend URL is in CORS_ORIGINS
   - Check that backend is running on correct port

### Debug Mode

Enable debug mode for detailed error messages:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Log Files

Check application logs:
```bash
# Backend logs
tail -f backend/logs/app.log

# Database logs
tail -f /var/log/postgresql/postgresql-*.log
```

## 📈 Performance Optimization

### Database Indexes

Key indexes are automatically created:
- Primary keys on all tables
- Foreign key relationships
- Search fields (company names, job titles)
- Timestamp fields for sorting

### Caching

- Redis can be added for session storage
- Application-level caching for frequent queries
- CDN for static assets

### Message Encryption Performance

- Keys are cached in memory
- Encryption operations are optimized
- Bulk operations for message retrieval

## 🔮 Next Steps (April Milestone)

The April milestone will include:
- PKI integration for digital signatures
- OTP with virtual keyboard
- Enhanced security defenses
- Blockchain-based audit logging
- Advanced admin features

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review API documentation at `http://localhost:8000/api/docs`
3. Check application logs
4. Verify database connectivity

## 📄 License

This project is part of CSE 345/545 Foundations to Computer Security course project.
