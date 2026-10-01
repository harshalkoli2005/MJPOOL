from app import app
from extensions import db, bcrypt
from models.customer import Customer

with app.app_context():

    customer = Customer(
        full_name="John Smith",
        mobile="9998887776",
        whatsapp="9998887776",
        email="john@gmail.com",
        address="Mumbai",
        pool_type="Residential",
        password=bcrypt.generate_password_hash(
            "123456"
        ).decode("utf-8")
    )

    db.session.add(customer)
    db.session.commit()

    print("Customer Registered Successfully!")