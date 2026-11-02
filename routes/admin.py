from flask import Blueprint, render_template, redirect, request, flash
from flask_login import login_required
from extensions import db, bcrypt, csrf

from models.booking import Booking
from models.customer import Customer
from models.employee import Employee
from models.service import Service
from models.service_price import ServicePrice
from models.contact import Contact
from datetime import datetime
from models.booking_service import BookingService
from models.payment import Payment

from sqlalchemy.exc import IntegrityError

admin_bp = Blueprint("admin", __name__)

# =========================
# BOOKINGS
# =========================
@admin_bp.route("/bookings")
@login_required
def all_bookings():
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    return render_template("admin/bookings.html", bookings=bookings)


@admin_bp.route("/status/<int:id>/<string:status>")
@login_required
def update_status(id, status):
    booking = Booking.query.get_or_404(id)
    booking.status = status
    db.session.commit()
    return redirect("/admin/bookings")


@admin_bp.route("/booking/delete/<int:id>", methods=["POST"])
@login_required
@csrf.exempt
def delete_booking(id):

    booking = Booking.query.get_or_404(id)

    # Related booking services delete
    BookingService.query.filter_by(
        booking_id=booking.booking_id
    ).delete()

    # Related payments delete
    Payment.query.filter_by(
        booking_id=booking.booking_id
    ).delete()

    # Delete booking
    db.session.delete(booking)

    db.session.commit()

    flash(
        "Booking Deleted Successfully",
        "success"
    )

    return redirect("/admin/bookings")


# =========================
# CUSTOMERS
# =========================
@admin_bp.route("/customers")
@login_required
def all_customers():

    search = request.args.get("search", "")

    if search:
        customers = Customer.query.filter(
            (Customer.full_name.ilike(f"%{search}%")) |
            (Customer.mobile.ilike(f"%{search}%"))
        ).all()
    else:
        customers = Customer.query.order_by(Customer.id.desc()).all()

    return render_template(
        "admin/customers.html",
        customers=customers,
        search=search
    )


@admin_bp.route("/customers/delete/<int:id>")
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return redirect("/admin/customers")


# =========================
# EMPLOYEES
# =========================
# =========================
# EMPLOYEES
# =========================

@admin_bp.route("/employees")
@login_required
def all_employees():

    employees = Employee.query.order_by(
        Employee.id.desc()
    ).all()

    return render_template(
        "admin/employees.html",
        employees=employees
    )


@admin_bp.route("/employees/add", methods=["GET", "POST"])
@login_required
@csrf.exempt
def add_employee():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip().lower()
        address = request.form.get("address", "").strip()
        role = request.form.get("role", "").strip()
        password = request.form.get("password", "")

        # Required fields
        if not all([name, mobile, email, address, role, password]):
            flash("All fields are required", "danger")
            return render_template("admin/add_employee.html")

        # Mobile validation
        if not mobile.isdigit() or len(mobile) != 10:
            flash("Enter a valid 10-digit mobile number", "danger")
            return render_template("admin/add_employee.html")

        # Duplicate mobile
        if Employee.query.filter_by(mobile=mobile).first():
            flash("This mobile number is already registered", "danger")
            return render_template("admin/add_employee.html")

        # Duplicate email
        if Employee.query.filter_by(email=email).first():
            flash("This email is already registered", "danger")
            return render_template("admin/add_employee.html")

        try:
            hashed_password = bcrypt.generate_password_hash(
                password
            ).decode("utf-8")

            emp = Employee(
                name=name,
                mobile=mobile,
                email=email,
                address=address,
                role=role,
                password=hashed_password,
                status="Active"
            )

            db.session.add(emp)
            db.session.commit()

            flash(
                f"Employee Added Successfully - {emp.employee_id}",
                "success"
            )
            return redirect("/admin/employees")

        except IntegrityError:
            db.session.rollback()
            flash(
                "Employee could not be added. Mobile or Email already exists.",
                "danger"
            )
            return render_template("admin/add_employee.html")

    return render_template("admin/add_employee.html")


# =========================
# ASSIGN EMPLOYEE
# =========================
@admin_bp.route("/assign/<int:id>", methods=["GET", "POST"])
@login_required
@csrf.exempt
def assign_employee(id):

    booking = Booking.query.get_or_404(id)

    # Completed / Cancelled booking पुन्हा assign करू नये
    if booking.status in ["Completed", "Cancelled"]:
        flash(
            "Completed or Cancelled booking cannot be assigned.",
            "warning"
        )
        return redirect("/admin/bookings")

    # फक्त Active employees दाखवायचे
    employees = Employee.query.filter_by(
        status="Active"
    ).order_by(
        Employee.id.desc()
    ).all()

    if request.method == "POST":

        employee_id = request.form.get("employee", "").strip()

        if not employee_id:
            flash("Please select an employee.", "danger")
            return render_template(
                "admin/assign_employee.html",
                booking=booking,
                employees=employees
            )

        # Selected employee database मध्ये आहे का + Active आहे का
        employee = Employee.query.filter_by(
            employee_id=employee_id,
            status="Active"
        ).first()

        if not employee:
            flash(
                "Selected employee is not available.",
                "danger"
            )
            return render_template(
                "admin/assign_employee.html",
                booking=booking,
                employees=employees
            )

        # Assignment
        booking.assigned_employee = employee.employee_id
        booking.status = "Assigned"

        db.session.commit()

        flash(
            f"Booking assigned to {employee.employee_id} successfully.",
            "success"
        )

        return redirect("/admin/bookings")

    return render_template(
        "admin/assign_employee.html",
        booking=booking,
        employees=employees
    )

