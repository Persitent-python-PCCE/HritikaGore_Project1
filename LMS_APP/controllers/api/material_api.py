from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from dao.material_dao import MaterialDAO
from services.material_service import MaterialService
from dao.course_dao import CourseDAO
from services.course_service import CourseService
from controllers.api import api_v2
from utils.rbac import role_required
from dao.enrollment_dao import EnrollmentDAO
from services.enrollment_service import EnrollmentService
material_dao = MaterialDAO()
material_service = MaterialService(material_dao)

enrollment_dao = EnrollmentDAO()
enrollment_service = EnrollmentService(enrollment_dao)
course_dao = CourseDAO()
course_service = CourseService(course_dao)


@api_v2.route(
    "/courses/<int:course_id>/materials",
    methods=["GET"]
)
@jwt_required()
@role_required("student", "instructor", "admin")
def get_course_materials(course_id):

    try:
        course = course_service.get_course(course_id)

        current_user_id = int(get_jwt_identity())

        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        role = claims.get("role")

        # Students can only access materials
        # for courses they are enrolled in
        if role == "student":
            enrollment = enrollment_service.get_enrollment(
                current_user_id,
                course_id
            )

            if not enrollment:
                return jsonify({
                    "msg": "Access denied"
                }), 403

        materials = material_service.get_course_materials(
            course_id
        )

        return jsonify([
            {
                "id": material.id,
                "title": material.title,
                "file_path": material.file_path,
                "material_type": material.material_type,
                "course_id": material.course_id,
                "module_id": material.module_id,
                "uploaded_by": material.uploaded_by
            }
            for material in materials
        ]), 200

    except ValueError as e:
        return jsonify({
            "msg": str(e)
        }), 404

@api_v2.route(
    "/courses/<int:course_id>/materials",
    methods=["POST"]
)
@jwt_required()
@role_required("instructor", "admin")
def create_material(course_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    try:
        course = course_service.get_course(course_id)

        current_user_id = int(get_jwt_identity())

        # Instructor can only add materials to their own course
        claims = get_jwt()
        role = claims.get("role")

        if role != "admin" and course.instructor_id != current_user_id:
            return jsonify({
                "message": "Access denied"
            }), 403

        title = data.get("title")
        file_path = data.get("file_path")
        material_type = data.get("material_type")
        module_id = data.get("module_id")

        material = material_service.create_material(
            title=title,
            file_path=file_path,
            material_type=material_type,
            course_id=course_id,
            module_id=module_id,
            uploaded_by=current_user_id
        )

        return jsonify({
            "message": "Material created successfully",
            "material": {
                "id": material.id,
                "title": material.title,
                "file_path": material.file_path,
                "material_type": material.material_type,
                "course_id": material.course_id,
                "module_id": material.module_id,
                "uploaded_by": material.uploaded_by
            }
        }), 201

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400


@api_v2.route(
    "/materials/<int:material_id>",
    methods=["GET"]
)
@jwt_required()
@role_required("student", "instructor", "admin")
def get_material(material_id):

    try:
        material = material_service.get_material(material_id)

        return jsonify({
            "id": material.id,
            "title": material.title,
            "file_path": material.file_path,
            "material_type": material.material_type,
            "course_id": material.course_id,
            "module_id": material.module_id,
            "uploaded_by": material.uploaded_by
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 404


@api_v2.route(
    "/materials/<int:material_id>",
    methods=["DELETE"]
)
@jwt_required()
@role_required("instructor", "admin")
def delete_material(material_id):

    try:
        material = material_service.get_material(material_id)

        current_user_id = int(get_jwt_identity())

        if material.uploaded_by != current_user_id:

            # Check whether admin
            claims = {}
            try:
                from flask_jwt_extended import get_jwt
                claims = get_jwt()
            except Exception:
                pass

            if claims.get("role") != "admin":
                return jsonify({
                    "msg": "Access denied"
                }), 403

        material_service.delete_material(material_id)

        return jsonify({
            "message": "Material deleted successfully"
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 404