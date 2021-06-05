from flask import Flask, render_template, request
import pandas as pd
from fhirpy import SyncFHIRClient
import plotly
import plotly.express as px
import json

app = Flask(__name__)

HAPI_BASE_URL = 'http://localhost:8080/baseR4'


def get_patients():
    client = SyncFHIRClient(HAPI_BASE_URL)
    resources = client.resources('Patient').search().limit(50)
    patients = resources.fetch()
    return patients


def get_patient_info(id, year):
    client = SyncFHIRClient(HAPI_BASE_URL)
    resources = client.resources('Patient').search(_id=id).limit(50)
    patients = resources.fetch()
    resources = client.resources('Observation').search(subject=id, date=year).limit(50)
    observations = resources.fetch()
    resources = client.resources('MedicationRequest').search(subject=id).limit(50)
    medication_requests = resources.fetch()
    return patients.pop(), observations, medication_requests


def get_observations(patient_id, observation):
    client = SyncFHIRClient(HAPI_BASE_URL)
    resources = client.resources('Observation').search(subject=patient_id, code=observation).limit(50)
    observations = resources.fetch()
    return observations


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
    return render_template('patient.html', patient=p, observations=observations,
                           medication_requests=medication_requests, year=year)


@app.route('/patient/<patient_id>/observation_details/<observation>', methods=['GET'])
def observation_details(patient_id, observation):
    observations = get_observations(patient_id, observation)
    values = [observation.valueQuantity.value for observation in observations]
    date = [observation.issued for observation in observations]
    df = pd.DataFrame(dict(values=values, date=date))
    fig = px.scatter(df, x="date", y="values")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('observation_details.html', name= observations[0].code.text, graphJSON=graphJSON)


if __name__ == '__main__':
    app.run()
