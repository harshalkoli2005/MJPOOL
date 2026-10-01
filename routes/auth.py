from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user

from models.admin import Admin
from models.customer import Customer
from models.employee import Employee
from models.booking import Booking

from extensions import bcrypt, csrf

auth_bp = Blueprint("auth", __name__)


# ==========================
# Admin Login
# ==========================
@auth_bp.route("/admin/login", methods=["GET", "POST"])
@csrf.exempt
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if admin and bcrypt.check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for("auth.dashboard"))

        return "Invalid Username or Password"

    return render_template("admin/login.html")


# ==========================
# Admin Dashboard
# ==========================
@auth_bp.route("/admin/dashboard")
@login_required
def dashboard():

    total_customers = Customer.query.count()
    total_employees = Employee.query.count()
    total_bookings = Booking.query.count()

    print("Customers:", total_customers)
    print("Employees:", total_employees)
    print("Bookings:", total_bookings)

    pending_jobs = Booking.query.filter_by(status="Pending").count()
    assigned_jobs = Booking.query.filter_by(status="Assigned").count()
    completed_jobs = Booking.query.filter_by(status="Completed").count()
    

    recent_bookings = Booking.query.order_by(
        Booking.id.desc()
    ).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_customers=total_customers,
        total_employees=total_employees,
        total_bookings=total_bookings,
        pending_jobs=pending_jobs,
        assigned_jobs=assigned_jobs,
        completed_jobs=completed_jobs,
        recent_bookings=recent_bookings
    )



# ==========================
# Logout
# ==========================
@auth_bp.route("/admin/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.admin_login"))