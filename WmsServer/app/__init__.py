import os

from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate
from app.utils.exceptions import WmsError
from app.utils.response import error_response


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.routes import auth, dashboard, products, warehouses, inventory, users
    from app.routes import inbound_orders, outbound_orders, stocktake_orders, health

    api_prefix = "/api/v1"
    app.register_blueprint(health.bp, url_prefix=api_prefix)
    app.register_blueprint(auth.bp, url_prefix=api_prefix)
    app.register_blueprint(products.bp, url_prefix=api_prefix)
    app.register_blueprint(warehouses.bp, url_prefix=api_prefix)
    app.register_blueprint(inventory.bp, url_prefix=api_prefix)
    app.register_blueprint(inbound_orders.bp, url_prefix=api_prefix)
    app.register_blueprint(outbound_orders.bp, url_prefix=api_prefix)
    app.register_blueprint(stocktake_orders.bp, url_prefix=api_prefix)
    app.register_blueprint(users.bp, url_prefix=api_prefix)
    app.register_blueprint(dashboard.bp, url_prefix=api_prefix)

    @app.errorhandler(WmsError)
    def handle_wms_error(e):
        return error_response(e.message, code=e.code, status=e.status, errors=e.errors)

    from werkzeug.exceptions import HTTPException

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return error_response(e.description, code="HTTP_ERROR", status=e.code)

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        if app.debug:
            raise e
        if os.getenv("FLASK_ENV") == "development":
            return error_response(str(e), code="INTERNAL_ERROR", status=500)
        return error_response("服务器内部错误", code="INTERNAL_ERROR", status=500)

    return app


def seed_data():
    """初始化种子数据（用户密码 admin123）。"""
    from app.models.user import User
    from app.models.product import Product
    from app.models.warehouse import Warehouse
    from app.models.location import Location

    users = [
        ("admin", "系统管理员", "admin"),
        ("keeper", "仓管员", "warehouse_keeper"),
        ("viewer", "查看员", "viewer"),
    ]
    for username, name, role in users:
        u = User.query.filter_by(username=username).first()
        if not u:
            u = User(username=username, name=name, role=role)
            db.session.add(u)
        u.name = name
        u.role = role
        u.is_active = True
        u.set_password("admin123")

    if not Warehouse.query.filter_by(code="WH01").first():
        wh = Warehouse(code="WH01", name="发电部仓库", address="上海市浦东新区示例路100号")
        db.session.add(wh)
        db.session.flush()
        for code, lname in [("A-01-01", "A区1排1位"), ("A-01-02", "A区1排2位"), ("B-01-01", "B区1排1位")]:
            db.session.add(Location(warehouse_id=wh.id, code=code, name=lname))

    products = [
        ("SKU-P001", "螺丝 M6×20", "不锈钢", "件", 100),
        ("SKU-P002", "包装箱 中号", "40×30×20cm", "个", 50),
    ]
    for sku, name, spec, unit, safe in products:
        if not Product.query.filter_by(sku_code=sku).first():
            db.session.add(Product(sku_code=sku, name=name, spec=spec, unit=unit, safe_stock=safe))

    db.session.commit()
