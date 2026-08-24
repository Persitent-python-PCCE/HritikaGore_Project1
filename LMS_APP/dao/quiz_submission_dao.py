from models.quiz_submission import QuizSubmission
from config.database import db

class QuizSubmissionDAO:
    def create_submission(self, submission):
        db.session.add(submission)
        db.session.commit()
        return submission

    def get_submission_by_id(self, submission_id):
        return QuizSubmission.query.get(submission_id)

    def get_student_submissions(self, student_id):
        return QuizSubmission.query.filter_by(
            student_id=student_id
        ).all()

    def get_quiz_submissions(self, quiz_id):
        return QuizSubmission.query.filter_by(
            quiz_id=quiz_id
        ).all()