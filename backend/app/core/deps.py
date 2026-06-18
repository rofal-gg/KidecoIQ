"""
KidecoIQ — Shared Dependencies
Reusable FastAPI dependencies across modules.
"""

from app.core.database import get_db as _get_db
from app.core.auth import get_current_user


# Re-export with aliases for clarity
get_db = _get_db
get_user = get_current_user
