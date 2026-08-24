from models.course import Course
from models.enrollment import Enrollment
from config.database import db

class CourseDAO:
    def create_course(self, course):
        db.session.add(course)
        db.session.commit()
        return course

    def get_course_by_id(self, course_id):
        return db.session.get(Course, course_id)

    def get_all_courses(self):
        return Course.query.all()

    def get_courses_by_instructor(self, instructor_id):
        return Course.query.filter_by(
            instructor_id=instructor_id
        ).all()

    def update_course(self, course):
        db.session.commit()
        return course

    def delete_course(self, course):
        Enrollment.query.filter_by(course_id=course.id).delete(synchronize_session=False)
        db.session.delete(course)
        db.session.commit()