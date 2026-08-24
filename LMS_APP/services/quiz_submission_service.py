from models.quiz_submission import QuizSubmission


class QuizSubmissionService:
    def __init__(self, submission_dao):
        self.submission_dao = submission_dao

    def create_submission(
        self,
        quiz_id,
        student_id,
        score
    ):
        submission = QuizSubmission(
            quiz_id=quiz_id,
            student_id=student_id,
            score=score
        )

        return self.submission_dao.create_submission(
            submission
        )

    def get_submission(self, submission_id):
        submission = (
            self.submission_dao.get_submission_by_id(
                submission_id
            )
        )

        if not submission:
            raise ValueError("Submission not found")

        return submission

    def get_student_submissions(self, student_id):
        return (
            self.submission_dao
            .get_student_submissions(student_id)
        )

    def get_quiz_submissions(self, quiz_id):
        return (
            self.submission_dao
            .get_quiz_submissions(quiz_id)
        )