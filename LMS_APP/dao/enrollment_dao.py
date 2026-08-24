from models.enrollment import Enrollment
from config.database import db

class EnrollmentDAO:
    def create_enrollment(self, enrollment):
        db.session.add(enrollment)
        db.session.commit()
        return enrollment

    def get_enrollment(self, student_id, course_id):
        return Enrollment.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()

    def get_student_enrollment(self, student_id):
        return Enrollment.query.filter_by(
            student_id=student_id
        ).all()

    def delete_enrollment(self, enrollment):
        db.session.delete(enrollment)
        db.session.commit()