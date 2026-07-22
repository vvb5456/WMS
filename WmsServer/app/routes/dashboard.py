from datetime import date, datetime, time, timedelta, timezone

from flask import Blueprint, request
from sqlalchemy import case, func

from app.extensions import db
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.utils.auth import login_required
from app.utils.exceptions import ValidationError
from app.utils.response import success_response

bp = Blueprint("dashboard", __name__)

# 业务按中国日历日统计；流水 created_at 存的是 UTC 墙钟时间
CN_TZ = timezone(timedelta(hours=8))


def parse_date(value, field_name):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name}格式无效，应为 YYYY-MM-DD")


def local_day_range_to_utc_naive(start_date: date, end_date: date):
    """把本地（东八区）闭区间日期转成 UTC naive [start, end) 供 DATETIME 比较。"""
    start_local = datetime.combine(start_date, time.min, tzinfo=CN_TZ)
    end_local = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=CN_TZ)
    start_at = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    end_at = end_local.astimezone(timezone.utc).replace(tzinfo=None)
    return start_at, end_at


@bp.get("/dashboard/product-movement")
@login_required
def product_movement():
    """周期内按产品汇总出入库。"""
    end_date = parse_date(request.args.get("end_date", date.today().isoformat()), "结束日期")
    start_date = parse_date(
        request.args.get("start_date", (end_date - timedelta(days=6)).isoformat()),
        "开始日期",
    )
    if start_date > end_date:
        raise ValidationError("开始日期不能晚于结束日期")
    if (end_date - start_date).days > 365:
        raise ValidationError("统计时间范围不能超过 366 天")

    raw_warehouse_id = request.args.get("warehouse_id")
    warehouse_id = request.args.get("warehouse_id", type=int)
    if raw_warehouse_id and (warehouse_id is None or warehouse_id <= 0):
        raise ValidationError("仓库参数无效")

    start_at, end_at = local_day_range_to_utc_naive(start_date, end_date)

    inbound_sum = func.coalesce(
        func.sum(
            case(
                (InventoryTransaction.ref_type == "inbound", func.abs(InventoryTransaction.delta_qty)),
                else_=0,
            )
        ),
        0,
    )
    outbound_sum = func.coalesce(
        func.sum(
            case(
                (InventoryTransaction.ref_type == "outbound", func.abs(InventoryTransaction.delta_qty)),
                else_=0,
            )
        ),
        0,
    )

    movement_query = (
        db.session.query(
            InventoryTransaction.product_id.label("product_id"),
            inbound_sum.label("inbound_quantity"),
            outbound_sum.label("outbound_quantity"),
        )
        .filter(InventoryTransaction.ref_type.in_(("inbound", "outbound")))
        .filter(InventoryTransaction.created_at >= start_at)
        .filter(InventoryTransaction.created_at < end_at)
    )
    if warehouse_id:
        movement_query = movement_query.filter(InventoryTransaction.warehouse_id == warehouse_id)

    movement_rows = movement_query.group_by(InventoryTransaction.product_id).all()

    product_ids = [row.product_id for row in movement_rows]
    products = {
        product.id: product
        for product in Product.query.filter(Product.id.in_(product_ids)).all()
    } if product_ids else {}

    stock_map = {}
    if product_ids:
        stock_query = (
            db.session.query(
                Inventory.product_id.label("product_id"),
                func.coalesce(func.sum(Inventory.quantity), 0).label("current_quantity"),
            )
            .filter(Inventory.product_id.in_(product_ids))
        )
        if warehouse_id:
            stock_query = stock_query.filter(Inventory.warehouse_id == warehouse_id)
        stock_map = {
            row.product_id: float(row.current_quantity or 0)
            for row in stock_query.group_by(Inventory.product_id).all()
        }

    items = []
    for row in movement_rows:
        product = products.get(row.product_id)
        if not product:
            continue
        inbound_quantity = float(row.inbound_quantity or 0)
        outbound_quantity = float(row.outbound_quantity or 0)
        if inbound_quantity <= 0 and outbound_quantity <= 0:
            continue
        current_quantity = stock_map.get(row.product_id, 0.0)
        items.append({
            "product_id": product.id,
            "sku_code": product.sku_code,
            "name": product.name,
            "spec": product.spec or "",
            "unit": product.unit,
            "inbound_quantity": inbound_quantity,
            "outbound_quantity": outbound_quantity,
            "net_consumption": outbound_quantity - inbound_quantity,
            "current_quantity": current_quantity,
            "safe_stock": float(product.safe_stock or 0),
            "suggested_purchase": max(0.0, outbound_quantity - current_quantity),
        })

    items.sort(key=lambda item: (-item["outbound_quantity"], item["sku_code"]))

    return success_response(data={
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "warehouse_id": warehouse_id,
        "formula": "suggested_purchase = max(0, outbound_quantity - current_quantity)",
        "items": items,
    })