# =========================
# SERVICES
# =========================

@admin_bp.route("/services")
@login_required
def all_services():

    services = Service.query.order_by(
        Service.id.desc()
    ).all()

    service_prices = {}

    for service in services:

        prices = ServicePrice.query.filter_by(
            service_id=service.id
        ).all()

        service_prices[service.id] = {}

        for price in prices:
            service_prices[service.id][
                price.pool_size
            ] = price.price

    return render_template(
        "admin/services.html",
        services=services,
        service_prices=service_prices
    )


@admin_bp.route(
    "/services/add",
    methods=["GET", "POST"]
)
@login_required
@csrf.exempt
def add_service():

    if request.method == "POST":

        service = Service(
    service_name=request.form["service_name"],
    price=0,
    duration=request.form["duration"],
    description=request.form["description"]
)
        db.session.add(service)

        # First save service so we get service.id
        db.session.flush()

        # Pool-size-wise prices
        small_price = request.form.get(
            "small_price", 0
        )

        medium_price = request.form.get(
            "medium_price", 0
        )

        large_price = request.form.get(
            "large_price", 0
        )

        db.session.add(
            ServicePrice(
                service_id=service.id,
                pool_size="Small",
                price=small_price
            )
        )

        db.session.add(
            ServicePrice(
                service_id=service.id,
                pool_size="Medium",
                price=medium_price
            )
        )

        db.session.add(
            ServicePrice(
                service_id=service.id,
                pool_size="Large",
                price=large_price
            )
        )

        db.session.commit()

        flash(
            "Service Added Successfully",
            "success"
        )

        return redirect("/admin/services")

    return render_template(
        "admin/add_service.html"
    )


@admin_bp.route(
    "/services/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
@csrf.exempt
def edit_service(id):

    service = Service.query.get_or_404(id)

    if request.method == "POST":

        service.service_name = request.form[
            "service_name"
        ]

        service.price = request.form.get(
            "price", 0
        )

        service.duration = request.form[
            "duration"
        ]

        service.description = request.form[
            "description"
        ]

        service.status = request.form[
            "status"
        ]

        # -------------------------
        # Update Pool Prices
        # -------------------------

        pool_prices = {
            "Small": request.form.get(
                "small_price", 0
            ),
            "Medium": request.form.get(
                "medium_price", 0
            ),
            "Large": request.form.get(
                "large_price", 0
            )
        }

        for pool_size, price in pool_prices.items():

            service_price = ServicePrice.query.filter_by(
                service_id=service.id,
                pool_size=pool_size
            ).first()

            if service_price:

                service_price.price = price

            else:

                service_price = ServicePrice(
                    service_id=service.id,
                    pool_size=pool_size,
                    price=price
                )

                db.session.add(service_price)

        db.session.commit()

        flash(
            "Service Updated Successfully",
            "success"
        )

        return redirect("/admin/services")

    # Existing prices
    prices = ServicePrice.query.filter_by(
        service_id=service.id
    ).all()

    service_prices = {}

    for price in prices:
        service_prices[price.pool_size] = price.price

    return render_template(
        "admin/edit_service.html",
        service=service,
        service_prices=service_prices
    )


@admin_bp.route(
    "/services/delete/<int:id>"
)
@login_required
def delete_service(id):

    service = Service.query.get_or_404(id)

    # Delete pool-size prices first
    ServicePrice.query.filter_by(
        service_id=service.id
    ).delete()

    db.session.delete(service)

    db.session.commit()

    flash(
        "Service Deleted Successfully",
        "success"
    )

    return redirect("/admin/services")

#----- Concact-----#

@admin_bp.route("/messages")
@login_required
def messages():

    messages = Contact.query.order_by(Contact.id.desc()).all()

    return render_template(
        "admin/messages.html",
        messages=messages
    )


#-----reports------#



from sqlalchemy import func

@admin_bp.route("/reports", methods=["GET", "POST"])
@login_required
@csrf.exempt
def reports():

    bookings = []
    report_date = None

    total = 0
    pending = 0
    completed = 0

    # Employee Performance Report
    employee_report = db.session.query(
        Booking.assigned_employee.label("assigned_employee"),
        func.count(Booking.id).label("total"),
        func.sum(Booking.status == "Completed").label("completed"),
        func.sum(Booking.status == "Pending").label("pending")
    ).filter(
        Booking.assigned_employee != None
    ).group_by(
        Booking.assigned_employee
    ).all()

    # Date Wise Report
    if request.method == "POST":

        report_date = datetime.strptime(
            request.form["date"], "%Y-%m-%d"
        ).date()

        bookings = Booking.query.filter_by(
            preferred_date=report_date
        ).all()

        total = len(bookings)
        pending = len([b for b in bookings if b.status == "Pending"])
        completed = len([b for b in bookings if b.status == "Completed"])

    return render_template(
        "admin/reports.html",
        bookings=bookings,
        report_date=report_date,
        total=total,
        pending=pending,
        completed=completed,
        employee_report=employee_report
    )