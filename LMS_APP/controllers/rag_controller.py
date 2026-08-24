from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    abort
)

from models.material import Material

from dao.enrollment_dao import EnrollmentDAO
from services.course_service import CourseService
from dao.course_dao import CourseDAO

from rag.service import RAGService
from rag.cache import RAGCache

rag_controller = Blueprint("rag_controller", __name__,url_prefix="/rag")


rag_service = RAGService()

rag_cache = RAGCache(ttl=600)

course_dao = CourseDAO()
course_service = CourseService(course_dao)

enrollment_dao = EnrollmentDAO()


@rag_controller.route("/assistant/<int:course_id>", methods=["GET", "POST"])
def assistant(course_id):
    if "user_id" not in session:
        return redirect(url_for("auth_controller.login"))

    user_id = session["user_id"]
    role = session.get("user_role")

    try:
        course = course_service.get_course(course_id)

    except ValueError:
        return "Course not found", 404

    if role == "instructor":
        if course.instructor_id != user_id:
            abort(403)

    elif role == "student":
        enrollment = enrollment_dao.get_enrollment( user_id,course_id)

        if not enrollment:
            return ("You are not enrolled in this course",403)

        if enrollment.status.lower() != "active":
            return ("Your enrollment is not active",403)

    elif role == "admin":
        pass
    else:
        abort(403)

    materials = Material.query.filter_by(course_id=course_id).all()

    result = None
    cache_status = None

    if request.method == "POST":
        question = request.form.get("question","").strip()

        if not question:
            return render_template(
                "ai_assistant.html",
                course=course,
                course_id=course_id,
                result=None,
                cache_status=None
            )

        if len(question) > 500:
            return (
                "Question is too long. "
                "Maximum 500 characters.",
                400
            )


        result = rag_cache.get(course_id, question)

        if result:
            cache_status = "HIT"

        else:
            cache_status = "MISS"

            if (rag_service.indexed_course_id!= course_id):
                rag_service.index_course_materials(course_id,materials)

            result = rag_service.answer(question,top_k=5)

            rag_cache.set( course_id, question,result)

    return render_template(
        "ai_assistant.html",
        course=course,
        course_id=course_id,
        result=result,
        cache_status=cache_status
    )