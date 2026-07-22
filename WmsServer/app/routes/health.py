from flask import Blueprint

from app.utils.response import success_response

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    return success_response(data={"status": "ok"})
