from flask_restful import Resource, reqparse
from models.admin import AdminModel
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    jwt_required,
    get_jwt_identity,
    get_jwt_claims,
)
from datetime import datetime, timedelta

BLANK = "This field cannot be left blank."
INVALID_CREDENTIALS = "Invalid Credintials"
USER_LOGGED_OUT = "Logged out successfully"


class AdminRegister(Resource):
    @classmethod
    # @jwt_required
    def post(cls):
        # if get_jwt_claims()["type"] != "admin":
        #    return {"message": "Admin authorization required."}, 401
        _admin_parser_ = reqparse.RequestParser()
        _admin_parser_.add_argument("username", type=str, required=True, help=BLANK)
        _admin_parser_.add_argument("password", type=str, required=True, help=BLANK)
        _admin_parser_.add_argument("first_name", type=str, required=True, help=BLANK)
        _admin_parser_.add_argument("last_name", type=str, required=True, help=BLANK)
        data = _admin_parser_.parse_args()
        if (
            data["username"].isspace()
            or data["password"].isspace()
            or data["first_name"].isspace()
            or data["last_name"].isspace()
        ):
            return {"message": "One of the inputs is empty"}, 400

        if len(data["username"]) < 5:
            return {"message": "Username is too short"}, 400

        if AdminModel.find_by_username(data["username"]):
            return {"message": "This admin already exists"}

        admin = AdminModel(**data)
        admin.save_to_db()
        return {"message": "Admin created successfully."}


class AdmingLogin(Resource):
    def post(cls):

        _admin_parser = reqparse.RequestParser()
        _admin_parser.add_argument("username", type=str, required=True, help=BLANK)

        _admin_parser.add_argument("password", type=str, required=True, help=BLANK)
        data = _admin_parser.parse_args()
        admin = AdminModel.find_by_username(data["username"])
        if admin and check_password_hash(admin.password, data["password"]):
            access_token = create_access_token(
                identity=admin.id,
                fresh=True,
                user_claims={"type": "admin"},
                expires_delta=timedelta(1),
            )
            refresh_token = create_refresh_token(
                identity=admin.id, user_claims={"type": "admin"}
            )
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        return {"message": INVALID_CREDENTIALS}, 401
