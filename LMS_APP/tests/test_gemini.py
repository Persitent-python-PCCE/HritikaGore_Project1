from rag.llm import GeminiLLM
llm = GeminiLLM()


context = """
Source: Python_Level1_Practice_Sheet.pdf
Page: 1

Check whether a number is prime by testing
divisibility up to its square root.

def is_prime(n):
    if n < 2:
        return False

    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False

    return True
"""


question = (
    "How can I check whether a number is prime "
    "in Python?"
)


answer = llm.generate_answer(
    question,
    context
)


print("\n=== GEMINI ANSWER ===\n")
print(answer)