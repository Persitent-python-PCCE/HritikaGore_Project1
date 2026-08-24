from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from dao.user_dao import UserDAO
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies

from services.auth_service import AuthService
from dao.enrollment_dao import EnrollmentDAO
from services.enrollment_service import EnrollmentService

from dao.module_dao import ModuleDAO
from services.module_service import ModuleService

from dao.lesson_dao import LessonDAO
from services.lesson_service import LessonService

from dao.progress_dao import ProgressDAO
from services.progress_service import ProgressService
from dao.course_dao import CourseDAO
from services.course_service import CourseService

from dao.quiz_submission_dao import QuizSubmissionDAO
from services.quiz_submission_service import QuizSubmissionService

auth_controller = Blueprint("auth_controller", __name__)

user_dao = UserDAO()
auth_service = AuthService(user_dao)

enrollment_dao = EnrollmentDAO()
enrollment_service = EnrollmentService(enrollment_dao)

module_dao = ModuleDAO()
module_service = ModuleService(module_dao)

lesson_dao = LessonDAO()
lesson_service = LessonService(lesson_dao)

progress_dao = ProgressDAO()
progress_service = ProgressService(progress_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

quiz_submission_dao = QuizSubmissionDAO()
quiz_submission_service = QuizSubmissionService(quiz_submission_dao)

@auth_controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    try:
        user = auth_service.login_user(
            email,
            password
        )

        if not user.is_active:
            return render_template("login.html", error="Your account has been disabled")

        access_token = create_access_token(identity=str(user.id),
            additional_claims={
                "role": user.role
            }
        )

        response = redirect(url_for("auth_controller.dashboard"))
        set_access_cookies(response, access_token)

        session["user_id"] = user.id
        session["user_role"] = user.role

        return response

    except ValueError as e:
        return render_template("login.html",error=str(e))


@auth_controller.route("/users")
def users():
    users = user_dao.get_all_users()
    return render_template("users.html",users=users)


@auth_controller.route("/logout")
def logout():
    response = redirect(url_for("auth_controller.login"))
    unset_jwt_cookies(response)
    session.clear()
    return response


@auth_controller.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    role = session.get("user_role")

    if role == "student":
        student_id = session["user_id"]

        enrollments = enrollment_service.get_student_enrollment(student_id)

        my_courses = []

        for enrollment in enrollments:
            if enrollment.status.lower() != "active":
                continue

            try:
                course = course_service.get_course(enrollment.course_id)

                progress = progress_service.get_course_progress(
                    student_id,
                    course.id,
                    module_service,
                    lesson_service
                )

                my_courses.append({
                    "course": course,
                    "progress": progress
                })

            except ValueError:
                continue

        quiz_history = (quiz_submission_service.get_student_submissions(student_id))

        return render_template(
            "dashboard.html",
            my_courses=my_courses,
            quiz_history=quiz_history
        )

    if role == "instructor":
        return render_template("instructor_dashboard.html")

    if role == "admin":
        return render_template("admin_dashboard.html")

    session.clear()
    return redirect(url_for("auth_controller.login"))