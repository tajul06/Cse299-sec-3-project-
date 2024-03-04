import os
from flask import Flask, flash, request ,url_for, redirect ,session , render_template

from google.oauth2.credentials import Credentials

from googleapiclient.discovery import build

import pandas as pd

import io

from authlib.integrations.flask_client import OAuth

from pymongo import MongoClient

from bson import ObjectId

import requests



app = Flask(__name__)
app.secret_key='justtry something'

# MongoDB connection
client = MongoClient("mongodb+srv://tajulislam06:trynothing@cluster0.x3lpi33.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['LLM_Marking']
teachers_collection = db['teacher']  # Collection for storing teachers
courses_collection = db['courses']  # Collection for storing courses
students_collection = db['students']

# oauth config
oauth = OAuth(app)
google =oauth.register(
     name='google',
     client_id='948138056692-l0ec5idekoun63t57696tic16qn6pej0.apps.googleusercontent.com',
     client_secret='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',
     access_token_url='https://accounts.google.com/o/oauth2/token',
     access_token_params=None,
     authorize_url='https://accounts.google.com/o/oauth2/auth',
     authorize_params=None,
     api_base_url='https://www.googleapis.com/oauth2/v1/',
     userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  
     client_kwargs={'scope': 'email profile'}
     
)

# Google Drive API config
GOOGLE_DRIVE_API_URL = 'https://www.googleapis.com/upload/drive/v3/files'
GOOGLE_DRIVE_API_TOKEN = '1//04GC6t9U38b9wCgYIARAAGAQSNwF-L9IrYYywCHrNZ2bbS095Dnk8CYuIyk7hzp26f3C3pl0Fkv-LKN0-rQC9hwM0XwK2N28HapM'  # Replace with your actual Google Drive API token

@app.route('/')
def home():
    email = dict(session).get('email', None)
    return render_template('login.html', email=email )


@app.route('/login')
def login():
    
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    try:
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        resp.raise_for_status() 
        user_info = resp.json()
        session['email'] = user_info['email']
        # Check if teacher exists in MongoDB
        teacher = teachers_collection.find_one({'email': user_info['email']})
        if teacher is None:
            # Add teacher to MongoDB
            teachers_collection.insert_one({'name': user_info['name'], 'email': user_info['email']})

    except Exception as e:
        
        print(f"Error in authorize route: {e}")
        return "An error occurred during authorization", 500  # Return a 500 Internal Server Error status code
    return redirect('/dashboard')

@app.route('/callback')
def callback():
    token = google.authorize_access_token()
    session['token'] = token
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    email = dict(session).get('email', None)
    if email:
        
        courses = courses_collection.find({'teacher_email': email})
        return render_template('dashboard.html', email=email, courses=courses)
    else:
        return redirect('/')



@app.route('/course/<course_id>')
def course_dashboard(course_id):
    email = dict(session).get('email', None)
    if email:
       
        course = courses_collection.find_one({'_id': ObjectId(course_id)})
        if course:
            return render_template('course_dashboard.html', email=email, course=course)
    return redirect('/dashboard')


@app.route('/add_course', methods=['POST'])
def add_course():
    email = dict(session).get('email', None)
    if email:
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        # Add the course to MongoDB
        course_id = courses_collection.insert_one({'name': name, 'description': description, 'start_date': start_date, 'end_date': end_date, 'teacher_email': email}).inserted_id
        return redirect(f'/course/{course_id}')
    return redirect('/dashboard')


@app.route('/edit_course/<course_id>', methods=['POST'])
def edit_course(course_id):
    email = dict(session).get('email', None)
    if email:
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        # Update the course in MongoDB
        courses_collection.update_one({'_id': ObjectId(course_id)}, {'$set': {'name': name, 'description': description, 'start_date': start_date, 'end_date': end_date}})
        return redirect(f'/course/{course_id}')
    return redirect('/')


@app.route('/delete_course/<course_id>')
def delete_course(course_id):
    email = dict(session).get('email', None)
    if email:
        # Delete the course from MongoDB
        courses_collection.delete_one({'_id': ObjectId(course_id)})
    return redirect('/dashboard')


@app.route('/upload_students/<course_id>', methods=['POST'])
def upload_students(course_id):
    email = dict(session).get('email', None)
    if email:
        # Check if the request contains a file
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file is uploaded
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            # Save the file temporarily
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            # Upload the file to Google Drive
            try:
                headers = {
                    'Authorization': f'Bearer {GOOGLE_DRIVE_API_TOKEN}',
                    'Content-Type': 'application/json',
                }
                params = {
                    'uploadType': 'media',
                    'name': file.filename,
                }
                response = requests.post(GOOGLE_DRIVE_API_URL, headers=headers, params=params, data=file.stream)
                response.raise_for_status()
                flash('File uploaded successfully')
            except Exception as e:
                flash(f'Failed to upload file: {e}')
            
            
            os.remove(file_path)
            
            return redirect('/course/' + course_id)
    
    return redirect('/dashboard')

@app.route('/create_assessment/<course_id>')
def create_assessment(course_id):
   
    return redirect('/course/' + course_id)


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)

