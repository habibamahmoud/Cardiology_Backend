from flask_restful import Resource, reqparse
from models.doctor import DoctorModel
from models.patient import PatientModel
from models.examination import ExaminationModel
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt_claims,
)
from datetime import datetime, timedelta

BLANK = "This field cannot be left blank."


BLANK_ERROR = "'{}' cannot be blank."
DOCTOR_ALREADY_EXISTS = "A doctor with that username already exists."
DOCTOR_ALREADY_EXISTS2 = "A doctor with that email already exists."
CREATED_SUCCESSFULLY = "Doctor created successfully."
USER_NOT_FOUND = "Doctor not found."
USER_DELETED = "Doctor deleted."
INVALID_CREDENTIALS = "Invalid credentials!"
USER_LOGGED_OUT = "Doctor <id={doctor_id}> successfully logged out."


class DoctorRegister(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        if get_jwt_claims()["type"] != "admin":
            return {"message": "only an admin can register doctors."}, 401
        _doctor_parser = reqparse.RequestParser()
        _doctor_parser.add_argument("username", type=str, required=True, help=BLANK)

        _doctor_parser.add_argument("password", type=str, required=True, help=BLANK)

        _doctor_parser.add_argument("first_name", type=str, required=True, help=BLANK)

        _doctor_parser.add_argument("last_name", type=str, required=True, help=BLANK)

        _doctor_parser.add_argument("email", type=str, required=True, help=BLANK)

        _doctor_parser.add_argument("mobile", type=str, required=True, help=BLANK)

        _doctor_parser.add_argument("gender", type=str, required=True, help=BLANK)

        _doctor_parser.add_argument("address", type=str, required=True, help=BLANK)

        _doctor_parser.add_argument("birthdate", type=str, required=True, help=BLANK)

        data = _doctor_parser.parse_args()

        data["gender"] = int(data["gender"])
        if data["gender"] != 0 and data["gender"] != 1:
            return {
                "message": "Invalid request: gender is only '0' if male or '1' if female"
            }
        if (
            data["username"].isspace()
            or data["password"].isspace()
            or data["address"].isspace()
            or data["mobile"].isspace()
            or data["email"].isspace()
            or data["first_name"].isspace()
            or data["last_name"].isspace()
        ):
            return {"message": "One of the inputs is empty"}, 400

        if len(data["username"]) < 4:
            return {"message": "Username is too short"}, 400

        if DoctorModel.find_by_username(data["username"]):
            return {"message": DOCTOR_ALREADY_EXISTS}, 400

        if DoctorModel.find_by_email(data["email"]):
            return {"message": DOCTOR_ALREADY_EXISTS2}, 400

        y, m, d = [int(x) for x in data["birthdate"].split("-")]
        data["birthdate"] = datetime(y, m, d)
        if ((datetime.now() - data["birthdate"]).days // 365) < 25:
            return {"message": "Invalid age"}, 400

        data["created_at"] = datetime.now().date()

        user = DoctorModel(**data)
        user.save_to_db()

        return {"message": CREATED_SUCCESSFULLY}


class Doctor(Resource):
    @classmethod
    def get(cls, doctor_id: int):
        user = DoctorModel.find_docotor_by_id_with_appointments(doctor_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return user.json_with_appointments()

    @classmethod
    @jwt_required
    def delete(cls, doctor_id: int):
        if get_jwt_claims()["type"] == "admin":
            doctor = DoctorModel.find_by_id(doctor_id)
            if not doctor:
                return {"message": USER_NOT_FOUND}, 404
            doctor.delete_from_db()
            return {"message": USER_DELETED}
        return {"message": "Admin authorization required."}


class DoctorLogin(Resource):
    @classmethod
    def post(cls):

        _doctor_parser = reqparse.RequestParser()
        _doctor_parser.add_argument("username", type=str, required=True, help=BLANK)

        _doctor_parser.add_argument("password", type=str, required=True, help=BLANK)

        data = _doctor_parser.parse_args()

        doctor = DoctorModel.find_by_username(data["username"])

        if doctor and check_password_hash(doctor.password, data["password"]):
            access_token = create_access_token(
                identity=doctor.id,
                fresh=True,
                user_claims={"type": "doctor"},
                expires_delta=timedelta(1),
            )
            refresh_token = create_refresh_token(
                identity=doctor.id, user_claims={"type": "doctor"}
            )
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        return {"message": INVALID_CREDENTIALS}, 401


class DoctorList(Resource):
    @classmethod
    def get(cls):

        doctors = DoctorModel.find_all()
        doctors_list = [doctor.json() for doctor in doctors]
        date = datetime(2021, 1, 12).date()
        return doctors_list, 200


class DoctorPatient(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        if get_jwt_claims()["type"] != "doctor":
            return {"message": "You must be a doctor"}

        identity = get_jwt_identity()
        results = PatientModel.find_by_doctor(identity)
        result_list = [result.json() for result in results]
        return result_list, 200
