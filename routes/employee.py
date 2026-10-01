from flask import Blueprint, render_template, request, redirect, session, flash
from extensions import db, bcrypt, csrf
from models.employee import Employee
from models.booking import Booking

employee_bp = Blueprint("employee", __name__)

# Employee Login
@employee_bp.route("/employee/login", methods=["GET","POST"])
@csrf.exempt
def employee_login():

    if request.method=="POST":

        emp_id = request.form["employee_id"]
        password = request.form["password"]

        employee = Employee.query.filter_by(employee_id=emp_id).first()

        if employee and bcrypt.check_password_hash(employee.password, password):

            session["emp"] = employee.employee_id
            return redirect("/employee/dashboard")

        flash("Invalid Employee ID or Password","danger")

    return render_template("employee/login.html")


# Dashboard
@employee_bp.route("/employee/dashboard")
def employee_dashboard():

    if "emp" not in session:
        return redirect("/employee/login")

    bookings = Booking.query.filter_by(
        assigned_employee=session["emp"]
    ).all()

    return render_template(
        "employee/dashboard.html",
        bookings=bookings,
        emp=session["emp"]
    )


# Complete Job
@employee_bp.route("/employee/complete/<int:id>")
def complete_job(id):

    booking = Booking.query.get_or_404(id)

    booking.status="Completed"

    db.session.commit()

    return redirect("/employee/dashboard")


# Logout
@employee_bp.route("/employee/logout")
def employee_logout():

    session.clear()

    return redirect("/employee/login")