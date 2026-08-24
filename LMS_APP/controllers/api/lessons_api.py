from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.module import Module
from services.lesson_service import LessonService
from dao.lesson_dao import LessonDAO
from controllers.api import api_v2
from models.course import Course
lesson_dao = LessonDAO()
lesson_service = LessonService(lesson_dao)

def get_current_user_id():
    identity = get_jwt_identity()

    if isinstance(identity, dict):
        return identity.get("id") or identity.get("user_id")

    return identity


def get_module(module_id):
    return Module.query.get(module_id)


def instructor_owns_module(module):
    user_id = get_current_user_id()

    if not module:
        return False

    course = Course.query.get(module.course_id)

    if not course:
        return False

    return course.instructor_id == int(user_id)


# =========================================================
# CREATE LESSON
# POST /api/v2/modules/<module_id>/lessons
# =========================================================

@api_v2.route( "/modules/<int:module_id>/lessons",methods=["POST"])
@jwt_required()
def create_lesson(module_id):

    module = get_module(module_id)

    if not module:
        return jsonify({
            "message": "Module not found"
        }), 404

    # Only instructors can create lessons
    if not instructor_owns_module(module):
        return jsonify({
            "message": "Access denied"
        }), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "msg": "Request body is required"
        }), 400

    title = data.get("title")
    content = data.get("content")

    try:
        lesson = lesson_service.create_lesson(
            title,
            content,
            module_id
        )

        return jsonify({
            "msg": "Lesson created successfully",
            "lesson": {
                "id": lesson.id,
                "title": lesson.title,
                "content": lesson.content,
                "module_id": lesson.module_id
            }
        }), 201

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400


# =========================================================
# GET MODULE LESSONS
# GET /api/v2/modules/<module_id>/lessons
# =========================================================

@api_v2.route(
    "/modules/<int:module_id>/lessons",
    methods=["GET"]
)
@jwt_required()
def get_module_lessons(module_id):

    module = get_module(module_id)

    if not module:
        return jsonify({
            "message": "Module not found"
        }), 404

    try:
        lessons = lesson_service.get_module_lesson(module_id)

        return jsonify([
        {
            "id": lesson.id,
            "title": lesson.title,
            "content": lesson.content,
            "module_id": lesson.module_id
        }
            for lesson in lessons
        ]), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 404


# =========================================================
# GET SINGLE LESSON
# GET /api/v2/lessons/<lesson_id>
# =========================================================

@api_v2.route(
    "/lessons/<int:lesson_id>",
    methods=["GET"]
)
@jwt_required()
def get_lesson(lesson_id):

    try:
        lesson = lesson_service.get_lesson(lesson_id)

        return jsonify({
            "id": lesson.id,
            "title": lesson.title,
            "content": lesson.content,
            "module_id": lesson.module_id
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 404


# =========================================================
# UPDATE LESSON
# PUT /api/v2/lessons/<lesson_id>
# =========================================================

@api_v2.route(
    "/lessons/<int:lesson_id>",
    methods=["PUT"]
)
@jwt_required()
def update_lesson(lesson_id):

    try:
        lesson = lesson_service.get_lesson(lesson_id)

        module = get_module(lesson.module_id)

        if not module:
            return jsonify({
                "message": "Module not found"
            }), 404

        if not instructor_owns_module(module):
            return jsonify({
                "message": "Access denied"
            }), 403

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "message": "Request body is required"
            }), 400

        title = data.get("title")
        content = data.get("content")

        updated_lesson = lesson_service.update_lesson(
            lesson_id,
            title,
            content
        )

        return jsonify({
            "msg": "Lesson updated successfully",
            "lesson": {
                "id": updated_lesson.id,
                "title": updated_lesson.title,
                "content": updated_lesson.content,
                "module_id": updated_lesson.module_id
            }
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400


# =========================================================
# DELETE LESSON
# DELETE /api/v2/lessons/<lesson_id>
# =========================================================

@api_v2.route(
    "/lessons/<int:lesson_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_lesson(lesson_id):

    try:
        lesson = lesson_service.get_lesson(lesson_id)

        module = get_module(lesson.module_id)

        if not module:
            return jsonify({
                "message": "Module not found"
            }), 404

        if not instructor_owns_module(module):
            return jsonify({
                "message": "Access denied"
            }), 403

        lesson_service.delete_lesson(lesson_id)

        return jsonify({
            "msg": "Lesson deleted successfully"
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 404