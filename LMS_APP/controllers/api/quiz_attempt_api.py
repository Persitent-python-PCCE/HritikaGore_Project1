from flask import request, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from controllers.api import api_v2

from dao.quiz_dao import QuizDAO
from services.quiz_service import QuizService

from dao.question_dao import QuestionDAO
from services.question_service import QuestionService

from dao.option_dao import OptionDAO
from services.option_service import OptionService

from dao.quiz_submission_dao import QuizSubmissionDAO
from services.quiz_submission_service import QuizSubmissionService

from dao.lesson_dao import LessonDAO
from services.lesson_service import LessonService

from dao.module_dao import ModuleDAO
from services.module_service import ModuleService

from dao.course_dao import CourseDAO
from services.course_service import CourseService

from dao.enrollment_dao import EnrollmentDAO
from services.enrollment_service import EnrollmentService

from models.answer import Answer

from config.database import db

from utils.rbac import role_required


quiz_dao = QuizDAO()
quiz_service = QuizService(quiz_dao)

question_dao = QuestionDAO()
question_service = QuestionService(question_dao)

option_dao = OptionDAO()
option_service = OptionService(option_dao)

submission_dao = QuizSubmissionDAO()
submission_service = QuizSubmissionService(
    submission_dao
)

lesson_dao = LessonDAO()
lesson_service = LessonService(lesson_dao)

