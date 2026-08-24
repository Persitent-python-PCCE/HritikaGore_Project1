from models.lesson import Lesson
from config.database import db

class LessonDAO:
    def create_lesson(self, lesson):
        db.session.add(lesson)
        db.session.commit()
        return lesson

    def get_lesson_by_id(self, lesson_id):
        return db.session.get(Lesson, lesson_id)

    def get_lesson_by_module(self, module_id):
        return Lesson.query.filter_by(module_id=module_id).all()

    def update_lesson(self, lesson):
        db.session.commit()
        return lesson

    def delete_lesson(self, lesson):
        db.session.delete(lesson)
        db.session.commit()