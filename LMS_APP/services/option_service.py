from models.option import Option

class OptionService:
    def __init__(self, option_dao):
        self.option_dao = option_dao

    def create_option(self,option_text,question_id, is_correct=False):
        if not option_text or not option_text.strip():
            raise ValueError("Option text is required")

        if not question_id:
            raise ValueError("Question is required")

        option = Option(
            option_text=option_text.strip(),
            question_id=question_id,
            is_correct=is_correct
        )

        return self.option_dao.create_option(option)

    def get_option(self, option_id):
        option = self.option_dao.get_option_by_id(option_id)

        if not option:
            raise ValueError("Option not found")

        return option

    def get_question_options(self, question_id):
        return self.option_dao.get_options_by_question(question_id)

    def update_option(self,option_id, option_text,is_correct):
        option = self.option_dao.get_option_by_id(option_id)

        if not option:
            raise ValueError("Option not found")

        option.option_text = option_text
        option.is_correct = is_correct

        return self.option_dao.update_option(option)

    def delete_option(self, option_id):
        option = self.get_option(option_id)

        self.option_dao.delete_option(option)