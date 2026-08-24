import hashlib
import time

class RAGCache:
    def __init__(self, ttl=600):
        self.ttl = ttl
        self.store = {}

    def _key(self, course_id, question):
        normalized = question.strip().lower()
        raw = f"{course_id}:{normalized}"

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    def get(self, course_id, question):
        key = self._key(
            course_id,
            question
        )

        item = self.store.get(key)

        if not item:
            return None

        if time.time() - item["time"] > self.ttl:
            del self.store[key]
            return None

        return item["value"]

    def set(self, course_id, question, value):
        key = self._key(course_id,question)

        self.store[key] = {
            "time": time.time(),
            "value": value
        }

    def clear(self):
        self.store.clear()