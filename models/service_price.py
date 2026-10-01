from extensions import db


class ServicePrice(db.Model):
    __tablename__ = "service_prices"

    id = db.Column(
        db.Integer,
        primary_key=True
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