from flask import request, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from controllers.api import api_v2

from dao.quiz_dao import QuizDAO
from services.quiz_service import QuizService

from dao.lesson_dao import LessonDAO
from services.lesson_service import LessonService

from dao.module_dao import ModuleDAO
from services.module_service import ModuleService

from dao.course_dao import CourseDAO
from services.course_service import CourseService

from dao.enrollment_dao import EnrollmentDAO
from services.enrollment_service import EnrollmentService

from utils.rbac import role_required


quiz_dao = QuizDAO()
quiz_service = QuizService(quiz_dao)

lesson_dao = LessonDAO()
lesson_service = LessonService(lesson_dao)

module_dao = ModuleDAO()
module_service = ModuleService(module_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

enrollment_dao = EnrollmentDAO()
enrollment_service = EnrollmentService(enrollment_dao)


def quiz_to_dict(quiz):
    return {
        "id": quiz.id,
        "lesson_id": quiz.lesson_id,
        "title": quiz.title,
        "description": quiz.description,
        "created_by": quiz.created_by,
        "created_at": (
            quiz.created_at.isoformat()
            if quiz.created_at
            else None
        )
    }


def get_quiz_course(quiz_id):
    quiz = quiz_service.get_quiz(quiz_id)

    lesson = lesson_service.get_lesson(
        quiz.lesson_id
    )

    module = module_service.get_module(
        lesson.module_id
    )

    course = course_service.get_course(
        module.course_id
    )

    return quiz, lesson, module, course


def instructor_owns_quiz(quiz_id, user_id):
    quiz, lesson, module, course = get_quiz_course(
        quiz_id
    )

    return course.instructor_id == user_id


def student_can_access_quiz(quiz_id, user_id):
    quiz, lesson, module, course = get_quiz_course(
        quiz_id
    )

    enrollment = enrollment_service.get_enrollment(
        user_id,
        course.id
    )

    return (
        enrollment
        and enrollment.status.lower() == "active"
    )


# --------------------------------------------------
# GET QUIZZES FOR LESSON
# --------------------------------------------------

@api_v2.route(
    "/lessons/<int:lesson_id>/quizzes",
    methods=["GET"]
)
@jwt_required()
def get_lesson_quizzes(lesson_id):

    try:
        lesson = lesson_service.get_lesson(
            lesson_id
        )

        module = module_service.get_module(
            lesson.module_id
        )

        course = course_service.get_course(
            module.course_id
        )

        current_user_id = int(
            get_jwt_identity()
        )

        if course.instructor_id == current_user_id:
            quizzes = quiz_service.get_lesson_quizzes(
                lesson_id
            )

            return jsonify([
                quiz_to_dict(quiz)
                for quiz in quizzes
            ]), 200

        enrollment = enrollment_service.get_enrollment(
            current_user_id,
            course.id
        )

        if not (
            enrollment
            and enrollment.status.lower() == "active"
        ):
            return jsonify({
                "error": "You do not have access to this lesson"
            }), 403

        quizzes = quiz_service.get_lesson_quizzes(
            lesson_id
        )

        return jsonify([
            quiz_to_dict(quiz)
            for quiz in quizzes
        ]), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# --------------------------------------------------
# CREATE QUIZ
# --------------------------------------------------

@api_v2.route(
    "/lessons/<int:lesson_id>/quizzes",
    methods=["POST"]
)
@jwt_required()
@role_required("instructor")
def create_quiz(lesson_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:
        lesson = lesson_service.get_lesson(
            lesson_id
        )

        module = module_service.get_module(
            lesson.module_id
        )

        course = course_service.get_course(
            module.course_id
        )

        current_user_id = int(
            get_jwt_identity()
        )

        if course.instructor_id != current_user_id:
            return jsonify({
                "error": "You can only create quizzes for your own courses"
            }), 403

        title = data.get("title")
        description = data.get("description")

        quiz = quiz_service.create_quiz(
            title,
            description,
            lesson_id,
            current_user_id
        )

        return jsonify({
            "message": "Quiz created successfully",
            "quiz": quiz_to_dict(quiz)
        }), 201

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400


# --------------------------------------------------
# UPDATE QUIZ
# --------------------------------------------------

@api_v2.route(
    "/quizzes/<int:quiz_id>",
    methods=["PUT", "PATCH"]
)
@jwt_required()
@role_required("instructor")
def update_quiz(quiz_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:
        current_user_id = int(
            get_jwt_identity()
        )

        if not instructor_owns_quiz(
            quiz_id,
            current_user_id
        ):
            return jsonify({
                "error": "You can only modify your own course quizzes"
            }), 403

        title = data.get("title")
        description = data.get("description")

        quiz = quiz_service.update_quiz(
            quiz_id,
            title,
            description
        )

        return jsonify({
            "message": "Quiz updated successfully",
            "quiz": quiz_to_dict(quiz)
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# --------------------------------------------------
# DELETE QUIZ
# --------------------------------------------------

@api_v2.route(
    "/quizzes/<int:quiz_id>",
    methods=["DELETE"]
)
@jwt_required()
@role_required("instructor")
def delete_quiz(quiz_id):

    try:
        current_user_id = int(
            get_jwt_identity()
        )

        if not instructor_owns_quiz(
            quiz_id,
            current_user_id
        ):
            return jsonify({
                "error": "You can only delete your own course quizzes"
            }), 403

        quiz_service.delete_quiz(
            quiz_id
        )

        return jsonify({
            "message": "Quiz deleted successfully"
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404