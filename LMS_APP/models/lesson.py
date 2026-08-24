from config.database import db

class Lesson(db.Model):
    __tablename__ = "lesson"

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(150), nullable = False)
    content = db.Column(db.Text, nullable = False)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default= db.func.now())
