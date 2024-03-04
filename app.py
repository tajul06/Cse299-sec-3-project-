import os
import re
from flask import Flask, flash, request ,url_for, redirect ,session , render_template

from google.oauth2.credentials import Credentials

from googleapiclient.discovery import build

import pandas as pd

import gspread

from oauth2client.service_account import ServiceAccountCredentials



from authlib.integrations.flask_client import OAuth

from pymongo import MongoClient

from bson import ObjectId

import requests
import gspread

import re


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



def extract_google_sheets_key(google_sheets_link):
    pattern = re.compile(r'^https?://docs.google.com/spreadsheets/d/([a-zA-Z0-9-_]+)')
    match = pattern.match(google_sheets_link)
    if match:
        return match.group(1)
    else:
        return None
    
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






@app.route('/course/<course_id>', methods=['GET', 'POST'])
def course_dashboard(course_id):
    email = dict(session).get('email', None)
    if email:
        if request.method == 'GET':
            course = courses_collection.find_one({'_id': ObjectId(course_id)})
            if course:
                return render_template('course_dashboard.html', email=email, course=course)
        elif request.method == 'POST':
            google_sheets_link = request.form.get('google_sheets_link')
            if not google_sheets_link:
                flash('Please provide a valid Google Sheets link')
                return redirect(request.url)
            sheets_key = extract_google_sheets_key(google_sheets_link)
            if not sheets_key:
                flash('Please provide a valid Google Sheets link')
                return redirect(request.url)
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
            client = gspread.authorize(credentials)
            try:
                doc = client.open_by_key(sheets_key)
                worksheet = doc.sheet1
                data = worksheet.get_all_values()
                students_data = []
                for row in data:
                    name, student_id, student_email = row
                    students_data.append({'name': name, 'student_id': student_id, 'email': student_email})
                students_collection.insert_many(students_data)
                flash('Students uploaded successfully')
                return redirect('/course/' + course_id)
            except Exception as e:
                flash('An error occurred while processing the Google Sheets data: {}'.format(str(e)))
                return redirect(request.url)
    return redirect('/dashboard')

@app.route('/students/<course_id>')
def get_students(course_id):
    email = dict(session).get('email', None)
    if email:
        course = courses_collection.find_one({'_id': ObjectId(course_id)})
        if course:
            students = students_collection.find({'course_id': ObjectId(course_id)})
            return render_template('students_list.html', email=email, course=course, students=students)
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

