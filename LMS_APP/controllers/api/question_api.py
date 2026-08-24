from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from controllers.api import api_v2

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


def question_to_dict(question):
    return {
        "id": question.id,
        "question_text": question.question_text,
        "difficulty": question.difficulty,
        "explanation": question.explanation,
        "quiz_id": question.quiz_id
    }


def instructor_owns_question(question):
    quiz = quiz_service.get_quiz(question.quiz_id)
    lesson = lesson_service.get_lesson(quiz.lesson_id)
    module = module_service.get_module(lesson.module_id)
    course = course_service.get_course(module.course_id)

    return course.instructor_id == int(get_current_user_id())


def instructor_owns_quiz(quiz):
    lesson = lesson_service.get_lesson(quiz.lesson_id)
    module = module_service.get_module(lesson.module_id)
    course = course_service.get_course(module.course_id)

    return course.instructor_id == int(get_current_user_id())


# =========================================================
# GET QUESTIONS FOR QUIZ
# GET /api/v2/quizzes/<quiz_id>/questions
# =========================================================

@api_v2.route(
    "/quizzes/<int:quiz_id>/questions",
    methods=["GET"]
)
@jwt_required()
def get_quiz_questions(quiz_id):

    try:
        quiz_service.get_quiz(quiz_id)

        questions = question_service.get_quiz_questions(
            quiz_id
        )

        return jsonify([
            question_to_dict(question)
            for question in questions
        ]), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# =========================================================
# GET SINGLE QUESTION
# GET /api/v2/questions/<question_id>
# =========================================================

@api_v2.route(
    "/questions/<int:question_id>",
    methods=["GET"]
)
@jwt_required()
def get_question(question_id):

    try:
        question = question_service.get_question(
            question_id
        )

        return jsonify(
            question_to_dict(question)
        ), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# =========================================================
# CREATE QUESTION
# POST /api/v2/quizzes/<quiz_id>/questions
# =========================================================

@api_v2.route(
    "/quizzes/<int:quiz_id>/questions",
    methods=["POST"]
)
@jwt_required()
@role_required("instructor")
def create_question(quiz_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:
        quiz = quiz_service.get_quiz(quiz_id)

        if not instructor_owns_quiz(quiz):
            return jsonify({
                "error": "You can only add questions to your own quizzes"
            }), 403

        question = question_service.create_question(
            data.get("question_text"),
            data.get("difficulty"),
            data.get("explanation"),
            quiz_id
        )

        return jsonify({
            "message": "Question created successfully",
            "question": question_to_dict(question)
        }), 201

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400


# =========================================================
# UPDATE QUESTION
# PUT/PATCH /api/v2/questions/<question_id>
# =========================================================

@api_v2.route(
    "/questions/<int:question_id>",
    methods=["PUT", "PATCH"]
)
@jwt_required()
@role_required("instructor")
def update_question(question_id):

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
                "error": "You can only modify your own course questions"
            }), 403

        updated_question = question_service.update_question(
            question_id,
            data.get("question_text"),
            data.get("difficulty"),
            data.get("explanation")
        )

        return jsonify({
            "message": "Question updated successfully",
            "question": question_to_dict(updated_question)
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# =========================================================
# DELETE QUESTION
# DELETE /api/v2/questions/<question_id>
# =========================================================

@api_v2.route(
    "/questions/<int:question_id>",
    methods=["DELETE"]
)
@jwt_required()
@role_required("instructor")
def delete_question(question_id):

    try:
        question = question_service.get_question(
            question_id
        )

        if not instructor_owns_question(question):
            return jsonify({
                "error": "You can only delete your own course questions"
            }), 403

        question_service.delete_question(
            question_id
        )

        return jsonify({
            "message": "Question deleted successfully"
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404