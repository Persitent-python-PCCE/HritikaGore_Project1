from models.module import Module

class ModuleService:
    def __init__(self, module_dao):
        self.module_dao = module_dao

    def create_module(self, title, description, course_id):
        if not title or not title.strip():
            raise ValueError("Module title is required")

        if not description or not description.strip():
            raise ValueError("Module description is required")

        if not course_id:
            raise ValueError("Course is required")

        module = Module(title=title.strip(), description=description.strip(), course_id=course_id)

        return self.module_dao.create_module(module)

    def get_module(self, module_id):
        module = self.module_dao.get_module_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        return module

    def get_course_modules(self, course_id):
        return self.module_dao.get_modules_by_course(course_id)

    def update_module(self, module_id, title, description):
        module = self.get_module(module_id)

        if not title or not title.strip():
            raise ValueError("Module title is required")

        if not description or not description.strip():
            raise ValueError("Module description is required")

        module.title = title.strip()
        module.description = description.strip()

        return self.module_dao.update_module(module)

    def delete_module(self, module_id):
        module = self.get_module(module_id)
        self.module_dao.delete_module(module)