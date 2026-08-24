from config.database import db

class Module(db.Model):
    __tablename__ = "modules"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150),nullable=False)
    description = db.Column(db.Text,nullable=False)
    course_id = db.Column(db.Integer,db.ForeignKey("courses.id"),nullable=False)
    created_at = db.Column(db.DateTime,server_default=db.func.now())