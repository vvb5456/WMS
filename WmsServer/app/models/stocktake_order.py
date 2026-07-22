from datetime import datetime, timezone

from app.extensions import db


class StocktakeOrder(db.Model):
    __tablename__ = "stocktake_order"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    warehouse_id = db.Column(db.BigInteger, db.ForeignKey("warehouse.id"), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="draft")
    remark = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    approved_by = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    warehouse = db.relationship("Warehouse")
    creator = db.relationship("User", foreign_keys=[created_by])
    approver = db.relationship("User", foreign_keys=[approved_by])
    lines = db.relationship("StocktakeOrderLine", backref="order", cascade="all, delete-orphan")

    def to_dict(self, with_lines=True):
        data = {
            "id": self.id,
            "order_no": self.order_no,
            "warehouse_id": self.warehouse_id,
            "status": self.status,
            "remark": self.remark,
            "created_by": self.created_by,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "warehouse": self.warehouse.to_dict() if self.warehouse else None,
        }
        if with_lines:
            data["lines"] = [line.to_dict() for line in self.lines]
        return data


class StocktakeOrderLine(db.Model):
    __tablename__ = "stocktake_order_line"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    stocktake_order_id = db.Column(db.BigInteger, db.ForeignKey("stocktake_order.id"), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey("product.id"), nullable=False)
    location_id = db.Column(db.BigInteger, db.ForeignKey("location.id"), nullable=False)
    book_qty = db.Column(db.Numeric(18, 3), nullable=False, default=0)
    counted_qty = db.Column(db.Numeric(18, 3), nullable=False, default=0)
    diff_qty = db.Column(db.Numeric(18, 3), nullable=False, default=0)

    product = db.relationship("Product")
    location = db.relationship("Location")

    def to_dict(self):
        return {
            "id": self.id,
            "stocktake_order_id": self.stocktake_order_id,
            "product_id": self.product_id,
            "location_id": self.location_id,
            "book_qty": float(self.book_qty),
            "counted_qty": float(self.counted_qty),
            "diff_qty": float(self.diff_qty),
            "product": self.product.to_dict() if self.product else None,
            "location": self.location.to_dict() if self.location else None,
        }
