from flask import Blueprint, request
import re

from app.extensions import db
from app.models.inventory import Inventory
from app.models.product import Product
from app.utils.auth import login_required, role_required
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.response import paginate_response, success_response

bp = Blueprint("products", __name__)

_CODE_PATTERN = re.compile(r"^(?:SKU-)?P(\d+)$", re.I)


def _next_product_code() -> str:
    max_num = 0
    for (code,) in db.session.query(Product.sku_code).all():
        m = _CODE_PATTERN.match(code or "")
        if m:
            max_num = max(max_num, int(m.group(1)))
    return f"P{max_num + 1:03d}"


@bp.get("/products/suggest-code")
@role_required("admin")
def suggest_product_code():
    return success_response(data={"sku_code": _next_product_code()})


@bp.get("/products")
@login_required
def list_products():
    page = min(int(request.args.get("page", 1)), 9999)
    per_page = min(int(request.args.get("per_page", 20)), 100)
    q = Product.query.filter_by(is_active=True)
    warehouse_id = request.args.get("warehouse_id", type=int)
    if warehouse_id:
        q = (
            q.join(Inventory, Inventory.product_id == Product.id)
            .filter(Inventory.warehouse_id == warehouse_id)
            .distinct()
        )
    sku = request.args.get("sku_code")
    if sku:
        q = q.filter(Product.sku_code.like(f"%{sku}%"))
    name = request.args.get("name")
    if name:
        q = q.filter(Product.name.like(f"%{name}%"))
    pagination = q.order_by(Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return success_response(data=paginate_response(
        [p.to_dict() for p in pagination.items], page, per_page, pagination.total
    ))


@bp.get("/products/<int:product_id>")
@login_required
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        raise NotFoundError("商品不存在")
    return success_response(data=product.to_dict())


@bp.post("/products")
@role_required("admin")
def create_product():
    data = request.get_json(silent=True) or {}
    sku_code = (data.get("sku_code") or "").strip()
    if not sku_code:
        sku_code = _next_product_code()
    if not data.get("name"):
        raise ValidationError("名称必填")
    if Product.query.filter_by(sku_code=sku_code).first():
        raise ConflictError("编码已存在")
    product = Product(
        sku_code=sku_code,
        name=data["name"],
        spec=data.get("spec", ""),
        unit=data.get("unit", "件"),
        barcode=data.get("barcode"),
        safe_stock=data.get("safe_stock", 0),
    )
    db.session.add(product)
    db.session.commit()
    return success_response(data=product.to_dict(), status=201)


@bp.put("/products/<int:product_id>")
@role_required("admin")
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        raise NotFoundError("商品不存在")
    data = request.get_json(silent=True) or {}
    for field in ("name", "spec", "unit", "barcode", "safe_stock", "is_active"):
        if field in data:
            setattr(product, field, data[field])
    db.session.commit()
    return success_response(data=product.to_dict())


@bp.delete("/products/<int:product_id>")
@role_required("admin")
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product or not product.is_active:
        raise NotFoundError("商品不存在")
    has_stock = Inventory.query.filter_by(product_id=product_id).filter(
        Inventory.quantity > 0
    ).first()
    if has_stock:
        raise ConflictError("商品仍有库存，无法删除")
    product.is_active = False
    db.session.commit()
    return success_response(message="商品已删除")
