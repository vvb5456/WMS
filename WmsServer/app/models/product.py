from datetime import datetime, timezone

from app.extensions import db


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sku_code = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    spec = db.Column(db.String(200), default="")
    unit = db.Column(db.String(16), nullable=False, default="件")
    barcode = db.Column(db.String(64), nullable=True)
    safe_stock = db.Column(db.Numeric(18, 3), nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "sku_code": self.sku_code,
            "name": self.name,
            "spec": self.spec,
            "unit": self.unit,
            "barcode": self.barcode,
            "safe_stock": float(self.safe_stock),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
