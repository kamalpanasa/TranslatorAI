from typing import Dict, Optional, List

# Extensive mapping of ISO-639-1 / common codes to NLLB-200 language identifiers
ISO_TO_NLLB: Dict[str, str] = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "fr": "fra_Latn",
    "es": "spa_Latn",
    "zh": "zho_Hans",
    "ar": "ara_Arab",
    "de": "deu_Latn",
    "ru": "rus_Cyrl",
    "ja": "jpn_Jpan",
    "pt": "por_Latn",
    "it": "ita_Latn",
    "ko": "kor_Kore",
    "nl": "nld_Latn",
    "tr": "tur_Latn",
    "vi": "vie_Latn",
    "pl": "pol_Latn",
    "uk": "ukr_Cyrl",
    "id": "ind_Latn",
    "th": "tha_Thai",
    "sv": "swe_Latn",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "bn": "ben_Beng",
    "mr": "mar_Deva",
    "gu": "guj_Gujr",
    "kn": "kan_Knda",
    "ml": "mal_Mlym",
    "pa": "pan_Guru",
    "ur": "urd_Arab",
    "fa": "pes_Arab",
    "he": "heb_Hebr",
    "ro": "ron_Latn",
    "el": "ell_Grek",
    "cs": "ces_Latn",
    "hu": "hun_Latn",
    "fi": "fin_Latn",
    "no": "nno_Latn", # Norwegian Nynorsk / bokmaal closest
    "da": "dan_Latn",
    "sk": "slk_Latn",
    "hr": "hrv_Latn",
    "sr": "srp_Cyrl",
    "bg": "bul_Cyrl",
    "lt": "lit_Latn",
    "lv": "lvs_Latn",
    "et": "est_Latn",
    "sl": "slv_Latn",
    "ms": "zsm_Latn",
    "tl": "tgl_Latn",
}

# Supported languages display names mapping
LANGUAGE_NAMES: Dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "es": "Spanish",
    "zh": "Chinese (Simplified)",
    "ar": "Arabic",
    "de": "German",
    "ru": "Russian",
    "ja": "Japanese",
    "pt": "Portuguese",
    "it": "Italian",
    "ko": "Korean",
    "nl": "Dutch",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "pl": "Polish",
    "uk": "Ukrainian",
    "id": "Indonesian",
    "th": "Thai",
    "sv": "Swedish",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
    "fa": "Persian",
    "he": "Hebrew",
    "ro": "Romanian",
    "el": "Greek",
    "cs": "Czech",
    "hu": "Hungarian",
    "fi": "Finnish",
    "no": "Norwegian",
    "da": "Danish",
    "sk": "Slovak",
    "hr": "Croatian",
    "sr": "Serbian",
    "bg": "Bulgarian",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "et": "Estonian",
    "sl": "Slovenian",
    "ms": "Malay",
    "tl": "Tagalog",
}

# Reverse mapping to allow lookups of NLLB-200 code directly
NLLB_SET = set(ISO_TO_NLLB.values())


def is_valid_language(lang_code: str) -> bool:
    """
    Checks if a language code is valid.
    Supports either the 2-letter ISO code or the exact NLLB code.
    """
    if not lang_code:
        return False
    lang_clean = lang_code.strip()
    return lang_clean in ISO_TO_NLLB or lang_clean in NLLB_SET


def resolve_to_nllb_code(lang_code: str) -> Optional[str]:
    """
    Resolves any input language code (ISO 2-letter or NLLB) to its valid NLLB code.
    Returns None if the language is unsupported.
    """
    if not lang_code:
        return None
    lang_clean = lang_code.strip()
    if lang_clean in NLLB_SET:
        return lang_clean
    return ISO_TO_NLLB.get(lang_clean.lower())


def get_supported_languages() -> List[Dict[str, str]]:
    """
    Returns a list of supported languages with their code and name.
    """
    return [
        {"code": iso, "name": name, "nllb_code": ISO_TO_NLLB[iso]}
        for iso, name in LANGUAGE_NAMES.items()
    ]
