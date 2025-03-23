import pytest
from app import app, db
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_hospital.db'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def auth_token_gm(client):
    response = client.post('/login', json={
        'username': 'admin',
        'password': 'admin'
    })
    data = response.get_json()
    return data['access_token']

@pytest.fixture
def auth_token_doctor(client):
    response = client.post('/login', json={
        'username': 'doctor',
        'password': 'doctor'
    })
    data = response.get_json()
    return data['access_token']

@pytest.fixture
def auth_token_assistant(client):
    response = client.post('/login', json={
        'username': 'assistant',
        'password': 'assistant'
    })
    data = response.get_json()
    return data['access_token']

def test_login(client):
    response = client.post('/login', json={'username': 'admin', 'password': 'admin'})
    data = response.get_json()
    assert response.status_code == 200
    assert 'access_token' in data

    response = client.post('/login', json={'username': 'doctor', 'password': 'doctor'})
    data = response.get_json()
    assert response.status_code == 200
    assert 'access_token' in data

    response = client.post('/login', json={'username': 'assistant', 'password': 'assistant'})
    data = response.get_json()
    assert response.status_code == 200
    assert 'access_token' in data

    response = client.post('/login', json={'username': 'wrong_user', 'password': 'wrong_pass'})
    data = response.get_json()
    assert response.status_code == 401
    assert "message" in data

def test_create_doctor_by_gm(client, auth_token_gm):
    response = client.post('/doctor', json={'name': 'Szabo Andreea'}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    data = response.get_json()
    assert response.status_code == 201
    assert data['message'] == 'Doctor ok'
    assert data['doctor']['name'] == 'Szabo Andreea'

def test_create_doctor_by_non_gm(client, auth_token_doctor):
    response = client.post('/doctor', json={'name': 'Szabo Andreea'}, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    data = response.get_json()
    assert response.status_code == 403

def test_create_patient_by_doctor(client, auth_token_doctor):
    client.post('/doctor', json={'name': 'Szabo Andreea'}, headers={'Authorization': f'Bearer {auth_token_doctor}'})

    response_create_patient = client.post('/patient', json={'name': 'Ana', 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    
    assert response_create_patient.status_code == 201
    data = response_create_patient.get_json()
    assert data['message'] == 'Patient ok'
    assert data['patient']['name'] == 'Ana'

def test_create_patient_by_gm(client, auth_token_gm):
    response_create_patient = client.post('/patient', json={'name': 'Mimi', 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    
    assert response_create_patient.status_code == 201
    data = response_create_patient.get_json()
    assert data['message'] == 'Patient ok'
    assert data['patient']['name'] == 'Mimi'

def test_create_assistant_by_gm(client, auth_token_gm):
    response = client.post('/assistant', json={'name': 'Maria'}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    data = response.get_json()
    assert response.status_code == 201
    assert data['message'] == 'Assistant ok'
    assert data['assistant']['name'] == 'Maria'

def test_create_assistant_by_non_gm(client, auth_token_doctor):
    response = client.post('/assistant', json={'name': 'Mihai'}, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    data = response.get_json()
    assert response.status_code == 403

def test_create_treatment_by_doctor(client, auth_token_doctor):
    client.post('/doctor', json={'name': 'Szabo Andreea'}, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    client.post('/patient', json={'name': 'Ana', 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    
    response_create_treatment = client.post('/treatment', json={'description': 'Cough syrup', 'patient_id': 1, 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    assert response_create_treatment.status_code == 201
    data = response_create_treatment.get_json()
    assert data['message'] == 'Treatment ok'
    assert data['treatment']['description'] == 'Cough syrup'

def test_create_treatment_by_gm(client, auth_token_gm):
    client.post('/doctor', json={'name': 'Szabo Andreea'}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    client.post('/patient', json={'name': 'Ana', 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    
    response_create_treatment = client.post('/treatment', json={'description': 'Cough syrup', 'patient_id': 1, 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    assert response_create_treatment.status_code == 201
    data = response_create_treatment.get_json()
    assert data['message'] == 'Treatment ok'
    assert data['treatment']['description'] == 'Cough syrup'

def test_treatment_recommended_by_doctor(client, auth_token_doctor):
    client.post('/doctor', json={'name': ' Szabo Andreea'}, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    client.post('/patient', json={'name': 'Ana', 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    
    response_create_treatment = client.post('/treatment', json={'description': 'Cough syrup', 'patient_id': 1, 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    assert response_create_treatment.status_code == 201

def test_assign_patient_to_assistant(client, auth_token_doctor, auth_token_gm):
    client.post('/doctor', json={'name': 'Szabo Andreea'}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    client.post('/assistant', json={'name': 'Maria'}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    client.post('/patient', json={'name': 'Ana', 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    
    response_assign_patient = client.post('/patient_assistant', json={'patient_id': 1, 'assistant_id': 1}, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    assert response_assign_patient.status_code == 201


def test_treatment_applied_by_assistant(client, auth_token_assistant):
    client.post('/doctor', json={'name': 'Szabo Andreea'}, headers={'Authorization': f'Bearer {auth_token_assistant}'})
    client.post('/patient', json={'name': 'Ana', 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_assistant}'})
    
    response_create_treatment = client.post('/treatment', json={
        'description': 'Cough syrup', 
        'patient_id': 1, 
        'doctor_id': 1, 
        'assistant_id': 1
    }, headers={'Authorization': f'Bearer {auth_token_assistant}'})


    assert response_create_treatment.status_code == 201

def test_report_doctors_patients_statistics(client, auth_token_gm):
    client.post('/doctor', json={'name': 'Szabo Andreea'}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    client.post('/patient', json={'name': 'Ana', 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    response = client.get('/report/doctors_patients', headers={'Authorization': f'Bearer {auth_token_gm}'})
    data = response.get_json()
    assert response.status_code == 200
    assert len(data['doctors_patients']) == 1
    assert data['statistics']['total_patients'] == 1

def test_report_treatments(client, auth_token_gm, auth_token_doctor):
    client.post('/doctor', json={'name': 'Szabo Andreea'}, headers={'Authorization': f'Bearer {auth_token_gm}'})
    client.post('/patient', json={'name': 'Ana', 'doctor_id': 1}, headers={'Authorization': f'Bearer {auth_token_gm}'})

    response_create_treatment = client.post('/treatment', json={
        'description': 'Cough syrup', 
        'patient_id': 1, 
        'doctor_id': 1
    }, headers={'Authorization': f'Bearer {auth_token_doctor}'})
    
    assert response_create_treatment.status_code == 201

    response = client.get('/report/treatments/1', headers={'Authorization': f'Bearer {auth_token_gm}'})
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['description'] == 'Cough syrup'

    response = client.get('/report/treatments/1', headers={'Authorization': f'Bearer {auth_token_doctor}'})
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == 1 
    assert data[0]['description'] == 'Cough syrup'