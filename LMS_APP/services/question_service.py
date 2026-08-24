from models.question import Question

class QuestionService:
    def __init__(self, question_dao):
        self.question_dao = question_dao

    def create_question(self, question_text, difficulty, explanation,quiz_id):
        if not question_text or not question_text.strip():
            raise ValueError("Question text is required")

        if not quiz_id:
            raise ValueError("Quiz is required")

        if difficulty not in ["easy", "medium", "hard"]:
            raise ValueError("Invalid difficulty")

        question = Question(
            question_text=question_text.strip(),
            difficulty=difficulty,
            explanation=(
                explanation.strip()
                if explanation
                else None
            ),
            quiz_id=quiz_id
        )

        return self.question_dao.create_question(
            question
        )

    def get_question(self, question_id):

        question = self.question_dao.get_question_by_id(
            question_id
        )

        if not question:
            raise ValueError("Question not found")

        return question

    def get_quiz_questions(self, quiz_id):

        return self.question_dao.get_question_by_quiz(
            quiz_id
        )

    def update_question(
        self,
        question_id,
        question_text,
        difficulty,
        explanation
    ):

        question = self.get_question(
            question_id
        )

        if not question_text or not question_text.strip():
            raise ValueError("Question text is required")

        if difficulty not in ["easy", "medium", "hard"]:
            raise ValueError("Invalid difficulty")

        question.question_text = question_text.strip()

        question.difficulty = difficulty

        question.explanation = (
            explanation.strip()
            if explanation
            else None
        )

        return self.question_dao.update_question(
            question
        )

    def delete_question(self, question_id):

        question = self.get_question(
            question_id
        )

        self.question_dao.delete_question(
            question
        )