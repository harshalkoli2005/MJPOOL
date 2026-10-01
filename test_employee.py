from app import app
from extensions import db, bcrypt
from models.employee import Employee

with app.app_context():

    emp = Employee(
        name="Rahul Patil",
        mobile="9876543210",
        email="rahul@gmail.com",
        address="Pune",
        role="Technician",
        password=bcrypt.generate_password_hash("123456").decode("utf-8")
    )

    db.session.add(emp)
    db.session.commit()

    print("Employee Added Successfully!")
    print("Employee ID:", emp.employee_id)