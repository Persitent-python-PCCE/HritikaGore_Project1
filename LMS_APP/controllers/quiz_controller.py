from flask import Blueprint,render_template, request,redirect,url_for,session, abort
from dao.quiz_dao import QuizDAO
from services.quiz_service import QuizService
from dao.lesson_dao import LessonDAO
from services.lesson_service import LessonService
from dao.module_dao import ModuleDAO
from services.module_service import ModuleService
from dao.course_dao import CourseDAO
from services.course_service import CourseService
from dao.question_dao import QuestionDAO
from services.question_service import QuestionService
from dao.option_dao import OptionDAO
from services.option_service import OptionService

quiz_controller = Blueprint("quiz_controller", __name__)

quiz_dao = QuizDAO()
quiz_service = QuizService(quiz_dao)

lesson_dao = LessonDAO()
lesson_service = LessonService(lesson_dao)

module_dao = ModuleDAO()
module_service = ModuleService(module_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

question_dao = QuestionDAO()
question_service = QuestionService(question_dao)
option_dao = OptionDAO() 
option_service = OptionService(option_dao)

@quiz_controller.route("/lessons/<int:lesson_id>/quizzes")
def quizzes(lesson_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    try:
        lesson = lesson_service.get_lesson(lesson_id)
        quizzes = quiz_service.get_lesson_quizzes(lesson_id)

        return render_template(
            "quizzes.html",
            lesson=lesson,
            quizzes=quizzes
        )

    except ValueError as e:
        return str(e), 404

@quiz_controller.route("/lessons/<int:lesson_id>/quizzes/create",methods=["GET", "POST"])
def create_quiz(lesson_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))
    
    if session.get("user_role") != "instructor":
        abort(403)
    
    try:
        lesson = lesson_service.get_lesson(lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)


        if course.instructor_id != session["user_id"]:
            abort(403)

        if request.method == "GET":
            return render_template("create_quiz.html", lesson=lesson, module=module,course=course)

        title = request.form.get("title")
        description = request.form.get("description")

        quiz_service.create_quiz(
            title,
            description,
            lesson_id,
            session["user_id"]
        )

        return redirect(url_for("quiz_controller.quizzes", lesson_id=lesson_id))

    except ValueError as e:
        return render_template("create_quiz.html", lesson=lesson,module=module, course=course,error=str(e))


@quiz_controller.route("/quizzes/edit/<int:quiz_id>", methods=["GET", "POST"])
def edit_quiz(quiz_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        abort(404)

    try:
        quiz = quiz_service.get_quiz(quiz_id)

        lesson = lesson_service.get_lesson( quiz.lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course( module.course_id)

        if course.instructor_id != session["user_id"]:
            abort(403)

        questions = question_service.get_quiz_questions(quiz_id)
        question_options = {}

        for question in questions:
            question_options[question.id] = (
                option_service.get_question_options(
                    question.id
                )
            )

        if request.method == "GET":
            return render_template(
                "edit_quiz.html",
                quiz=quiz,
                lesson=lesson,
                module=module,
                course=course,
                questions=questions,
                question_options=question_options
            )

        title = request.form.get("title")
        description = request.form.get("description")

        quiz_service.update_quiz(
            quiz_id,
            title,
            description
        )

        return redirect(url_for("quiz_controller.edit_quiz", quiz_id=quiz_id))

    except ValueError as e:
        return render_template(
            "edit_quiz.html",
            quiz=quiz,
            lesson=lesson,
            module=module,
            course=course,
            questions=questions,
            question_options=question_options,
            error=str(e)
        )


@quiz_controller.route("/quizzes/delete/<int:quiz_id>",methods=["POST"])
def delete_quiz(quiz_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        abort(403)

    try:
        quiz = quiz_service.get_quiz(quiz_id)
        lesson = lesson_service.get_lesson(quiz.lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)

        if course.instructor_id != session["user_id"]:
            abort(403)

        lesson_id = quiz.lesson_id

        quiz_service.delete_quiz(quiz_id)

        return redirect(url_for("quiz_controller.quizzes", lesson_id=lesson_id))

    except ValueError as e:
        return str(e), 404