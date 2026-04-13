# Deployment Guide (Vercel + FastAPI Backend)

This project should be deployed as:
- Frontend (React) on **Vercel**
- Backend (FastAPI) on **Render** (or Railway/Fly)
- Database on managed **PostgreSQL** (Neon/Supabase/Render PG)

This setup lets anyone use your app from a public URL.

---

## 1) Deploy PostgreSQL (Neon example)

1. Create a Neon project.
2. Copy the connection string, e.g.:
   - `postgresql://USER:PASSWORD@HOST/DB?sslmode=require`
3. Keep this for backend `DATABASE_URL`.

---

## 2) Deploy Backend (Render)

1. Push project to GitHub.
2. In Render, create **Web Service** from repo.
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**:
     - `pip install -r requirements.txt`
   - **Start Command**:
     - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Add backend environment variables:

- `DATABASE_URL=<your managed postgres url>`
- `SECRET_KEY=<long-random-secret>`
- `ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=30`
- `REFRESH_TOKEN_EXPIRE_DAYS=7`
- `OTP_SECRET_KEY=<long-random-secret>`
- `OTP_EXPIRE_MINUTES=5`
- `OTP_LENGTH=6`
- `SMTP_SERVER=smtp.gmail.com`
- `SMTP_PORT=587`
- `SMTP_USERNAME=<your email>`
- `SMTP_PASSWORD=<app password>`
- `SMTP_FROM_EMAIL=<your sender email>`
- `ENCRYPTION_KEY=<fernet-key>`
- `USE_SSL=False`
- `DEBUG=False`

5. CORS:
   - Update backend config for production origins to include your Vercel domain.
   - Ensure `CORS_ORIGINS` contains:
     - `https://<your-vercel-domain>`

6. After deploy, note backend URL:
   - e.g. `https://secure-job-backend.onrender.com`

Health check:
- `https://<backend-domain>/api/health`

---

## 3) Deploy Frontend (Vercel)

1. In Vercel, import same GitHub repo.
2. Configure:
   - **Root Directory**: `frontend`
   - Framework preset: Create React App (auto-detected)
   - Build command: `npm run build`
   - Output: default for CRA

3. Add frontend environment variable:
   - `REACT_APP_API_BASE_URL=https://<backend-domain>/api`

4. Deploy.

Your frontend URL:
- `https://<project>.vercel.app`

---

## 4) Post-Deploy Verification (must pass)

1. Register + verify user
2. Login/logout
3. Recruiter creates company + job
4. User sees job in search and applies
5. Recruiter sees applicants and updates status
6. Messaging works between users
7. Admin suspend/reactivate/delete works
8. Admin Audit Logs page shows real log entries
9. OTP virtual keyboard works for high-risk actions
10. TOTP setup/enable in Profile works

---

## 5) Production Notes

- Resume file storage:
  - local disk is not ideal long-term on ephemeral hosts.
  - move uploads to S3/R2 for durable storage.
- Keep secrets only in platform env vars (never commit).
- Rotate secrets before final public demo.
- Enable DB backups and retention.

---

## 6) Local to Production delta you already needed

Frontend now reads API URL from env:
- `frontend/src/services/api.js`
- uses:
  - `process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api"`

So local still works, and Vercel can point to deployed backend.
