"""
Resume Service
Handles encrypted resume storage
"""

import os
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Tuple, List
from datetime import datetime

from app.config import settings


class ResumeService:

    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    async def upload_resume(
        self,
        db,
        user_id: int,
        file_content: bytes,
        filename: str
    ) -> Tuple[bool, str, str]:

        # Validate file type
        if not filename.endswith((".pdf", ".docx")):
            return False, "Only PDF and DOCX allowed", ""

        if len(file_content) > 10 * 1024 * 1024:
            return False, "File exceeds 10MB limit", ""

        # Create user directory
        user_dir = Path(settings.UPLOAD_DIR) / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)

        # Encrypt file
        encrypted_content = self.fernet.encrypt(file_content)

        # Generate encrypted filename
        timestamp = int(datetime.utcnow().timestamp())
        encrypted_filename = f"{timestamp}_{filename}.encrypted"

        file_path = user_dir / encrypted_filename

        with open(file_path, "wb") as f:
            f.write(encrypted_content)

        return True, "Resume uploaded securely", str(encrypted_filename)

    async def download_resume(
        self,
        db,
        user_id: int,
        file_path: str
    ) -> Tuple[bool, str, bytes]:

        path = Path(file_path)

        if not path.exists():
            return False, "File not found", b""

        with open(path, "rb") as f:
            encrypted_content = f.read()

        decrypted_content = self.fernet.decrypt(encrypted_content)

        return True, "Resume downloaded", decrypted_content

    async def delete_resume(
        self,
        db,
        user_id: int,
        file_path: str
    ) -> Tuple[bool, str]:

        path = Path(file_path)

        if not path.exists():
            return False, "File not found"

        path.unlink()

        return True, "Resume deleted successfully"

    async def list_user_resumes(self, user_id: int) -> List[str]:

        user_dir = Path(settings.UPLOAD_DIR) / f"user_{user_id}"

        if not user_dir.exists():
            return []

        return [file.name for file in user_dir.iterdir() if file.is_file()]


resume_service = ResumeService()
