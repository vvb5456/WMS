from datetime import datetime, timezone

from app.extensions import db


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey("product.id"), nullable=False)
    warehouse_id = db.Column(db.BigInteger, db.ForeignKey("warehouse.id"), nullable=False)
    location_id = db.Column(db.BigInteger, db.ForeignKey("location.id"), nullable=False)
    quantity = db.Column(db.Numeric(18, 3), nullable=False, default=0)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint("product_id", "warehouse_id", "location_id"),)

    product = db.relationship("Product")
    warehouse = db.relationship("Warehouse")
    location = db.relationship("Location")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "warehouse_id": self.warehouse_id,
            "location_id": self.location_id,
            "quantity": float(self.quantity),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "product": self.product.to_dict() if self.product else None,
            "warehouse": self.warehouse.to_dict() if self.warehouse else None,
            "location": self.location.to_dict() if self.location else None,
        }
