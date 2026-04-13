"""Social graph and connection APIs."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from .auth import get_current_user
from app.schemas import UserResponse, SuccessResponse
from ..models import Connection, ConnectionStatus, User, ProfileViewerSetting

router = APIRouter()


def _accepted_connection_query(db: Session, user_id: int):
    return db.query(Connection).filter(
        Connection.status == ConnectionStatus.ACCEPTED,
        ((Connection.requester_id == user_id) | (Connection.recipient_id == user_id)),
    )


@router.post("/connections/request/{target_user_id}", response_model=SuccessResponse)
async def send_connection_request(
    target_user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot connect with yourself")
    target = db.query(User).filter(User.id == target_user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")

    existing = db.query(Connection).filter(
        ((Connection.requester_id == current_user.id) & (Connection.recipient_id == target_user_id))
        | ((Connection.requester_id == target_user_id) & (Connection.recipient_id == current_user.id))
    ).first()
    if existing:
        return SuccessResponse(message="Connection already exists or pending", data={"connection_id": existing.id})

    connection = Connection(
        requester_id=current_user.id,
        recipient_id=target_user_id,
        status=ConnectionStatus.PENDING,
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return SuccessResponse(message="Connection request sent", data={"connection_id": connection.id})


@router.post("/connections/{connection_id}/accept", response_model=SuccessResponse)
async def accept_connection_request(
    connection_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection request not found")
    if connection.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only recipient can accept this request")
    connection.status = ConnectionStatus.ACCEPTED
    db.commit()
    return SuccessResponse(message="Connection request accepted", data={"connection_id": connection.id})


@router.delete("/connections/{connection_id}", response_model=SuccessResponse)
async def remove_connection(
    connection_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if current_user.id not in [connection.requester_id, connection.recipient_id]:
        raise HTTPException(status_code=403, detail="Not allowed to remove this connection")
    db.delete(connection)
    db.commit()
    return SuccessResponse(message="Connection removed", data={"connection_id": connection_id})


@router.get("/connections", response_model=dict)
async def list_connections(
    include_pending: bool = Query(False),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Connection).filter(
        (Connection.requester_id == current_user.id) | (Connection.recipient_id == current_user.id)
    )
    if not include_pending:
        query = query.filter(Connection.status == ConnectionStatus.ACCEPTED)
    rows = query.order_by(Connection.created_at.desc()).all()

    users = db.query(User).filter(User.id.in_([
        c.requester_id if c.requester_id != current_user.id else c.recipient_id
        for c in rows
    ])).all() if rows else []
    user_map = {u.id: u for u in users}

    items = []
    for c in rows:
        other_id = c.requester_id if c.requester_id != current_user.id else c.recipient_id
        other = user_map.get(other_id)
        items.append({
            "connection_id": c.id,
            "status": c.status.value if hasattr(c.status, "value") else str(c.status),
            "user_id": other_id,
            "name": f"{(other.first_name or '').strip()} {(other.last_name or '').strip()}".strip() if other else "",
            "email": other.email if other else "",
            "created_at": c.created_at,
        })
    return {"connections": items}


@router.get("/graph", response_model=dict)
async def connection_graph(
    depth: int = Query(1, ge=1, le=2),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Limited graph: depth 1 for direct accepted connections only.
    # Depth 2 returns one additional hop but still restricted.
    direct = _accepted_connection_query(db, current_user.id).all()
    direct_ids = set()
    for c in direct:
        direct_ids.add(c.requester_id if c.requester_id != current_user.id else c.recipient_id)

    nodes = {current_user.id}
    edges = []
    for uid in direct_ids:
        nodes.add(uid)
        edges.append({"from": current_user.id, "to": uid})

    if depth > 1 and direct_ids:
        second_hop = db.query(Connection).filter(
            Connection.status == ConnectionStatus.ACCEPTED,
            ((Connection.requester_id.in_(direct_ids)) | (Connection.recipient_id.in_(direct_ids))),
        ).all()
        for c in second_hop:
            a = c.requester_id
            b = c.recipient_id
            if a in direct_ids and b not in [current_user.id]:
                nodes.add(b)
                edges.append({"from": a, "to": b})
            if b in direct_ids and a not in [current_user.id]:
                nodes.add(a)
                edges.append({"from": b, "to": a})

    users = db.query(User).filter(User.id.in_(list(nodes))).all()
    label_map = {
        u.id: {
            "id": u.id,
            "name": f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}".strip() or u.email,
            "email": u.email,
        }
        for u in users
    }
    return {"nodes": [label_map[n] for n in nodes if n in label_map], "edges": edges}


@router.post("/viewer-settings", response_model=SuccessResponse)
async def update_viewer_identity_setting(
    payload: dict,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    show_identity = bool(payload.get("show_identity", True))
    setting = db.query(ProfileViewerSetting).filter(ProfileViewerSetting.user_id == current_user.id).first()
    if not setting:
        setting = ProfileViewerSetting(user_id=current_user.id, show_identity=show_identity)
        db.add(setting)
    else:
        setting.show_identity = show_identity
    db.commit()
    return SuccessResponse(message="Viewer identity setting updated", data={"show_identity": show_identity})
