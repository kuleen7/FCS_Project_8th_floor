"""
Encrypted Messaging Service
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime
import json
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

from ..models import Message, Conversation, ConversationParticipant, User, ConversationType
from ..schemas import MessageCreate, ConversationCreate


class MessageService:
    """Service for managing encrypted conversations and messages"""
    
    def __init__(self):
        # Generate or load encryption key
        self._master_key = self._get_or_create_master_key()
    
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""
        key_file = "message_encryption.key"
        try:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                return key
        except Exception:
            # Fallback to generated key if file operations fail
            return Fernet.generate_key()
    
    def _derive_conversation_key(self, conversation_id: int) -> bytes:
        """Derive a shared encryption key for a conversation."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=f"{conversation_id}".encode(),
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self._master_key))
    
    def _encrypt_message(self, content: str, conversation_id: int, sender_id: int) -> Tuple[str, str]:
        """Encrypt message content and return encrypted content and hash"""
        key = self._derive_conversation_key(conversation_id)
        fernet = Fernet(key)
        
        # Encrypt content
        encrypted_content = fernet.encrypt(content.encode()).decode()
        
        # Generate hash for integrity verification
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        return encrypted_content, content_hash
    
    def _decrypt_message(self, encrypted_content: str, conversation_id: int, user_id: int) -> str:
        """Decrypt message content"""
        key = self._derive_conversation_key(conversation_id)
        fernet = Fernet(key)
        
        try:
            decrypted_content = fernet.decrypt(encrypted_content.encode()).decode()
            return decrypted_content
        except Exception as e:
            raise ValueError(f"Failed to decrypt message: {str(e)}")
    
    def create_conversation(self, db: Session, conversation_data: ConversationCreate, creator_id: int) -> Optional[Conversation]:
        """Create a new conversation"""
        try:
            # Create conversation
            conversation = Conversation(
                type=conversation_data.type,
                name=conversation_data.name,
                created_by=creator_id
            )
            db.add(conversation)
            db.flush()  # Get the conversation ID
            
            # Add participants
            participant_ids = list(set(conversation_data.participant_ids + [creator_id]))
            for participant_id in participant_ids:
                # Verify user exists
                user = db.query(User).filter(User.id == participant_id).first()
                if not user:
                    raise ValueError(f"User with ID {participant_id} does not exist")
                
                participant = ConversationParticipant(
                    conversation_id=conversation.id,
                    user_id=participant_id,
                    role="admin" if participant_id == creator_id else "participant"
                )
                db.add(participant)
            
            db.commit()
            db.refresh(conversation)
            return conversation
        except Exception as e:
            db.rollback()
            raise e
    
    def get_conversation_by_id(self, db: Session, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """Get conversation by ID if user is a participant"""
        return (
            db.query(Conversation)
            .join(ConversationParticipant)
            .filter(
                and_(
                    Conversation.id == conversation_id,
                    ConversationParticipant.user_id == user_id,
                    ConversationParticipant.is_active == True,
                    Conversation.is_active == True
                )
            )
            .first()
        )
    
    def get_user_conversations(self, db: Session, user_id: int, page: int = 1, limit: int = 20) -> Tuple[List[Conversation], int]:
        """Get all conversations for a user"""
        query = (
            db.query(Conversation)
            .join(ConversationParticipant)
            .filter(
                and_(
                    ConversationParticipant.user_id == user_id,
                    ConversationParticipant.is_active == True,
                    Conversation.is_active == True
                )
            )
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        conversations = (
            query
            .order_by(desc(Conversation.updated_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        return conversations, total
    
    def send_message(self, db: Session, message_data: MessageCreate, sender_id: int) -> Optional[Message]:
        """Send a new message"""
        # Verify user is participant in conversation
        conversation = self.get_conversation_by_id(db, message_data.conversation_id, sender_id)
        if not conversation:
            raise PermissionError("User is not a participant in this conversation")
        
        try:
            # Encrypt message content
            encrypted_content, content_hash = self._encrypt_message(
                message_data.content, 
                message_data.conversation_id, 
                sender_id
            )
            
            # Create message
            message = Message(
                conversation_id=message_data.conversation_id,
                sender_id=sender_id,
                content_encrypted=encrypted_content,
                content_hash=content_hash,
                message_type=message_data.message_type,
                reply_to_id=message_data.reply_to_id
            )
            
            db.add(message)
            
            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            
            # Update participant last_read_at for sender
            participant = (
                db.query(ConversationParticipant)
                .filter(
                    and_(
                        ConversationParticipant.conversation_id == message_data.conversation_id,
                        ConversationParticipant.user_id == sender_id
                    )
                )
                .first()
            )
            if participant:
                participant.last_read_at = datetime.utcnow()
            
            db.commit()
            db.refresh(message)
            return message
        except Exception as e:
            db.rollback()
            raise e
    
    def get_conversation_messages(self, db: Session, conversation_id: int, user_id: int, 
                                page: int = 1, limit: int = 50) -> Tuple[List[Message], int]:
        """Get messages in a conversation with decrypted content"""
        # Verify user is participant
        conversation = self.get_conversation_by_id(db, conversation_id, user_id)
        if not conversation:
            raise PermissionError("User is not a participant in this conversation")
        
        query = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .filter(Message.is_deleted == False)
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        messages = (
            query
            .order_by(Message.created_at)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        # Decrypt messages for this user
        decrypted_messages = []
        for message in messages:
            try:
                decrypted_content = self._decrypt_message(
                    message.content_encrypted, 
                    conversation_id, 
                    user_id
                )
                # Create a copy with decrypted content
                message_dict = {
                    "id": message.id,
                    "conversation_id": message.conversation_id,
                    "sender_id": message.sender_id,
                    "content": decrypted_content,  # Decrypted content
                    "content_encrypted": message.content_encrypted,
                    "content_hash": message.content_hash,
                    "message_type": message.message_type,
                    "reply_to_id": message.reply_to_id,
                    "is_deleted": message.is_deleted,
                    "is_edited": message.is_edited,
                    "created_at": message.created_at,
                    "updated_at": message.updated_at,
                    "sender": message.sender
                }
                decrypted_messages.append(message_dict)
            except Exception:
                # If decryption fails, skip this message
                continue
        
        return decrypted_messages, total
    
    def mark_messages_as_read(self, db: Session, conversation_id: int, user_id: int) -> bool:
        """Mark messages as read for a user"""
        participant = (
            db.query(ConversationParticipant)
            .filter(
                and_(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == user_id
                )
            )
            .first()
        )
        
        if participant:
            participant.last_read_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    def add_participant_to_conversation(self, db: Session, conversation_id: int, user_id: int, 
                                       new_participant_id: int, requester_id: int) -> bool:
        """Add a participant to a conversation"""
        # Check if requester has permission
        participant = (
            db.query(ConversationParticipant)
            .filter(
                and_(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == requester_id,
                    ConversationParticipant.role.in_(["admin"])
                )
            )
            .first()
        )
        
        if not participant:
            raise PermissionError("User does not have permission to add participants")
        
        # Check if new participant already exists
        existing = (
            db.query(ConversationParticipant)
            .filter(
                and_(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == new_participant_id
                )
            )
            .first()
        )
        
        if existing:
            if not existing.is_active:
                existing.is_active = True
                db.commit()
                return True
            return False
        
        try:
            new_participant = ConversationParticipant(
                conversation_id=conversation_id,
                user_id=new_participant_id,
                role="participant"
            )
            db.add(new_participant)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    def remove_participant_from_conversation(self, db: Session, conversation_id: int, user_id: int, 
                                           requester_id: int) -> bool:
        """Remove a participant from a conversation"""
        # Check if requester has permission or is removing themselves
        requester_participant = (
            db.query(ConversationParticipant)
            .filter(
                and_(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == requester_id
                )
            )
            .first()
        )
        
        if not requester_participant:
            raise PermissionError("User is not a participant in this conversation")
        
        # Users can remove themselves, admins can remove others
        if requester_id != user_id and requester_participant.role != "admin":
            raise PermissionError("User does not have permission to remove this participant")
        
        participant = (
            db.query(ConversationParticipant)
            .filter(
                and_(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == user_id
                )
            )
            .first()
        )
        
        if participant:
            participant.is_active = False
            db.commit()
            return True
        return False
    
    def delete_message(self, db: Session, message_id: int, user_id: int) -> bool:
        """Delete a message (soft delete)"""
        message = (
            db.query(Message)
            .filter(Message.id == message_id)
            .first()
        )
        
        if not message:
            return False
        
        # Only sender can delete their own messages
        if message.sender_id != user_id:
            raise PermissionError("Only message sender can delete their own messages")
        
        try:
            message.is_deleted = True
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    def get_unread_message_count(self, db: Session, user_id: int) -> int:
        """Get count of unread messages for a user"""
        return (
            db.query(Message)
            .join(ConversationParticipant)
            .filter(
                and_(
                    ConversationParticipant.user_id == user_id,
                    ConversationParticipant.is_active == True,
                    Message.is_deleted == False,
                    or_(
                        ConversationParticipant.last_read_at.is_(None),
                        Message.created_at > ConversationParticipant.last_read_at
                    ),
                    Message.sender_id != user_id  # Exclude own messages
                )
            )
            .count()
        )


# Create singleton instance
message_service = MessageService()
