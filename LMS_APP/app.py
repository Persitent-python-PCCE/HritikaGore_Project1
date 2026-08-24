from flask import Flask, render_template
import os

from config.database import db, init_db
from config.jwt import jwt
from config.logging_config import setup_logging
from models.user import User
from models.course import Course
from models.module import Module
from models.lesson import Lesson
from models.enrollment import Enrollment
from models.material import Material
from models.answer import Answer
from models.option import Option
from models.progress import Progress
from models.question import Question
from models.quiz import Quiz
from models.quiz_submission import QuizSubmission

from dotenv import load_dotenv

from controllers.auth_controller import auth_controller
from controllers.course_controller import course_controller
from controllers.module_controller import module_controller
from controllers.lesson_controller import lesson_controller
from controllers.enrollment_controller import enrollment_controller
from controllers.material_controller import material_controller
from controllers.quiz_controller import quiz_controller
from controllers.question_controller import question_controller
from controllers.admin_controller import admin_controller
from controllers.option_controller import option_controller
from controllers.quiz_attempt_controller import quiz_attempt_controller
from controllers.api import api_v2
from controllers.rag_controller import rag_controller

load_dotenv()

app = Flask(__name__)
setup_logging(app)

app.secret_key = os.getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

jwt.init_app(app)
init_db(app)

if not app.config.get("TESTING"):
    with app.app_context():
        db.create_all()

app.register_blueprint(auth_controller)
app.register_blueprint(course_controller)
app.register_blueprint(module_controller)
app.register_blueprint(lesson_controller)
app.register_blueprint(enrollment_controller)
app.register_blueprint(material_controller)
app.register_blueprint(quiz_controller)
app.register_blueprint(question_controller)
app.register_blueprint(admin_controller)
app.register_blueprint(option_controller)
app.register_blueprint(quiz_attempt_controller)
app.register_blueprint(rag_controller)
app.register_blueprint(api_v2)


@app.errorhandler(403)
def forbidden(error):
    return render_template(
        "error.html",
        error_code=403,
        error_title="Access Denied",
        error_message="You do not have permission to access this page."
    ), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "error.html",
        error_code=404,
        error_title="Page Not Found",
        error_message=(
            "The page or resource you requested could not be found."
        )
    ), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template(
        "error.html",
        error_code=500,
        error_title="Something Went Wrong",
        error_message=(
            "An unexpected error occurred. Please try again."
        )
    ), 500

if __name__ == "__main__":
    app.run(debug=True)