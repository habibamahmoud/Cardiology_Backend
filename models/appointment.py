from db import db
from datetime import datetime, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class AppointmentModel(db.Model):
    __tablename__ = "Appointments"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    created_at = db.Column(db.Date)
    description = db.Column(db.String(5000))

    doctor_id = db.Column(db.Integer, db.ForeignKey("Doctors.id", ondelete="SET NULL"))
    patient_id = db.Column(
        db.Integer, db.ForeignKey("Patients.id", ondelete="SET NULL")
    )
    patient_username = db.Column(db.String(80))
    doctor_username = db.Column(db.String(80))

    doctor = db.relationship("DoctorModel")
    patient = db.relationship("PatientModel")

    def __init__(self, date, doctor_id, patient_id, created_at, description,patient_username,doctor_username):
        self.date = date
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.patient_username = patient_username
        self.doctor_username = doctor_username
        self.created_at = created_at
        self.description = description

    def json(self):
        return {
            "_id": self.id,
            "date": self.date.strftime("%Y-%m-%d"),
            "patient_id": self.patient_id,
            "patient_username": self.patient_username,
            "doctor_id": self.doctor_id,
            "doctor_username": self.doctor_username,
            "date_of_reservation": self.created_at.strftime("%Y-%m-%d"),
            "description": self.description,
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
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_date(cls, date):
        return cls.query.filter_by(date=date).all()

    def main(start_time):

        SCOPES = ["https://www.googleapis.com/auth/calendar"]
        creds = None

        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secrets2.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        service = build("calendar", "v3", credentials=creds)

        app_date = start_time.strftime("%Y-%m-%d")

        y1, m1, d1 = [int(x) for x in app_date.split("-")]

        app_date = datetime(y1, m1, d1, 9, 0, 0)

        end_time = app_date + timedelta(hours=4)
        event = {
            "summary": "Doctor Appointment",
            "location": "Cairo",
            "description": "",
            "start": {
                "dateTime": app_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "Africa/Cairo",
            },
            "end": {
                "dateTime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "Africa/Cairo",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 10},
                ],
            },
        }

        service.events().insert(calendarId="primary", body=event).execute()

    # def calendar (start_time,email):

    #     calendar = GoogleCalendar('momen99223@gmail.com')

    #     # event = Event(
    #     #  'The Glass Menagerie',
    #     #   start=start_time,
    #     #   #location='Africa/Cairo',
    #     #   minutes_before_popup_reminder=15
    #     #  )
    #     event = {
    #     'summary': 'Doctor Appointment',
    #     'location': 'Cairo',
    #     'description': '',
    #     'start': {
    #     'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
    #     'timeZone': 'Africa/Cairo',
    #      },
    #     'end': {
    #     'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
    #     'timeZone': 'Africa/Cairo',
    #     },
    #     'reminders': {
    #     'useDefault': False,
    #  #'overrides': [
    #   #{'method': 'email', 'minutes': 24 * 60},
    #   #{'method': 'popup', 'minutes': 10},
    #   #],
    #     },
    #     }
    #     calendar.add_event(event)
