from extensions import db


class BookingService(db.Model):
    __tablename__ = "booking_services"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(
        db.String(20),
        nullable=False
    )

    service_id = db.Column(
        db.Integer,
        nullable=False
    )

    pool_size = db.Column(
        db.String(50),
        nullable=False
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )