"""Password hashing and sessions for Campus Customs.

Stored format (matches the seed DB): pbkdf2_sha256$<salt>$<hex digest>
- PBKDF2-HMAC-SHA256, 120,000 iterations
- salt is a random text string, hashed as its UTF-8 bytes
- digest is the 32-byte result written as 64 hex characters
Signup and login both go through hash_password(), so the settings can never drift apart.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000
SESSION_TTL = 7 * 24 * 3600  # seconds
SESSION_COOKIE = "cc_session"


def hash_password(password: str, salt: str | None = None) -> str:
    """New signup: no salt given, so make a fresh random one. Login: pass the stored salt back in."""
    salt = salt or secrets.token_urlsafe(12)  # URL-safe text, never contains "$"
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS).hex()
    return f"{ALGORITHM}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    """Re-hash the typed password with the stored salt and compare in constant time. Never 'unhash'."""
    try:
        algorithm, salt, _ = stored.split("$", 2)
    except ValueError:
        return False
    if algorithm != ALGORITHM:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


# A real hash of a random password, so unknown emails cost the same time as wrong passwords.
DUMMY_HASH = hash_password(secrets.token_urlsafe(16))

# Opaque session token -> (user_id, expires_at). In memory: restarting the API logs everyone out.
_SESSIONS: dict[str, tuple[int, float]] = {}


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    _SESSIONS[token] = (user_id, time.time() + SESSION_TTL)
    return token


def session_user_id(token: str | None) -> int | None:
    if not token or token not in _SESSIONS:
        return None
    user_id, expires = _SESSIONS[token]
    if expires < time.time():
        _SESSIONS.pop(token, None)
        return None
    return user_id


def end_session(token: str | None) -> None:
    if token:
        _SESSIONS.pop(token, None)
