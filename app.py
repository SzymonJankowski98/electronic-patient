from datetime import date

from flask import Flask, render_template, request
from fhirpy import SyncFHIRClient

app = Flask(__name__)

HAPI_BASE_URL = 'http://localhost:8080/baseR4'


def get_patients():
    client = SyncFHIRClient(HAPI_BASE_URL)
    resources = client.resources('Patient').search()
    patients = resources.fetch()
    return patients


def get_patient_info(id, year):
    client = SyncFHIRClient(HAPI_BASE_URL)
    resources = client.resources('Patient').search(_id=id)
    patients = resources.fetch()
    resources = client.resources('Observation').search(subject=id, date=year)
    observations = resources.fetch()
    resources = client.resources('MedicationRequest').search(subject=id)
    medication_requests = resources.fetch()
    return patients.pop(), observations, medication_requests


@app.route('/')
def index():
    patients = get_patients()
    return render_template('index.html', patients=patients)


@app.route('/patient/<patient_id>', methods=['GET'])
def patient(patient_id):
    year = "2015"
    if 'year' in request.args:
        year = request.args.get('year')
    p, observations, medication_requests = get_patient_info(patient_id, year)
    return render_template('patient.html', patient=p, observations=observations, medication_requests=medication_requests, year=year)


if __name__ == '__main__':
    app.run()
