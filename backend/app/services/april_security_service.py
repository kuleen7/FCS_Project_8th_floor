"""
April milestone security service:
- Virtual keyboard OTP challenge
- PKI digital signatures
- Blockchain-style audit blocks
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import random
import secrets
import re
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..models import AuditBlock, OTPVerification, SecurityEvent, UserSigningKey, Job
from .resume_service import resume_service


class AprilSecurityService:
    """Implements April milestone and bonus security capabilities."""

    def __init__(self):
        self._otp_challenges: Dict[str, dict] = {}
        self._challenge_ttl_seconds = 300
        self._key_dir = Path(__file__).resolve().parents[2] / "keys"
        self._key_dir.mkdir(parents=True, exist_ok=True)

    def create_virtual_keyboard_challenge(self, user_id: int) -> dict:
        digits = list("0123456789")
        random.shuffle(digits)
        challenge_id = secrets.token_urlsafe(18)
        expires_at = datetime.utcnow() + timedelta(seconds=self._challenge_ttl_seconds)
        self._otp_challenges[challenge_id] = {
            "user_id": user_id,
            "layout": digits,
            "expires_at": expires_at,
        }
        return {
            "challenge_id": challenge_id,
            "layout": digits,
            "expires_at": expires_at.isoformat() + "Z",
        }

    def verify_keyboard_otp(
        self, db: Session, user_id: int, challenge_id: str, positions: List[int], otp_type: str
    ) -> Tuple[bool, str]:
        challenge = self._otp_challenges.get(challenge_id)
        if not challenge:
            return False, "Challenge not found"
        if challenge["user_id"] != user_id:
            return False, "Challenge does not belong to this user"
        if datetime.utcnow() > challenge["expires_at"]:
            return False, "Challenge expired"
        if len(positions) != 6:
            return False, "Exactly 6 virtual-keyboard positions are required"

        layout = challenge["layout"]
        try:
            otp_code = "".join(layout[idx] for idx in positions)
        except IndexError:
            return False, "Invalid position index in payload"

        otp_entry = (
            db.query(OTPVerification)
            .filter(
                OTPVerification.user_id == user_id,
                OTPVerification.otp_code == otp_code,
                OTPVerification.otp_type == otp_type,
                OTPVerification.is_used.is_(False),
            )
            .order_by(desc(OTPVerification.created_at))
            .first()
        )
        if not otp_entry:
            self._log_security_event(db, user_id, "otp_failed_keyboard", "medium")
            return False, "Invalid OTP"

        if otp_entry.expires_at.replace(tzinfo=None) < datetime.utcnow():
            return False, "OTP expired"

        otp_entry.is_used = True
        db.commit()
        self._otp_challenges.pop(challenge_id, None)
        return True, "OTP verified"

    def verify_high_risk_action(
        self,
        db: Session,
        user_id: int,
        action: str,
        payload_json: str,
        signature_b64: str,
        challenge_id: str,
        positions: List[int],
    ) -> Tuple[bool, str]:
        try:
            payload = json.loads(payload_json)
        except Exception:
            return False, "Invalid security payload JSON"

        payload_action = payload.get("action")
        payload_ts = payload.get("ts")
        if payload_action != action:
            return False, "Signed action mismatch"

        if not payload_ts:
            return False, "Signed payload missing timestamp"

        try:
            ts = datetime.fromisoformat(payload_ts.replace("Z", ""))
        except Exception:
            return False, "Invalid signed payload timestamp"

        # Normalize timezone awareness before comparison.
        if ts.tzinfo is not None:
            now = datetime.now(ts.tzinfo)
        else:
            now = datetime.utcnow()

        if now - ts > timedelta(minutes=5):
            return False, "Signed payload expired"

        if not self.verify_signature(db, user_id, payload, signature_b64):
            self._log_security_event(db, user_id, "signature_verification_failed", "high")
            return False, "Signature verification failed"

        otp_ok, otp_msg = self.verify_keyboard_otp(
            db, user_id, challenge_id, positions, otp_type="high_risk"
        )
        if not otp_ok:
            return False, f"High-risk OTP failed: {otp_msg}"
        return True, "Security verification passed"

    def generate_or_rotate_keys(self, db: Session, user_id: int) -> dict:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        fingerprint = hashlib.sha256(public_pem).hexdigest()

        user_key_dir = self._key_dir / f"user_{user_id}"
        user_key_dir.mkdir(parents=True, exist_ok=True)
        (user_key_dir / "private.pem").write_bytes(private_pem)

        db_key = db.query(UserSigningKey).filter(UserSigningKey.user_id == user_id).first()
        if db_key:
            db_key.public_key_pem = public_pem.decode("utf-8")
            db_key.key_fingerprint = fingerprint
            db_key.rotated_at = datetime.utcnow()
        else:
            db_key = UserSigningKey(
                user_id=user_id,
                public_key_pem=public_pem.decode("utf-8"),
                key_fingerprint=fingerprint,
            )
            db.add(db_key)

        db.commit()
        return {
            "fingerprint": fingerprint,
            "public_key": public_pem.decode("utf-8"),
            "private_key_path": str(user_key_dir / "private.pem"),
        }

    def sign_payload(self, user_id: int, payload: dict) -> dict:
        private_path = self._key_dir / f"user_{user_id}" / "private.pem"
        if not private_path.exists():
            raise ValueError("Private key not found for this user")

        private_key = serialization.load_pem_private_key(private_path.read_bytes(), password=None)
        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = private_key.sign(
            payload_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return {"signature_b64": base64.b64encode(signature).decode("utf-8")}

    def verify_signature(self, db: Session, user_id: int, payload: dict, signature_b64: str) -> bool:
        key_record = db.query(UserSigningKey).filter(UserSigningKey.user_id == user_id).first()
        if not key_record:
            return False

        public_key = serialization.load_pem_public_key(key_record.public_key_pem.encode("utf-8"))
        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = base64.b64decode(signature_b64)
        try:
            public_key.verify(
                signature,
                payload_bytes,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    def append_audit_block(self, db: Session, event_type: str, payload: dict) -> AuditBlock:
        last_block = db.query(AuditBlock).order_by(desc(AuditBlock.block_index)).first()
        previous_hash = last_block.block_hash if last_block else None
        block_index = 0 if not last_block else last_block.block_index + 1
        payload_json = json.dumps({"event_type": event_type, "payload": payload}, sort_keys=True)
        block_hash = hashlib.sha256(f"{block_index}|{previous_hash}|{payload_json}".encode("utf-8")).hexdigest()

        block = AuditBlock(
            block_index=block_index,
            previous_hash=previous_hash,
            block_hash=block_hash,
            payload=payload_json,
        )
        db.add(block)
        db.commit()
        db.refresh(block)
        return block

    def verify_audit_chain(self, db: Session) -> dict:
        blocks = db.query(AuditBlock).order_by(AuditBlock.block_index).all()
        previous_hash = None
        violations = []
        for block in blocks:
            expected = hashlib.sha256(
                f"{block.block_index}|{previous_hash}|{block.payload}".encode("utf-8")
            ).hexdigest()
            if block.previous_hash != previous_hash or block.block_hash != expected:
                violations.append(block.block_index)
            previous_hash = block.block_hash
        return {"valid": len(violations) == 0, "total_blocks": len(blocks), "violations": violations}

    def _log_security_event(self, db: Session, user_id: int, event_type: str, severity: str) -> None:
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            details=json.dumps({"source": "april_security_service"}),
        )
        db.add(event)
        db.commit()

    async def parse_resume(self, db: Session, user_id: int, filename: str) -> dict:
        file_path = self._get_user_resume_path(user_id, filename)
        success, message, content = await resume_service.download_resume(db, user_id, file_path)
        if not success:
            raise ValueError(message)
        text = self._extract_resume_text(filename, content)
        skills = self._extract_skills(text)
        return {
            "filename": filename,
            "text_preview": text[:1200],
            "skills": sorted(skills),
            "quality": "high" if self._looks_human_text(text) else "low",
            "note": "If quality is low, upload DOCX or a text-based PDF for better parsing.",
        }

    async def match_resume_to_job(self, db: Session, user_id: int, filename: str, job_id: int) -> dict:
        parsed = await self.parse_resume(db, user_id, filename)
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")

        job_text = " ".join(
            [
                job.title or "",
                job.description or "",
                job.required_skills or "",
                job.location or "",
            ]
        ).lower()
        resume_skills = set(parsed["skills"])
        job_skills = self._extract_skills(job_text)

        overlap = resume_skills.intersection(job_skills)
        base = len(job_skills) if job_skills else 1
        score = round((len(overlap) / base) * 100, 2)
        return {
            "job_id": job_id,
            "filename": filename,
            "match_score": score,
            "matched_skills": sorted(overlap),
            "missing_skills": sorted(job_skills - resume_skills),
        }

    def _get_user_resume_path(self, user_id: int, filename: str) -> str:
        return str((Path("uploads") / f"user_{user_id}" / filename).resolve())

    def _extract_resume_text(self, filename: str, content: bytes) -> str:
        lower = filename.lower()
        if lower.endswith(".docx") or lower.endswith(".docx.encrypted"):
            return self._extract_docx_text(content)
        if lower.endswith(".pdf") or lower.endswith(".pdf.encrypted"):
            return self._extract_pdf_text(content)
        return content.decode("utf-8", errors="ignore")

    def _extract_docx_text(self, content: bytes) -> str:
        try:
            with zipfile.ZipFile(io.BytesIO(content), "r") as zf:
                raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
                raw = re.sub(r"<[^>]+>", " ", raw)
                return re.sub(r"\s+", " ", raw).strip()
        except Exception:
            return ""

    def _extract_pdf_text(self, content: bytes) -> str:
        # Prefer robust parser when available.
        try:
            from pypdf import PdfReader  # type: ignore
            reader = PdfReader(io.BytesIO(content))
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            joined = " ".join(pages).strip()
            if joined:
                return re.sub(r"\s+", " ", joined).strip()
        except Exception:
            pass

        # Fallback heuristic extraction.
        text = content.decode("latin1", errors="ignore")
        extracted = re.findall(r"\(([^()]*)\)\s*Tj", text)
        combined = " ".join(extracted)
        if combined.strip():
            return re.sub(r"\s+", " ", combined).strip()
        return re.sub(r"\s+", " ", text).strip()

    def _looks_human_text(self, text: str) -> bool:
        if not text or len(text) < 40:
            return False
        printable = sum(1 for c in text if c.isalnum() or c.isspace() or c in ".,-:/()@")
        return (printable / max(len(text), 1)) > 0.8

    def _extract_skills(self, text: str) -> set[str]:
        corpus = text.lower()
        known = {
            "python", "java", "javascript", "react", "fastapi", "sql", "postgresql",
            "docker", "kubernetes", "aws", "git", "linux", "node", "typescript",
            "security", "cryptography", "machine learning", "nlp", "django",
            "flask", "html", "css", "rest", "api", "c++", "go", "devops",
        }
        found = set()
        for skill in known:
            if skill in corpus:
                found.add(skill)
        return found


april_security_service = AprilSecurityService()
