import logfire
from google import genai
from groq import Groq

from app.config import settings

_gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
_groq_client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """

You are a reading companion answering questions about a book the user
is currently reading. Only use the provided context to answer. It contains
only content up to where the reader currently is. If the answer isn't in the
context, say you don't have enough information yet based on what's been read
so far. Never use outside knowledge of the book, even if you recognize it, since
that could reveal spoilers.

"""

def build_prompt(question: str, chunks: list) -> str:
    context = '\n\n'.join(c.payload["text"] for c in chunks)
    return f"Context:\n{context}\n\nQuestion: {question}"

def generate_answer(question: str, chunks: list) -> str:
    prompt = build_prompt(question, chunks)

    with logfire.span("generate_answer", num_chunks=len(chunks)):
        try:
            response = _gemini_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config={"system_instruction": SYSTEM_PROMPT},
            )
            logfire.info("Gemini model is in use.")
            return response.text
        
        except Exception as e:     # noqa: BLE001 -- intentional fallback on any Gemini failure
            logfire.error("Gemini isnt working. Fallback to groq", error=str(e))
            response = _groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ]
            )
            return response.choices[0].message.content