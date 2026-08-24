from flask import (Blueprint, render_template, request, redirect, url_for, session, send_from_directory, make_response)
from config.cache import cache
import os
from werkzeug.utils import secure_filename

from dao.material_dao import MaterialDAO
from services.material_service import MaterialService

from dao.course_dao import CourseDAO
from services.course_service import CourseService

from dao.module_dao import ModuleDAO
from services.module_service import ModuleService

from dao.enrollment_dao import EnrollmentDAO
from services.enrollment_service import EnrollmentService

material_controller = Blueprint( "material_controller", __name__)

ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "mp4",
    "webm",
    "doc",
    "docx",
    "ppt",
    "pptx",
    "txt"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )

material_dao = MaterialDAO()
material_service = MaterialService(material_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

module_dao = ModuleDAO()
module_service = ModuleService(module_dao)

enrollment_dao = EnrollmentDAO()
enrollment_service = EnrollmentService(enrollment_dao)


@material_controller.route("/courses/<int:course_id>/materials")
def materials(course_id):

    if "user_id" not in session:
        return redirect(
            url_for("auth_controller.login")
        )

    try:
        course = course_service.get_course(course_id)

        materials = material_service.get_course_materials(course_id)

        response = render_template(
            "materials.html",
            course=course,
            materials=materials
        )

        response = make_response(response)

        response.headers["Cache-Control"] = ("no-store, no-cache, must-revalidate, max-age=0")
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response

    except ValueError as e:
        return str(e), 404


@material_controller.route("/courses/<int:course_id>/materials/create",methods=["GET", "POST"])
def create_material(course_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access denied", 403

    try:
        course = course_service.get_course(course_id)

        if course.instructor_id != session["user_id"]:
            return "Access denied", 403

        modules = module_service.get_course_modules(course_id)

        if request.method == "GET":
            return render_template("create_material.html", course=course, modules=modules)

        title = request.form.get("title")
        module_id = request.form.get("module_id")
        file = request.files.get("file")


        if not file or not file.filename:
            return render_template("create_material.html",
                course=course,
                modules=module_service.get_course_modules(course_id),
                error="Please select a file"
            )

        if not allowed_file(file.filename):
            return render_template("create_material.html",
            course=course,
            modules=modules,
            error=(
            "File type not allowed. "
            "Allowed: PDF, images, videos, Word, "
            "PowerPoint and text files."
            )
        )

        filename = secure_filename(file.filename)

        if not filename:
            return render_template("create_material.html",
                course=course,
                modules=module_service.get_course_modules(course_id),
                error=("File type not allowed. Allowed: PDF, images, video, Word, PowerPoint and text files")
            )

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return render_template("create_material.html",
            course=course,
            modules=module_service.get_course_modules(course_id),
            error="File size must be 10 MB or less"
        )

        upload_folder = os.path.join(os.getcwd(), "uploads", str(course_id))

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        file_path = os.path.join(upload_folder,filename)
        file.save(file_path)

        stored_path = os.path.join(
            "uploads",
            str(course_id),
            filename
        ).replace("\\", "/")


        material_service.create_material(
            title,
            stored_path,
            file.content_type,
            course_id,
            int(module_id) if module_id else None,
            session["user_id"]
        )

        return redirect(url_for("material_controller.materials", course_id=course_id))

    except ValueError as e:
        return render_template("create_material.html", course=course,
            modules=module_service.get_course_modules(course_id),
            error=str(e)
        )

@material_controller.route("/materials/delete/<int:material_id>",methods=["POST"])
def delete_material(material_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "instructor":
        return "Access denied", 403

    try:
        material = material_service.get_material(material_id)

        course = course_service.get_course(material.course_id)

        if course.instructor_id != session["user_id"]:
            return "Access denied", 403


        relative_path = material.file_path.replace(
            "\\",
            "/"
        )

        if relative_path.startswith("uploads/"):
            relative_path = relative_path[
                len("uploads/"):
            ]

        full_path = os.path.join(
            os.getcwd(),
            "uploads",
            *relative_path.split("/")
        )

        if os.path.isfile(full_path):
            os.remove(full_path)
            print("Deleted file:",full_path)


        material_service.delete_material(material_id)

        return redirect(url_for("material_controller.materials", course_id=material.course_id))

    except ValueError as e:
        return str(e), 404


@material_controller.route("/materials/download/<int:material_id>")
def download_material(material_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    try:
        material = material_service.get_material(material_id)
    except ValueError:
        return "Material not found", 404

    user_id = session["user_id"]
    role = session.get("user_role")

    if role == "instructor":
        course = course_service.get_course(material.course_id)

        if course.instructor_id != user_id:
            return "Access denied", 403

    elif role == "student":
        enrollment = enrollment_dao.get_enrollment(
            user_id,
            material.course_id
        )

        if not enrollment:
            return "You are not enrolled in this course", 403

        if enrollment.status.lower() != "active":
            return "Your enrollment is not active", 403

    elif role == "admin":
        pass

    else:
        return "Access denied", 403

    upload_folder = os.path.join(
        os.getcwd(),
        "uploads"
    )

    relative_path = material.file_path

   
    if relative_path.startswith("uploads/"):
        relative_path = relative_path[
            len("uploads/"):]
    elif relative_path.startswith("uploads\\"):
        relative_path = relative_path[
            len("uploads\\"):]

    relative_path = relative_path.replace("\\", "/")

    full_path = os.path.join(upload_folder, *relative_path.split("/"))

    if not os.path.isfile(full_path):
        return "File not found on server", 404

    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)

    return send_from_directory(
        directory,
        filename,
        as_attachment=False
    )


@material_controller.route("/uploads/<path:filename>")
def uploaded_file(filename):
    upload_folder = os.path.join(
        os.getcwd(),
        "uploads"
    )

    return send_from_directory(
        upload_folder,
        filename
    )