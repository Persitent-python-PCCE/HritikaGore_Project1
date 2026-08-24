from models.course import Course

class CourseService:
    def __init__(self, course_dao):
        self.course_dao = course_dao

    def create_course(self, title, description, instructor_id):
        if not title or not title.strip():
            raise ValueError("Course title is required")

        if not description or not description.strip():
            raise ValueError("Course description is required")

        if not instructor_id:
            raise ValueError("Instructor is required")

        course = Course(
            title = title.strip(),
            description= description.strip(),
            instructor_id=instructor_id
        )
        return self.course_dao.create_course(course)


    def get_all_courses(self):
        return self.course_dao.get_all_courses()

    def get_course(self, course_id):
        course = self.course_dao.get_course_by_id(course_id)

        if not course:
            raise ValueError("Course not found")
        return course

    def get_instructor_courses(self, instructor_id):
        return self.course_dao.get_courses_by_instructor(instructor_id)

    def update_course(self, course_id, title, description):
        course = self.get_course(course_id)

        if not title or not title.strip():
            raise ValueError("Course title is required")

        if not description or not description.strip():
            raise ValueError("Course description is required")

        course.title = title.strip()
        course.description = description.strip()

        return self.course_dao.update_course(course)

    def delete_course(self, course_id):
        course = self.get_course(course_id)
        self.course_dao.delete_course(course)
