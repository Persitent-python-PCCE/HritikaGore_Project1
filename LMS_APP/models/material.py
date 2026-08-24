from config.database import db

class Material(db.Model):
    __tablename__ = "materials"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    material_type = db.Column(db.String(50), nullable=False)
    course_id = db.Column(db.Integer,db.ForeignKey("courses.id"),nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=True)
    uploaded_by = db.Column(db.Integer,db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column( db.DateTime, server_default=db.func.now())