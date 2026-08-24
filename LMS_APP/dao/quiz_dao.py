from models.quiz import Quiz
from config.database import db

class QuizDAO:
    def create_quiz(self, quiz):
        db.session.add(quiz)
        db.session.commit()
        return quiz

    def get_quiz_by_id(self, quiz_id):
        return Quiz.query.get(quiz_id)

    def get_quizzes_by_lesson(self, lesson_id):
        return Quiz.query.filter_by(
            lesson_id=lesson_id
        ).all()

    def get_quizzes_by_course(self, course_id):
        from models.lesson import Lesson
        from models.module import Module

        return Quiz.query.join(
            Lesson,
            Quiz.lesson_id == Lesson.id
        ).join(
            Module,
            Lesson.module_id == Module.id
        ).filter(
            Module.course_id == course_id
        ).all()

    def update_quiz(self, quiz):
        db.session.commit()
        return quiz

    def delete_quiz(self, quiz):
        db.session.delete(quiz)
        db.session.commit()