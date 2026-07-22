from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db
from app.models.stocktake_order import StocktakeOrder, StocktakeOrderLine
from app.models.warehouse import Warehouse
from app.services import inventory_service
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.order_no import generate_order_no


def list_orders(page=1, per_page=20, status=None, warehouse_id=None):
    q = StocktakeOrder.query
    if status:
        q = q.filter_by(status=status)
    if warehouse_id:
        q = q.filter_by(warehouse_id=warehouse_id)
    q = q.order_by(StocktakeOrder.created_at.desc())
    return q.paginate(page=page, per_page=per_page, error_out=False)


def get_order(order_id):
    order = StocktakeOrder.query.get(order_id)
    if not order:
        raise NotFoundError("盘点单不存在")
    return order


def create_order(data, operator_id):
    if not Warehouse.query.get(data.get("warehouse_id")):
        raise ValidationError("仓库不存在")
    order = StocktakeOrder(
        order_no=generate_order_no("ST"),
        warehouse_id=data["warehouse_id"],
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

    for line in order.lines:
        book = inventory_service.get_available_qty(
            line.product_id, order.warehouse_id, line.location_id
        )
        line.book_qty = book
        line.diff_qty = line.counted_qty - book
        if line.counted_qty == 0 and book > 0:
            raise ValidationError(
                f"明细实盘数量为 0，但账面仍有 {float(book)}，请核对后再审核"
            )
        if line.diff_qty != 0:
            inventory_service.adjust_quantity(
                line.product_id, order.warehouse_id, line.location_id,
                line.diff_qty, "stocktake", order.id, operator_id,
                remark=f"盘点单 {order.order_no}",
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
    StocktakeOrderLine.query.filter_by(stocktake_order_id=order.id).delete()
    for item in lines_data:
        counted = Decimal(str(item.get("counted_qty", 0)))
        line = StocktakeOrderLine(
            stocktake_order_id=order.id,
            product_id=item["product_id"],
            location_id=item["location_id"],
            book_qty=Decimal("0"),
            counted_qty=counted,
            diff_qty=Decimal("0"),
        )
        db.session.add(line)
