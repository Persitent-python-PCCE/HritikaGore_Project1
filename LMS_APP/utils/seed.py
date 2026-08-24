from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import app
from config.database import db

from models.user import User
from models.course import Course
from models.module import Module
from models.lesson import Lesson
from models.enrollment import Enrollment
from models.quiz import Quiz
from models.question import Question
from models.option import Option
from models.progress import Progress
from models.quiz_submission import QuizSubmission
from models.answer import Answer


def get_or_create_user(name, email, password, role):
    user = User.query.filter_by(email=email).first()

    if user:
        print(f"Already exists: {email}")
        return user

    user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        role=role,
        is_active=True
    )

    db.session.add(user)
    db.session.flush()

    print(f"Created user: {email}")
    return user


def get_or_create_course(title, description, instructor_id):
    course = Course.query.filter_by(title=title).first()

    if course:
        return course

    course = Course(
        title=title,
        description=description,
        instructor_id=instructor_id
    )

    db.session.add(course)
    db.session.flush()

    print(f"Created course: {title}")
    return course


def get_or_create_module(title, description, course_id):
    module = Module.query.filter_by(
        title=title,
        course_id=course_id
    ).first()

    if module:
        return module

    module = Module(
        title=title,
        description=description,
        course_id=course_id
    )

    db.session.add(module)
    db.session.flush()

    return module


def get_or_create_lesson(title, content, module_id):
    lesson = Lesson.query.filter_by(
        title=title,
        module_id=module_id
    ).first()

    if lesson:
        return lesson

    lesson = Lesson(
        title=title,
        content=content,
        module_id=module_id
    )

    db.session.add(lesson)
    db.session.flush()

    return lesson


def enroll_student(student_id, course_id):
    enrollment = Enrollment.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()

    if enrollment:
        return enrollment

    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id,
        status="active"
    )

    db.session.add(enrollment)
    db.session.flush()

    return enrollment




def create_quiz(title, description, lesson_id, created_by):

    quiz = Quiz.query.filter_by(
        title=title,
        lesson_id=lesson_id
    ).first()

    if quiz:
        return quiz

    quiz = Quiz(
        title=title,
        description=description,
        lesson_id=lesson_id,
        created_by=created_by
    )

    db.session.add(quiz)
    db.session.flush()

    return quiz


def create_question(quiz_id, question_text,
                    correct_answer,
                    wrong_answers):

    question = Question.query.filter_by(
        quiz_id=quiz_id,
        question_text=question_text
    ).first()

    if question:
        return question

    question = Question(
        quiz_id=quiz_id,
        question_text=question_text,
        difficulty="medium"
    )

    db.session.add(question)
    db.session.flush()

    answers = [correct_answer] + wrong_answers

    for index, text in enumerate(answers):

        option = Option(
            question_id=question.id,
            option_text=text,
            is_correct=(index == 0)
        )

        db.session.add(option)

    db.session.flush()

    return question


def complete_lesson(student_id, lesson_id):

    progress = Progress.query.filter_by(
        student_id=student_id,
        lesson_id=lesson_id
    ).first()

    if progress:
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        return progress

    progress = Progress(
        student_id=student_id,
        lesson_id=lesson_id,
        completed=True,
        completed_at=datetime.utcnow()
    )

    db.session.add(progress)
    db.session.flush()

    return progress


def create_quiz_submission(student, quiz, score, answers):

    submission = QuizSubmission(
        quiz_id=quiz.id,
        student_id=student.id,
        score=score,
        submitted_at=datetime.utcnow()
    )

    db.session.add(submission)
    db.session.flush()

    for question, selected_option in answers:

        answer = Answer(
            submission_id=submission.id,
            question_id=question.id,
            selected_option_id=selected_option.id
        )

        db.session.add(answer)

    db.session.flush()

    return submission


