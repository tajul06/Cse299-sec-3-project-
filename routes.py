from flask import Blueprint, jsonify, request
from models import Teacher, Course, Student, Question

# Create a Blueprint for the routes
routes = Blueprint('routes', __name__)

# Define routes for teachers
@routes.route('/teachers', methods=['POST'])
def create_teacher():
    data = request.json
    if 'name' in data and 'email' in data:
        teacher = Teacher.create(data)
        return jsonify({'message': 'Teacher created successfully', 'teacher_id': str(teacher['_id'])}), 201
    else:
        return jsonify({'error': 'Name and email are required fields'}), 400

@routes.route('/teachers/<teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    teacher = Teacher.find_by_id(teacher_id)
    if teacher:
        return jsonify(teacher), 200
    else:
        return jsonify({'error': 'Teacher not found'}), 404

# Define routes for courses
@routes.route('/courses', methods=['POST'])
def create_course():
    data = request.json
    if 'name' in data and 'teacher_id' in data:
        course = Course.create(data)
        return jsonify({'message': 'Course created successfully', 'course_id': str(course['_id'])}), 201
    else:
        return jsonify({'error': 'Name and teacher_id are required fields'}), 400

@routes.route('/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.find_by_id(course_id)
    if course:
        return jsonify(course), 200
    else:
        return jsonify({'error': 'Course not found'}), 404

# Define routes for students
@routes.route('/students', methods=['POST'])
def create_student():
    data = request.json
    if 'name' in data and 'email' in data:
        student = Student.create(data)
        return jsonify({'message': 'Student created successfully', 'student_id': str(student['_id'])}), 201
    else:
        return jsonify({'error': 'Name and email are required fields'}), 400

@routes.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.find_by_id(student_id)
    if student:
        return jsonify(student), 200
    else:
        return jsonify({'error': 'Student not found'}), 404

# Define routes for questions
@routes.route('/questions', methods=['POST'])
def create_question():
    data = request.json
    if 'text' in data:
        question = Question.create(data)
        return jsonify({'message': 'Question created successfully', 'question_id': str(question['_id'])}), 201
    else:
        return jsonify({'error': 'Text is a required field'}), 400

@routes.route('/questions/<question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.find_by_id(question_id)
    if question:
        return jsonify(question), 200
    else:
        return jsonify({'error': 'Question not found'}), 404

# Add more routes for other resources as needed

