from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functools import wraps

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    patients = db.relationship('Patient', backref='doctor', lazy=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    assistants = db.relationship('Assistant', secondary='patient_assistant', lazy='subquery', back_populates='patients')

class Assistant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    patients = db.relationship('Patient', secondary='patient_assistant', lazy='subquery', back_populates='assistants')

class PatientAssistant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    assistant_id = db.Column(db.Integer, db.ForeignKey('assistant.id'), nullable=False)

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    assistant_id = db.Column(db.Integer, db.ForeignKey('assistant.id'), nullable=True)

def role_required(roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            current_user = get_jwt_identity()
            if current_user not in roles:
                return jsonify({"message": "Unauthorized"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if username == 'admin' and password == 'admin':
        access_token = create_access_token(identity='General Manager')
        return jsonify(access_token=access_token)
    elif username == 'doctor' and password == 'doctor':
        access_token = create_access_token(identity='Doctor')
        return jsonify(access_token=access_token)
    elif username == 'assistant' and password == 'assistant':
        access_token = create_access_token(identity='Assistant')
        return jsonify(access_token=access_token)
    return jsonify({"message": "Bad credentials"}), 401

@app.route('/doctor', methods=['POST'])
@jwt_required()
@role_required('General Manager')
def create_doctor():
    data = request.get_json()
    new_doctor = Doctor(name=data['name'])
    db.session.add(new_doctor)
    db.session.commit()
    return jsonify({"message": "Doctor ok", "doctor": {"id": new_doctor.id, "name": new_doctor.name}}), 201

@app.route('/doctor', methods=['GET'])
@jwt_required()
def get_all_doctors():
    doctors = Doctor.query.all()
    return jsonify([{"id": doctor.id, "name": doctor.name} for doctor in doctors])

@app.route('/doctor/<int:id>', methods=['GET'])
@jwt_required()
def get_doctor(id):
    doctor = db.session.get(Doctor, id)
    return jsonify({"id": doctor.id, "name": doctor.name})

@app.route('/patient', methods=['POST'])
@jwt_required()
@role_required(['Doctor', 'General Manager'])
def create_patient():
    data = request.get_json()
    new_patient = Patient(name=data['name'], doctor_id=data['doctor_id'])
    db.session.add(new_patient)
    db.session.commit()
    return jsonify({"message": "Patient ok", "patient": {"id": new_patient.id, "name": new_patient.name}}), 201

@app.route('/patient/<int:id>', methods=['GET'])
@jwt_required()
def get_patient(id):
    patient = db.session.get(Patient, id)
    return jsonify({"id": patient.id, "name": patient.name, "doctor_id": patient.doctor_id})

@app.route('/assistant', methods=['POST'])
@jwt_required()
@role_required('General Manager')
def create_assistant():
    data = request.get_json()
    new_assistant = Assistant(name=data['name'])
    db.session.add(new_assistant)
    db.session.commit()
    return jsonify({"message": "Assistant ok", "assistant": {"id": new_assistant.id, "name": new_assistant.name}}), 201

@app.route('/assistant/<int:id>', methods=['GET'])
@jwt_required()
def get_assistant(id):
    assistant = db.session.get(Assistant, id)
    return jsonify({"id": assistant.id, "name": assistant.name})

@app.route('/treatment', methods=['POST'])
@jwt_required()
@role_required(['Doctor', 'General Manager', 'Assistant'])
def create_treatment():
    data = request.get_json()
    new_treatment = Treatment(
        description=data['description'], 
        patient_id=data['patient_id'], 
        doctor_id=data['doctor_id'],
        assistant_id=data.get('assistant_id')
    )
    db.session.add(new_treatment)
    db.session.commit()
    return jsonify({
        "message": "Treatment ok", 
        "treatment": {"id": new_treatment.id, "description": new_treatment.description}
    }), 201

@app.route('/treatment/<int:id>', methods=['GET'])
@jwt_required()
def get_treatment(id):
    treatment = db.session.get(Treatment, id)
    return jsonify({"id": treatment.id, "description": treatment.description})

@app.route('/report/doctors_patients', methods=['GET'])
@jwt_required()
@role_required('General Manager')
def report_doctors_patients():
    doctors = Doctor.query.all()
    result = []
    total_patients = 0

    for doctor in doctors:
        patients = [{"id": patient.id, "name": patient.name} for patient in doctor.patients]
        result.append({
            "doctor": {"id": doctor.id, "name": doctor.name}, 
            "patients": patients
        })
        total_patients += len(patients)

    statistics = {
        "total_doctors": len(doctors),
        "total_patients": total_patients
    }
    
    return jsonify({"doctors_patients": result, "statistics": statistics})

@app.route('/report/treatments/<int:patient_id>', methods=['GET'])
@jwt_required()
@role_required(['Doctor', 'General Manager'])
def report_treatments(patient_id):
    treatments = Treatment.query.filter_by(patient_id=patient_id).all()
    result = [{"id": treatment.id, "description": treatment.description} for treatment in treatments]
    return jsonify(result)

@app.route('/patient_assistant', methods=['POST'])
@jwt_required()
@role_required(['Doctor', 'General Manager'])
def assign_patient_to_assistant():
    data = request.get_json()
    patient_id = data['patient_id']
    assistant_id = data['assistant_id']
    
    patient = db.session.get(Patient, patient_id)
    assistant = db.session.get(Assistant, assistant_id)
    
    if not patient or not assistant:
        return jsonify({"message": "Patient or Assistant not found"}), 404
    
    patient.assistants.append(assistant)
    db.session.commit()
    
    return jsonify({"message": "Patient assigned to assistant"}), 201

if __name__ == '__main__':
    app.run(debug=True)