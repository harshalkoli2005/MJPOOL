import os

class Config:
    SECRET_KEY = "smart_pool_secret_2026"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root123@localhost/pool_service_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join("static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024


    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")