from datetime import datetime, timezone

from app.extensions import db


class InventoryTransaction(db.Model):
    __tablename__ = "inventory_transaction"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey("product.id"), nullable=False)
    warehouse_id = db.Column(db.BigInteger, db.ForeignKey("warehouse.id"), nullable=False)
    location_id = db.Column(db.BigInteger, db.ForeignKey("location.id"), nullable=False)
    delta_qty = db.Column(db.Numeric(18, 3), nullable=False)
    balance_after = db.Column(db.Numeric(18, 3), nullable=False)
    ref_type = db.Column(db.String(32), nullable=False)
    ref_id = db.Column(db.BigInteger, nullable=False)
    operator_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    remark = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product")
    warehouse = db.relationship("Warehouse")
    location = db.relationship("Location")
    operator = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "warehouse_id": self.warehouse_id,
            "location_id": self.location_id,
            "delta_qty": float(self.delta_qty),
            "balance_after": float(self.balance_after),
            "ref_type": self.ref_type,
            "ref_id": self.ref_id,
            "operator_id": self.operator_id,
            "remark": self.remark,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "product": self.product.to_dict() if self.product else None,
            "warehouse": self.warehouse.to_dict() if self.warehouse else None,
            "location": self.location.to_dict() if self.location else None,
            "operator": self.operator.to_dict() if self.operator else None,
        }
