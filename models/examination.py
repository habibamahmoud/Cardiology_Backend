from db import db
from sqlalchemy import select
from models.doctor import DoctorModel as Doctor
import models.patient as Patient
from models.appointment import AppointmentModel as Appointment


class ExaminationModel(db.Model):
    __tablename__ = "Examinations"

    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.String(5000))
    prescription = db.Column(db.String(5000))

    appointment_id = db.Column(
        db.Integer, db.ForeignKey("Appointments.id", ondelete="SET NULL")
    )

    appointment = db.relationship("AppointmentModel")

    def __init__(self, appointment_id: int, diagnosis: str, prescription: str):
        self.diagnosis = diagnosis
        self.prescription = prescription
        self.appointment_id = appointment_id

    def json(self):
        return {
            "_id": self.id,
            "diagnosis": self.diagnosis,
            "prescription": self.prescription,
            "appointment_id": self.appointment_id,
        }

    def mini_json(self):
        return {
            "_id": self.id,
            "diagnosis": self.diagnosis,
            "prescription": self.prescription,
        }

    def json_with_info(self):
        return {
            "_id": self.id,
            "diagnosis": self.diagnosis,
            "prescription": self.prescription,
            "appointment": {**self.appointment.json()},
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_id_with_info(cls, _id):
        return (
            cls.query.filter(cls.id == _id)
            .join(Appointment, Appointment.id == cls.appointment_id)
            .join(
                Patient.PatientModel, Patient.PatientModel.id == Appointment.patient_id
            )
            .join(Doctor, Doctor.id == Appointment.doctor_id)
            .first()
        )

    @classmethod
    def find_all_filtered(cls, patient_id):
        return (
            cls.query.join(Appointment, Appointment.id == cls.appointment_id)
            .join(
                Patient.PatientModel, Patient.PatientModel.id == Appointment.patient_id
            )
            .filter(Patient.PatientModel.id == patient_id)
            .join(Doctor, Doctor.id == Appointment.doctor_id)
            .all()
        )

    @classmethod
    def find_all(cls):
        return (
            cls.query.join(Appointment, Appointment.id == cls.appointment_id)
            .outerjoin(
                Patient.PatientModel, Patient.PatientModel.id == Appointment.patient_id
            )
            .outerjoin(Doctor, Doctor.id == Appointment.doctor_id)
            .all()
        )
