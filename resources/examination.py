from models.examination import ExaminationModel
from models.appointment import AppointmentModel
from flask_restful import Resource, reqparse
from datetime import datetime
from models.doctor import DoctorModel
from models.patient import PatientModel
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt_claims,
)

BLANK = "This field cannot be left blank"


class ExaminationRegister(Resource):
    examination_parser = reqparse.RequestParser()
    examination_parser.add_argument("diagnosis", type=str, required=True, help=BLANK)
    examination_parser.add_argument("prescription", type=str, required=True, help=BLANK)

    @classmethod
    @jwt_required
    def post(cls, app_id):
        data = cls.examination_parser.parse_args()
        if data["diagnosis"].isspace() or data["prescription"].isspace():
            return {"message": "One of the inputs is empty"}, 400
        if get_jwt_claims()["type"] == "doctor":
            appointment = AppointmentModel.find_by_id(app_id)
            if appointment:
                examination = ExaminationModel(**data, appointment_id=app_id)
                examination.save_to_db()
                return {"message": "Added Successfully."}, 200
            else:
                return {"message": "No appointment with this id exists"}, 404
        return {"message": "Authorization required: You must be a doctor."}, 401


class PatientExaminations(Resource):
    @classmethod
    @jwt_required
    def get(cls, patient_id):
        if get_jwt_claims()["type"] == "doctor":
            examinations = ExaminationModel.find_all_filtered(patient_id)
            examination_list = [
                examination.json_with_info() for examination in examinations
            ]
            return examination_list, 200
        return {"message": "Unauthorized: You must be a doctor"}


class Examination(Resource):
    @classmethod
    @jwt_required
    def get(cls, examination_id):
        if get_jwt_claims()["type"] == "doctor" or get_jwt_claims()["type"] == "admin":
            examination = ExaminationModel.find_by_id_with_info(examination_id)
            if not examination:
                return {"message": "Examination not found"}, 404
            return examination.json()
        return {"message": "Invalid authorization"}

    @classmethod
    @jwt_required
    def delete(cls, examination_id):
        if get_jwt_claims()["type"] == "admin":
            examination = ExaminationModel.find_by_id(examination_id)
            if not examination:
                return {"message": "Examination not found"}, 404
            examination.delete_from_db()
            return {"message": "Deleted Successfully."}
        return {"message": "Unauthorized: Admin authorization required."}


class ExaminationList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        if get_jwt_claims()["type"] == "admin":
            examinations = ExaminationModel.find_all()

            examinations_list = [
                examination.json_with_info() for examination in examinations
            ]
            return examinations_list, 200

        elif get_jwt_claims()["type"] == "patient":
            patient_id = get_jwt_identity()
            examinations = ExaminationModel.find_all_filtered(patient_id)
            examination_list = [
                examination.json_with_info() for examination in examinations
            ]
            return examination_list, 200
        else:
            return {"message": "Authorization required"}
