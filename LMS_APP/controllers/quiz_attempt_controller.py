from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session, 
    abort
)
from dao.lesson_dao import LessonDAO
from services.lesson_service import LessonService
from dao.module_dao import ModuleDAO
from services.module_service import ModuleService
from dao.course_dao import CourseDAO
from services.course_service import CourseService
from dao.quiz_dao import QuizDAO
from services.quiz_service import QuizService

from dao.question_dao import QuestionDAO
from services.question_service import QuestionService

from dao.option_dao import OptionDAO
from services.option_service import OptionService

from dao.quiz_submission_dao import QuizSubmissionDAO
from services.quiz_submission_service import QuizSubmissionService

from models.answer import Answer
from config.database import db

quiz_attempt_controller = Blueprint( "quiz_attempt_controller", __name__)

quiz_service = QuizService(QuizDAO())
question_service = QuestionService(QuestionDAO())
option_service = OptionService(OptionDAO())
lesson_service = LessonService(LessonDAO())
module_service = ModuleService(ModuleDAO())
course_service = CourseService(CourseDAO())
submission_service = QuizSubmissionService(QuizSubmissionDAO())


@quiz_attempt_controller.route("/quizzes/<int:quiz_id>/take")
def take_quiz(quiz_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    if session.get("user_role") != "student":
        abort(403)

    try:
        quiz = quiz_service.get_quiz(quiz_id)

        questions = (question_service.get_quiz_questions(quiz_id))

        question_options = {}

        for question in questions:
            question_options[question.id] = (
                option_service.get_question_options(
                    question.id
                )
            )

        return render_template(
            "take_quiz.html",
            quiz=quiz,
            questions=questions,
            question_options=question_options
        )

    except ValueError as e:
        return str(e), 404

@quiz_attempt_controller.route("/quizzes/<int:quiz_id>/submit",methods=["POST"])
def submit_quiz(quiz_id):

    if "user_id" not in session:
        return redirect(
            url_for("auth_controller.login")
        )

    if session.get("user_role") != "student":
        abort(403)

    try:
        quiz = quiz_service.get_quiz(quiz_id)

        questions = (
            question_service.get_quiz_questions(
                quiz_id
            )
        )

        score = 0
        selected_answers = []

        for question in questions:
            selected_option_id = request.form.get(f"question_{question.id}")

            if not selected_option_id:
                continue

            selected_option_id = int(selected_option_id)

            options = option_service.get_question_options(question.id)

            selected_option = next(
                (
                    option
                    for option in options
                    if option.id == selected_option_id
                ),
                None
            )

            if not selected_option:
                return "Invalid option", 400

            if selected_option.is_correct:
                score += 1

            selected_answers.append(
                (
                    question.id,
                    selected_option_id
                )
            )

        submission = (
            submission_service.create_submission(
                quiz_id,
                session["user_id"],
                score
            )
        )

        for question_id, option_id in selected_answers:

            answer = Answer(
                submission_id=submission.id,
                question_id=question_id,
                selected_option_id=option_id
            )

            db.session.add(answer)

        db.session.commit()

        return redirect(
            url_for(
                "quiz_attempt_controller.quiz_result",
                submission_id=submission.id
            )
        )

    except ValueError as e:
        return str(e), 404

@quiz_attempt_controller.route("/quiz-submissions/<int:submission_id>/result")
def quiz_result(submission_id):
    if "user_id" not in session:
        return redirect( url_for("auth_controller.login"))

    if session.get("user_role") != "student":
        abort(403)

    try:
        submission = (
            submission_service.get_submission(
                submission_id
            )
        )

        if submission.student_id != session["user_id"]:
            abort(403)

        quiz = quiz_service.get_quiz(
            submission.quiz_id
        )

        questions = (
            question_service.get_quiz_questions(
                submission.quiz_id
            )
        )

        total = len(questions)

        percentage = (
            (submission.score / total) * 100
            if total > 0
            else 0
        )

        return render_template(
            "quiz_result.html",
            submission=submission,
            quiz=quiz,
            total=total,
            percentage=percentage
        )

    except ValueError as e:
        return str(e), 404


@quiz_attempt_controller.route("/student/quiz-results")
def student_quiz_results():
    if "user_id" not in session:
        return redirect(
            url_for("auth_controller.login")
        )

    if session.get("user_role") != "student":
        abort(403)

    submissions = (
        submission_service.get_student_submissions(
            session["user_id"]
        )
    )

    results = []

    for submission in submissions:

        quiz = quiz_service.get_quiz(
            submission.quiz_id
        )

        questions = (
            question_service.get_quiz_questions(
                submission.quiz_id
            )
        )

        total = len(questions)

        percentage = (
            (submission.score / total) * 100
            if total > 0
            else 0
        )

        results.append({
            "submission": submission,
            "quiz": quiz,
            "total": total,
            "percentage": percentage
        })

    return render_template(
        "student_quiz_results.html",
        results=results
    )


@quiz_attempt_controller.route("/my-quiz-results")
def my_quiz_results():
    if "user_id" not in session:
        return redirect(
            url_for("auth_controller.login")
        )

    if session.get("user_role") != "student":
        abort(403)

    submissions = submission_service.get_student_submissions(
        session["user_id"]
    )

    return render_template("quiz_history.html",submissions=submissions)

@quiz_attempt_controller.route("/quizzes/<int:quiz_id>/submissions")
def quiz_submissions(quiz_id):
    if "user_id" not in session:
        return redirect(
            url_for("auth_controller.login")
        )

    if session.get("user_role") != "instructor":
        abort(403)

    try:
        quiz = quiz_service.get_quiz(quiz_id)

        lesson = lesson_service.get_lesson(quiz.lesson_id)
        module = module_service.get_module(lesson.module_id)
        course = course_service.get_course(module.course_id)

        if course.instructor_id != session["user_id"]:
            return "Access Denied", 403

        submissions = (
            submission_service.get_quiz_submissions(
                quiz_id
            )
        )

        return render_template("quiz_submissions.html",quiz=quiz,submissions=submissions)

    except ValueError as e:
        return str(e), 404

