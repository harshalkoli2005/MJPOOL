from flask import Blueprint, render_template, request, redirect, session, flash
from extensions import db, bcrypt, csrf
from models.employee import Employee
from models.booking import Booking

employee_bp = Blueprint("employee", __name__)


# =========================
# Employee Login
# =========================
@employee_bp.route("/employee/login", methods=["GET", "POST"])
@csrf.exempt
def employee_login():

    if request.method == "POST":

        emp_id = request.form.get("employee_id", "").strip()
        password = request.form.get("password", "")

        if not emp_id or not password:
            flash("Employee ID and Password are required", "danger")
            return render_template("employee/login.html")

        employee = Employee.query.filter_by(
            employee_id=emp_id
        ).first()

        if employee and bcrypt.check_password_hash(
            employee.password,
            password
        ):

            session.clear()
            session["emp"] = employee.employee_id

            return redirect("/employee/dashboard")

        flash("Invalid Employee ID or Password", "danger")

    return render_template("employee/login.html")


# =========================
# Employee Dashboard
# =========================
@employee_bp.route("/employee/dashboard")
def employee_dashboard():

    if "emp" not in session:
        flash("Please login first", "warning")
        return redirect("/employee/login")

    bookings = Booking.query.filter_by(
        assigned_employee=session["emp"]
    ).order_by(
        Booking.id.desc()
    ).all()

    return render_template(
        "employee/dashboard.html",
        bookings=bookings,
        emp=session["emp"]
    )


# =========================
# Complete Assigned Job
# =========================
@employee_bp.route("/employee/complete/<int:id>", methods=["POST"])
@csrf.exempt
def complete_job(id):

    # Employee login check
    if "emp" not in session:
        flash("Please login first", "warning")
        return redirect("/employee/login")

    booking = Booking.query.get_or_404(id)

    # Ownership check
    if booking.assigned_employee != session["emp"]:
        flash("You are not authorized to complete this booking", "danger")
        return redirect("/employee/dashboard")

    # Only assigned jobs can be completed
    if booking.status != "Assigned":
        flash("Only assigned bookings can be completed", "warning")
        return redirect("/employee/dashboard")

    booking.status = "Completed"

    db.session.commit()

    flash("Job completed successfully", "success")

    return redirect("/employee/dashboard")


# =========================
# Employee Logout
# =========================
@employee_bp.route("/employee/logout")
def employee_logout():

    session.clear()

    return redirect("/employee/login")