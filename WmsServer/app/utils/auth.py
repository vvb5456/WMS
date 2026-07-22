import functools
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app, g, request

from app.models.user import User
from app.utils.exceptions import ForbiddenError, UnauthorizedError


def create_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        hours=current_app.config["JWT_EXPIRE_HOURS"]
    )
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


def login_required(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise UnauthorizedError()
        try:
            payload = decode_token(auth[7:])
            user = User.query.get(int(payload["sub"]))
            if not user or not user.is_active:
                raise UnauthorizedError()
            g.current_user = user
        except jwt.PyJWTError:
            raise UnauthorizedError()
        return fn(*args, **kwargs)

    return wrapper


def role_required(*roles):
    def decorator(fn):
        @functools.wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            if g.current_user.role not in roles and g.current_user.role != "admin":
                raise ForbiddenError()
            return fn(*args, **kwargs)

        return wrapper

    return decorator
