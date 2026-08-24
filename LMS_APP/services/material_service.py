from models.material import Material

class MaterialService:

    ALLOWED_EXTENSIONS = {
        "pdf",
        "png",
        "jpg",
        "jpeg",
        "gif",
        "mp4",
        "avi",
        "mov",
        "doc",
        "docx",
        "ppt",
        "pptx",
        "txt"
    }

    MAX_FILE_SIZE = 50 * 1024 * 1024

    def __init__(self, material_dao):
        self.material_dao = material_dao

    def validate_file(self, filename, file_size):

        if not filename:
            raise ValueError("File is required")

        if "." not in filename:
            raise ValueError("File must have an extension")

        extension = filename.rsplit(".", 1)[1].lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                "File type not allowed. "
                "Allowed: PDF, images, videos and documents"
            )

        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                "File size must not exceed 50 MB"
            )

    def create_material(
        self,
        title,
        file_path,
        material_type,
        course_id,
        module_id,
        uploaded_by
    ):

        if not title or not title.strip():
            raise ValueError("Material title is required")

        if not file_path:
            raise ValueError("File is required")

        if not course_id:
            raise ValueError("Course is required")

        if not uploaded_by:
            raise ValueError("Uploader is required")

        material = Material(
            title=title.strip(),
            file_path=file_path,
            material_type=material_type,
            course_id=course_id,
            module_id=module_id,
            uploaded_by=uploaded_by
        )

        return self.material_dao.create_material(material)

    def get_course_materials(self, course_id):
        return self.material_dao.get_course_materials(course_id)

    def get_material(self, material_id):

        material = self.material_dao.get_material(material_id)

        if not material:
            raise ValueError("Material not found")

        return material

    def update_material(
        self,
        material_id,
        title,
        module_id=None
    ):

        material = self.get_material(material_id)

        if not title or not title.strip():
            raise ValueError("Material title is required")

        material.title = title.strip()
        material.module_id = module_id

        return self.material_dao.update_material(material)

    def delete_material(self, material_id):

        material = self.get_material(material_id)

        self.material_dao.delete_material(material)