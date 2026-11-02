import os
from flask import Flask, render_template, session
from config import Config
from extensions import db, bcrypt, login_manager, csrf

# मॉडेल इंपोर्ट्स
from models.admin import Admin
from models.customer import Customer
from models.employee import Employee
from models.service import Service
from models.booking import Booking
from models.payment import Payment
from models.contact import Contact

# Flask Application
app = Flask(__name__)
app.config.from_object(Config)

# एक्स्टेन्शन्स सुरू करणे
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)

login_manager.login_view = "auth.admin_login"

# अपलोड फोल्डर आपोआप तयार करणे (नसल्यास एरर येणार नाही)


# Admin, Customer, Employee तिघांसाठी काम करणारा user loader
@login_manager.user_loader
def load_user(user_id):
    role = session.get('_user_role')
    user_id = int(user_id)
    
    if role == 'employee':
        return db.session.get(Employee, user_id)
    elif role == 'customer':
        return db.session.get(Customer, user_id)
    return db.session.get(Admin, user_id)

# BluePrint Conncected
from routes.auth import auth_bp
from routes.customer import customer_bp
from routes.employee import employee_bp
from routes.admin import admin_bp

app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(employee_bp)

# Home Page
@app.route("/")
def home():
    return render_template("index.html")



# Run to Application
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False)