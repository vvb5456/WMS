from flask import Blueprint, request

from app.extensions import db
from app.models.inventory import Inventory
from app.models.location import Location
from app.models.warehouse import Warehouse
from app.utils.auth import login_required, role_required
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.response import paginate_response, success_response

bp = Blueprint("warehouses", __name__)


@bp.get("/warehouses")
@login_required
def list_warehouses():
    page = min(int(request.args.get("page", 1)), 9999)
    per_page = min(int(request.args.get("per_page", 20)), 100)
    pagination = Warehouse.query.order_by(Warehouse.id).paginate(page=page, per_page=per_page, error_out=False)
    return success_response(data=paginate_response(
        [w.to_dict() for w in pagination.items], page, per_page, pagination.total
    ))


@bp.post("/warehouses")
@role_required("admin")
def create_warehouse():
    data = request.get_json(silent=True) or {}
    if not data.get("code") or not data.get("name"):
        raise ValidationError("编码和名称必填")
    wh = Warehouse(code=data["code"], name=data["name"], address=data.get("address"))
    db.session.add(wh)
    db.session.commit()
    return success_response(data=wh.to_dict(), status=201)


@bp.put("/warehouses/<int:warehouse_id>")
@role_required("admin")
def update_warehouse(warehouse_id):
    wh = Warehouse.query.get(warehouse_id)
    if not wh:
        raise NotFoundError("仓库不存在")
    data = request.get_json(silent=True) or {}
    for field in ("name", "address", "is_active"):
        if field in data:
            setattr(wh, field, data[field])
    db.session.commit()
    return success_response(data=wh.to_dict())


@bp.get("/locations")
@login_required
def list_locations():
    page = min(int(request.args.get("page", 1)), 9999)
    per_page = min(int(request.args.get("per_page", 20)), 100)
    q = Location.query.filter_by(is_active=True)
    wh_id = request.args.get("warehouse_id")
    if wh_id:
        q = q.filter_by(warehouse_id=wh_id)
    pagination = q.order_by(Location.id).paginate(page=page, per_page=per_page, error_out=False)
    return success_response(data=paginate_response(
        [loc.to_dict() for loc in pagination.items], page, per_page, pagination.total
    ))


@bp.post("/locations")
@role_required("admin")
def create_location():
    data = request.get_json(silent=True) or {}
    if not data.get("warehouse_id") or not data.get("code"):
        raise ValidationError("仓库和库位编码必填")
    loc = Location(
        warehouse_id=data["warehouse_id"],
        code=data["code"],
        name=data.get("name"),
    )
    db.session.add(loc)
    db.session.commit()
    return success_response(data=loc.to_dict(), status=201)


@bp.delete("/locations/<int:location_id>")
@role_required("admin")
def delete_location(location_id):
    loc = Location.query.get(location_id)
    if not loc or not loc.is_active:
        raise NotFoundError("库位不存在")
    has_stock = Inventory.query.filter_by(location_id=location_id).filter(
        Inventory.quantity > 0
    ).first()
    if has_stock:
        raise ConflictError("库位仍有库存，无法删除")
    loc.is_active = False
    db.session.commit()
    return success_response(message="库位已删除")
