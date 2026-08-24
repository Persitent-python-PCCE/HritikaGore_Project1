from pathlib import Path

from rag.document_loader import extract_text_from_pdf
from rag.chunker import chunk_text
from rag.embeddings import (
    create_embeddings,
    create_query_embedding
)
from rag.vector_store import VectorStore
from rag.llm import GeminiLLM


class RAGService:

    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = GeminiLLM()

        # Track which course the current FAISS index belongs to
        self.indexed_course_id = None

    # =========================================================
    # INDEX COURSE MATERIALS
    # =========================================================

    def index_course_materials(
        self,
        course_id,
        materials
    ):
        """
        Index all PDF materials belonging to one course.

        materials should contain Material model objects.
        """

        all_chunks = []

        for material in materials:

            # RAG currently supports PDF files
            file_path = material.file_path

            if not file_path:
                continue

            if not file_path.lower().endswith(".pdf"):
                continue

            # material.file_path looks like:
            #
            # uploads/1/Python_Level1_Practice_Sheet.pdf
            #
            # Convert it to an absolute filesystem path.

            pdf_path = Path(file_path)

            if not pdf_path.is_absolute():
                pdf_path = Path.cwd() / pdf_path

            if not pdf_path.exists():
                print(
                    f"RAG: File not found: {pdf_path}"
                )
                continue

            try:

                pages = extract_text_from_pdf(
                    pdf_path
                )

                chunks = chunk_text(
                    pages
                )

                for chunk in chunks:

                    # Add material information to each chunk
                    chunk["material_id"] = material.id
                    chunk["material_title"] = material.title
                    chunk["course_id"] = course_id
                    chunk["source"] = material.title

                all_chunks.extend(chunks)

            except Exception as error:

                print(
                    f"RAG: Failed to index "
                    f"{material.title}: {error}"
                )

        if not all_chunks:

            raise ValueError(
                "No readable PDF course materials "
                "were found for this course."
            )

        texts = [
            chunk["text"]
            for chunk in all_chunks
        ]

        embeddings = create_embeddings(
            texts
        )

        self.vector_store.build(
            embeddings,
            all_chunks
        )

        self.indexed_course_id = course_id

        return {
            "course_id": course_id,
            "materials": len(materials),
            "chunks": len(all_chunks)
        }

    # =========================================================
    # SEARCH
    # =========================================================

    def search(
        self,
        question,
        top_k=5
    ):

        if self.indexed_course_id is None:

            raise RuntimeError(
                "No course material has been indexed."
            )

        if not question.strip():
            return []

        query_embedding = create_query_embedding(
            question.strip()
        )

        return self.vector_store.search(
            query_embedding,
            top_k=top_k
        )

    # =========================================================
    # FILTER RESULTS
    # =========================================================

    def _filter_results(
        self,
        results,
        min_score=0.40
    ):

        filtered = []
        seen = set()

        for result in results:

            score = result.get(
                "score",
                0
            )

            text = result.get(
                "text",
                ""
            ).strip()

            if not text:
                continue

            if score < min_score:
                continue

            normalized = " ".join(
                text.split()
            ).lower()

            if normalized in seen:
                continue

            seen.add(normalized)

            filtered.append(result)

        return filtered

    # =========================================================
    # BUILD CONTEXT
    # =========================================================

    def build_context(
        self,
        results
    ):

        context_parts = []

        for result in results:

            source = result.get(
                "source",
                result.get(
                    "material_title",
                    "Course Material"
                )
            )

            page = result.get(
                "page",
                "Unknown"
            )

            text = result.get(
                "text",
                ""
            ).strip()

            context_parts.append(
                f"""
SOURCE: {source}
PAGE: {page}

{text}
"""
            )

        return "\n\n".join(
            context_parts
        )

    # =========================================================
    # ANSWER
    # =========================================================

    def answer(
        self,
        question,
        top_k=5
    ):

        results = self.search(
            question,
            top_k=top_k
        )

        results = self._filter_results(
            results,
            min_score=0.40
        )

        if not results:

            return {
                "question": question,
                "answer": (
                    "I couldn't find enough information "
                    "in this course's material to answer "
                    "that question."
                ),
                "sources": [],
                "context": ""
            }

        context = self.build_context(
            results
        )

        answer = self.llm.generate_answer(
            question,
            context
        )

        sources = []

        for result in results:

            sources.append({
                "source": result.get(
                    "source",
                    result.get(
                        "material_title",
                        "Course Material"
                    )
                ),
                "page": result.get(
                    "page",
                    "Unknown"
                ),
                "score": round(
                    result.get(
                        "score",
                        0
                    ),
                    4
                )
            })

        return {
            "question": question,
            "answer": answer,
            "context": context,
            "sources": sources
        }

    # =========================================================
    # BACKWARD COMPATIBILITY
    # =========================================================

    def answer_from_context(
        self,
        question,
        top_k=3
    ):

        return self.answer(
            question,
            top_k=top_k
        )

    def answer_without_llm(
        self,
        question,
        top_k=3
    ):

        return self.answer(
            question,
            top_k=top_k
        )