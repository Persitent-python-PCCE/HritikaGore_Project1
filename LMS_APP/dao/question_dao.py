from models.question import Question
from config.database import db

class QuestionDAO:
    def create_question(self, question):
        db.session.add(question)
        db.session.commit()
        return question

    def get_question_by_id(self, question_id):
        return Question.query.get(question_id)

    def get_question_by_quiz(self, quiz_id):
        return Question.query.filter_by(quiz_id=quiz_id).all()

    def update_question(self, question):
        db.session.commit()
        return question

    def delete_question(self, question):
        db.session.delete(question)
        db.session.commit()

            