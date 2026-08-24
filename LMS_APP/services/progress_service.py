from datetime import datetime
from models.progress import Progress

class ProgressService:
    def __init__(self, progress_dao):
        self.progress_dao = progress_dao

    def complete_lesson(self, student_id, lesson_id):
        progress = self.progress_dao.get_progress(student_id,lesson_id)

        if progress:
            progress.completed = True
            progress.completed_at = datetime.utcnow()

            return self.progress_dao.update_progress( progress)

        progress = Progress(
            student_id=student_id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.utcnow()
        )

        return self.progress_dao.create_progress(progress)

    def get_student_progress(self, student_id):
        return self.progress_dao.get_student_progress(student_id)

    def get_completed_lessons(self, student_id):
        return self.progress_dao.get_completed_lessons( student_id)

    def get_course_progress(
        self,
        student_id,
        course_id,
        module_service,
        lesson_service
    ):

        modules = module_service.get_course_modules(
            course_id
        )

        total_lessons = 0
        completed_lessons = 0

        completed_progress = (
            self.progress_dao.get_completed_lessons(
                student_id
            )
        )

        completed_lesson_ids = {
            progress.lesson_id
            for progress in completed_progress
        }

        for module in modules:

            lessons = lesson_service.get_module_lesson(
                module.id
            )

            total_lessons += len(lessons)

            for lesson in lessons:

                if lesson.id in completed_lesson_ids:
                    completed_lessons += 1

        if total_lessons == 0:
            percentage = 0
        else:
            percentage = (
                completed_lessons / total_lessons
            ) * 100

        return {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "percentage": percentage
        }