from datetime import date, datetime, time, timedelta

from flask import Blueprint, request
from sqlalchemy import func

from app.extensions import db
from app.models.inventory_transaction import InventoryTransaction
from app.utils.auth import login_required
from app.utils.exceptions import ValidationError
from app.utils.response import success_response

bp = Blueprint("dashboard", __name__)


def parse_date(value, field_name):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name}格式无效，应为 YYYY-MM-DD")


@bp.get("/dashboard/inventory-trend")
@login_required
def inventory_trend():
    end_date = parse_date(request.args.get("end_date", date.today().isoformat()), "结束日期")
    start_date = parse_date(
        request.args.get("start_date", (end_date - timedelta(days=6)).isoformat()),
        "开始日期",
    )
    if start_date > end_date:
        raise ValidationError("开始日期不能晚于结束日期")
    if (end_date - start_date).days > 365:
        raise ValidationError("统计时间范围不能超过 366 天")

    day_expression = func.date(InventoryTransaction.created_at)
    query = (
        db.session.query(
            day_expression.label("day"),
            InventoryTransaction.ref_type,
            func.sum(InventoryTransaction.delta_qty).label("quantity"),
        )
        .filter(InventoryTransaction.ref_type.in_(("inbound", "outbound")))
        .filter(InventoryTransaction.created_at >= datetime.combine(start_date, time.min))
        .filter(
            InventoryTransaction.created_at
            < datetime.combine(end_date + timedelta(days=1), time.min)
        )
    )

    raw_warehouse_id = request.args.get("warehouse_id")
    warehouse_id = request.args.get("warehouse_id", type=int)
    if raw_warehouse_id and (warehouse_id is None or warehouse_id <= 0):
        raise ValidationError("仓库参数无效")
    if warehouse_id:
        query = query.filter(InventoryTransaction.warehouse_id == warehouse_id)

    raw_product_id = request.args.get("product_id")
    product_id = request.args.get("product_id", type=int)
    if raw_product_id and (product_id is None or product_id <= 0):
        raise ValidationError("产品参数无效")
    if product_id:
        query = query.filter(InventoryTransaction.product_id == product_id)

    rows = query.group_by(day_expression, InventoryTransaction.ref_type).all()
    quantities = {}
    for day, ref_type, quantity in rows:
        day_key = day.isoformat() if hasattr(day, "isoformat") else str(day)
        quantities[(day_key, ref_type)] = abs(float(quantity or 0))

    items = []
    current = start_date
    while current <= end_date:
        day_key = current.isoformat()
        items.append({
            "date": day_key,
            "inbound_quantity": quantities.get((day_key, "inbound"), 0),
            "outbound_quantity": quantities.get((day_key, "outbound"), 0),
        })
        current += timedelta(days=1)

    return success_response(data={
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "warehouse_id": warehouse_id,
        "product_id": product_id,
        "items": items,
    })
