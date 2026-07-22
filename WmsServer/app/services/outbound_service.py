from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db
from app.models.outbound_order import OutboundOrder, OutboundOrderLine
from app.models.warehouse import Warehouse
from app.services import inventory_service
from app.utils.exceptions import ConflictError, InsufficientStockError, NotFoundError, ValidationError
from app.utils.order_no import generate_order_no


def list_orders(page=1, per_page=20, status=None, warehouse_id=None):
    q = OutboundOrder.query
    if status:
        q = q.filter_by(status=status)
    if warehouse_id:
        q = q.filter_by(warehouse_id=warehouse_id)
    q = q.order_by(OutboundOrder.created_at.desc())
    return q.paginate(page=page, per_page=per_page, error_out=False)


def get_order(order_id):
    order = OutboundOrder.query.get(order_id)
    if not order:
        raise NotFoundError("出库单不存在")
    return order


def create_order(data, operator_id):
    if not Warehouse.query.get(data.get("warehouse_id")):
        raise ValidationError("仓库不存在")
    order = OutboundOrder(
        order_no=generate_order_no("OUT"),
        warehouse_id=data["warehouse_id"],
        customer_name=data.get("customer_name"),
        remark=data.get("remark"),
        status="draft",
        created_by=operator_id,
    )
    db.session.add(order)
    db.session.flush()
    _replace_lines(order, data.get("lines", []))
    db.session.commit()
    return order


def update_order(order_id, data, operator_id):
    order = get_order(order_id)
    if order.status != "draft":
        raise ConflictError("仅草稿状态可编辑")
    if "warehouse_id" in data:
        order.warehouse_id = data["warehouse_id"]
    if "customer_name" in data:
        order.customer_name = data["customer_name"]
    if "remark" in data:
        order.remark = data["remark"]
    if "lines" in data:
        _replace_lines(order, data["lines"])
    db.session.commit()
    return order


def submit(order_id, operator_id):
    order = get_order(order_id)
    if order.status != "draft":
        raise ConflictError("仅草稿可提交")
    if not order.lines:
        raise ValidationError("单据明细不能为空")
    order.status = "submitted"
    db.session.commit()
    return order


def approve(order_id, operator_id):
    order = get_order(order_id)
    if order.status != "submitted":
        raise ConflictError("仅已提交单据可审核")
    now = datetime.now(timezone.utc)
    order.approved_by = operator_id
    order.approved_at = now

    errors = {}
    for i, line in enumerate(order.lines):
        qty = line.actual_qty if line.actual_qty > 0 else line.planned_qty
        if qty <= 0:
            raise ValidationError("明细数量必须大于0")
        available = inventory_service.get_available_qty(
            line.product_id, order.warehouse_id, line.location_id
        )
        if available < qty:
            sku = line.product.sku_code if line.product else str(line.product_id)
            loc = line.location.code if line.location else str(line.location_id)
            errors[f"lines[{i}].actual_qty"] = [f"可用 {float(available)}，请求 {float(qty)}"]
    if errors:
        raise InsufficientStockError(
            f"库存不足，无法出库", errors=errors
        )

    for line in order.lines:
        qty = line.actual_qty if line.actual_qty > 0 else line.planned_qty
        line.actual_qty = qty
        inventory_service.adjust_quantity(
            line.product_id, order.warehouse_id, line.location_id,
            -qty, "outbound", order.id, operator_id,
            remark=f"出库单 {order.order_no}",
        )

    order.status = "completed"
    order.completed_at = now
    db.session.commit()
    return order


def reject(order_id, operator_id):
    order = get_order(order_id)
    if order.status != "submitted":
        raise ConflictError("仅已提交单据可驳回")
    order.status = "draft"
    db.session.commit()
    return order


def cancel(order_id, operator_id):
    order = get_order(order_id)
    if order.status not in ("draft", "submitted"):
        raise ConflictError("当前状态不可取消")
    order.status = "cancelled"
    db.session.commit()
    return order


def delete_order(order_id, operator_id):
    order = get_order(order_id)
    if order.status != "draft":
        raise ConflictError("仅草稿可删除")
    db.session.delete(order)
    db.session.commit()


def _replace_lines(order, lines_data):
    OutboundOrderLine.query.filter_by(outbound_order_id=order.id).delete()
    for item in lines_data:
        line = OutboundOrderLine(
            outbound_order_id=order.id,
            product_id=item["product_id"],
            location_id=item["location_id"],
            planned_qty=Decimal(str(item.get("planned_qty", 0))),
            actual_qty=Decimal(str(item.get("actual_qty", 0))),
        )
        db.session.add(line)
