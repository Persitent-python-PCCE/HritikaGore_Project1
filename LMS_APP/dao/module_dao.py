from models.module import Module
from config.database import db

class ModuleDAO:
    def create_module(self, module):
        db.session.add(module)
        db.session.commit()
        return module

    def get_module_by_id(self, module_id):
        return db.session.get(Module, module_id)

    def get_modules_by_course(self, course_id):
        return Module.query.filter_by(
            course_id=course_id
        ).all()

    def update_module(self, module):
        db.session.commit()
        return module

    def delete_module(self, module):
        db.session.delete(module)
        db.session.commit()