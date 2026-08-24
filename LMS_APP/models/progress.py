from config.database import db


class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer,primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id"),nullable=False)
    completed = db.Column(db.Boolean, nullable=False,default=False)
    completed_at = db.Column( db.DateTime,nullable=True)

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "lesson_id",
            name="unique_student_lesson_progress"
        ),
    )