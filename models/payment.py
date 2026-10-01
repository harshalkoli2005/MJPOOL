from extensions import db
from datetime import datetime


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    payment_id = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    booking_id = db.Column(
        db.String(20),
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        nullable=True
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    payment_status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )

    payment_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )