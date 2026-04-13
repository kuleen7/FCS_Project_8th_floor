from datetime import datetime
from typing import List, Dict

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "healthy", "https": False}


@app.get("/api/")
def root():
    return {"message": "secure job platform skeleton running"}


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    mobile: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Profile(BaseModel):
    name: str = ""
    email: EmailStr
    mobile: str = ""
    status: str = "Active"
    accountType: str = "Candidate"


class ProfileUpdate(BaseModel):
    name: str = ""
    mobile: str = ""


class ResumeMeta(BaseModel):
    id: str
    filename: str
    originalName: str
    createdAt: datetime


# In-memory demo storage (resets when server restarts)
current_profile: Dict[str, Profile] = {}
resume_files: Dict[str, bytes] = {}
resume_list: List[ResumeMeta] = []


@app.post("/api/auth/register")
def register_user(payload: RegisterRequest):
    if len(payload.password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters."
        )

    # Initialize a basic profile for this email
    current_profile[payload.email] = Profile(
        name="",
        email=payload.email,
        mobile=payload.mobile,
    )

    return {
        "message": "Account created successfully.",
        "email": payload.email,
    }


@app.post("/api/auth/login")
def login_user(payload: LoginRequest):
    if len(payload.password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters."
        )

    # Ensure we have a profile entry
    if payload.email not in current_profile:
        current_profile[payload.email] = Profile(
            name="",
            email=payload.email,
            mobile="",
        )

    return {
        "message": "Login successful.",
        "token": "demo-token",
        "user": {"email": payload.email},
    }


@app.get("/api/auth/me")
def get_current_user():
    # Demo: return the first profile if any; otherwise a default
    if current_profile:
        # Get arbitrary first profile
        profile = next(iter(current_profile.values()))
        return profile
    return Profile(email="demo@example.com")


@app.get("/api/users/profile")
def get_profile():
    if current_profile:
        return next(iter(current_profile.values()))
    raise HTTPException(status_code=404, detail="Profile not found.")


@app.put("/api/users/profile")
def update_profile(update: ProfileUpdate):
    if not current_profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    email, profile = next(iter(current_profile.items()))
    updated = profile.copy(update=update.dict())
    current_profile[email] = updated
    return updated


@app.post("/api/users/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    from uuid import uuid4

    file_id = str(uuid4())
    content = await file.read()
    resume_files[file_id] = content

    meta = ResumeMeta(
        id=file_id,
        filename=file_id,
        originalName=file.filename or "resume",
        createdAt=datetime.utcnow(),
    )
    resume_list.append(meta)
    return meta


@app.get("/api/users/resume/list", response_model=List[ResumeMeta])
def list_resumes():
    return resume_list


@app.get("/api/users/resume/download/{filename}")
def download_resume(filename: str):
    if filename not in resume_files:
        raise HTTPException(status_code=404, detail="Resume not found.")
    data = resume_files[filename]
    return StreamingResponse(
        iter([data]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.delete("/api/users/resume/{filename}")
def delete_resume(filename: str):
    global resume_list
    if filename in resume_files:
        del resume_files[filename]
        resume_list = [
            r for r in resume_list if r.filename != filename and r.id != filename
        ]
        return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Resume not found.")
