from models.lesson import Lesson

class LessonService:
    def __init__(self, lesson_dao):
        self.lesson_dao=lesson_dao

    def create_lesson(self, title, content, module_id):
        if not title or not title.strip():
            raise ValueError("Title is required")

        if not content or not content.strip():
            raise ValueError(" Lesson Content is required")

        if not module_id:
            raise ValueError("Module id is required")

        lesson = Lesson(
            title=title.strip(),
            content=content.strip(),
            module_id=module_id
        )

        return self.lesson_dao.create_lesson(lesson)

    def get_lesson(self, lesson_id):
        lesson = self.lesson_dao.get_lesson_by_id(lesson_id)

        if not lesson:
            raise ValueError("Lesson not found")

        return lesson

    def get_module_lesson(self, module_id):
        return self.lesson_dao.get_lesson_by_module(module_id)

    def update_lesson(self, lesson_id, title, content):
        lesson = self.lesson_dao.get_lesson_by_id(lesson_id)

        if not lesson:
            raise ValueError("Lesson not found")

        if not title or not title.strip():
            raise ValueError("Lesson title is required")

        if not content or not content.strip():
            raise ValueError("Lesson content is required")

        lesson.title = title.strip()
        lesson.content = content.strip()

        return self.lesson_dao.update_lesson(lesson)

    def delete_lesson(self, lesson_id):
        lesson = self.get_lesson(lesson_id)
        self.lesson_dao.delete_lesson(lesson)
