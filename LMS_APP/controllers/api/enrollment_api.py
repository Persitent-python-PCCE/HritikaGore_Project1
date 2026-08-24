from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from controllers.api import api_v2

from dao.enrollment_dao import EnrollmentDAO
from services.enrollment_service import EnrollmentService

from dao.course_dao import CourseDAO
from services.course_service import CourseService

from utils.rbac import role_required


enrollment_dao = EnrollmentDAO()
enrollment_service = EnrollmentService(enrollment_dao)

course_dao = CourseDAO()
course_service = CourseService(course_dao)


# ============================================================
# ENROLL IN COURSE
# ============================================================

@api_v2.route(
    "/courses/<int:course_id>/enroll",
    methods=["POST"]
)
@jwt_required()
@role_required("student")
def enroll_course(course_id):

    student_id = int(get_jwt_identity())

    try:

        # Make sure course exists
        course_service.get_course(course_id)

        enrollment = enrollment_service.enroll_students(
            student_id,
            course_id
        )

        return jsonify({
            "message": "Course enrollment successful",
            "enrollment": {
                "id": enrollment.id,
                "student_id": enrollment.student_id,
                "course_id": enrollment.course_id,
                "status": enrollment.status,
                "enrolled_at": (
                    enrollment.enrolled_at.isoformat()
                    if enrollment.enrolled_at
                    else None
                )
            }
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400


# ============================================================
# MY ENROLLED COURSES
# ============================================================

@api_v2.route(
    "/my-courses",
    methods=["GET"]
)
@jwt_required()
@role_required("student")
def my_courses():

    student_id = int(get_jwt_identity())

    enrollments = enrollment_service.get_student_enrollment(
        student_id
    )

    results = []

    for enrollment in enrollments:

        try:
            course = course_service.get_course(
                enrollment.course_id
            )

            results.append({
                "enrollment_id": enrollment.id,
                "course_id": course.id,
                "course_title": course.title,
                "course_description": course.description,
                "status": enrollment.status,
                "enrolled_at": (
                    enrollment.enrolled_at.isoformat()
                    if enrollment.enrolled_at
                    else None
                )
            })

        except ValueError:
            # Skip orphaned enrollment records
            continue

    return jsonify(results), 200


# ============================================================
# CHECK ENROLLMENT
# ============================================================

@api_v2.route(
    "/courses/<int:course_id>/enrollment",
    methods=["GET"]
)
@jwt_required()
@role_required("student")
def check_enrollment(course_id):

    student_id = int(get_jwt_identity())

    # Make sure course exists
    try:
        course_service.get_course(course_id)
    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404

    enrollment = enrollment_service.get_enrollment(
        student_id,
        course_id
    )

    if not enrollment:
        return jsonify({
            "enrolled": False,
            "course_id": course_id
        }), 200

    return jsonify({
        "enrolled": True,
        "enrollment": {
            "id": enrollment.id,
            "student_id": enrollment.student_id,
            "course_id": enrollment.course_id,
            "status": enrollment.status,
            "enrolled_at": (
                enrollment.enrolled_at.isoformat()
                if enrollment.enrolled_at
                else None
            )
        }
    }), 200