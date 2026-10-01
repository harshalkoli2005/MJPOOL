from extensions import db
from datetime import datetime
from sqlalchemy import event


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.String(20),
        unique=True
    )

    # ==========================
    # Customer Details
    # ==========================
    customer_name = db.Column(
        db.String(100),
        nullable=False
    )

    mobile = db.Column(
        db.String(10),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    address = db.Column(
        db.Text,
        nullable=False
    )

    # ==========================
    # Pool / Service Details
    # ==========================
    pool_size = db.Column(
        db.String(50)
    )

    service = db.Column(
        db.String(100)
    )

    preferred_date = db.Column(
        db.Date
    )

    preferred_time = db.Column(
        db.String(20)
    )

    plan = db.Column(
        db.String(30)
    )

    instruction = db.Column(
        db.Text
    )

    # ==========================
    # Booking Status
    # ==========================
    status = db.Column(
        db.String(20),
        default="Pending"
    )

    assigned_employee = db.Column(
        db.String(20),
        nullable=True
    )

    # ==========================
    # Payment Details
    # ==========================
    total_amount = db.Column(
        db.Float,
        default=0
    )

    advance_amount = db.Column(
        db.Float,
        default=0
    )

    balance_amount = db.Column(
        db.Float,
        default=0
    )

    payment_status = db.Column(
        db.String(20),
        default="Pending"
    )

    payment_id = db.Column(
        db.String(100),
        nullable=True
    )

    payment_date = db.Column(
        db.DateTime,
        nullable=True
    )

    # Razorpay Order ID
    razorpay_order_id = db.Column(
        db.String(100),
        nullable=True
    )

    # ==========================
    # Created Date
    # ==========================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ==========================
# Generate Booking ID
# ==========================
@event.listens_for(Booking, "before_insert")
def generate_booking_id(mapper, connection, target):

    last = connection.execute(
        db.text(
            "SELECT id FROM bookings "
            "ORDER BY id DESC LIMIT 1"
        )
    ).fetchone()

    next_id = 1 if last is None else last[0] + 1

    target.booking_id = (
        f"MJ{datetime.now().year}{next_id:04d}"
    )