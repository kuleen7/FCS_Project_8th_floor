# Final System Demo Submission (April 30)

## Scope Covered

- PKI integration for security-critical actions
- Virtual keyboard OTP for high-risk actions
- Tamper-evident logging and integrity verification
- Demonstrated defenses against common web attacks
- Bonus blockchain logging and resume intelligent matching

## Demo Steps

1. Login and obtain JWT.
2. Rotate PKI keys: `POST /api/april/pki/keys/rotate`.
3. Request high-risk OTP + keyboard challenge: `POST /api/april/otp/high-risk/request`.
4. Sign action payload:
   - `POST /api/april/pki/sign` with payload:
     - `{"data": {"action":"job.create","ts":"<ISO-UTC>"}}`
5. Call protected critical endpoint (job create/update or admin suspend/reactivate/delete) with:
   - `Authorization: Bearer <token>`
   - `X-Security-Payload`
   - `X-Security-Signature`
   - `X-OTP-Challenge-ID`
   - `X-OTP-Positions`
6. Append blockchain audit block:
   - `POST /api/april/audit/block`
7. Verify blockchain integrity (admin):
   - `GET /api/april/audit/chain/verify`
8. Upload resume, then:
   - Parse: `GET /api/users/resume/parse/{filename}`
   - Match: `GET /api/users/resume/match/{filename}/{job_id}`

## Web Attack Defense Demonstration

Run:

```bash
python3 web_attack_defense_demo.py
```

This demonstrates:

- Security response headers
- Blocking suspicious query patterns
- Rate limiting under request bursts

## Files Added/Updated for April

- `backend/app/services/april_security_service.py`
- `backend/app/api/april.py`
- `backend/app/models/__init__.py`
- `backend/app/api/jobs.py`
- `backend/app/api/admin.py`
- `backend/app/api/users.py`
- `backend/app/main.py`
- `APRIL_MILESTONE_IMPLEMENTATION.md`
- `FINAL_SYSTEM_DEMO_SUBMISSION.md`
- `test_april_milestone.py`
- `web_attack_defense_demo.py`
