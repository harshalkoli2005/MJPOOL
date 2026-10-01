from app import app
from extensions import db, bcrypt
from models.admin import Admin

with app.app_context():
    admin = Admin.query.filter_by(username="admin").first()

    if not admin:
        password = bcrypt.generate_password_hash("admin123").decode("utf-8")

        new_admin = Admin(
            username="admin",
            email="admin@pool.com",
            password=password
        )

        db.session.add(new_admin)
        db.session.commit()
        print("Admin Created Successfully!")
    else:
        print("Admin Already Exists!")