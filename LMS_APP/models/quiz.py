from config.database import db

class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer,primary_key=True)
    lesson_id = db.Column(db.Integer,db.ForeignKey("lesson.id"),nullable=False)
    title = db.Column(db.String(200),nullable=False)
    description = db.Column(db.Text,nullable=False)
    created_by = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    created_at = db.Column(db.DateTime,server_default=db.func.now())