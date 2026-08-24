from flask import Blueprint, render_template, request, redirect, url_for, session,abort

from dao.module_dao import ModuleDAO
from services.module_service import ModuleService
from services.course_service import CourseService
from dao.course_dao import CourseDAO

from dao.enrollment_dao import EnrollmentDAO
from services.enrollment_service import EnrollmentService

module_controller = Blueprint("module_controller",__name__)

module_dao = ModuleDAO()
module_service = ModuleService(module_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)
enrollment_dao = EnrollmentDAO()
enrollment_service = EnrollmentService(enrollment_dao)

@module_controller.route("/courses/<int:course_id>/modules")
def modules(course_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    try:
        course = course_service.get_course(course_id)

        role = session.get("user_role")
        user_id = session.get("user_id")


        if role == "student":
            enrollment = enrollment_service.get_enrollment(
                user_id,
                course_id
            )

            if not enrollment:
                return "You are not enrolled in this course", 403

            if enrollment.status != "active":
                return "Your enrollment is not active", 403

        elif role == "instructor":
            if course.instructor_id != user_id:
                abort(403)

        elif role == "admin":
            pass
        else:
            abort(403)

        modules = module_service.get_course_modules(course_id)

        return render_template("modules.html",course=course, modules=modules)

    except ValueError as e:
        return str(e), 404

@module_controller.route("/courses/<int:course_id>/modules/create",methods=["GET", "POST"])
def create_module(course_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        abort(403)

    try:
        course = course_service.get_course(course_id)

        if course.instructor_id != session["user_id"]:
            abort(403)

        if request.method == "GET":
            return render_template("create_module.html", course=course)

        title = request.form.get("title")
        description = request.form.get("description")

        module_service.create_module(
            title,
            description,
            course_id
        )

        return redirect(url_for("module_controller.modules",course_id=course_id))

    except ValueError as e:
        return render_template("create_module.html",course=course,error=str(e))

@module_controller.route("/modules/edit/<int:module_id>", methods=["GET", "POST"])
def edit_module(module_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        abort(403)

    try:
        module = module_service.get_module(module_id)
        course = course_service.get_course(module.course_id)

        if course.instructor_id != session["user_id"]:
            abort(403)

        if request.method == "GET":
            return render_template("edit_module.html", module=module, course= course)

        title = request.form.get("title")
        description = request.form.get("description")

        module_service.update_module(module_id, title, description)

        return redirect(url_for("module_controller.modules", course_id = module.course_id))

    except ValueError as e:
        return render_template("edit_module.html", module=module, course=course, error=str(e))


@module_controller.route("/modules/delete/<int:module_id>", methods=["POST"])
def delete_module(module_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        abort(403)

    try:
        module = module_service.get_module(module_id)
        course = course_service.get_course(module.course_id)

        if course.instructor_id != session["user_id"]:
            abort(403)

        course_id = module.course_id
        module_service.delete_module(module_id)

        return redirect(url_for("module_controller.modules",course_id=course_id))

    except ValueError as e:
        return str(e), 404

