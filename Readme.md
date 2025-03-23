# Hospital Management System

This project is a hospital management system built using **Flask**. It allows for managing doctors, patients, assistants, treatments, and generating reports. The solution includes an API with different endpoints accessible based on user roles. 

## Features

- **Login**: Allows users to authenticate as **General Manager**, **Doctor**, or **Assistant** using JWT tokens.
- **Doctor Management**: General Manager can create and view doctors.
- **Patient Management**: Both Doctor and General Manager can create and view patients.
- **Assistant Management**: General Manager can create and view assistants.
- **Treatment Management**: Both Doctor and General Manager can create treatments.
- **Treatment Recommendation**: Only Doctors can recommend treatments for patients.
- **Patient Assignment to Assistant**: Both Doctor and General Manager can assign patients to assistants.
- **Treatment Application**: Only assistants can apply treatments.
- **Reports**: Generate reports of doctors with their associated patients, and treatments applied to a patient.

## Usage:
python -m venv venv
source venv/bin/activate
pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-JWT-Extended pytest
flask run
pytest test.py (to run the tests that I created for every operation)
## Endpoints
- Authentication
POST /login: Authenticates the user and returns a JWT token. You can log in as:
admin / admin -> General Manager
doctor / doctor -> Doctor
assistant / assistant -> Assistant
- Doctor Management
POST /doctor: Creates a new doctor (General Manager only).
GET /doctor: Retrieves all doctors.
GET /doctor/<id>: Retrieves a specific doctor by ID.
- Patient Management
POST /patient: Creates a new patient (Doctor or General Manager).
GET /patient/<id>: Retrieves a specific patient by ID.
- Assistant Management
POST /assistant: Creates a new assistant (General Manager only).
GET /assistant/<id>: Retrieves a specific assistant by ID.
- Treatment Management
POST /treatment: Creates a new treatment (Doctor or General Manager).
GET /treatment/<id>: Retrieves a specific treatment by ID.
- Patient Assignment to Assistant
POST /patient_assistant: Assigns a patient to an assistant (Doctor or General Manager only).
- Treatment Application by Assistant
POST /treatment: Only an assistant can apply a treatment (the assistant ID must be provided).
- Reports
GET /report/doctors_patients: Returns a list of doctors and their associated patients, along with statistics data (General Manager only).
GET /report/treatments/<patient_id>: Returns all treatments applied to a specific patient (Doctor or General Manager).

Potential Vulnerabilities
- JWT Token Expiry: tokens are currently set to expire after a default duration, and there is no refresh token mechanism
- Password Storage: Passwords are currently not hashed
- There are no tests created for ensuring scalability
