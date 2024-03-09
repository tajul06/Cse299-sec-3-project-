from pymongo import MongoClient
from bson import ObjectId

class Database:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client.get_database()

class Teacher:
    def __init__(self, database):
        self.collection = database.teachers_collection

    def create(self, teacher_data):
        return self.collection.insert_one(teacher_data)

    def find_by_id(self, teacher_id):
        return self.collection.find_one({'_id': ObjectId(teacher_id)})

    # Add other methods as needed

class Course:
    def __init__(self, database):
        self.collection = database.courses_collection

    def create(self, course_data):
        return self.collection.insert_one(course_data)

    def find_by_id(self, course_id):
        return self.collection.find_one({'_id': ObjectId(course_id)})
    
    def update(self, teacher_id, update_data):
        return self.collection.update_one({'_id': ObjectId(teacher_id)}, {'$set': update_data})

    def delete(self, teacher_id):
        return self.collection.delete_one({'_id': ObjectId(teacher_id)})

    # Add other methods as needed

class Student:
    def __init__(self, database):
        self.collection = database.students_collection

    def create(self, student_data):
        return self.collection.insert_one(student_data)

    def find_by_id(self, student_id):
        return self.collection.find_one({'_id': ObjectId(student_id)})

    # Add other methods as needed

class Question:
    def __init__(self, database):
        self.collection = database.questions_collection

    def create(self, question_data):
        return self.collection.insert_one(question_data)

    def find_by_id(self, question_id):
        return self.collection.find_one({'_id': ObjectId(question_id)})

    # Add other methods as needed

class FormLink:
    def __init__(self, database):
        self.collection = database.form_links_collection

    def create(self, form_link_data):
        return self.collection.insert_one(form_link_data)

    def find_by_id(self, form_link_id):
        return self.collection.find_one({'_id': ObjectId(form_link_id)})

    # Add other methods as needed

class Rubric:
    def __init__(self, database):
        self.collection = database.rubrics_collection

    def create(self, rubric_data):
        return self.collection.insert_one(rubric_data)

    def find_by_id(self, rubric_id):
        return self.collection.find_one({'_id': ObjectId(rubric_id)})