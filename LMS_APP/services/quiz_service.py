from models.quiz import Quiz

class QuizService:
    def __init__(self, quiz_dao):
        self.quiz_dao = quiz_dao

    def create_quiz(self,title, description, lesson_id, created_by):
        if not title or not title.strip():
            raise ValueError("Quiz title is required")

        if not description or not description.strip():
            raise ValueError("Quiz description is required")

        if not lesson_id:
            raise ValueError("Lesson is required")

        if not created_by:
            raise ValueError("Creator is required")

        quiz = Quiz(
            title=title.strip(),
            description=description.strip(),
            lesson_id=lesson_id,
            created_by=created_by
        )

        return self.quiz_dao.create_quiz(quiz)

    def get_quiz(self, quiz_id):
        quiz = self.quiz_dao.get_quiz_by_id(quiz_id)

        if not quiz:
            raise ValueError("Quiz not found")

        return quiz

    def get_lesson_quizzes(self, lesson_id):
        return self.quiz_dao.get_quizzes_by_lesson(lesson_id)

    def get_course_quizzes(self, course_id):
        return self.quiz_dao.get_quizzes_by_course(
        course_id
        )

    def update_quiz(self,quiz_id,title, description):
        quiz = self.get_quiz(quiz_id)

        if not title or not title.strip():
            raise ValueError("Quiz title is required")

        if not description or not description.strip():
            raise ValueError("Quiz description is required")

        quiz.title = title.strip()
        quiz.description = description.strip()

        return self.quiz_dao.update_quiz(quiz)

    def delete_quiz(self, quiz_id):
        quiz = self.get_quiz(quiz_id)
        self.quiz_dao.delete_quiz(quiz)