with app.app_context():

    print("\n==============================")
    print(" LMS COMPLETE SEED")
    print("==============================\n")

    # =========================================================
    # USERS
    # =========================================================

    admin = get_or_create_user(
        "System Admin",
        "admin@lms.com",
        "Admin@123",
        "admin"
    )

    instructors = []

    instructors.append(
        get_or_create_user(
            "Sneha Joshi",
            "sneha@instructor.com",
            "Instructor@123",
            "instructor"
        )
    )

    instructors.append(
        get_or_create_user(
            "Vikram Deshmukh",
            "vikram@instructor.com",
            "Instructor@123",
            "instructor"
        )
    )

    instructors.append(
        get_or_create_user(
            "Neha Kulkarni",
            "neha@instructor.com",
            "Instructor@123",
            "instructor"
        )
    )

    students = []

    student_data = [
        ("Rahul Sharma", "rahul@student.com"),
        ("Priya Patil", "priya@student.com"),
        ("Amit Kulkarni", "amit@student.com"),
        ("Sneha Shah", "sneha.student@student.com"),
        ("Rohan Mehta", "rohan@student.com"),
        ("Ananya Desai", "ananya@student.com"),
        ("Karan Joshi", "karan@student.com"),
        ("Pooja More", "pooja@student.com"),
    ]

    for name, email in student_data:

        students.append(
            get_or_create_user(
                name,
                email,
                "Student@123",
                "student"
            )
        )

    # =========================================================
    # COURSES
    # =========================================================

    course_data = [

        (
            "Python Programming",
            "Complete Python programming course from beginner to advanced.",
            instructors[0]
        ),

        (
            "Web Development with Flask",
            "Build modern web applications using Python and Flask.",
            instructors[0]
        ),

        (
            "SQL and Database Management",
            "Learn SQL, relational databases, MySQL and database design.",
            instructors[1]
        ),

        (
            "HTML and CSS",
            "Learn the fundamentals of modern HTML and CSS.",
            instructors[2]
        ),

        (
            "Data Analysis with Python",
            "Learn NumPy, Pandas, visualization and practical data analysis.",
            instructors[2]
        )

    ]

    courses = []

    for title, description, instructor in course_data:

        courses.append(
            get_or_create_course(
                title,
                description,
                instructor.id
            )
        )

    # =========================================================
    # PYTHON COURSE
    # =========================================================

    python_course = courses[0]

    python_modules = []

    python_modules.append(
        get_or_create_module(
            "Python Basics",
            "Variables, data types and basic Python syntax.",
            python_course.id
        )
    )

    python_modules.append(
        get_or_create_module(
            "Control Flow",
            "Conditions and loops in Python.",
            python_course.id
        )
    )

    python_modules.append(
        get_or_create_module(
            "Functions",
            "Functions, parameters and return values.",
            python_course.id
        )
    )

    python_modules.append(
        get_or_create_module(
            "Object Oriented Programming",
            "Classes, objects, inheritance and encapsulation.",
            python_course.id
        )
    )

    python_lessons = []

    python_lessons.append(
        get_or_create_lesson(
            "Variables and Data Types",
            """
Python variables store values.

Common data types include:
int
float
str
bool
list
tuple
set
dict

Example:

name = "Rahul"
age = 22
            """,
            python_modules[0].id
        )
    )

    python_lessons.append(
        get_or_create_lesson(
            "Python Operators",
            """
Python supports arithmetic, comparison,
logical and assignment operators.

Example:

a = 10
b = 5

print(a + b)
print(a > b)
            """,
            python_modules[0].id
        )
    )

    python_lessons.append(
        get_or_create_lesson(
            "If Else Statements",
            """
Conditional statements allow a program
to make decisions.

Example:

age = 18

if age >= 18:
    print("Adult")
else:
    print("Minor")
            """,
            python_modules[1].id
        )
    )

    python_lessons.append(
        get_or_create_lesson(
            "Loops",
            """
Python provides for and while loops.

Example:

for i in range(5):
    print(i)
            """,
            python_modules[1].id
        )
    )

    python_lessons.append(
        get_or_create_lesson(
            "Functions",
            """
Functions allow reusable blocks of code.

Example:

def add(a, b):
    return a + b
            """,
            python_modules[2].id
        )
    )

    python_lessons.append(
        get_or_create_lesson(
            "Classes and Objects",
            """
Classes define objects and their behavior.

Example:

class Student:
    def __init__(self, name):
        self.name = name
            """,
            python_modules[3].id
        )
    )

    # =========================================================
    # FLASK COURSE
    # =========================================================

    flask_course = courses[1]

    flask_modules = [
        get_or_create_module(
            "Flask Fundamentals",
            "Introduction to Flask.",
            flask_course.id
        ),

        get_or_create_module(
            "Routing",
            "Flask routes and URL parameters.",
            flask_course.id
        ),

        get_or_create_module(
            "Templates",
            "Jinja2 templates and template inheritance.",
            flask_course.id
        ),

        get_or_create_module(
            "Database Integration",
            "SQLAlchemy and Flask database integration.",
            flask_course.id
        )
    ]

    flask_lessons = [

        get_or_create_lesson(
            "Creating a Flask Application",
            "Learn how to create and configure a Flask application.",
            flask_modules[0].id
        ),

        get_or_create_lesson(
            "Flask Routes",
            "Learn GET and POST routes and URL parameters.",
            flask_modules[1].id
        ),

        get_or_create_lesson(
            "Jinja2 Templates",
            "Learn how to render dynamic HTML using Jinja2.",
            flask_modules[2].id
        ),

        get_or_create_lesson(
            "SQLAlchemy Models",
            "Learn how to create database models using SQLAlchemy.",
            flask_modules[3].id
        )
    ]

    # =========================================================
    # SQL COURSE
    # =========================================================

    sql_course = courses[2]

    sql_modules = [
        get_or_create_module(
            "SQL Basics",
            "SELECT, INSERT, UPDATE and DELETE.",
            sql_course.id
        ),

        get_or_create_module(
            "Filtering and Sorting",
            "WHERE, ORDER BY and LIMIT.",
            sql_course.id
        ),

        get_or_create_module(
            "Joins",
            "INNER JOIN, LEFT JOIN and RIGHT JOIN.",
            sql_course.id
        ),

        get_or_create_module(
            "Database Design",
            "Keys, relationships and normalization.",
            sql_course.id
        )
    ]

    sql_lessons = [

        get_or_create_lesson(
            "SELECT Queries",
            "Learn how to retrieve records from SQL tables.",
            sql_modules[0].id
        ),

        get_or_create_lesson(
            "INSERT UPDATE DELETE",
            "Learn how to modify database records.",
            sql_modules[0].id
        ),

        get_or_create_lesson(
            "WHERE Clause",
            "Filter records using conditions.",
            sql_modules[1].id
        ),

        get_or_create_lesson(
            "SQL Joins",
            "Combine information from multiple tables.",
            sql_modules[2].id
        ),

        get_or_create_lesson(
            "Primary and Foreign Keys",
            "Understand relational database keys.",
            sql_modules[3].id
        )
    ]

    # =========================================================
    # HTML / CSS COURSE
    # =========================================================

    web_course = courses[3]

    web_modules = [
        get_or_create_module(
            "HTML Basics",
            "HTML structure and elements.",
            web_course.id
        ),

        get_or_create_module(
            "Forms",
            "HTML forms and inputs.",
            web_course.id
        ),

        get_or_create_module(
            "CSS Basics",
            "Selectors and styling.",
            web_course.id
        )
    ]

    web_lessons = [

        get_or_create_lesson(
            "HTML Document Structure",
            "DOCTYPE, html, head and body elements.",
            web_modules[0].id
        ),

        get_or_create_lesson(
            "HTML Forms",
            "Build forms using input, select and button.",
            web_modules[1].id
        ),

        get_or_create_lesson(
            "CSS Selectors",
            "Learn element, class and ID selectors.",
            web_modules[2].id
        ),

        get_or_create_lesson(
            "CSS Box Model",
            "Understand margin, border, padding and content.",
            web_modules[2].id
        )
    ]

    # =========================================================
    # DATA ANALYSIS COURSE
    # =========================================================

    data_course = courses[4]

    data_modules = [
        get_or_create_module(
            "NumPy",
            "Numerical computing using NumPy.",
            data_course.id
        ),

        get_or_create_module(
            "Pandas",
            "Data manipulation using Pandas.",
            data_course.id
        ),

        get_or_create_module(
            "Visualization",
            "Create charts and graphs.",
            data_course.id
        )
    ]

    data_lessons = [

        get_or_create_lesson(
            "NumPy Arrays",
            "Introduction to NumPy arrays.",
            data_modules[0].id
        ),

        get_or_create_lesson(
            "Pandas DataFrames",
            "Create and manipulate DataFrames.",
            data_modules[1].id
        ),

        get_or_create_lesson(
            "Reading CSV Files",
            "Load CSV data using Pandas.",
            data_modules[1].id
        ),

        get_or_create_lesson(
            "Data Visualization",
            "Create charts using Matplotlib.",
            data_modules[2].id
        )
    ]

    # =========================================================
    # ENROLLMENTS
    # =========================================================

    # Rahul - all courses
    for course in courses:
        enroll_student(students[0].id, course.id)

    # Priya - Python, Flask, SQL
    for course in courses[:3]:
        enroll_student(students[1].id, course.id)

    # Amit - Python and Data Analysis
    enroll_student(students[2].id, python_course.id)
    enroll_student(students[2].id, data_course.id)

    # Sneha - Flask and HTML
    enroll_student(students[3].id, flask_course.id)
    enroll_student(students[3].id, web_course.id)

    # Rohan - Python and SQL
    enroll_student(students[4].id, python_course.id)
    enroll_student(students[4].id, sql_course.id)

    # Ananya - HTML and Data Analysis
    enroll_student(students[5].id, web_course.id)
    enroll_student(students[5].id, data_course.id)

    # Karan - Flask
    enroll_student(students[6].id, flask_course.id)

    # Pooja - Python
    enroll_student(students[7].id, python_course.id)

   
    # =========================================================
    # PYTHON QUIZ
    # =========================================================

    python_quiz = create_quiz(
        "Python Basics Quiz",
        "Test your understanding of Python fundamentals.",
        python_lessons[0].id,
        instructors[0].id
    )

    q1 = create_question(
        python_quiz.id,
        "Which keyword is used to define a function in Python?",
        "def",
        ["function", "func", "define"]
    )

    q2 = create_question(
        python_quiz.id,
        "Which data type stores True or False?",
        "bool",
        ["int", "str", "float"]
    )

    q3 = create_question(
        python_quiz.id,
        "Which symbol is used for comments in Python?",
        "#",
        ["//", "/*", "--"]
    )

    q4 = create_question(
        python_quiz.id,
        "Which collection stores key-value pairs?",
        "dictionary",
        ["list", "tuple", "set"]
    )

    # =========================================================
    # FLASK QUIZ
    # =========================================================

    flask_quiz = create_quiz(
        "Flask Fundamentals Quiz",
        "Test your Flask fundamentals.",
        flask_lessons[0].id,
        instructors[0].id
    )

    fq1 = create_question(
        flask_quiz.id,
        "Which library is used to create Flask applications?",
        "Flask",
        ["Django", "FastAPI", "Pyramid"]
    )

    fq2 = create_question(
        flask_quiz.id,
        "Which decorator creates a Flask route?",
        "@app.route",
        ["@route", "@flask.url", "@path"]
    )

    fq3 = create_question(
        flask_quiz.id,
        "Which template engine does Flask use?",
        "Jinja2",
        ["React", "Angular", "Twig"]
    )

    # =========================================================
    # SQL QUIZ
    # =========================================================

    sql_quiz = create_quiz(
        "SQL Basics Quiz",
        "Test your SQL knowledge.",
        sql_lessons[0].id,
        instructors[1].id
    )

    sq1 = create_question(
        sql_quiz.id,
        "Which command retrieves data from a table?",
        "SELECT",
        ["GET", "FETCH", "READ"]
    )

    sq2 = create_question(
        sql_quiz.id,
        "Which command adds a new record?",
        "INSERT",
        ["ADD", "CREATE", "APPEND"]
    )

    sq3 = create_question(
        sql_quiz.id,
        "Which clause filters records?",
        "WHERE",
        ["FILTER", "HAVING ONLY", "IF"]
    )

    # =========================================================
    # HTML QUIZ
    # =========================================================

    html_quiz = create_quiz(
        "HTML Basics Quiz",
        "Test your HTML knowledge.",
        web_lessons[0].id,
        instructors[2].id
    )

    hq1 = create_question(
        html_quiz.id,
        "Which tag creates a paragraph?",
        "<p>",
        ["<paragraph>", "<text>", "<para>"]
    )

    hq2 = create_question(
        html_quiz.id,
        "Which tag creates a hyperlink?",
        "<a>",
        ["<link>", "<href>", "<url>"]
    )

    # =========================================================
    # PROGRESS
    # =========================================================

    # Rahul completed first 4 Python lessons
    for lesson in python_lessons[:4]:
        complete_lesson(
            students[0].id,
            lesson.id
        )

    # Rahul completed Flask lessons
    for lesson in flask_lessons[:3]:
        complete_lesson(
            students[0].id,
            lesson.id
        )

    # Priya completed first 3 Python lessons
    for lesson in python_lessons[:3]:
        complete_lesson(
            students[1].id,
            lesson.id
        )

    # Amit completed Python basics
    for lesson in python_lessons[:2]:
        complete_lesson(
            students[2].id,
            lesson.id
        )

    # Rohan completed first Python lesson
    complete_lesson(
        students[4].id,
        python_lessons[0].id
    )

    # =========================================================
    # QUIZ SUBMISSIONS
    # =========================================================

    # Rahul - Python quiz - 4/4
    python_options = {
        q.id: Option.query.filter_by(
            question_id=q.id,
            is_correct=True
        ).first()
        for q in [q1, q2, q3, q4]
    }

    create_quiz_submission(
        students[0],
        python_quiz,
        4,
        [
            (q1, python_options[q1.id]),
            (q2, python_options[q2.id]),
            (q3, python_options[q3.id]),
            (q4, python_options[q4.id])
        ]
    )

    # Priya - Python quiz - 3/4
    q2_wrong = Option.query.filter(
        Option.question_id == q2.id,
        Option.is_correct == False
    ).first()

    create_quiz_submission(
        students[1],
        python_quiz,
        3,
        [
            (q1, python_options[q1.id]),
            (q2, q2_wrong),
            (q3, python_options[q3.id]),
            (q4, python_options[q4.id])
        ]
    )

    # Rahul - Flask quiz - 3/3
    flask_options = {
        q.id: Option.query.filter_by(
            question_id=q.id,
            is_correct=True
        ).first()
        for q in [fq1, fq2, fq3]
    }

    create_quiz_submission(
        students[0],
        flask_quiz,
        3,
        [
            (fq1, flask_options[fq1.id]),
            (fq2, flask_options[fq2.id]),
            (fq3, flask_options[fq3.id])
        ]
    )

    # Rahul - SQL quiz - 2/3
    sql_options = {
        q.id: Option.query.filter_by(
            question_id=q.id,
            is_correct=True
        ).first()
        for q in [sq1, sq2, sq3]
    }

    sq3_wrong = Option.query.filter(
        Option.question_id == sq3.id,
        Option.is_correct == False
    ).first()

    create_quiz_submission(
        students[0],
        sql_quiz,
        2,
        [
            (sq1, sql_options[sq1.id]),
            (sq2, sql_options[sq2.id]),
            (sq3, sq3_wrong)
        ]
    )

    # =========================================================
    # COMMIT
    # =========================================================

    db.session.commit()

    print("\n======================================")
    print(" COMPLETE LMS SEED FINISHED")
    print("======================================")

    print("\nUsers:")
    print("Admin:")
    print("  admin@lms.com / Admin@123")

    print("\nInstructors:")
    print("  sneha@instructor.com / Instructor@123")
    print("  vikram@instructor.com / Instructor@123")
    print("  neha@instructor.com / Instructor@123")

    print("\nStudents:")
    print("  rahul@student.com / Student@123")
    print("  priya@student.com / Student@123")
    print("  amit@student.com / Student@123")
    print("  sneha.student@student.com / Student@123")
    print("  rohan@student.com / Student@123")
    print("  ananya@student.com / Student@123")
    print("  karan@student.com / Student@123")
    print("  pooja@student.com / Student@123")

    print("\nCourses created:")
    for course in courses:
        print(f"  - {course.title}")

    print("\nSeed complete.")