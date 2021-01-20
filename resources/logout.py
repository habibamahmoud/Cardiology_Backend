from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_raw_jwt
from blacklist import BLACKLIST


class Logout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]  # jti is a "JWT ID", a unique identifier for a JWT
        BLACKLIST.add(jti)
        return {"message": "Sucessfully logged out"}, 200
