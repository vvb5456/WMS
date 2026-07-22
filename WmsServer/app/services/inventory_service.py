from decimal import Decimal

from app.extensions import db
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.utils.exceptions import InsufficientStockError


def get_or_create_inventory(product_id, warehouse_id, location_id) -> Inventory:
    inv = Inventory.query.filter_by(
        product_id=product_id,
        warehouse_id=warehouse_id,
        location_id=location_id,
    ).first()
    if not inv:
        inv = Inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            quantity=Decimal("0"),
        )
        db.session.add(inv)
        db.session.flush()
    return inv


def get_available_qty(product_id, warehouse_id, location_id) -> Decimal:
    inv = Inventory.query.filter_by(
        product_id=product_id,
        warehouse_id=warehouse_id,
        location_id=location_id,
    ).first()
    return inv.quantity if inv else Decimal("0")


def adjust_quantity(
    product_id,
    warehouse_id,
    location_id,
    delta_qty,
    ref_type,
    ref_id,
    operator_id,
    remark=None,
):
    """唯一允许修改 inventory.quantity 的入口。"""
    delta = Decimal(str(delta_qty))
    inv = get_or_create_inventory(product_id, warehouse_id, location_id)

    if delta < 0 and inv.quantity + delta < 0:
        raise InsufficientStockError(
            f"可用库存不足，当前 {float(inv.quantity)}，请求变动 {float(delta)}"
        )

    inv.quantity += delta
    balance = inv.quantity

    tx = InventoryTransaction(
        product_id=product_id,
        warehouse_id=warehouse_id,
        location_id=location_id,
        delta_qty=delta,
        balance_after=balance,
        ref_type=ref_type,
        ref_id=ref_id,
        operator_id=operator_id,
        remark=remark,
    )
    db.session.add(tx)
    db.session.flush()
    return inv, tx
