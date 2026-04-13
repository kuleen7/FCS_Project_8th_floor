"""
Encrypted Messaging API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from math import ceil

from app.database import get_db
from app.schemas import (
    MessageCreate, MessageResponse, ConversationCreate, ConversationResponse,
    ConversationMessagesResponse, SuccessResponse
)
from ..services.message_service import message_service
from ..models import User
from .auth import get_current_user
from app.schemas import UserResponse

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation
    
    - Users can create one-to-one or group conversations
    - Creator automatically becomes admin participant
    """
    try:
        conversation = message_service.create_conversation(db, conversation_data, current_user.id)
        return ConversationResponse.from_orm(conversation)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for the current user
    """
    try:
        conversations, total = message_service.get_user_conversations(db, current_user.id, page, limit)
        return [ConversationResponse.from_orm(conv) for conv in conversations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.get("/user-directory", response_model=list[dict])
async def get_user_directory(
    q: str = Query("", description="Search by name or email"),
    limit: int = Query(30, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Messaging user directory for participant selection.
    Includes active users except current user.
    """
    query = db.query(User).filter(User.id != current_user.id).filter(User.is_active == True)
    if q:
        like_q = f"%{q}%"
        query = query.filter(
            (User.first_name.ilike(like_q)) |
            (User.last_name.ilike(like_q)) |
            (User.email.ilike(like_q))
        )

    users = query.order_by(User.id.desc()).limit(limit).all()
    return [
        {
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
            "role": u.role.value if hasattr(u.role, "value") else str(u.role),
            "is_verified": bool(u.is_verified),
        }
        for u in users
    ]


@router.post("/resolve-participants", response_model=dict)
async def resolve_participants(
    payload: dict,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Resolve participant emails to user IDs for conversation creation.
    """
    emails = payload.get("emails", [])
    if not isinstance(emails, list) or not emails:
        raise HTTPException(status_code=400, detail="emails must be a non-empty list")

    normalized = [str(e).strip().lower() for e in emails if str(e).strip()]
    if not normalized:
        raise HTTPException(status_code=400, detail="No valid emails provided")

    users = (
        db.query(User)
        .filter(User.email.in_(normalized))
        .filter(User.id != current_user.id)
        .all()
    )
    found_map = {u.email.lower(): u for u in users}

    found = []
    missing = []
    for email in normalized:
        user = found_map.get(email)
        if user:
            found.append(
                {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            )
        else:
            missing.append(email)

    return {"found": found, "missing": missing}


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get conversation details by ID
    
    - Only participants can view conversation details
    """
    try:
        conversation = message_service.get_conversation_by_id(db, conversation_id, current_user.id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return ConversationResponse.from_orm(conversation)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to a conversation
    
    - Only participants can send messages
    - Messages are encrypted end-to-end
    """
    try:
        # Override conversation_id from URL
        message_data.conversation_id = conversation_id
        message = message_service.send_message(db, message_data, current_user.id)
        return MessageResponse.from_orm(message)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send message"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=ConversationMessagesResponse)
async def get_conversation_messages(
    conversation_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get messages in a conversation
    
    - Only participants can view messages
    - Messages are decrypted for the current user
    """
    try:
        # Get conversation details
        conversation = message_service.get_conversation_by_id(db, conversation_id, current_user.id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages
        messages, total = message_service.get_conversation_messages(
            db, conversation_id, current_user.id, page, limit
        )
        
        # Convert to response format
        message_responses = []
        for msg_dict in messages:
            msg_response = MessageResponse(
                id=msg_dict["id"],
                conversation_id=msg_dict["conversation_id"],
                sender_id=msg_dict["sender_id"],
                content_encrypted=msg_dict.get("content", msg_dict["content_encrypted"]),
                content_hash=msg_dict.get("content_hash"),
                message_type=msg_dict["message_type"],
                reply_to_id=msg_dict.get("reply_to_id"),
                is_deleted=msg_dict["is_deleted"],
                is_edited=msg_dict["is_edited"],
                created_at=msg_dict["created_at"],
                updated_at=msg_dict.get("updated_at"),
                sender=msg_dict.get("sender")
            )
            message_responses.append(msg_response)
        
        total_pages = ceil(total / limit)
        
        return ConversationMessagesResponse(
            conversation=ConversationResponse.from_orm(conversation),
            messages=message_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )


@router.post("/conversations/{conversation_id}/read", response_model=SuccessResponse)
async def mark_conversation_as_read(
    conversation_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark messages in a conversation as read
    
    - Updates the user's last_read_at timestamp
    """
    try:
        success = message_service.mark_messages_as_read(db, conversation_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return SuccessResponse(message="Conversation marked as read")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark conversation as read"
        )


@router.post("/conversations/{conversation_id}/participants/{user_id}", response_model=SuccessResponse)
async def add_participant_to_conversation(
    conversation_id: int,
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a participant to a conversation
    
    - Only conversation admins can add participants
    """
    try:
        success = message_service.add_participant_to_conversation(
            db, conversation_id, user_id, current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to add participant"
            )
        return SuccessResponse(message="Participant added successfully")
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add participant"
        )


@router.delete("/conversations/{conversation_id}/participants/{user_id}", response_model=SuccessResponse)
async def remove_participant_from_conversation(
    conversation_id: int,
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a participant from a conversation
    
    - Conversation admins can remove any participant
    - Users can remove themselves
    """
    try:
        success = message_service.remove_participant_from_conversation(
            db, conversation_id, user_id, current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participant not found"
            )
        return SuccessResponse(message="Participant removed successfully")
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove participant"
        )


@router.delete("/messages/{message_id}", response_model=SuccessResponse)
async def delete_message(
    message_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a message (soft delete)
    
    - Only message sender can delete their own messages
    """
    try:
        success = message_service.delete_message(db, message_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        return SuccessResponse(message="Message deleted successfully")
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete message"
        )


@router.get("/unread/count", response_model=dict)
async def get_unread_message_count(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get count of unread messages for the current user
    """
    try:
        count = message_service.get_unread_message_count(db, current_user.id)
        return {"unread_count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve unread message count"
        )


@router.get("/conversations/{conversation_id}/exists", response_model=dict)
async def check_conversation_exists(
    conversation_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a conversation exists and user is a participant
    """
    try:
        conversation = message_service.get_conversation_by_id(db, conversation_id, current_user.id)
        return {"exists": conversation is not None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check conversation existence"
        )
