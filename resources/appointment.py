from flask_restful import Resource, reqparse
from models.appointment import AppointmentModel
from datetime import datetime
from models.doctor import DoctorModel
from models.patient import PatientModel
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt_claims,
)


class appointment(Resource):
    appointment_parser = reqparse.RequestParser()
    appointment_parser.add_argument(
        "doctor_id", type=str, required=True, help="This field cannot be blank."
    )
    appointment_parser.add_argument("description", type=str, required=False)
    appointment_parser.add_argument("patient_id", type=int, required=False)
    appointment_parser.add_argument(
        "date", type=str, required=True, help="This field cannot be blank."
    )

    @classmethod
    @jwt_required
    def post(cls):
        claims = get_jwt_claims()
        if claims["type"] != "patient":
            return {"message": "Access denied"}

        data = cls.appointment_parser.parse_args()
        identity = get_jwt_identity()

        if data["date"].isspace():
            return {"message": "One of the inputs is empty"}, 400

        data["patient_id"] = identity

        data['patient_username'] = PatientModel.find_by_id(identity).username

        data["doctor_id"] = int(data["doctor_id"])

        data['doctor_username'] = DoctorModel.find_by_id(data['doctor_id']).username

        doctor = DoctorModel.find_by_id(data["doctor_id"])
        if not doctor:
            return {"message": "Doctor not found"}, 404

        data["created_at"] = datetime.now().date()
        y1, m1, d1 = [int(x) for x in data["date"].split("-")]

        app_date = datetime(y1, m1, d1).date()

        if app_date < data["created_at"]:
            return {"message": "Invalid date"}

        apps_date = AppointmentModel.find_by_date(app_date)

        for app in apps_date:
            if app.patient_id == identity:
                return {"message": "Appointment already exists at the same date"}

        AppointmentModel.main(app_date)
        appointment = AppointmentModel(**data)
        appointment.save_to_db()

        return {"message": "Appointment created successfully."}, 201

    @classmethod
    @jwt_required
    def get(cls):
        identity = get_jwt_identity()
        claims = get_jwt_claims()

        if claims["type"] == "doctor":
            doctor_appointments = DoctorModel.find_by_id(identity).appointments

            doctorapp = [appointment.json() for appointment in doctor_appointments]
            return doctorapp, 200

        elif claims["type"] == "patient":
            patient_appointments = PatientModel.find_by_id(identity).appointments

            patientapp = [appointment.json() for appointment in patient_appointments]
            return patientapp

        else:
            appointments = AppointmentModel.find_all()
            appointments_list = [appointment.json() for appointment in appointments]
            return appointments_list, 200


class deleteAppointments(Resource):
    @classmethod
    @jwt_required
    def delete(cls, app_id):
        claims = get_jwt_claims()
        if claims["type"] != "admin":
            return {"message": "access denied"}

        app = AppointmentModel.find_by_id(app_id)
        if not app:
            return {"message": "Appointment not found"}, 404
        app.delete_from_db()
        return {"message": "Appointment deleted"}
