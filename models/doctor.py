from db import db
from werkzeug.security import generate_password_hash
from models.appointment import AppointmentModel
from datetime import datetime


class DoctorModel(db.Model):
    __tablename__ = "Doctors"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(128))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    gender = db.Column(db.Integer)
    address = db.Column(db.String(80))
    mobile = db.Column(db.String(80))
    birthdate = db.Column(db.Date)
    created_at = db.Column(db.Date)

    appointments = db.relationship("AppointmentModel")

    def __init__(
        self,
        first_name,
        last_name,
        email,
        mobile,
        gender,
        birthdate,
        username,
        password,
        address,
        created_at,
    ):
        self.username = username
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.gender = gender
        self.mobile = mobile
        self.address = address
        self.birthdate = birthdate
        self.created_at = created_at

    def json(self):
        return {
            "_id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "mobile": self.mobile,
            "gender": "male" if self.gender == 0 else "female",
            "birthdate": str(self.birthdate),
            "age": (datetime.now().date() - self.birthdate).days // 365,
            "username": self.username,
            "address": self.address
            # 'appointments': [appointment.json() for appointment in self.appointments.all()],
        }

    def json_with_appointments(self):
        return {
            "_id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "mobile": self.mobile,
            "gender": "male" if self.gender == 0 else "female",
            "birthdate": str(self.birthdate),
            "age": (datetime.now().date() - self.birthdate).days // 365,
            "username": self.username,
            "appointments": [appointment.json() for appointment in self.appointments],
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_docotor_by_id_with_appointments(cls, doctor_id):
        return (
            cls.query.outerjoin(AppointmentModel, AppointmentModel.doctor_id == cls.id)
            .filter(doctor_id == cls.id)
            .first()
        )
