from extensions import db
from flask_login import UserMixin
from datetime import datetime

class Customer(UserMixin, db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    whatsapp = db.Column(db.String(10))
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    pool_type = db.Column(db.String(50))
    password = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.String(255), default="default.png")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)