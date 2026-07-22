from flask import Blueprint, g, request

from app.extensions import db
from app.models.user import User
from app.utils.auth import login_required, role_required
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.response import paginate_response, success_response

bp = Blueprint("users", __name__)

DEFAULT_PASSWORD = "888888"
VALID_ROLES = {"admin", "warehouse_keeper", "viewer"}


@bp.get("/users")
@role_required("admin")
def list_users():
    page = min(int(request.args.get("page", 1)), 9999)
    per_page = min(int(request.args.get("per_page", 20)), 100)
    pagination = (
        User.query.filter_by(is_active=True)
        .order_by(User.id)
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return success_response(data=paginate_response(
        [u.to_dict() for u in pagination.items], page, per_page, pagination.total
    ))


@bp.post("/users")
@role_required("admin")
def create_user():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    name = (data.get("name") or "").strip()
    password = (data.get("password") or "").strip() or DEFAULT_PASSWORD
    role = (data.get("role") or "").strip()

    if not username or not name:
        raise ValidationError("用户名和姓名必填")
    if role not in VALID_ROLES:
        raise ValidationError("角色无效")
    if User.query.filter_by(username=username).first():
        raise ConflictError("用户名已存在")

    user = User(username=username, name=name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return success_response(data=user.to_dict(), status=201)


@bp.post("/users/<int:user_id>/reset-password")
@role_required("admin")
def reset_user_password(user_id):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("用户不存在")
    user.set_password(DEFAULT_PASSWORD)
    db.session.commit()
    return success_response(message=f"密码已重置为 {DEFAULT_PASSWORD}")


@bp.delete("/users/<int:user_id>")
@role_required("admin")
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user or not user.is_active:
        raise NotFoundError("用户不存在")
    if user.id == g.current_user.id:
        raise ValidationError("不能删除当前登录用户")
    if user.role == "admin":
        active_admin_count = User.query.filter_by(role="admin", is_active=True).count()
        if active_admin_count <= 1:
            raise ValidationError("不能删除最后一个管理员")

    user.is_active = False
    db.session.commit()
    return success_response(message="用户已删除")
