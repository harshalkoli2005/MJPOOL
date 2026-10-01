from flask import Flask, render_template
from config import Config
from extensions import db, bcrypt, login_manager, csrf

# Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)

# Login Page
login_manager.login_view = "auth.admin_login"

# ==========================
# Import Models
# ==========================
from models.admin import Admin
from models.customer import Customer
from models.employee import Employee
from models.service import Service
from models.booking import Booking
from models.payment import Payment
from models.contact import Contact

# ==========================
# User Loader
# ==========================
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# ==========================
# Register Blueprints
# ==========================
from routes.auth import auth_bp
from routes.customer import customer_bp
from routes.employee import employee_bp
from routes.admin import admin_bp



app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(employee_bp)


# ==========================
# Public Home Page
# ==========================
@app.route("/")
def home():
    return render_template("index.html")

# ==========================
# Run App
# ==========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False)