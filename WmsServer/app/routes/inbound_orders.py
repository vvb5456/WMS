from flask import Blueprint, g, request

from app.services import inbound_service
from app.utils.auth import login_required, role_required
from app.utils.response import paginate_response, success_response

bp = Blueprint("inbound_orders", __name__)


@bp.get("/inbound-orders")
@login_required
def list_orders():
    page = min(int(request.args.get("page", 1)), 9999)
    per_page = min(int(request.args.get("per_page", 20)), 100)
    pagination = inbound_service.list_orders(
        page=page, per_page=per_page,
        status=request.args.get("status"),
        warehouse_id=request.args.get("warehouse_id"),
    )
    return success_response(data=paginate_response(
        [o.to_dict() for o in pagination.items], page, per_page, pagination.total
    ))


@bp.get("/inbound-orders/<int:order_id>")
@login_required
def get_order(order_id):
    return success_response(data=inbound_service.get_order(order_id).to_dict())


@bp.post("/inbound-orders")
@role_required("admin", "warehouse_keeper", "viewer")
def create_order():
    data = request.get_json(silent=True) or {}
    order = inbound_service.create_order(data, g.current_user.id)
    return success_response(data=order.to_dict(), status=201)


@bp.put("/inbound-orders/<int:order_id>")
@role_required("admin", "warehouse_keeper", "viewer")
def update_order(order_id):
    data = request.get_json(silent=True) or {}
    order = inbound_service.update_order(order_id, data, g.current_user.id)
    return success_response(data=order.to_dict())


@bp.post("/inbound-orders/<int:order_id>/submit")
@role_required("admin", "warehouse_keeper", "viewer")
def submit_order(order_id):
    order = inbound_service.submit(order_id, g.current_user.id)
    return success_response(data=order.to_dict())


@bp.post("/inbound-orders/<int:order_id>/approve")
@role_required("admin", "warehouse_keeper")
def approve_order(order_id):
    from app.utils.gpio_control import approve_message, pulse_on_approve
    order = inbound_service.approve(order_id, g.current_user.id)
    pulse_on_approve()
    return success_response(data=order.to_dict(), message=approve_message())


@bp.post("/inbound-orders/<int:order_id>/reject")
@role_required("admin", "warehouse_keeper")
def reject_order(order_id):
    order = inbound_service.reject(order_id, g.current_user.id)
    return success_response(data=order.to_dict())


@bp.post("/inbound-orders/<int:order_id>/cancel")
@role_required("admin", "warehouse_keeper")
def cancel_order(order_id):
    order = inbound_service.cancel(order_id, g.current_user.id)
    return success_response(data=order.to_dict())


@bp.delete("/inbound-orders/<int:order_id>")
@role_required("admin", "warehouse_keeper", "viewer")
def delete_order(order_id):
    inbound_service.delete_order(order_id, g.current_user.id)
    return success_response(message="已删除")
