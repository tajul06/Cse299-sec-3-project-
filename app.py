from flask import Flask,  jsonify, request , url_for ,  session, redirect
import gspread
from models import Teacher, Course, Student, Question ,Rubric
from oauth2client.service_account import ServiceAccountCredentials
from authlib.integrations.flask_client import OAuth
app = Flask(__name__)
app.secret_key = 'trynothing'

# Initialize OAuth
oauth = OAuth(app)
# OAuth configuration
google = oauth.register(
    name='google',
    client_id='775320630498-127d9mg649fsbpkcn6v2or2b2tcaqk1t.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    redirect_uri='http://localhost:5000/login/callback',  # Adjust this to match your local URI
    client_kwargs={'scope': 'email profile'}
)



# Define index route
@app.route('/')
def index():
    return 'Welcome to my Flask app!'


# OAuth login route
@app.route('/login')
def login():
      
    return google.authorize_redirect(url_for('.authorized', _external=True))

# OAuth callback route
@app.route('/login/callback')
def authorized():
    google=oauth.create_client('google')
    token = google.authorize_access_token()
    if token is None:
        return jsonify({'error': 'Access denied: unable to obtain access token'}), 403

    google_user = oauth.parse_id_token(token)
    if google_user is None or 'email' not in google_user:
        return jsonify({'error': 'Failed to retrieve user information from Google'}), 403

    email = google_user['email']
    teacher = Teacher.query.filter_by(email=email).first()
    if teacher is None:
        teacher = Teacher(email=email)
        teacher.save()  # Assuming you have a method to save teacher to the database

    session['email'] = email
    return redirect(url_for('index'))  # Redirect to the index route or any other route

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


#Define the scope and credentials to access Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds_dev.json', scope)

