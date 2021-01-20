from models.contact_us import ContactUsModel
from flask_restful import Resource, reqparse
from datetime import datetime
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims
)

AUTHORIZATION_ERROR = "Admin authorization required"
DELETED = "Deleted Successfully"
BLANK_ERROR = "This field cannot be left blank"
NOT_FOUND = "Form not found"


class ContactUsRegister(Resource):
    _contact_us_parser = reqparse.RequestParser()
    _contact_us_parser.add_argument("first_name", type=str, help=BLANK_ERROR)
    _contact_us_parser.add_argument("last_name", type=str, help=BLANK_ERROR)
    _contact_us_parser.add_argument("email", type=str, help=BLANK_ERROR)
    _contact_us_parser.add_argument("mobile", type=str, help=BLANK_ERROR)
    _contact_us_parser.add_argument("text", type=str, help=BLANK_ERROR)

    @classmethod
    def post(cls):
        data = cls._contact_us_parser.parse_args()
        if (
            data["text"].isspace()
            or data["mobile"].isspace()
            or data["email"].isspace()
            or data["first_name"].isspace()
            or data["last_name"].isspace()
        ):
            return {"message": BLANK_ERROR}, 400
        form = ContactUsModel(**data)
        form.save_to_db()
        return {"message": "Submitted successfully"}, 200


class ContactUs(Resource):
    @classmethod
    @jwt_required
    def get(cls, form_id):
        if get_jwt_claims()["type"] != "admin":
            return {"message": AUTHORIZATION_ERROR}, 401
        form = ContactUsModel.find_by_id(form_id)
        if form:
            return form.json()
        return {"message": NOT_FOUND}

    @classmethod
    @jwt_required
    def delete(cls, form_id):
        if get_jwt_claims()["type"] != "admin":
            return {"message": AUTHORIZATION_ERROR}, 401
        form = ContactUsModel.find_by_id(form_id)
        if form:
            form.delete_from_db()
            return {"message": DELETED}, 200
        return {"message": NOT_FOUND}


class ContactUsList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        if get_jwt_claims()["type"] != "admin":
            return {"message": AUTHORIZATION_ERROR}
        forms = ContactUsModel.find_all()
        forms_list = [form.json() for form in forms]
        return forms_list, 200
