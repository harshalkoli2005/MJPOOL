from flask_login import UserMixin
from sqlalchemy import event
from extensions import db

class Employee(UserMixin, db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)

    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)

    role = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    status = db.Column(db.String(20), default="Active")


@event.listens_for(Employee, "before_insert")
def generate_employee_id(mapper, connection, target):
    last = connection.execute(
        db.text("SELECT id FROM employees ORDER BY id DESC LIMIT 1")
    ).fetchone()

    next_id = 1 if last is None else last[0] + 1
    target.employee_id = f"EMP-{next_id:04d}"