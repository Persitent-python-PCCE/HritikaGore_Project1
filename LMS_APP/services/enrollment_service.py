from models.enrollment import Enrollment


class EnrollmentService:

    def __init__(self, enrollment_dao):
        self.enrollment_dao = enrollment_dao


    def enroll_students(self, student_id, course_id):

        existing = self.enrollment_dao.get_enrollment(
            student_id,
            course_id
        )

        if existing:

            if existing.status.lower() == "active":

                raise ValueError(
                    "You have already enrolled for this course"
                )

            # Reactivate inactive enrollment
            existing.status = "ACTIVE"

            from config.database import db
            db.session.commit()

            return existing

        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            status="ACTIVE"
        )

        return self.enrollment_dao.create_enrollment(
            enrollment
        )


    def get_student_enrollment(self, student_id):

        return self.enrollment_dao.get_student_enrollment(
            student_id
        )

    def get_enrollment(self, student_id, course_id):
        return self.enrollment_dao.get_enrollment(
            student_id,
            course_id
        )