from app.extensions import db


class OrderNoSeq(db.Model):
    __tablename__ = "order_no_seq"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    prefix = db.Column(db.String(8), nullable=False)
    seq_date = db.Column(db.Date, nullable=False)
    last_seq = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (db.UniqueConstraint("prefix", "seq_date"),)
