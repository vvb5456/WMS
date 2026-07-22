from datetime import date

from app.extensions import db
from app.models.order_no_seq import OrderNoSeq


def generate_order_no(prefix: str) -> str:
    today = date.today()
    seq_row = (
        OrderNoSeq.query.filter_by(prefix=prefix, seq_date=today)
        .with_for_update()
        .first()
    )
    if not seq_row:
        seq_row = OrderNoSeq(prefix=prefix, seq_date=today, last_seq=0)
        db.session.add(seq_row)
        db.session.flush()
    seq_row.last_seq += 1
    db.session.flush()
    return f"{prefix}{today.strftime('%Y%m%d')}{seq_row.last_seq:04d}"
