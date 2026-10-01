from extensions import db

class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    mobile = db.Column(db.String(15))
    subject = db.Column(db.String(150))
    message = db.Column(db.Text)