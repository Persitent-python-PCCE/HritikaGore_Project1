from models.option import Option
from config.database import db

class OptionDAO:
    def create_option(self, option):
        db.session.add(option)
        db.session.commit()
        return option

    def get_option_by_id(self, option_id):
        return Option.query.get(option_id)

    def get_options_by_question(self, question_id):
        return Option.query.filter_by(question_id=question_id).all()

    def update_option(self, option):
        db.session.commit()
        return option

    def delete_option(self, option):
        db.session.delete(option)
        db.session.commit()    