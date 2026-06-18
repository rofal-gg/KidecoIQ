"""
KidecoIQ — Authentication Stub
JWT-based auth placeholder. Will be expanded in later phases.
Currently allows all requests (no-auth mode for MVP development).
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Stub: in MVP phase, returns a hardcoded user ID.
    In production, would decode JWT and return the user subject.

    Returns:
        str: username / user ID
    """
    # For MVP, allow anonymous access
    # If credentials are provided, attempt to decode them
    if credentials is not None:
        try:
            from jose import jwt as jose_jwt
            from app.core.config import get_settings
            settings = get_settings()
            payload = jose_jwt.decode(
                credentials.credentials,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload.get("sub", "anonymous")
        except Exception:
            # Invalid token → fall through to anonymous
            pass
    return "anonymous"
