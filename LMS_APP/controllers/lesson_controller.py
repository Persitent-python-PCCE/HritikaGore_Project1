from flask import Blueprint, render_template, request, redirect, url_for, session
from dao.lesson_dao import LessonDAO
from services.lesson_service import LessonService
from dao.module_dao import ModuleDAO
from services.module_service import ModuleService
from dao.course_dao import CourseDAO
from services.course_service import CourseService
from dao.progress_dao import ProgressDAO
from services.progress_service import ProgressService
from dao.quiz_dao import QuizDAO
from services.quiz_service import QuizService
from dao.enrollment_dao import EnrollmentDAO
from services.enrollment_service import EnrollmentService

from dao.quiz_submission_dao import QuizSubmissionDAO
from services.quiz_submission_service import QuizSubmissionService

lesson_controller = Blueprint("lesson_controller", __name__)
lesson_dao= LessonDAO()
lesson_service = LessonService(lesson_dao)

module_dao = ModuleDAO()
module_service = ModuleService(module_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

progress_dao = ProgressDAO()
progress_service = ProgressService(progress_dao)

quiz_dao = QuizDAO()
quiz_service = QuizService(quiz_dao)

enrollment_dao = EnrollmentDAO()
enrollment_service = EnrollmentService(enrollment_dao)

quiz_submission_dao = QuizSubmissionDAO()
quiz_submission_service = QuizSubmissionService(quiz_submission_dao)

@lesson_controller.route("/modules/<int:module_id>/lessons")
def lessons(module_id):

    if "user_id" not in session:
        return redirect(
            url_for("auth_controller.login")
        )

    try:
        module = module_service.get_module(module_id)
        course = course_service.get_course(module.course_id)

        role = session.get("user_role")
        user_id = session.get("user_id")

        
        if role == "student":
            enrollment = enrollment_service.get_enrollment(
                user_id,
                course.id
            )

            if not enrollment:
                return "You are not enrolled in this course", 403

            if enrollment.status != "active":
                return "Your enrollment is not active", 403

        elif role == "instructor":
            if course.instructor_id != user_id:
                return "Access denied", 403

        elif role == "admin":
            pass

        else:
            return "Access denied", 403

        lessons = lesson_service.get_module_lesson(module_id)

        return render_template(
            "lessons.html",
            module=module,
            lessons=lessons
        )

    except ValueError as e:
        return str(e), 404


@lesson_controller.route("/modules/<int:module_id>/lessons/create", methods=["GET", "POST"])
def create_lesson(module_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access Denied", 403

    try:
        module = module_service.get_module(module_id)
        course = course_service.get_course(module.course_id)

        if course.instructor_id != session["user_id"]:
            return "Access denied", 403

        if request.method == "GET":
            return render_template("create_lesson.html",module=module)

        title = request.form.get("title")
        content = request.form.get("content")

        lesson_service.create_lesson(
            title,
            content,
            module_id
        )

        return redirect(url_for("lesson_controller.lessons", module_id=module_id))

    except ValueError as e:
        return render_template("create_lesson.html", module=module, error=str(e))


@lesson_controller.route("/lessons/edit/<int:lesson_id>", methods=["GET", "POST"])
def edit_lesson(lesson_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access denied", 403

    try:
        lesson = lesson_service.get_lesson(lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)

        # Only course owner can edit lesson
        if course.instructor_id != session["user_id"]:
            return "Access denied", 403

        if request.method == "GET":
            return render_template("edit_lesson.html",lesson=lesson,module=module)

        title = request.form.get("title")
        content = request.form.get("content")

        lesson_service.update_lesson(
            lesson_id,
            title,
            content
        )

        return redirect(url_for( "lesson_controller.lessons",module_id=lesson.module_id))

    except ValueError as e:
        return render_template("edit_lesson.html",lesson=lesson,module=module,error=str(e))


@lesson_controller.route("/lessons/delete/<int:lesson_id>",methods=["POST"])
def delete_lesson(lesson_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access denied", 403

    try:
        lesson = lesson_service.get_lesson(lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)

        # Only course owner can delete lesson
        if course.instructor_id != session["user_id"]:
            return "Access denied", 403

        module_id = lesson.module_id
        lesson_service.delete_lesson(lesson_id)

        return redirect(url_for( "lesson_controller.lessons",module_id=module_id))

    except ValueError as e:
        return str(e), 404

@lesson_controller.route("/lessons/<int:lesson_id>")
def lesson_detail(lesson_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    try:
        lesson = lesson_service.get_lesson(lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)

        role = session.get("user_role")
        user_id = session.get("user_id")

        # Students must be enrolled
        if role == "student":
            enrollment = enrollment_service.get_enrollment(
                user_id,
                course.id
            )

            if not enrollment:
                return "You are not enrolled in this course", 403

            if enrollment.status.lower() != "active":
                return "Your enrollment is not active", 403

        # Instructor can access only own course
        elif role == "instructor":

            if course.instructor_id != user_id:
                return "Access denied", 403

        # Admin allowed
        elif role == "admin":
            pass

        else:
            return "Access denied", 403

        progress = progress_dao.get_progress(
            user_id,
            lesson_id
        )

        return render_template(
            "lesson_detail.html",
            lesson=lesson,
            module=module,
            course=course,
            progress=progress
        )

    except ValueError as e:
        return str(e), 404
    
@lesson_controller.route("/lessons/<int:lesson_id>/complete",methods=["POST"])
def complete_lesson(lesson_id):
    if "user_id" not in session:
        return redirect(
            url_for("auth_controller.login")
        )

    if session.get("user_role") != "student":
        return "Access Denied", 403

    try:
        lesson = lesson_service.get_lesson(lesson_id)
        progress_service.complete_lesson(
            session["user_id"],
            lesson_id
        )

        return redirect(url_for("lesson_controller.lessons",module_id=lesson.module_id))

    except ValueError as e:
        return str(e), 404

@lesson_controller.route("/courses/<int:course_id>/progress")
def course_progress(course_id):

    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "student":
        return "Access Denied", 403

    try:
        student_id = session["user_id"]

        course = course_service.get_course(course_id)

        progress = progress_service.get_course_progress(
            student_id,
            course_id,
            module_service,
            lesson_service
        )

        submissions = (quiz_submission_service.get_student_submissions(student_id))
        quizzes = quiz_service.get_course_quizzes(course_id)

        course_quiz_ids = {
            quiz.id
            for quiz in quizzes
        }

        quiz_history = [
            submission
            for submission in submissions
            if submission.quiz_id in course_quiz_ids
        ]

        return render_template(
            "course_progress.html",
            course=course,
            progress=progress,
            quiz_history=quiz_history,
            quizzes=quizzes
        )

    except ValueError as e:
        return str(e), 404

    
@lesson_controller.route("/progress")
def progress():
    if "user_id" not in session:
        return redirect(
            url_for("auth_controller.login")
        )

    if session.get("user_role") != "student":
        return "Access denied", 403

    student_id = session["user_id"]

    progress_data = progress_service.get_student_progress(student_id)

    return render_template("progress.html", progress=progress_data)