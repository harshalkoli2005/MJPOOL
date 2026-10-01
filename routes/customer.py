from flask import Blueprint, render_template, request, redirect, flash

from extensions import db, csrf

from models.booking import Booking
from models.booking_service import BookingService
from models.customer import Customer
from models.service import Service
from models.service_price import ServicePrice
from models.contact import Contact
from models.payment import Payment

from datetime import datetime
import re


customer_bp = Blueprint("customer", __name__)


# =========================================================
# BOOKING
# =========================================================

@customer_bp.route("/booking", methods=["GET", "POST"])
@csrf.exempt
def booking_page():

    # =====================================================
    # ACTIVE SERVICES
    # =====================================================

    services = Service.query.filter_by(
        status="Active"
    ).all()

    # =====================================================
    # SERVICE PRICES
    # =====================================================

    service_prices = {}

    for service in services:

        prices = ServicePrice.query.filter_by(
            service_id=service.id
        ).all()

        service_prices[str(service.id)] = {}

        for p in prices:

            service_prices[str(service.id)][
                p.pool_size
            ] = float(p.price)

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        # -------------------------
        # GET FORM DATA
        # -------------------------

        name = request.form.get(
            "name",
            ""
        ).strip()

        mobile = request.form.get(
            "mobile",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        pool_size = request.form.get(
            "pool_size",
            ""
        ).strip()

        service_ids = request.form.getlist(
            "service_ids"
        )

        plan = request.form.get(
            "plan",
            ""
        ).strip()

        instruction = request.form.get(
            "instruction",
            ""
        ).strip()

        date = request.form.get(
            "date",
            ""
        ).strip()

        time = request.form.get(
            "time",
            ""
        ).strip()

        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not name:

            flash(
                "Please enter your name",
                "danger"
            )

            return redirect("/booking")

        if not re.fullmatch(
            r"[6-9]\d{9}",
            mobile
        ):

            flash(
                "Enter valid 10 digit mobile number",
                "danger"
            )

            return redirect("/booking")

        if not re.fullmatch(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            email
        ):

            flash(
                "Invalid email address",
                "danger"
            )

            return redirect("/booking")

        if not address:

            flash(
                "Please enter your address",
                "danger"
            )

            return redirect("/booking")

        if pool_size not in [
            "Small",
            "Medium",
            "Large"
        ]:

            flash(
                "Please select pool size",
                "danger"
            )

            return redirect("/booking")

        if not service_ids:

            flash(
                "Please select at least one service",
                "danger"
            )

            return redirect("/booking")

        if not date:

            flash(
                "Please select preferred date",
                "danger"
            )

            return redirect("/booking")

        if not time:

            flash(
                "Please select preferred time",
                "danger"
            )

            return redirect("/booking")

        # =================================================
        # DATE VALIDATION
        # =================================================

        try:

            booking_date = datetime.strptime(
                date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Invalid booking date",
                "danger"
            )

            return redirect("/booking")

        if booking_date <= datetime.today().date():

            flash(
                "Please select a future date",
                "danger"
            )

            return redirect("/booking")

        # =================================================
        # DUPLICATE BOOKING
        # =================================================

        duplicate = Booking.query.filter_by(
            mobile=mobile,
            preferred_date=booking_date
        ).first()

        if duplicate:

            flash(
                "Booking already exists for this mobile & date",
                "danger"
            )

            return redirect("/booking")

        # =================================================
        # SERVER-SIDE PRICE CHECK
        # =================================================

        selected_services = []

        total_amount = 0

        for service_id in service_ids:

            try:

                service_id = int(service_id)

            except ValueError:

                flash(
                    "Invalid service selected",
                    "danger"
                )

                return redirect("/booking")

            # -------------------------
            # SERVICE CHECK
            # -------------------------

            service = Service.query.filter_by(
                id=service_id,
                status="Active"
            ).first()

            if not service:

                flash(
                    "Invalid service selected",
                    "danger"
                )

                return redirect("/booking")

            # -------------------------
            # PRICE CHECK
            # -------------------------

            service_price = ServicePrice.query.filter_by(
                service_id=service.id,
                pool_size=pool_size
            ).first()

            if not service_price:

                flash(
                    f"Price not available for "
                    f"{service.service_name} - "
                    f"{pool_size} pool",
                    "danger"
                )

                return redirect("/booking")

            price = float(
                service_price.price
            )

            selected_services.append({
                "service": service,
                "price": price
            })

            total_amount += price

        # =================================================
        # PAYMENT CALCULATION
        # =================================================

        advance_amount = round(
            total_amount * 0.30,
            2
        )

        balance_amount = round(
            total_amount - advance_amount,
            2
        )

        # =================================================
        # CUSTOMER
        # =================================================

        customer = Customer.query.filter_by(
            mobile=mobile
        ).first()

        if not customer:

            customer = Customer(
                full_name=name,
                mobile=mobile,
                whatsapp=mobile,
                email=email,
                address=address,
                pool_type=pool_size,
                password=""
            )

            db.session.add(customer)

            db.session.flush()

        else:

            # Update latest customer details

            customer.full_name = name
            customer.email = email
            customer.whatsapp = mobile
            customer.address = address
            customer.pool_type = pool_size

        # =================================================
        # CREATE BOOKING
        # =================================================

        booking = Booking(

            customer_name=name,

            mobile=mobile,

            email=email,

            address=address,

            pool_size=pool_size,

            service=", ".join(
                item["service"].service_name
                for item in selected_services
            ),

            preferred_date=booking_date,

            preferred_time=time,

            plan=plan,

            instruction=instruction,

            total_amount=total_amount,

            advance_amount=advance_amount,

            balance_amount=balance_amount,

            payment_status="Pending",

            status="Pending Payment"
        )

        db.session.add(booking)

        # Generate booking ID

        db.session.flush()

        # =================================================
        # SAVE SELECTED SERVICES
        # =================================================

        for item in selected_services:

            booking_service = BookingService(

                booking_id=booking.booking_id,

                service_id=item["service"].id,

                pool_size=pool_size,

                price=item["price"]
            )

            db.session.add(
                booking_service
            )

        # =================================================
        # SAVE BOOKING
        # =================================================

        try:

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            print(
                "BOOKING SAVE ERROR:",
                e
            )

            flash(
                "Unable to save booking. Please try again.",
                "danger"
            )

            return redirect("/booking")

        # =================================================
        # OPEN DEMO PAYMENT PAGE
        # =================================================

        return render_template(
            "payment.html",
            booking=booking,
            amount=int(
                round(
                    advance_amount * 100
                )
            )
        )

    # =====================================================
    # BOOKING PAGE
    # =====================================================

    return render_template(
        "booking.html",
        services=services,
        service_prices=service_prices
    )


# =========================================================
# DEMO PAYMENT SUCCESS
# =========================================================

@customer_bp.route(
    "/payment/demo-success",
    methods=["POST"]
)
@csrf.exempt
def demo_payment_success():

    booking_id = request.form.get(
        "booking_id",
        ""
    ).strip()

    # =====================================================
    # FIND BOOKING
    # =====================================================

    booking = Booking.query.filter_by(
        booking_id=booking_id
    ).first()

    if not booking:

        flash(
            "Booking not found.",
            "danger"
        )

        return redirect("/booking")

    # =====================================================
    # ALREADY PAID
    # =====================================================

    if booking.payment_status == "Paid":

        return redirect(
            f"/receipt/{booking.booking_id}"
        )

    # =====================================================
    # DEMO PAYMENT ID
    # =====================================================

    demo_payment_id = (
        f"DEMO_{booking.booking_id}_"
        f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    try:

        # =================================================
        # UPDATE BOOKING PAYMENT
        # =================================================

        booking.payment_status = "Paid"

        booking.payment_id = demo_payment_id

        booking.payment_date = datetime.utcnow()

        # Paid booking becomes Pending Job

        booking.status = "Pending"

        # =================================================
        # CUSTOMER ID
        # =================================================

        customer = Customer.query.filter_by(
            mobile=booking.mobile
        ).first()

        customer_id = None

        if customer:

            customer_id = customer.id

        # =================================================
        # SAVE PAYMENT
        # =================================================

        existing_payment = Payment.query.filter_by(
            payment_id=demo_payment_id
        ).first()

        if not existing_payment:

            payment = Payment(

                payment_id=demo_payment_id,

                booking_id=booking.booking_id,

                customer_id=customer_id,

                amount=booking.advance_amount,

                payment_status="Paid",

                payment_date=datetime.utcnow()
            )

            db.session.add(payment)

        # =================================================
        # COMMIT PAYMENT
        # =================================================

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        print(
            "DEMO PAYMENT ERROR:",
            e
        )

        flash(
            "Unable to complete demo payment.",
            "danger"
        )

        return redirect(
            f"/receipt/{booking.booking_id}"
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    flash(
        "Demo payment successful! Booking confirmed.",
        "booking_success"
    )

    return redirect(
        f"/receipt/{booking.booking_id}"
    )


# =========================================================
# RECEIPT
# =========================================================

@customer_bp.route(
    "/receipt/<booking_id>"
)
def receipt(booking_id):

    booking = Booking.query.filter_by(
        booking_id=booking_id
    ).first_or_404()

    return render_template(
        "receipt.html",
        booking=booking
    )


# =========================================================
# TRACK BOOKING
# =========================================================

@customer_bp.route(
    "/track",
    methods=["GET", "POST"]
)
@csrf.exempt
def track_booking():

    if request.method == "POST":

        booking_id = request.form.get(
            "booking_id",
            ""
        ).strip().upper()

        booking = Booking.query.filter_by(
            booking_id=booking_id
        ).first()

        if booking:

            return render_template(
                "track_result.html",
                booking=booking
            )

        flash(
            "Booking ID Not Found",
            "danger"
        )

        return redirect("/track")

    return render_template(
        "track_booking.html"
    )


# =========================================================
# CONTACT
# =========================================================

@customer_bp.route(
    "/contact",
    methods=["GET", "POST"]
)
@csrf.exempt
def contact():

    if request.method == "POST":

        msg = Contact(

            name=request.form.get(
                "name",
                ""
            ),

            email=request.form.get(
                "email",
                ""
            ),

            mobile=request.form.get(
                "mobile",
                ""
            ),

            subject=request.form.get(
                "subject",
                ""
            ),

            message=request.form.get(
                "message",
                ""
            )
        )

        db.session.add(msg)

        db.session.commit()

        flash(
            "Message Sent Successfully!",
            "contact_success"
        )

        return redirect("/contact")

    return render_template(
        "contact.html"
    )