from db import db
from datetime import datetime


class ContactUsModel(db.Model):
    __tablename__ = "Contact_Us"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    mobile = db.Column(db.String(80))
    created_at = db.Column(db.DateTime)
    text = db.Column(db.String(5000))

    def __init__(
        self, first_name: str, last_name: str, text: str, email: str, mobile: str
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.mobile = mobile
        self.created_at = datetime.now()
        self.text = text

    def json(self):
        return {
            "_id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "mobile": self.mobile,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
            "text": self.text,
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id: int):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()
