from pymongo import MongoClient
from bson.objectid import ObjectId

class MongoModel:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://tajulislam06:trynothing@cluster0.x3lpi33.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.db = self.client['LLM_Marking']

class Serializable:
    def serialize(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)
    
class Teacher(MongoModel, Serializable):
    def __init__(self, name, email):
        super().__init__()
        self.collection = self.db['teachers']
        self.name = name
        self.email = email

    def save(self):
        teacher_data = {'name': self.name, 'email': self.email}
        result = self.collection.insert_one(teacher_data)
        return result.inserted_id

    @classmethod
    def find_by_email(cls, email):
        teacher_data = cls.collection.find_one({'email': email})
        if teacher_data:
            return cls(teacher_data['name'], teacher_data['email'])
        return None

    @staticmethod
    def get_all():
        return [Teacher.deserialize(teacher) for teacher in Teacher.collection.find()]

class Course(MongoModel, Serializable):
    def __init__(self, name,section,description, teacher_id):
        super().__init__()
        self.collection = self.db['courses']
        self.name = name
        self.teacher_id = teacher_id
        self.section =section
        self.description =description

    def save(self):
        course_data = {'name': self.name,'section': self.section, 'description':self.description, 'teacher_id': self.teacher_id}
        result = self.collection.insert_one(course_data)
        return result.inserted_id

    @classmethod
    def find_by_id(cls, course_id):
        course_data = cls.collection.find_one({'_id': ObjectId(course_id)})
        if course_data:
            return cls(course_data['name'], course_data['teacher_id'] ,course_data['section'],course_data['section'])
        return None
    
    @staticmethod
    def get_all():
        return [Course.deserialize(course) for course in Course.collection.find()]

class Student(MongoModel, Serializable):
    def __init__(self, name, email, course_id):
        super().__init__()
        self.collection = self.db['students']
        self.name = name
        self.email = email
        self.course_id = course_id

    def save(self):
        student_data = {'name': self.name, 'email': self.email, 'course_id': self.course_id}
        result = self.collection.insert_one(student_data)
        return result.inserted_id

    @classmethod
    def find_by_id(cls, student_id):
        student_data = cls.collection.find_one({'_id': ObjectId(student_id)})
        if student_data:
            return cls(student_data['name'], student_data['email'], student_data['course_id'])
        return None

    @staticmethod
    def get_all():
        return [Student.deserialize(student) for student in Student.collection.find()]

class Assessment(MongoModel,Serializable):
    def __init__(self, title, description, total_marks, deadline, course_id):
        super().__init__()
        self.collection = self.db['assessments']
        self.title = title
        self.description = description
        self.total_marks = total_marks
        self.deadline = deadline
        self.course_id = course_id

    def save(self):
        assessment_data = {
            'title': self.title,
            'description': self.description,
            'total_marks': self.total_marks,
            'deadline': self.deadline,
            'course_id': self.course_id
        }
        result = self.collection.insert_one(assessment_data)
        return result.inserted_id

    @classmethod
    def find_by_id(cls, assessment_id):
        assessment_data = cls.collection.find_one({'_id': ObjectId(assessment_id)})
        if assessment_data:
            return cls(
                assessment_data['title'],
                assessment_data['description'],
                assessment_data['total_marks'],
                assessment_data['deadline'],
                assessment_data['course_id']
            )
        return None     

    @staticmethod
    def get_all():
        assessments_data = Assessment.collection.find({})
        return [Assessment.deserialize(assessment) for assessment in assessments_data]

class Question(MongoModel ,Serializable):
    def __init__(self, qs_no ,text,marks, assessment_id):
        super().__init__()
        self.collection = self.db['questions']
        self.qs_no = qs_no
        self.text = text
        self.marks = marks
        self.assessment_id = assessment_id

    def save(self):
        question_data = {'qs_no': self.qs_no,'text': self.text, 'marks': self.marks,'assessment_id': self.assessment_id}
        result = self.collection.insert_one(question_data)
        return result.inserted_id

    @classmethod
    def find_by_id(cls, question_id):
        question_data = cls.collection.find_one({'_id': ObjectId(question_id)})
        if question_data:
            return cls(question_data['qs_no'],question_data['text'], question_data['marks'], question_data['assessment_id'])
        return None

    @staticmethod
    def get_all():
        return [Question.deserialize(question) for question in Question.collection.find()]

class Rubric(MongoModel, Serializable):
    def __init__(self, question_id, level, criteria, marks):
        super().__init__()
        self.collection = self.db['rubrics']
        self.question_id = question_id
        self.level = level
        self.criteria = criteria
        self.marks = marks

    def save(self):
        rubric_data = {
            'question_id': self.question_id,
            'level': self.level,
            'criteria': self.criteria,
            'marks': self.marks
        }
        result = self.collection.insert_one(rubric_data)
        return result.inserted_id

    @classmethod
    def find_by_id(cls, rubric_id):
        rubric_data = cls.collection.find_one({'_id': ObjectId(rubric_id)})
        if rubric_data:
            return cls(
                rubric_data['question_id'],
                rubric_data['level'],
                rubric_data['criteria'],
                rubric_data['marks']
            )
        return None

    @staticmethod
    def get_all():
        return [Rubric.deserialize(rubric) for rubric in Rubric.collection.find()]

class Answer(MongoModel, Serializable):
    def __init__(self, student_id, question_id, text):
        super().__init__()
        self.collection = self.db['answers']
        self.student_id = student_id
        self.question_id = question_id
        self.text = text

    def save(self):
        answer_data = {'student_id': self.student_id, 'question_id': self.question_id, 'text': self.text}
        result = self.collection.insert_one(answer_data)
        return result.inserted_id

    @classmethod
    def find_by_id(cls, answer_id):
        answer_data = cls.collection.find_one({'_id': ObjectId(answer_id)})
        if answer_data:
            return cls(
                answer_data['student_id'],
                answer_data['question_id'],
                answer_data['text']
            )
        return None
    
    @staticmethod
    def get_all():
        return [Answer.deserialize(answer) for answer in Answer.collection.find()]    