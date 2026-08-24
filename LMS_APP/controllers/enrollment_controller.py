from flask import (Blueprint, render_template, redirect, url_for, session)
from dao.enrollment_dao import EnrollmentDAO
from services.enrollment_service import EnrollmentService

from dao.course_dao import CourseDAO
from services.course_service import CourseService

enrollment_controller = Blueprint("enrollment_controller",__name__)

enrollment_dao = EnrollmentDAO()
enrollment_service = EnrollmentService(enrollment_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

@enrollment_controller.route("/courses/<int:course_id>/enroll",methods=["POST"])
def enroll(course_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "student":
        return "Only students can enroll", 403

    try:
        course_service.get_course(course_id)

        enrollment_service.enroll_students(
            session["user_id"],
            course_id
        )

        return redirect(url_for("enrollment_controller.my_courses"))

    except ValueError as e:
        return str(e), 400


@enrollment_controller.route("/my-courses")
def my_courses():
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "student":
        return "Access denied", 403

    enrollments = enrollment_service.get_student_enrollment(
        session["user_id"]
    )

    courses = []

    for enrollment in enrollments:
        courses.append(
            course_service.get_course(
                enrollment.course_id
            )
        )

    return render_template("my_courses.html",courses=courses)