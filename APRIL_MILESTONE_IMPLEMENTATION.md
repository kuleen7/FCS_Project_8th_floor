# April Milestone + Bonus Implementation

This project now includes complete April milestone coverage with integrated enforcement in high-risk workflows.

## 1) PKI Integration (Security-Critical Functions)

PKI is implemented using RSA keypairs per user:

- `POST /api/april/pki/keys/rotate` generates/rotates keypair.
- `POST /api/april/pki/sign` signs canonical JSON payloads.
- `POST /api/april/pki/verify` verifies signatures.

PKI enforcement is applied to two critical functions:

- Job posting create: `POST /api/jobs/`
- Job posting update: `PUT /api/jobs/{job_id}`
- Admin account control actions:
  - `POST /api/admin/users/{user_id}/suspend`
  - `POST /api/admin/users/{user_id}/reactivate`
  - `DELETE /api/admin/users/{user_id}`

Required headers for protected routes:

- `X-Security-Payload` (JSON string with `action` and `ts`)
- `X-Security-Signature` (base64 signature)
- `X-OTP-Challenge-ID`
- `X-OTP-Positions` (comma-separated virtual keyboard indexes)

## 2) OTP with Virtual Keyboard for High-Risk Actions

- `POST /api/april/otp/high-risk/request` sends OTP and returns randomized virtual keyboard challenge.
- `POST /api/april/otp/keyboard-verify` verifies position-based OTP input.

OTP enforcement is used for high-risk actions:

- Resume download/delete (`/api/users/resume/download/*`, `/api/users/resume/*`)
- PKI-protected job/admin critical operations (combined with signature verification)

## 3) Tamper-Evident Secure Audit Logs

Two layers are available:

1. Existing audit hash-chain logs (`audit_logs`)
2. Blockchain-style chain (`audit_blocks`) with:
   - `POST /api/april/audit/block`
   - `GET /api/april/audit/chain/verify` (admin)

## 4) Demonstration of Defenses Against Common Web Attacks

Implemented server defenses:

- Security headers middleware (CSP, X-Frame-Options, nosniff, etc.)
- Basic per-IP rate limiting
- Suspicious query pattern blocking

Demo script:

- `python3 web_attack_defense_demo.py`

## 5) Final System Demo and Documentation

- This file (`APRIL_MILESTONE_IMPLEMENTATION.md`)
- `FINAL_SYSTEM_DEMO_SUBMISSION.md`
- `test_april_milestone.py`
- `web_attack_defense_demo.py`

## Bonus

### +6% Blockchain-based tamper-evident integrity

Implemented via `AuditBlock` model and chain verification endpoint.

### +2% Resume parsing and intelligent matching

Implemented in resume workflow:

- `GET /api/users/resume/parse/{filename}`
- `GET /api/users/resume/match/{filename}/{job_id}`

The matcher extracts skills from resume text and compares to job text/required skills.

## Notes

- New tables are auto-created by startup `Base.metadata.create_all`.
- User private keys are stored under `backend/keys/user_<id>/private.pem`.
- Public keys and fingerprints are stored in `user_signing_keys`.
