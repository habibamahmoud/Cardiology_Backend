from flask import Flask, request, send_file
from flask_restful import Resource, Api, reqparse
from flask_uploads import UploadNotAllowed
from models import image_helper
from werkzeug.datastructures import FileStorage
import traceback
import os
from flask_jwt_extended import jwt_required, get_jwt_claims
from models.patient import PatientModel


class UploadImage(Resource):
    @jwt_required
    def post(self, patient_id):

        if get_jwt_claims()["type"] == "patient":
            {"message": "Invalid authorization"}, 401
        if not PatientModel.find_by_id(patient_id):
            return {"message": "A patient with this id does not exist"}, 404

        data = request.files
        print(request.files)
        if type(data["image"]) != FileStorage:

            return {"message": "Invalid data."}
        image_path = image_helper.save_image(
            data["image"], folder=f"patient_{patient_id}"
        )
        basename = image_helper.get_basename(image_path)
        return {"message": "image uploaded"}, 201


class PatientImages(Resource):
    @jwt_required
    def get(self, patient_id):
        if get_jwt_claims()["type"] == "patient":
            return {
                "message": "Invalid authorization: you must be a doctor or an admin."
            }, 401
        if not PatientModel.find_by_id(patient_id):
            return {"message": "A patient with this id does not exist"}
        folder = os.getcwd()
        dirs = os.listdir(f"{folder}/static/images/patient_{patient_id}")
        file_list = []
        for file in dirs:
            file_list.append(
                {
                    "image": f"http://localhost:5000/static/images/patient_{patient_id}/{file}"
                }
            )
        return file_list


class DeleteImage(Resource):
    @jwt_required
    def delete(self, patient_id):
        if get_jwt_claims()["type"] != "admin":
            return {"message": "Invalid authorization, you have to be an admin."}, 401
        if not PatientModel.find_by_id(patient_id):
            return {"message": "A patient with this id does not exist"}, 404
        filename = request.args.get("filename")
        folder = os.getcwd()
        dirs = os.listdir(f"{folder}/static/images/patient_{patient_id}")
        for file in dirs:
            if filename == file:
                os.remove(
                    image_helper.get_path(
                        file, folder=f"{folder}/static/images/patient_{patient_id}"
                    )
                )
                return {"message": "file deleted"}
        return {"message": "file not found"}, 404
