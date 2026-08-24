from flask import request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from controllers.api import api_v2

from dao.module_dao import ModuleDAO
from services.module_service import ModuleService

from dao.course_dao import CourseDAO
from services.course_service import CourseService

from dao.enrollment_dao import EnrollmentDAO
from services.enrollment_service import EnrollmentService

from utils.rbac import role_required


module_dao = ModuleDAO()
module_service = ModuleService(module_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

enrollment_dao = EnrollmentDAO()
enrollment_service = EnrollmentService(enrollment_dao)


def module_to_dict(module):
    return {
        "id": module.id,
        "title": module.title,
        "description": module.description,
        "course_id": module.course_id,
        "created_at": (
            module.created_at.isoformat()
            if module.created_at
            else None
        )
    }


@api_v2.route(
    "/courses/<int:course_id>/modules",
    methods=["GET"]
)
@jwt_required()
def get_course_modules(course_id):

    try:
        course_service.get_course(course_id)

        current_user_id = int(get_jwt_identity())

        enrollment = enrollment_service.get_enrollment(
            current_user_id,
            course_id
        )

        # Students must be enrolled
        if enrollment and enrollment.status.lower() == "active":
            modules = module_service.get_course_modules(course_id)

            return jsonify([
                module_to_dict(module)
                for module in modules
            ]), 200

        # Instructor owning the course
        course = course_service.get_course(course_id)

        if course.instructor_id == current_user_id:
            modules = module_service.get_course_modules(course_id)

            return jsonify([
                module_to_dict(module)
                for module in modules
            ]), 200

        return jsonify({
            "error": "You do not have access to this course"
        }), 403

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


@api_v2.route(
    "/modules/<int:module_id>",
    methods=["GET"]
)
@jwt_required()
def get_module(module_id):

    try:
        module = module_service.get_module(module_id)

        current_user_id = int(get_jwt_identity())

        enrollment = enrollment_service.get_enrollment(
            current_user_id,
            module.course_id
        )

        course = course_service.get_course(
            module.course_id
        )

        if (
            course.instructor_id != current_user_id
            and not (
                enrollment
                and enrollment.status.lower() == "active"
            )
        ):
            return jsonify({
                "error": "You do not have access to this module"
            }), 403

        return jsonify(
            module_to_dict(module)
        ), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


@api_v2.route(
    "/courses/<int:course_id>/modules",
    methods=["POST"]
)
@jwt_required()
@role_required("instructor")
def create_module(course_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:
        course = course_service.get_course(course_id)

        current_user_id = int(
            get_jwt_identity()
        )

        if course.instructor_id != current_user_id:
            return jsonify({
                "error": "You can only add modules to your own courses"
            }), 403

        title = data.get("title")
        description = data.get("description")

        module = module_service.create_module(
            title,
            description,
            course_id
        )

        return jsonify({
            "message": "Module created successfully",
            "module": module_to_dict(module)
        }), 201

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400


@api_v2.route(
    "/modules/<int:module_id>",
    methods=["PUT", "PATCH"]
)
@jwt_required()
@role_required("instructor")
def update_module(module_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:
        module = module_service.get_module(
            module_id
        )

        course = course_service.get_course(
            module.course_id
        )

        current_user_id = int(
            get_jwt_identity()
        )

        if course.instructor_id != current_user_id:
            return jsonify({
                "error": "You can only modify your own course modules"
            }), 403

        title = data.get("title")
        description = data.get("description")

        module = module_service.update_module(
            module_id,
            title,
            description
        )

        return jsonify({
            "message": "Module updated successfully",
            "module": module_to_dict(module)
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


@api_v2.route(
    "/modules/<int:module_id>",
    methods=["DELETE"]
)
@jwt_required()
@role_required("instructor")
def delete_module(module_id):

    try:
        module = module_service.get_module(
            module_id
        )

        course = course_service.get_course(
            module.course_id
        )

        current_user_id = int(
            get_jwt_identity()
        )

        if course.instructor_id != current_user_id:
            return jsonify({
                "error": "You can only delete your own course modules"
            }), 403

        module_service.delete_module(
            module_id
        )

        return jsonify({
            "message": "Module deleted successfully"
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404