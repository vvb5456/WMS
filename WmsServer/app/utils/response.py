from flask import jsonify


def success_response(data=None, message="操作成功", code="OK", status=200):
    return jsonify({
        "success": True,
        "code": code,
        "message": message,
        "data": data,
    }), status


def error_response(message, code="INTERNAL_ERROR", status=500, errors=None):
    return jsonify({
        "success": False,
        "code": code,
        "message": message,
        "data": None,
        "errors": errors,
    }), status


def paginate_response(items, page, per_page, total):
    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
    }
