from config.database import db

class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer,db.ForeignKey("courses.id"), nullable=False)
    enrolled_at = db.Column(db.DateTime,server_default=db.func.now())
    status = db.Column(db.String(20), nullable=False,default="active")
    
    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "course_id",
            name="unique_student_course"
        ),
    )