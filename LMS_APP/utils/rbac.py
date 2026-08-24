from functools import wraps

from flask import jsonify, render_template, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def role_required(*allowed_roles):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()

            claims = get_jwt()
            role = claims.get("role")

            if role not in allowed_roles:
                if request_wants_json():
                    return jsonify({
                        "message": "Access Denied",
                        "error": "INSUFFICIENT_ROLE"
                    }), 403

                return render_template("403.html"), 403
            return function(*args, **kwargs)
        return wrapper
    return decorator


def request_wants_json():
    return (
        request.path.startswith("/api/") or request.headers.get(
            "Accept",
            ""
        ).startswith("application/json")
    )