client = gspread.authorize(creds)
# Define app for teachers
@app.route('/teachers/<teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    teacher = Teacher.find_by_id(teacher_id)
    if teacher:
        return jsonify(teacher), 200
    else:
        return jsonify({'error': 'Teacher not found'}), 404

# Route to create a new course
@app.route('/courses', methods=['POST'])
def create_course():
    data = request.json
    name = data.get('name')
    section = data.get('section')
    description = data.get('description')

    course = Course(name=name, section=section, description=description)
    course.save()  # Assuming you have a method to save the course to the database

    return jsonify({'message': 'Course created successfully', 'course_id': str(course.id)}), 201

# Route to get all courses
@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.get_all()  # Assuming you have a method to retrieve all courses from the database
    return jsonify([course.serialize() for course in courses]), 200

# Route to get a specific course by ID
@app.route('/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.find_by_id(course_id)  # Assuming you have a method to retrieve a course by ID from the database
    if course:
        return jsonify(course.serialize()), 200
    return jsonify({'error': 'Course not found'}), 404

# Route to update a course by ID
@app.route('/courses/<course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.json
    name = data.get('name')
    section = data.get('section')
    description = data.get('description')

    course = Course.find_by_id(course_id)
    if course:
        course.name = name
        course.section = section
        course.description = description
        course.save()  # Update the course in the database
        return jsonify({'message': 'Course updated successfully'}), 200
    return jsonify({'error': 'Course not found'}), 404

# Route to delete a course by ID
@app.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    course = Course.find_by_id(course_id)
    if course:
        course.delete()  # Delete the course from the database
        return jsonify({'message': 'Course deleted successfully'}), 200
    return jsonify({'error': 'Course not found'}), 404

# Define app for students
# Function to extract student data from the Google Sheet link
def extract_students_from_sheet(sheet_link):
    # Open the Google Sheet by its URL
    sheet = client.open_by_url(sheet_link)

    # Select the first worksheet (assuming student data is in the first sheet)
    worksheet = sheet.get_worksheet(0)

    # Get all values from the worksheet
    values = worksheet.get_all_values()

    # Assuming the first row contains headers and student data starts from the second row
    headers = values[0]
    student_data = values[1:]

    # Assuming the student data is organized in columns like 'Name', 'Email', 'Course ID', etc.
    # You need to adjust this based on your actual sheet structure
    students = []
    for row in student_data:
        student = dict(zip(headers, row))
        students.append(student)

    return students

@app.route('/students', methods=['POST'])
def add_students_from_sheet():
    data = request.json  # Assuming the request body contains the Google Sheet link
    sheet_link = data.get('sheet_link')

    # Extract student data from the Google Sheet link
    students = extract_students_from_sheet(sheet_link)

    # Add the extracted student data to the database
    for student_data in students:
        student = Student(**student_data)  # Assuming the Student model constructor accepts keyword arguments
        student.save()  # Assuming the Student model has a save method

    return jsonify({'message': 'Students added successfully'}), 200

@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.find_by_id(student_id)
    if student:
        return jsonify(student), 200
    else:
        return jsonify({'error': 'Student not found'}), 404

def extract_questions_from_sheet(sheet_link):
    # Open the Google Sheet by its URL
    sheet = client.open_by_url(sheet_link)

    # Select the first worksheet (assuming questions data is in the first sheet)
    worksheet = sheet.get_worksheet(0)

    # Get all values from the worksheet
    values = worksheet.get_all_values()

    # Assuming the question data is organized in columns like 'Question No', 'Question Text', 'Marks', etc.
    # You need to adjust this based on your actual sheet structure
    headers = values[0]
    question_data = values[1:]

    questions = []
    for row in question_data:
        # Assuming the columns are in order: Question No, Question Text, Marks
        question = {
            'question_no': row[0],
            'question_text': row[1],
            'marks': row[2]
            # Add more fields if necessary based on your sheet structure
        }
        questions.append(question)

    return questions

# Define app for questions
@app.route('/questions', methods=['POST'])
def add_questions_from_sheet():
    sheet_link = request.json.get('sheet_link')

    if not sheet_link:
        return jsonify({'error': 'Google Sheet link is missing in the request body'}), 400

    # Extract question data from the Google Sheet link
    questions = extract_questions_from_sheet(sheet_link)

    # Add the extracted question data to the database
    for question_data in questions:
        question = Question(**question_data)  # Assuming the Question model constructor accepts keyword arguments
        question.save()  # Assuming the Question model has a save method

    return jsonify({'message': 'Questions added successfully'}), 200


@app.route('/questions/<question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.find_by_id(question_id)
    if question:
        return jsonify(question), 200
    else:
        return jsonify({'error': 'Question not found'}), 404

def extract_rubrics_from_sheet(sheet_link):
    # Open the Google Sheet by its URL
    sheet = client.open_by_url(sheet_link)

    # Select the first worksheet (assuming rubrics data is in the first sheet)
    worksheet = sheet.get_worksheet(0)

    # Get all values from the worksheet
    values = worksheet.get_all_values()

    # Assuming the rubric data is organized in columns like 'Question No', 'Level', 'Criteria', 'Marks', etc.
    headers = values[0]
    rubric_data = values[1:]

    rubrics = []
    for row in rubric_data:
        # Assuming the columns are in order: Question No, Level, Criteria, Marks
        rubric = {
            'question_no': row[0],
            'level': row[1],
            'criteria': row[2],
            'marks': row[3]
            # Add more fields if necessary based on your sheet structure
        }
        rubrics.append(rubric)

    return rubrics

@app.route('/rubrics', methods=['POST'])
def add_rubrics_from_sheet():
    sheet_link = request.json.get('sheet_link')

    if not sheet_link:
        return jsonify({'error': 'Google Sheet link is missing in the request body'}), 400

    # Extract rubric data from the Google Sheet link
    rubrics = extract_rubrics_from_sheet(sheet_link)

    # Add the extracted rubric data to the database
    for rubric_data in rubrics:
        rubric = Rubric(**rubric_data)  # Assuming the Rubric model constructor accepts keyword arguments
        rubric.save()  # Assuming the Rubric model has a save method

    return jsonify({'message': 'Rubrics added successfully'}), 200


# Error handling
@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({'error': str(error)}), 500

if __name__ == "__main__":
    app.run(debug=True)