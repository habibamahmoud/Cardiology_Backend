from datetime import datetime, timedelta
from models.patient import PatientModel
from models.doctor import DoctorModel
from models.appointment import AppointmentModel
from sqlalchemy import func


def find_count(date: datetime):

    end_date = datetime.now().date()
    analytics_list = []
    while date <= end_date:
        analytics_list.append(
            {"date": date, "doctors": "0", "patients": "0", "appointments": "0"}
        )
        date += timedelta(days=1)

    appointments = (
        AppointmentModel.query.with_entities(
            AppointmentModel.created_at, func.count(AppointmentModel.id)
        )
        .group_by(AppointmentModel.created_at)
        .all()
    )
    doctors = (
        DoctorModel.query.with_entities(
            DoctorModel.created_at, func.count(DoctorModel.id)
        )
        .group_by(DoctorModel.created_at)
        .all()
    )
    patients = (
        PatientModel.query.with_entities(
            PatientModel.created_at, func.count(PatientModel.id)
        )
        .group_by(PatientModel.created_at)
        .all()
    )
    appointment = 0
    doctor = 0
    patient = 0
    
    for x in analytics_list:
        if appointments and appointment<len(appointments):
            if x["date"] == appointments[appointment][0]:
                x["appointments"] = appointments[appointment][1]
                appointment += 1

        if doctors and doctor<len(doctors):
            if x["date"] == doctors[doctor][0]:
                x["doctors"] = doctors[doctor][1]
                doctor += 1
        if patients and patient<len(patients):
            if x["date"] == patients[patient][0]:
                x["patients"] = patients[patient][1]
                patient += 1
        x["date"] = x["date"].strftime("%Y-%m-%d")

    return analytics_list
