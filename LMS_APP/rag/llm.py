import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

class GeminiLLM:
    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Check your .env file."
            )

        self.client = genai.Client(api_key=api_key)

        # Primary model
        self.model = "gemini-3.6-flash"

        # Fallback model
        self.fallback_model = "gemini-3.5-flash-lite"

    def _generate(self,model,prompt):

        response = self.client.models.generate_content(
            model=model,
            contents=prompt
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text.strip()

    def generate_answer(self,question,context):
        prompt = f"""
            You are an AI Course Assistant inside a Learning
            Management System.

            The student asked:
            {question}

            The following information was retrieved from
            the student's course material.

            --- COURSE MATERIAL START ---
            {context}

            --- COURSE MATERIAL END ---

            Answer the student's question using ONLY the
            course material above.

            Rules:

            1. Do not invent information.
            2. Do not use outside knowledge.
            3. If the material does not contain enough
            information, say:
            "I couldn't find enough information in the
            course material to answer that question."
            4. Give the direct answer first.
            5. Explain the concept clearly.
            6. Include relevant code when appropriate.
            7. Do not dump the retrieved document.
            8. Do not repeat irrelevant information.
            9. Use Markdown formatting.
            10. Keep the answer concise but useful.
            11. Answer like a helpful course instructor.
        """

        # Try primary model up to 3 times
        for attempt in range(3):
            try:
                return self._generate(self.model, prompt)

            except Exception as error:
                error_text = str(error)

                # Retry temporary 503 errors
                if "503" in error_text:

                    if attempt < 2:
                        time.sleep(
                            2 ** attempt
                        )
                        continue
                break

        # Fallback model
        try:
            return self._generate( self.fallback_model, prompt)

        except Exception as error:
            raise RuntimeError(
                "Gemini generation failed. "
                f"Primary and fallback models "
                f"were unavailable: {error}"
            )