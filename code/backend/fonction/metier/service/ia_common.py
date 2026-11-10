import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - compat environnement sans python-dotenv
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()

from google import genai
from google.genai import types

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY manquante dans le fichier .env")
        _client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30_000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
    return _client


def strip_special_tokens(texte):
    for token in ("<bos>", "<eos>", "<start_of_turn>", "<end_of_turn>"):
        texte = texte.replace(token, "")
    return texte
