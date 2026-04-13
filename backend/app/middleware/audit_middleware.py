"""
Audit Middleware for Automatic Action Logging
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional
import json
import time

from ..services.audit_service import audit_service
from ..security import JWTHandler
from ..database import SessionLocal


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically audit API actions"""
    
    # Define which endpoints to audit and their action types
    AUDIT_ENDPOINTS = {
        # Authentication
        "POST:/api/auth/register": "USER_REGISTER",
        "POST:/api/auth/login": "USER_LOGIN",
        "POST:/api/auth/logout": "USER_LOGOUT",
        
        # User actions
        "PUT:/api/users/profile": "PROFILE_UPDATE",
        "POST:/api/users/resume/upload": "RESUME_UPLOAD",
        "DELETE:/api/users/resume/": "RESUME_DELETE",
        
        # Company actions
        "POST:/api/companies/": "COMPANY_CREATE",
        "PUT:/api/companies/": "COMPANY_UPDATE",
        "DELETE:/api/companies/": "COMPANY_DELETE",
        "POST:/api/companies//members": "COMPANY_MEMBER_ADD",
        "DELETE:/api/companies//members/": "COMPANY_MEMBER_REMOVE",
        
        # Job actions
        "POST:/api/jobs/": "JOB_CREATE",
        "PUT:/api/jobs/": "JOB_UPDATE",
        "DELETE:/api/jobs/": "JOB_DELETE",
        
        # Application actions
        "POST:/api/applications/": "APPLICATION_SUBMIT",
        "PUT:/api/applications/": "APPLICATION_UPDATE",
        "DELETE:/api/applications//withdraw": "APPLICATION_WITHDRAW",
        
        # Message actions
        "POST:/api/messages/conversations": "CONVERSATION_CREATE",
        "POST:/api/messages/conversations//messages": "MESSAGE_SEND",
        "DELETE:/api/messages/": "MESSAGE_DELETE",
        
        # Admin actions
        "DELETE:/api/admin/users/": "ADMIN_USER_DELETE",
        "PUT:/api/admin/users//suspend": "ADMIN_USER_SUSPEND",
    }
    
    async def dispatch(self, request: Request, call_next):
        # Get request info
        method = request.method
        path = request.url.path
        
        # Check if this endpoint should be audited
        action = self._get_action_for_endpoint(method, path)
        
        if not action:
            # No auditing needed for this endpoint
            return await call_next(request)
        
        # Get user info if authenticated
        user_id = await self._get_user_id(request)
        
        # Get request metadata
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent")
        
        # Get resource information
        resource_type, resource_id = self._extract_resource_info(path)
        
        # Process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Only log successful requests (2xx status codes)
        if 200 <= response.status_code < 300:
            # Get request details if needed
            details = await self._get_request_details(request, action)
            
            # Add response metadata
            details["response_status"] = response.status_code
            details["process_time_ms"] = round(process_time * 1000, 2)
            
            # Log the action
            try:
                db = request.state.db if hasattr(request.state, 'db') and request.state.db else SessionLocal()
                audit_service.log_action(
                    db=db,
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                if not (hasattr(request.state, 'db') and request.state.db):
                    db.close()
            except Exception as e:
                # Don't let audit logging break the application
                print(f"Audit logging failed: {e}")
        
        return response
    
    def _get_action_for_endpoint(self, method: str, path: str) -> Optional[str]:
        """Get the audit action for a specific endpoint"""
        endpoint_key = f"{method}:{path}"
        
        # Check for exact match
        if endpoint_key in self.AUDIT_ENDPOINTS:
            return self.AUDIT_ENDPOINTS[endpoint_key]
        
        # Check for pattern matches (with IDs)
        for pattern, action in self.AUDIT_ENDPOINTS.items():
            if self._path_matches_pattern(path, pattern.split(":")[1]):
                return action
        
        return None
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if a path matches a pattern with ID placeholders"""
        path_parts = path.strip("/").split("/")
        pattern_parts = pattern.strip("/").split("/")
        
        if len(path_parts) != len(pattern_parts):
            return False
        
        for path_part, pattern_part in zip(path_parts, pattern_parts):
            # If pattern part is empty, it's an ID placeholder
            if pattern_part == "" and path_part.isdigit():
                continue
            elif pattern_part != path_part:
                return False
        
        return True
    
    async def _get_user_id(self, request: Request) -> Optional[int]:
        """Extract user ID from JWT token"""
        try:
            authorization = request.headers.get("authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None
            
            token = authorization.split(" ")[1]
            payload = JWTHandler.decode_token(token)
            return payload.get("user_id")
        except Exception:
            return None
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to client IP
        return request.client.host if request.client else None
    
    def _extract_resource_info(self, path: str) -> tuple[Optional[str], Optional[int]]:
        """Extract resource type and ID from path"""
        parts = path.strip("/").split("/")
        
        if len(parts) >= 2:
            resource_type = parts[0]
            if len(parts) >= 3 and parts[2].isdigit():
                resource_id = int(parts[2])
                return resource_type, resource_id
        
        return None, None
    
    async def _get_request_details(self, request: Request, action: str) -> dict:
        """Get relevant details from the request based on action type"""
        details = {}
        
        try:
            if action in ["USER_REGISTER", "USER_LOGIN"]:
                # Don't log sensitive data, just that it occurred
                details["endpoint"] = f"{request.method} {request.url.path}"
            
            elif action in ["COMPANY_CREATE", "JOB_CREATE", "APPLICATION_SUBMIT"]:
                # Try to get request body for creation actions
                if hasattr(request, '_body'):
                    body = request._body.decode()
                    body_data = json.loads(body) if body else {}
                    
                    # Only log non-sensitive fields
                    if action == "COMPANY_CREATE":
                        details["company_name"] = body_data.get("name")
                    elif action == "JOB_CREATE":
                        details["job_title"] = body_data.get("title")
                        details["company_id"] = body_data.get("company_id")
                    elif action == "APPLICATION_SUBMIT":
                        details["job_id"] = body_data.get("job_id")
                        details["has_cover_note"] = bool(body_data.get("cover_note"))
            
            elif action == "MESSAGE_SEND":
                # Log that a message was sent but not the content
                details["conversation_id"] = None  # Will be set from path
                details["message_type"] = "text"
            
            details["method"] = request.method
            details["path"] = request.url.path
            
        except Exception:
            # If we can't get details, just log basic info
            details["method"] = request.method
            details["path"] = request.url.path
        
        return details
