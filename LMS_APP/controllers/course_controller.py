from flask import Blueprint, render_template, request, redirect, url_for, session  
from dao.course_dao import CourseDAO
from services.course_service import CourseService
course_controller = Blueprint("course_controller", __name__)
course_dao= CourseDAO()
course_service = CourseService(course_dao)

@course_controller.route("/courses")
def courses():
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    courses = course_service.get_all_courses()

    return render_template("courses.html", courses= courses)

@course_controller.route("/courses/create", methods= ["GET", "POST"])
def create_course():
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access denied", 403

    if request.method == "GET":
        return render_template("create_course.html")

    title = request.form.get("title")
    description = request.form.get("description")

    try:
        course_service.create_course(
            title,
            description,
            session["user_id"]
        )
        return redirect(url_for("course_controller.courses"))
    except ValueError as e:
        print("COURSE ERROR ",e)
        return render_template("create_course.html", error=str(e))

@course_controller.route("/courses/edit/<int:course_id>", methods=["GET", "POST"])
def edit_course(course_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access denied", 403

    try:
        course = course_service.get_course(course_id)

        if course.instructor_id != session["user_id"]:
            return "Access denied", 403

        if request.method == "GET":
            return render_template("edit_course.html", course=course)

        title = request.form.get("title")
        description = request.form.get("description")

        course_service.update_course(course_id,title,description)

        return redirect(url_for("course_controller.courses"))

    except ValueError as e:
        return render_template("edit_course.html", course=course, error=str(e))


@course_controller.route("/courses/delete/<int:course_id>", methods=["POST"])
def delete_course(course_id):

    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access denied", 403

    try:
        course = course_service.get_course(course_id)

        if course.instructor_id != session["user_id"]:
            return "Access denied", 403

        course_service.delete_course(course_id)

        return redirect(
            url_for("course_controller.courses")
        )

    except ValueError as e:
        return str(e), 404