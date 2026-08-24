from config.database import db

class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("quiz_submissions.id"), nullable=False)
    question_id = db.Column(db.Integer,db.ForeignKey("questions.id"),nullable=False)
    selected_option_id = db.Column(db.Integer,db.ForeignKey("options.id"),nullable=False)