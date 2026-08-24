from config.database import db
from models.progress import Progress

class ProgressDAO:
    def get_progress(self, student_id, lesson_id):
        return Progress.query.filter_by(
            student_id=student_id,
            lesson_id=lesson_id
        ).first()

    def create_progress(self, progress):
        db.session.add(progress)
        db.session.commit()
        return progress

    def update_progress(self, progress):
        db.session.commit()
        return progress

    def get_student_progress(self, student_id):
        return Progress.query.filter_by(
            student_id=student_id
        ).all()

    def get_completed_lessons(self, student_id):
        return Progress.query.filter_by( student_id=student_id, completed=True).all()