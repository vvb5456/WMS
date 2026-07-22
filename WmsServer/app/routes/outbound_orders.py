from flask import Blueprint, g, request

from app.services import outbound_service
from app.utils.auth import login_required, role_required
from app.utils.response import paginate_response, success_response

bp = Blueprint("outbound_orders", __name__)


@bp.get("/outbound-orders")
@login_required
def list_orders():
    page = min(int(request.args.get("page", 1)), 9999)
    per_page = min(int(request.args.get("per_page", 20)), 100)
    pagination = outbound_service.list_orders(
        page=page, per_page=per_page,
        status=request.args.get("status"),
        warehouse_id=request.args.get("warehouse_id"),
    )
    return success_response(data=paginate_response(
        [o.to_dict() for o in pagination.items], page, per_page, pagination.total
    ))


@bp.get("/outbound-orders/<int:order_id>")
@login_required
def get_order(order_id):
    return success_response(data=outbound_service.get_order(order_id).to_dict())


@bp.post("/outbound-orders")
@role_required("admin", "warehouse_keeper", "viewer")
def create_order():
    data = request.get_json(silent=True) or {}
    order = outbound_service.create_order(data, g.current_user.id)
    return success_response(data=order.to_dict(), status=201)


@bp.put("/outbound-orders/<int:order_id>")
@role_required("admin", "warehouse_keeper", "viewer")
def update_order(order_id):
    data = request.get_json(silent=True) or {}
    order = outbound_service.update_order(order_id, data, g.current_user.id)
    return success_response(data=order.to_dict())


@bp.post("/outbound-orders/<int:order_id>/submit")
@role_required("admin", "warehouse_keeper", "viewer")
def submit_order(order_id):
    order = outbound_service.submit(order_id, g.current_user.id)
    return success_response(data=order.to_dict())


@bp.post("/outbound-orders/<int:order_id>/approve")
@role_required("admin", "warehouse_keeper")
def approve_order(order_id):
    from app.utils.gpio_control import approve_message, pulse_on_approve
    order = outbound_service.approve(order_id, g.current_user.id)
    pulse_on_approve()
    return success_response(data=order.to_dict(), message=approve_message())


@bp.post("/outbound-orders/<int:order_id>/reject")
@role_required("admin", "warehouse_keeper")
def reject_order(order_id):
    order = outbound_service.reject(order_id, g.current_user.id)
    return success_response(data=order.to_dict())


@bp.post("/outbound-orders/<int:order_id>/cancel")
@role_required("admin", "warehouse_keeper")
def cancel_order(order_id):
    order = outbound_service.cancel(order_id, g.current_user.id)
    return success_response(data=order.to_dict())


@bp.delete("/outbound-orders/<int:order_id>")
@role_required("admin", "warehouse_keeper", "viewer")
def delete_order(order_id):
    outbound_service.delete_order(order_id, g.current_user.id)
    return success_response(message="已删除")
