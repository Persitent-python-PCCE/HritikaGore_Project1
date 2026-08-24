from config.database import db

class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer,primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), nullable=False, default="medium")
   