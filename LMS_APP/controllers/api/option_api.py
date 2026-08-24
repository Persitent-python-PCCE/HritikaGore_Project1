from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from controllers.api import api_v2

from dao.option_dao import OptionDAO
from services.option_service import OptionService

from dao.question_dao import QuestionDAO
from services.question_service import QuestionService

from dao.quiz_dao import QuizDAO
from services.quiz_service import QuizService

from dao.lesson_dao import LessonDAO
from services.lesson_service import LessonService

from dao.module_dao import ModuleDAO
from services.module_service import ModuleService

from dao.course_dao import CourseDAO
from services.course_service import CourseService

from utils.rbac import role_required


option_service = OptionService(OptionDAO())
question_service = QuestionService(QuestionDAO())
quiz_service = QuizService(QuizDAO())
lesson_service = LessonService(LessonDAO())
module_service = ModuleService(ModuleDAO())
course_service = CourseService(CourseDAO())


def get_current_user_id():
    identity = get_jwt_identity()

    if isinstance(identity, dict):
        return identity.get("id") or identity.get("user_id")

    return identity


def option_to_dict(option):
    return {
        "id": option.id,
        "option_text": option.option_text,
        "is_correct": option.is_correct,
        "question_id": option.question_id
    }


def instructor_owns_question(question):

    quiz = quiz_service.get_quiz(
        question.quiz_id
    )

    lesson = lesson_service.get_lesson(
        quiz.lesson_id
    )

    module = module_service.get_module(
        lesson.module_id
    )

    course = course_service.get_course(
        module.course_id
    )

    return course.instructor_id == int(
        get_current_user_id()
    )


# =========================================================
# GET OPTIONS FOR QUESTION
# GET /api/v2/questions/<question_id>/options
# =========================================================

@api_v2.route(
    "/questions/<int:question_id>/options",
    methods=["GET"]
)
@jwt_required()
def get_question_options(question_id):

    try:
        question_service.get_question(
            question_id
        )

        options = option_service.get_question_options(
            question_id
        )

        return jsonify([
            option_to_dict(option)
            for option in options
        ]), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# =========================================================
# GET SINGLE OPTION
# GET /api/v2/options/<option_id>
# =========================================================

@api_v2.route(
    "/options/<int:option_id>",
    methods=["GET"]
)
@jwt_required()
def get_option(option_id):

    try:
        option = option_service.get_option(
            option_id
        )

        return jsonify(
            option_to_dict(option)
        ), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# =========================================================
# CREATE OPTION
# POST /api/v2/questions/<question_id>/options
# =========================================================

@api_v2.route(
    "/questions/<int:question_id>/options",
    methods=["POST"]
)
@jwt_required()
@role_required("instructor")
def create_option(question_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:
        question = question_service.get_question(
            question_id
        )

        if not instructor_owns_question(question):
            return jsonify({
                "error": "You can only add options to your own course questions"
            }), 403

        option = option_service.create_option(
            data.get("option_text"),
            question_id,
            data.get("is_correct", False)
        )

        return jsonify({
            "message": "Option created successfully",
            "option": option_to_dict(option)
        }), 201

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400


# =========================================================
# UPDATE OPTION
# PUT/PATCH /api/v2/options/<option_id>
# =========================================================

@api_v2.route(
    "/options/<int:option_id>",
    methods=["PUT", "PATCH"]
)
@jwt_required()
@role_required("instructor")
def update_option(option_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:
        option = option_service.get_option(
            option_id
        )

        question = question_service.get_question(
            option.question_id
        )

        if not instructor_owns_question(question):
            return jsonify({
                "error": "You can only modify your own course options"
            }), 403

        updated_option = option_service.update_option(
            option_id,
            data.get("option_text"),
            data.get("is_correct", False)
        )

        return jsonify({
            "message": "Option updated successfully",
            "option": option_to_dict(updated_option)
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# =========================================================
# DELETE OPTION
# DELETE /api/v2/options/<option_id>
# =========================================================

@api_v2.route(
    "/options/<int:option_id>",
    methods=["DELETE"]
)
@jwt_required()
@role_required("instructor")
def delete_option(option_id):

    try:
        option = option_service.get_option(
            option_id
        )

        question = question_service.get_question(
            option.question_id
        )

        if not instructor_owns_question(question):
            return jsonify({
                "error": "You can only delete your own course options"
            }), 403

        option_service.delete_option(
            option_id
        )

        return jsonify({
            "message": "Option deleted successfully"
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404