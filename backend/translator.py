"""NLLB-200 translation helpers."""

from typing import Dict
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

_MODEL_NAME = "facebook/nllb-200-distilled-600M"

LANGUAGE_TOKENS: Dict[str, str] = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "mr": "mar_Deva",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "kn": "kan_Knda",
    "ml": "mal_Mlym",
    "gu": "guj_Gujr",
    "bn": "ben_Beng",
    "pa": "pan_Guru",
}

_TOKENIZER = None
_MODEL = None


def _ensure_model_loaded() -> None:
    global _TOKENIZER, _MODEL
    if _TOKENIZER is not None and _MODEL is not None:
        return
    _TOKENIZER = AutoTokenizer.from_pretrained(_MODEL_NAME)
    _MODEL = AutoModelForSeq2SeqLM.from_pretrained(_MODEL_NAME)
    _MODEL.to(torch.device("cpu"))
    _MODEL.eval()


def _translate(text: str, source_lang: str, target_lang: str) -> str:
    if not text:
        return ""
    if source_lang not in LANGUAGE_TOKENS or target_lang not in LANGUAGE_TOKENS:
        return text

    _ensure_model_loaded()

    _TOKENIZER.src_lang = LANGUAGE_TOKENS[source_lang]
    inputs = _TOKENIZER(text, return_tensors="pt", padding=True, truncation=True)
    forced_bos_token_id = _TOKENIZER.convert_tokens_to_ids(LANGUAGE_TOKENS[target_lang])

    with torch.no_grad():
        generated_tokens = _MODEL.generate(
            **inputs,
            forced_bos_token_id=forced_bos_token_id,
            max_length=512,
        )

    outputs = _TOKENIZER.batch_decode(generated_tokens, skip_special_tokens=True)
    return outputs[0] if outputs else ""


def translate_to_english(text: str, source_lang: str) -> str:
    """Translate source language to English using NLLB-200."""
    if source_lang == "en":
        return text
    return _translate(text, source_lang, "en")


def translate_from_english(text: str, target_lang: str) -> str:
    """Translate English text to target language using NLLB-200."""
    if target_lang == "en":
        return text
    return _translate(text, "en", target_lang)
