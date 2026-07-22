from datetime import datetime, timezone

from app.extensions import db


class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    warehouse_id = db.Column(db.BigInteger, db.ForeignKey("warehouse.id"), nullable=False)
    code = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint("warehouse_id", "code"),)

    def to_dict(self):
        return {
            "id": self.id,
            "warehouse_id": self.warehouse_id,
            "code": self.code,
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
