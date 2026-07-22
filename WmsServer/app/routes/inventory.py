from flask import Blueprint, request

from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.utils.auth import login_required
from app.utils.response import paginate_response, success_response

bp = Blueprint("inventory", __name__)


@bp.get("/inventory")
@login_required
def list_inventory():
    page = min(int(request.args.get("page", 1)), 9999)
    per_page = min(int(request.args.get("per_page", 20)), 100)
    q = Inventory.query
    wh_id = request.args.get("warehouse_id")
    if wh_id:
        q = q.filter_by(warehouse_id=wh_id)
    if request.args.get("in_stock") in ("1", "true", "yes"):
        q = q.filter(Inventory.quantity > 0)
    sku = request.args.get("sku_code")
    if sku:
        q = q.join(Product).filter(Product.sku_code.like(f"%{sku}%"))
    pagination = q.order_by(Inventory.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = [inv.to_dict() for inv in pagination.items]
    return success_response(data=paginate_response(items, page, per_page, pagination.total))


@bp.get("/inventory/transactions")
@login_required
def list_transactions():
    page = min(int(request.args.get("page", 1)), 9999)
    per_page = min(int(request.args.get("per_page", 20)), 100)
    q = InventoryTransaction.query
    wh_id = request.args.get("warehouse_id")
    if wh_id:
        q = q.filter_by(warehouse_id=wh_id)
    ref_type = request.args.get("ref_type")
    if ref_type:
        q = q.filter_by(ref_type=ref_type)
    pagination = q.order_by(InventoryTransaction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return success_response(data=paginate_response(
        [tx.to_dict() for tx in pagination.items], page, per_page, pagination.total
    ))


@bp.get("/inventory/alerts")
@login_required
def low_stock_alerts():
    from sqlalchemy import func
    from app.extensions import db
    rows = (
        db.session.query(Inventory, Product)
        .join(Product, Inventory.product_id == Product.id)
        .filter(Inventory.quantity < Product.safe_stock)
        .filter(Product.is_active.is_(True))
        .all()
    )
    items = []
    for inv, prod in rows:
        d = inv.to_dict()
        d["safe_stock"] = float(prod.safe_stock)
        items.append(d)
    return success_response(data=items)
