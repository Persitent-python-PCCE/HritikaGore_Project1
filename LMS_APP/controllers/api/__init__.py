from flask import Blueprint

api_v2 = Blueprint("api_v2", __name__,url_prefix="/api/v2")

from controllers.api import course_api
from controllers.api import auth_api
from controllers.api import enrollment_api
from controllers.api import module_api
from controllers.api import material_api
from controllers.api import lessons_api
from controllers.api import question_api
from controllers.api import quiz_api
from controllers.api import option_api
from controllers.api import quiz_attempt_api