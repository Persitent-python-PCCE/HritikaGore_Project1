from flask import Blueprint, request, redirect, url_for, session, render_template
from dao.option_dao import OptionDAO
from services.option_service import OptionService

from dao.question_dao import QuestionDAO
from services.question_service import QuestionService

from dao.quiz_dao import QuizDAO
from services.quiz_service import QuizService

from dao.lesson_dao import LessonDAO
from services.lesson_service import LessonService

from dao.module_dao import ModuleDAO
from services.module_service import ModuleService

from dao.course_dao import CourseDAO
from services.course_service import CourseService


option_controller = Blueprint("option_controller",__name__)


option_dao = OptionDAO()
option_service = OptionService(option_dao)

question_dao = QuestionDAO()
question_service = QuestionService(question_dao)

quiz_dao = QuizDAO()
quiz_service = QuizService(quiz_dao)

lesson_dao = LessonDAO()
lesson_service = LessonService(lesson_dao)

module_dao = ModuleDAO()
module_service = ModuleService(module_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

@option_controller.route("/questions/<int:question_id>/options", methods=["GET"])
def options(question_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    try:
        question = question_service.get_question(question_id)
        options = option_service.get_question_options(question_id)

        return render_template( "options.html", question=question,options=options)

    except ValueError as e:
        return str(e), 404


@option_controller.route("/questions/<int:question_id>/options/create", methods=["GET", "POST"])
def create_option(question_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access Denied", 403

    try:
        question = question_service.get_question(question_id)

        if request.method == "GET":
            return render_template("create_option.html", question=question)

        quiz = quiz_service.get_quiz(question.quiz_id)
        lesson = lesson_service.get_lesson(quiz.lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)

        if course.instructor_id != session["user_id"]:
            return "Access Denied", 403

        option_text = request.form.get("option_text")

        is_correct = request.form.get("is_correct") == "true"

        option_service.create_option(
            option_text,
            question_id,
            is_correct
        )

        return redirect(url_for("question_controller.questions", quiz_id=question.quiz_id))

    except ValueError as e:
        return str(e), 404


@option_controller.route("/options/edit/<int:option_id>",methods=["GET", "POST"])
def edit_option(option_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access Denied", 403

    try:
        option = option_service.get_option(option_id)
        question = question_service.get_question(option.question_id)

        quiz = quiz_service.get_quiz(question.quiz_id)
        lesson = lesson_service.get_lesson(quiz.lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)

        if course.instructor_id != session["user_id"]:
            return "Access Denied", 403

        if request.method == "GET":
            return render_template(
                "edit_option.html",
                option=option,
                question=question
            )

        option_text = request.form.get("option_text")

        is_correct = (
            request.form.get("is_correct") == "true"
        )

        option_service.update_option(
            option_id,
            option_text,
            is_correct
        )

        return redirect(url_for("quiz_controller.edit_quiz", quiz_id=question.quiz_id))

    except ValueError as e:
        return str(e), 404


@option_controller.route("/options/delete/<int:option_id>", methods=["POST"])
def delete_option(option_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access Denied", 403

    try:
        option = option_service.get_option(option_id)
        question = question_service.get_question(option.question_id)

        quiz = quiz_service.get_quiz( question.quiz_id)
        lesson = lesson_service.get_lesson(quiz.lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)

        if course.instructor_id != session["user_id"]:
            return "Access Denied", 403

        quiz_id = question.quiz_id

        option_service.delete_option(option_id)

        return redirect(url_for( "question_controller.questions",quiz_id=quiz_id))
    
    except ValueError as e:
        return str(e), 404