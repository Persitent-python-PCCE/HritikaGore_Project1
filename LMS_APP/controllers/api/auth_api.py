from flask import request, jsonify

from flask_jwt_extended import create_access_token

from controllers.api import api_v2

from dao.user_dao import UserDAO
from services.auth_service import AuthService


user_dao = UserDAO()
auth_service = AuthService(user_dao)


@api_v2.route("/auth/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    try:

        user = auth_service.login_user(
            email,
            password
        )

        if not user.is_active:

            return jsonify({
                "error": "Account is disabled"
            }), 403

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role
            }
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }), 200

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 401