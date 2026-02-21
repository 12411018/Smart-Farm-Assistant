"""Multilingual wrapper around the existing RAG pipeline."""

from typing import Callable, Optional
from language_detector_fasttext import detect_language
from translator import translate_to_english, translate_from_english

_RAG_RUNNER: Optional[Callable[[str], str]] = None


def set_rag_pipeline(fn: Callable[[str], str]) -> None:
    """Register the existing English RAG pipeline function."""
    global _RAG_RUNNER
    _RAG_RUNNER = fn


def _run_rag_pipeline(query: str) -> str:
    if _RAG_RUNNER is None:
        raise RuntimeError("RAG pipeline is not registered")
    return _RAG_RUNNER(query)


def process_multilingual_query(user_query: str, user_language: str = "en") -> str:
    """
    Process query with auto-language detection.
    Detect language, translate to English, run RAG, translate response back.
    
    Args:
        user_query: The user's input message
        user_language: Optional explicit language code (en, hi, mr, ta, te, kn, ml, gu, bn, pa)
    
    Returns:
        Response in the detected/specified language
    """
    if not user_query:
        return ""

    # Auto-detect language using Lingua (for native scripts)
    # If explicit language provided and not English, use that
    if user_language and user_language.lower() != "en":
        original_lang = user_language.lower()
    else:
        # Auto-detect for English or when no language specified
        original_lang = detect_language(user_query)
    
    english_query = user_query

    # Translate to English if needed
    if original_lang != "en":
        try:
            english_query = translate_to_english(user_query, original_lang)
        except Exception:
            english_query = user_query
            original_lang = "en"

    # Run RAG pipeline with English query
    try:
        rag_response = _run_rag_pipeline(english_query)
    except Exception:
        return _run_rag_pipeline(user_query)

    # Translate response back to original language
    if original_lang != "en":
        try:
            return translate_from_english(rag_response, original_lang)
        except Exception:
            return rag_response

    return rag_response
