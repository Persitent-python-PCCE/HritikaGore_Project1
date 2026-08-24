from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app
)

from dao.course_dao import CourseDAO
from services.course_service import CourseService

course_controller = Blueprint("course_controller",__name__)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

@course_controller.route("/courses")
def courses():
    if "user_id" not in session:
        return redirect( url_for("auth_controller.login"))

    courses = course_service.get_all_courses()

    current_app.logger.info(
        "Courses viewed | user_id=%s | count=%s",
        session["user_id"],
        len(courses)
    )

    return render_template("courses.html",courses=courses)

@course_controller.route("/courses/create",methods=["GET", "POST"])
def create_course():
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        current_app.logger.warning(
            "Course creation denied | user_id=%s | role=%s",
            session.get("user_id"),
            session.get("user_role")
        )

        return "Access denied", 403

    if request.method == "GET":
        return render_template("create_course.html")

    title = request.form.get("title")
    description = request.form.get("description")

    try:
        course = course_service.create_course(
            title,
            description,
            session["user_id"]
        )

        current_app.logger.info(
            "Course created | course_id=%s | instructor_id=%s | title=%s",
            course.id,
            session["user_id"],
            title
        )

        return redirect(url_for("course_controller.courses"))

    except ValueError as e:
        current_app.logger.error(
            "Course creation failed | user_id=%s | error=%s",
            session.get("user_id"),
            str(e)
        )

        return render_template(
            "create_course.html",
            error=str(e)
        )


@course_controller.route( "/courses/edit/<int:course_id>", methods=["GET", "POST"])
def edit_course(course_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        current_app.logger.warning(
            "Course edit denied | user_id=%s | course_id=%s | role=%s",
            session.get("user_id"),
            course_id,
            session.get("user_role")
        )

        return "Access denied", 403

    try:
        course = course_service.get_course(course_id)
        if course.instructor_id != session["user_id"]:
            current_app.logger.warning(
                "Course edit denied | user_id=%s | course_id=%s | reason=not_owner",
                session["user_id"],
                course_id
            )

            return "Access denied", 403

        if request.method == "GET":
            return render_template(
                "edit_course.html",
                course=course
            )

        title = request.form.get("title")
        description = request.form.get("description")

        course_service.update_course(
            course_id,
            title,
            description
        )

        current_app.logger.info(
            "Course updated | course_id=%s | instructor_id=%s",
            course_id,
            session["user_id"]
        )

        return redirect(
            url_for("course_controller.courses")
        )

    except ValueError as e:
        current_app.logger.error(
            "Course update failed | course_id=%s | user_id=%s | error=%s",
            course_id,
            session.get("user_id"),
            str(e)
        )

        return render_template(
            "edit_course.html",
            course=course,
            error=str(e)
        )


@course_controller.route("/courses/delete/<int:course_id>",methods=["POST"])
def delete_course(course_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        current_app.logger.warning(
            "Course deletion denied | user_id=%s | course_id=%s | role=%s",
            session.get("user_id"),
            course_id,
            session.get("user_role")
        )

        return "Access denied", 403

    try:
        course = course_service.get_course(course_id)

        if course.instructor_id != session["user_id"]:
            current_app.logger.warning(
                "Course deletion denied | user_id=%s | course_id=%s | reason=not_owner",
                session["user_id"],
                course_id
            )

            return "Access denied", 403

        course_service.delete_course(course_id)

        current_app.logger.info(
            "Course deleted | course_id=%s | instructor_id=%s | title=%s",
            course_id,
            session["user_id"],
            course.title
        )

        return redirect(
            url_for("course_controller.courses")
        )

    except ValueError as e:
        current_app.logger.error(
            "Course deletion failed | course_id=%s | user_id=%s | error=%s",
            course_id,
            session.get("user_id"),
            str(e)
        )

        return str(e), 404