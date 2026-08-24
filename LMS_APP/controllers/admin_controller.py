from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from flask_jwt_extended import jwt_required
from dao.user_dao import UserDAO
from services.admin_user_service import AdminUserService
from utils.rbac import role_required

admin_controller = Blueprint("admin_controller",__name__,url_prefix="/admin")
user_dao = UserDAO()

admin_user_service = AdminUserService(user_dao)


@admin_controller.route("/users")
@jwt_required()
@role_required("admin")
def users():
    users = user_dao.get_all_users()
    return render_template("admin_users.html",users=users)


@admin_controller.route("/users/create", methods=["GET", "POST"])
@jwt_required()
@role_required("admin")
def create_user():
    if request.method == "GET":
        return render_template("admin_create_user.html")

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")

    try:
        admin_user_service.create_user(
            name,
            email,
            password,
            role
        )

        return redirect(url_for("admin_controller.users"))

    except ValueError as e:
        return render_template("admin_create_user.html",error=str(e))