module_dao = ModuleDAO()
module_service = ModuleService(module_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

enrollment_dao = EnrollmentDAO()
enrollment_service = EnrollmentService(
    enrollment_dao
)


# --------------------------------------------------
# SERIALIZERS
# --------------------------------------------------

def option_to_dict(option):
    return {
        "id": option.id,
        "question_id": option.question_id,
        "option_text": option.option_text,
        "is_correct": option.is_correct
    }


def question_to_dict(question):
    options = option_service.get_question_options(
        question.id
    )

    return {
        "id": question.id,
        "quiz_id": question.quiz_id,
        "question_text": question.question_text,
        "difficulty": question.difficulty,
        "explanation": question.explanation,
        "options": [
            option_to_dict(option)
            for option in options
        ]
    }


def submission_to_dict(
    submission,
    total_questions=None
):
    percentage = None

    if total_questions is not None:
        percentage = (
            (submission.score / total_questions) * 100
            if total_questions > 0
            else 0
        )

    return {
        "id": submission.id,
        "quiz_id": submission.quiz_id,
        "student_id": submission.student_id,
        "score": submission.score,
        "total_questions": total_questions,
        "percentage": percentage,
        "submitted_at": (
            submission.submitted_at.isoformat()
            if submission.submitted_at
            else None
        )
    }


def get_quiz_course(quiz_id):

    quiz = quiz_service.get_quiz(
        quiz_id
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

    return quiz, lesson, module, course


# --------------------------------------------------
# TAKE QUIZ
# --------------------------------------------------

@api_v2.route(
    "/quizzes/<int:quiz_id>/take",
    methods=["GET"]
)
@jwt_required()
@role_required("student")
def take_quiz(quiz_id):

    try:
        quiz, lesson, module, course = (
            get_quiz_course(quiz_id)
        )

        current_user_id = int(
            get_jwt_identity()
        )

        enrollment = (
            enrollment_service.get_enrollment(
                current_user_id,
                course.id
            )
        )

        if not (
            enrollment
            and enrollment.status.lower() == "active"
        ):
            return jsonify({
                "error": "You must be enrolled in this course"
            }), 403

        questions = (
            question_service.get_quiz_questions(
                quiz_id
            )
        )

        return jsonify({
            "quiz": {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "lesson_id": quiz.lesson_id
            },
            "questions": [
                question_to_dict(question)
                for question in questions
            ]
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# --------------------------------------------------
# SUBMIT QUIZ
# --------------------------------------------------

@api_v2.route(
    "/quizzes/<int:quiz_id>/submit",
    methods=["POST"]
)
@jwt_required()
@role_required("student")
def submit_quiz(quiz_id):

    data = request.get_json(
        silent=True
    )

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:
        quiz, lesson, module, course = (
            get_quiz_course(quiz_id)
        )

        current_user_id = int(
            get_jwt_identity()
        )

        enrollment = (
            enrollment_service.get_enrollment(
                current_user_id,
                course.id
            )
        )

        if not (
            enrollment
            and enrollment.status.lower() == "active"
        ):
            return jsonify({
                "error": "You must be enrolled in this course"
            }), 403

        answers = data.get(
            "answers"
        )

        if not isinstance(answers, list):
            return jsonify({
                "error": "answers must be a list"
            }), 400

        questions = (
            question_service.get_quiz_questions(
                quiz_id
            )
        )

        score = 0
        selected_answers = []

        for answer_data in answers:

            question_id = answer_data.get(
                "question_id"
            )

            option_id = answer_data.get(
                "option_id"
            )

            if not question_id or not option_id:
                return jsonify({
                    "error": "Each answer requires question_id and option_id"
                }), 400

            # Make sure question belongs to this quiz
            question = next(
                (
                    q for q in questions
                    if q.id == question_id
                ),
                None
            )

            if not question:
                return jsonify({
                    "error": "Invalid question for this quiz"
                }), 400

            options = (
                option_service.get_question_options(
                    question_id
                )
            )

            selected_option = next(
                (
                    option
                    for option in options
                    if option.id == option_id
                ),
                None
            )

            if not selected_option:
                return jsonify({
                    "error": "Invalid option for question"
                }), 400

            if selected_option.is_correct:
                score += 1

            selected_answers.append({
                "question_id": question_id,
                "option_id": option_id
            })

        submission = (
            submission_service.create_submission(
                quiz_id,
                current_user_id,
                score
            )
        )

        for selected_answer in selected_answers:

            answer = Answer(
                submission_id=submission.id,
                question_id=selected_answer[
                    "question_id"
                ],
                selected_option_id=selected_answer[
                    "option_id"
                ]
            )

            db.session.add(answer)

        db.session.commit()

        total = len(questions)

        return jsonify({
            "message": "Quiz submitted successfully",
            "result": submission_to_dict(
                submission,
                total
            )
        }), 201

    except ValueError as e:
        db.session.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------------------------
# VIEW SINGLE RESULT
# --------------------------------------------------

@api_v2.route(
    "/quiz-submissions/<int:submission_id>",
    methods=["GET"]
)
@jwt_required()
def get_quiz_result(submission_id):

    try:
        submission = (
            submission_service.get_submission(
                submission_id
            )
        )

        current_user_id = int(
            get_jwt_identity()
        )

        quiz = quiz_service.get_quiz(
            submission.quiz_id
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

        # Student can only see own result
        if submission.student_id != current_user_id:

            # Instructor can see results
            if course.instructor_id != current_user_id:
                return jsonify({
                    "error": "Access denied"
                }), 403

        questions = (
            question_service.get_quiz_questions(
                submission.quiz_id
            )
        )

        total = len(questions)

        return jsonify({
            "quiz": {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description
            },
            "result": submission_to_dict(
                submission,
                total
            )
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# --------------------------------------------------
# STUDENT QUIZ HISTORY
# --------------------------------------------------

@api_v2.route(
    "/student/quiz-results",
    methods=["GET"]
)
@jwt_required()
@role_required("student")
def student_quiz_results():

    try:
        current_user_id = int(
            get_jwt_identity()
        )

        submissions = (
            submission_service.get_student_submissions(
                current_user_id
            )
        )

        results = []

        for submission in submissions:

            questions = (
                question_service.get_quiz_questions(
                    submission.quiz_id
                )
            )

            total = len(questions)

            quiz = quiz_service.get_quiz(
                submission.quiz_id
            )

            results.append({
                "quiz": {
                    "id": quiz.id,
                    "title": quiz.title
                },
                "result": submission_to_dict(
                    submission,
                    total
                )
            })

        return jsonify({
            "results": results
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# --------------------------------------------------
# INSTRUCTOR: VIEW QUIZ SUBMISSIONS
# --------------------------------------------------

@api_v2.route(
    "/quizzes/<int:quiz_id>/submissions",
    methods=["GET"]
)
@jwt_required()
@role_required("instructor")
def get_quiz_submissions(quiz_id):

    try:
        quiz, lesson, module, course = (
            get_quiz_course(quiz_id)
        )

        current_user_id = int(
            get_jwt_identity()
        )

        if course.instructor_id != current_user_id:
            return jsonify({
                "error": "You can only view results for your own quizzes"
            }), 403

        # Get all submissions for the quiz.
        # If your DAO doesn't have this method yet,
        # we will add it next.
        submissions = (
            submission_dao.get_quiz_submissions(
                quiz_id
            )
        )

        questions = (
            question_service.get_quiz_questions(
                quiz_id
            )
        )

        total = len(questions)

        return jsonify({
            "quiz": {
                "id": quiz.id,
                "title": quiz.title
            },
            "submissions": [
                submission_to_dict(
                    submission,
                    total
                )
                for submission in submissions
            ]
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404