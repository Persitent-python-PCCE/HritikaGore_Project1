from models.material import Material
from config.database import db

class MaterialDAO:
    def create_material(self, material):
        try:
            db.session.add(material)
            db.session.commit()
            return material
        except Exception:
            db.session.rollback()
            raise

    def get_material(self, material_id):
        return db.session.get(Material, material_id)

    def get_course_materials(self, course_id):
        return (
            db.session.query(Material)
            .filter(Material.course_id == course_id)
            .order_by(Material.id.desc())
            .all()
        )

    def update_material(self, material):
        try:
            db.session.commit()
            return material
        except Exception:
            db.session.rollback()
            raise

    def delete_material(self, material):
        try:
            db.session.delete(material)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise