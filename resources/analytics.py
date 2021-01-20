from flask import request
from flask_restful import Resource
from datetime import datetime
from models.analytics import find_count
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    jwt_required,
    get_raw_jwt,
    get_jwt_identity,
    get_jwt_claims,
)


class Analytics(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        if get_jwt_claims()["type"] != "admin":
            return {"message": "Access denied"}

        date = request.args.get("date")
        y, m, d = [int(x) for x in date.split("-")]
        date = datetime(y, m, d).date()
        return find_count(date)
