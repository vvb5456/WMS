from datetime import datetime, timezone

from flask import Blueprint, g, request

from app.models.user import User
from app.utils.auth import create_token, login_required
from app.utils.exceptions import UnauthorizedError, ValidationError
from app.utils.response import success_response

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        raise ValidationError("用户名和密码不能为空")
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password) or not user.is_active:
        raise UnauthorizedError("用户名或密码错误")
    user.last_login_at = datetime.now(timezone.utc)
    from app.extensions import db
    db.session.commit()
    token = create_token(user.id, user.role)
    return success_response(data={"token": token, "user": user.to_dict()})


@bp.get("/me")
@login_required
def me():
    return success_response(data=g.current_user.to_dict())


@bp.post("/me/change-password")
@login_required
def change_password():
    data = request.get_json(silent=True) or {}
    old_password = data.get("old_password") or ""
    new_password = (data.get("new_password") or "").strip()

    if not old_password or not new_password:
        raise ValidationError("原密码和新密码不能为空")
    if not g.current_user.check_password(old_password):
        raise UnauthorizedError("原密码错误")
    if old_password == new_password:
        raise ValidationError("新密码不能与原密码相同")

    from app.extensions import db
    g.current_user.set_password(new_password)
    db.session.commit()
    return success_response(message="密码修改成功")
