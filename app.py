from flask import Flask, render_template
from fhirpy import SyncFHIRClient

app = Flask(__name__)

HAPI_BASE_URL = 'http://localhost:8080/baseR4'


def get_patients():
    client = SyncFHIRClient(HAPI_BASE_URL)
    resources = client.resources('Patient').search()
    patients = resources.fetch()
    return patients


@app.route('/')
def index():
    patients = get_patients()
    return render_template('index.html', patients=patients)


if __name__ == '__main__':
    app.run()
