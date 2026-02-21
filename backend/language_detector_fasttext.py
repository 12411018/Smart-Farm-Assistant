"""Language detection using Lingua library - works with native Indian language scripts."""

from typing import Optional

try:
    from lingua import Language, LanguageDetectorBuilder
except ImportError:
    Language = None
    LanguageDetectorBuilder = None

SUPPORTED_LANGUAGES = {"en", "hi", "mr", "ta", "te", "kn", "ml", "gu", "bn", "pa"}

_DETECTOR = None


def _build_detector():
    """Build language detector with available languages."""
    global _DETECTOR
    if _DETECTOR is not None:
        return _DETECTOR
    
    if Language is None:
        return None
    
    # Dynamically check which languages are available in Lingua enum
    languages_to_use = []
    lang_mapping = {
        "en": "ENGLISH",
        "hi": "HINDI",
        "mr": "MARATHI",
        "ta": "TAMIL",
        "te": "TELUGU",
        "kn": "KANNADA",
        "ml": "MALAYALAM",
        "gu": "GUJARATI",
        "bn": "BENGALI",
        "pa": "PUNJABI",
    }
    
    for iso_code, lingua_name in lang_mapping.items():
        if hasattr(Language, lingua_name):
            languages_to_use.append(getattr(Language, lingua_name))
    
    if languages_to_use:
        _DETECTOR = LanguageDetectorBuilder.from_languages(*languages_to_use).build()
    
    return _DETECTOR


def detect_language(text: str) -> str:
    """
    Detect language using Lingua.
    
    Args:
        text: Input text in native script or English
    
    Returns:
        ISO 639-1 language code (en, hi, mr, ta, te, kn, ml, gu, bn, pa) or 'en' as fallback
    """
    if not text or not text.strip():
        return "en"
    
    try:
        detector = _build_detector()
        if detector is None:
            return "en"
        
        detected = detector.detect_language_of(text)
        if detected is None:
            return "en"
        
        # Lingua returns Language enum, need to map to ISO code
        lang_name = detected.name
        lang_mapping = {
            "ENGLISH": "en",
            "HINDI": "hi",
            "MARATHI": "mr",
            "TAMIL": "ta",
            "TELUGU": "te",
            "KANNADA": "kn",
            "MALAYALAM": "ml",
            "GUJARATI": "gu",
            "BENGALI": "bn",
            "PUNJABI": "pa",
        }
        
        iso_code = lang_mapping.get(lang_name, "en")
        return iso_code if iso_code in SUPPORTED_LANGUAGES else "en"
        
    except Exception as e:
        print(f"Language detection error: {e}, defaulting to English")
        return "en"


# Test the detector with various inputs
if __name__ == "__main__":
    test_queries = [
        "कृषि योजना क्या हैं",  # Hindi (native script)
        "मराठी शेळी",  # Marathi (native script)
        "மாவட்ட தோட்டப் பயிர் மேலாண்மை",  # Tamil (native script)
        "paddy field management tips",  # English
    ]
    
    for query in test_queries:
        lang = detect_language(query)
        print(f"Query: {query[:40]:40} -> Language: {lang}")


