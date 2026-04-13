"""
April milestone APIs:
- Virtual keyboard OTP
- PKI signatures
- Blockchain-backed audit verification
- Bonus admin security dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SecurityEvent
from app.schemas import UserResponse
from ..services.april_security_service import april_security_service
from ..services.otp_service import otp_service
from .auth import get_current_user

router = APIRouter()


@router.post("/otp/keyboard-challenge", response_model=dict)
async def create_keyboard_otp_challenge(current_user: UserResponse = Depends(get_current_user)):
    """Returns a randomized virtual numeric keyboard challenge."""
    return april_security_service.create_virtual_keyboard_challenge(current_user.id)


@router.post("/otp/high-risk/request", response_model=dict)
async def request_high_risk_otp(
    current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Generate high-risk OTP and virtual keyboard challenge.
    OTP is delivered via existing OTP service; challenge is returned in response.
    """
    success, message = await otp_service.generate_and_send_otp(
        db, current_user.id, "high_risk", email=current_user.email
    )
    if not success:
        raise HTTPException(status_code=500, detail=message)
    challenge = april_security_service.create_virtual_keyboard_challenge(current_user.id)
    return {"message": "High-risk OTP sent", "challenge": challenge}


@router.post("/otp/keyboard-verify", response_model=dict)
async def verify_keyboard_otp(
    payload: dict,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verify OTP using keyboard positions instead of direct digit entry."""
    challenge_id = payload.get("challenge_id")
    positions = payload.get("positions")
    otp_type = payload.get("otp_type", "email")
    if not challenge_id or not isinstance(positions, list):
        raise HTTPException(status_code=400, detail="challenge_id and positions are required")

    success, message = april_security_service.verify_keyboard_otp(
        db, current_user.id, challenge_id, positions, otp_type
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "verified": True}


@router.post("/pki/keys/rotate", response_model=dict)
async def rotate_signing_keys(
    current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Generate or rotate user signing key pair."""
    return april_security_service.generate_or_rotate_keys(db, current_user.id)


@router.post("/pki/sign", response_model=dict)
async def sign_payload(payload: dict, current_user: UserResponse = Depends(get_current_user)):
    """Digitally sign payload using user private key."""
    if "data" not in payload:
        raise HTTPException(status_code=400, detail="Payload must include 'data'")
    try:
        return april_security_service.sign_payload(current_user.id, payload["data"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/pki/verify", response_model=dict)
async def verify_signature(
    payload: dict, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Verify signature for given user payload."""
    user_id = payload.get("user_id", current_user.id)
    data = payload.get("data")
    signature_b64 = payload.get("signature_b64")
    if data is None or not signature_b64:
        raise HTTPException(status_code=400, detail="data and signature_b64 are required")
    valid = april_security_service.verify_signature(db, user_id, data, signature_b64)
    return {"valid": valid}


@router.post("/audit/block", response_model=dict)
async def append_audit_block(
    payload: dict, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Append event as blockchain-inspired audit block."""
    event_type = payload.get("event_type", "generic_event")
    event_payload = payload.get("payload", {})
    block = april_security_service.append_audit_block(
        db,
        event_type,
        {"user_id": current_user.id, "payload": event_payload},
    )
    return {"block_index": block.block_index, "block_hash": block.block_hash}


@router.get("/audit/chain/verify", response_model=dict)
async def verify_blockchain_audit_chain(
    current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Admin-only blockchain integrity verification."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can verify blockchain audit chain",
        )
    return april_security_service.verify_audit_chain(db)


@router.get("/admin/security-dashboard", response_model=dict)
async def security_dashboard(
    current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Bonus: basic security dashboard with event counters."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access security dashboard",
        )

    events = db.query(SecurityEvent).all()
    counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for event in events:
        counts[event.severity] = counts.get(event.severity, 0) + 1
    return {"total_events": len(events), "severity_breakdown": counts}
