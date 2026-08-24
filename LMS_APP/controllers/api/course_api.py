from flask import request, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from controllers.api import api_v2

from dao.course_dao import CourseDAO
from services.course_service import CourseService

from utils.rbac import role_required


course_dao = CourseDAO()
course_service = CourseService(course_dao)


@api_v2.route("/courses", methods=["GET"])
@jwt_required()
def get_courses():

    courses = course_service.get_all_courses()

    return jsonify([
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "instructor_id": course.instructor_id,
            "created_at": (
                course.created_at.isoformat()
                if course.created_at
                else None
            )
        }
        for course in courses
    ]), 200


@api_v2.route("/courses/<int:course_id>", methods=["GET"])
@jwt_required()
def get_course(course_id):

    try:

        course = course_service.get_course(
            course_id
        )

        return jsonify({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "instructor_id": course.instructor_id,
            "created_at": (
                course.created_at.isoformat()
                if course.created_at
                else None
            )
        }), 200

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404



@api_v2.route("/courses", methods=["POST"])
@jwt_required()
@role_required("instructor")
def create_course():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400

    title = data.get("title")
    description = data.get("description")

    instructor_id = int(
        get_jwt_identity()
    )

    try:

        course = course_service.create_course(
            title,
            description,
            instructor_id
        )

        return jsonify({
            "message": "Course created successfully",
            "course": {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "instructor_id": course.instructor_id
            }
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400


@api_v2.route(
    "/courses/<int:course_id>",
    methods=["PUT", "PATCH"]
)
@jwt_required()
@role_required("instructor")
def update_course(course_id):

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400

    title = data.get("title")
    description = data.get("description")

    try:

        course = course_service.get_course(
            course_id
        )

        current_user_id = int(
            get_jwt_identity()
        )

        # Ownership check
        if course.instructor_id != current_user_id:

            return jsonify({
                "error": "You can only modify your own courses"
            }), 403

        course = course_service.update_course(
            course_id,
            title,
            description
        )

        return jsonify({
            "message": "Course updated successfully",
            "course": {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "instructor_id": course.instructor_id
            }
        }), 200

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404


@api_v2.route(
    "/courses/<int:course_id>",
    methods=["DELETE"]
)
@jwt_required()
@role_required("instructor")
def delete_course(course_id):

    try:

        course = course_service.get_course(
            course_id
        )

        current_user_id = int(
            get_jwt_identity()
        )

        # Ownership check
        if course.instructor_id != current_user_id:

            return jsonify({
                "error": "You can only delete your own courses"
            }), 403

        course_service.delete_course(
            course_id
        )

        return jsonify({
            "message": "Course deleted successfully"
        }), 200

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404