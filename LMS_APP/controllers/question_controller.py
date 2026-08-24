from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from dao.question_dao import QuestionDAO
from services.question_service import QuestionService

from dao.option_dao import OptionDAO
from services.option_service import OptionService

from dao.quiz_dao import QuizDAO
from services.quiz_service import QuizService

from dao.lesson_dao import LessonDAO
from services.lesson_service import LessonService

from dao.module_dao import ModuleDAO
from services.module_service import ModuleService

from dao.course_dao import CourseDAO
from services.course_service import CourseService

question_controller = Blueprint( "question_controller", __name__)

question_dao = QuestionDAO()
question_service = QuestionService(question_dao)

option_dao = OptionDAO()
option_service = OptionService(option_dao)

quiz_dao = QuizDAO()
quiz_service = QuizService(quiz_dao)

lesson_dao = LessonDAO()
lesson_service = LessonService(lesson_dao)

module_dao = ModuleDAO()
module_service = ModuleService(module_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

@question_controller.route("/quizzes/<int:quiz_id>/questions")
def questions(quiz_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    try:
        quiz = quiz_service.get_quiz(quiz_id)

        questions = question_service.get_quiz_questions( quiz_id)

        question_options = {}

        for question in questions:
            question_options[question.id] = (
                option_service.get_question_options(
                    question.id
                )
            )

        return render_template(
            "questions.html",
            quiz=quiz,
            questions=questions,
            question_options=question_options
        )

    except ValueError as e:
        return str(e), 404

@question_controller.route("/quizzes/<int:quiz_id>/questions/create",methods=["GET", "POST"])
def create_question(quiz_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access Denied", 403

    try:
        quiz = quiz_service.get_quiz(quiz_id)
        lesson = lesson_service.get_lesson(quiz.lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)

        if course.instructor_id != session["user_id"]:
            return "Access Denied", 403

        if request.method == "GET":
            return render_template("create_question.html",quiz=quiz)

        question_text = request.form.get("question_text")
        explanation = request.form.get("explanation")
        difficulty = request.form.get("difficulty")

        question_service.create_question(
            question_text,
            difficulty,
            explanation,
            quiz_id
        )

        return redirect(url_for("question_controller.questions",quiz_id=quiz_id))

    except ValueError as e:
        return render_template(
            "create_question.html",
            quiz=quiz,
            error=str(e)
        )

@question_controller.route("/questions/delete/<int:question_id>",methods=["POST"])
def delete_question(question_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access Denied", 403

    try:
        question = question_service.get_question( question_id)
        quiz = quiz_service.get_quiz( question.quiz_id)

        lesson = lesson_service.get_lesson( quiz.lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)

        if course.instructor_id != session["user_id"]:
            return "Access Denied", 403

        quiz_id = question.quiz_id

        question_service.delete_question(question_id)

        return redirect(url_for("question_controller.questions",quiz_id=quiz_id))

    except ValueError as e:
        return str(e), 404

@question_controller.route( "/questions/edit/<int:question_id>",  methods=["GET", "POST"])
def edit_question(question_id):
    if "user_id" not in session:
        return redirect( url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access Denied", 403

    try:
        question = question_service.get_question(question_id)
        quiz = quiz_service.get_quiz( question.quiz_id)

        lesson = lesson_service.get_lesson(quiz.lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)


        if course.instructor_id != session["user_id"]:
            return "Access Denied", 403

        if request.method == "GET":
            return render_template(
                "edit_question.html",
                question=question,
                quiz=quiz
            )

        question_text = request.form.get( "question_text")

        explanation = request.form.get("explanation")

        difficulty = request.form.get("difficulty")

        question_service.update_question(
            question_id,
            question_text,
            difficulty,
            explanation
        )

        return redirect(url_for( "question_controller.questions", quiz_id=question.quiz_id))

    except ValueError as e:
        return render_template(
            "edit_question.html",
            question=question,
            quiz=quiz,
            error=str(e)
        )