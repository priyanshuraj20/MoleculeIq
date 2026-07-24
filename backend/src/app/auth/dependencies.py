"""
app/auth/dependencies.py

FastAPI dependency for protecting API endpoints with custom JWT authentication.
Supports both HttpOnly cookies and Bearer Authorization headers.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import decode_access_token

logger = logging.getLogger(__name__)

# Security scheme for OpenAPI docs (optional Bearer)
security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Dict[str, Any]:
    """
    FastAPI dependency that extracts and validates custom JWT.
    
    Checks in order:
      1. HttpOnly cookie named 'access_token'
      2. Authorization: Bearer <token> header
      3. Query parameter 'token' (for EventSource SSE streaming connections)
      
    Returns decoded user payload or raises 401 Unauthorized exception.
    """
    token: Optional[str] = None

    # 1. Check HttpOnly cookie
    if "access_token" in request.cookies:
        token = request.cookies["access_token"]

    # 2. Check Bearer Authorization header
    elif token_auth and token_auth.credentials:
        token = token_auth.credentials

    # 3. Check query string token (useful for EventSource SSE which cannot send custom headers)
    elif "token" in request.query_params:
        token = request.query_params["token"]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Please log in with Google.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and validate JWT
    payload = decode_access_token(token)
    return payload
