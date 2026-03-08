from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence


@dataclass
class Detection:
    entity_type: str
    start: int
    end: int
    score: float


INLINE_WS_PATTERN = r"[ \t]+"
NAME_TOKEN_PATTERN = r"(?:[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]+|[A-ZÀ-ÖØ-Ý]['’][A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]+)(?:[-'’][A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]+)*"
INITIAL_TOKEN_PATTERN = r"[A-Z]\."
ORG_WORD_PATTERN = r"[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ0-9&'’-]*"
PERSON_TITLE_PATTERN = r"(?:Mr|Mrs|Ms|Dr|Prof)"
STREET_SUFFIX_WORDS = {
    "road",
    "lane",
    "street",
    "terrace",
    "view",
    "avenue",
    "drive",
    "close",
    "way",
    "court",
    "square",
    "place",
    "plaza",
    "boulevard",
    "sq",
    "pl",
    "blvd",
}
STREET_PREFIX_WORDS = {"via"}
ORG_HINT_WORDS = {
    "lab",
    "labs",
    "research",
    "initiative",
    "alliance",
    "group",
    "institute",
    "network",
    "foundation",
    "university",
    "bank",
    "council",
    "office",
    "agency",
    "department",
    "school",
    "faculty",
    "consulting",
    "analytics",
    "systems",
    "instituto",
}
ORG_SUFFIX_WORDS = {
    "ltd",
    "limited",
    "inc",
    "llc",
    "consulting",
    "initiative",
    "university",
    "lab",
    "labs",
    "research",
    "alliance",
    "group",
    "institute",
    "network",
    "foundation",
    "agency",
    "council",
    "bank",
    "office",
    "department",
    "school",
    "faculty",
    "systems",
    "analytics",
    "instituto",
}
ORG_PREFIX_WORDS = {"department", "institute", "school", "faculty"}
NON_PERSON_NAME_WORDS = {
    "coordination",
    "meeting",
    "review",
    "report",
    "summary",
    "infrastructure",
    "climate",
    "urgent",
    "subject",
    "relevant",
    "resources",
    "internal",
    "shared",
    "server",
    "systems",
    "data",
    "strategy",
    "director",
    "united",
    "kingdom",
    "hi",
    "hello",
    "dear",
    "best",
    "regards",
}
ADDRESS_STREET_WORDS = r"(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd|Rue|Calle|Via|Strasse|Strada)"
ADDRESS_CONNECTOR_WORDS = r"(?:de|del|de la|du|des|di|da|la)"
CITY_TOKEN_PATTERN = r"[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'’-]+"
IGNORED_ENTITY_PREFIXES = (
    ("department", "of"),
    ("school", "of"),
    ("institute", "of"),
    ("faculty", "of"),
    ("centre", "for"),
    ("center", "for"),
)
NAME_TOKEN_RE = re.compile(rf"^{NAME_TOKEN_PATTERN}$")
INITIAL_TOKEN_RE = re.compile(rf"^{INITIAL_TOKEN_PATTERN}$")
PERSON_SINGLE_NAME_RE = re.compile(rf"\b{NAME_TOKEN_PATTERN}\b")
IPV4_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
IPV6_RE = re.compile(r"\b(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}\b")
AT_USERNAME_RE = re.compile(r"(?<![\w/])@\w[\w.-]+\b")
LABELED_VALUE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z ]{0,32})\s*(?::|->|→)\s*(.+?)\s*$")

_REGEX_DETECTORS = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "PHONE": re.compile(r"(?:\+?\d[\d\s().-]{7,}\d|\(\d{2,5}\)[\d\s.-]{5,}\d)"),
    "URL": re.compile(r"\bhttps?://[^\s]+\b", re.IGNORECASE),
    "IP_ADDRESS_V4": IPV4_RE,
    "IP_ADDRESS_V6": IPV6_RE,
    "UK_REF": re.compile(r"\b(?:UAN|GWF|CAS|COS|CoS)[-:\s]*[A-Z0-9]{5,16}\b", re.IGNORECASE),
    "PASSPORT": re.compile(r"\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b|\b\d{9}\b"),
    "DATE": re.compile(
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b",
        re.IGNORECASE,
    ),
    "ORG_PREFIXED": re.compile(
        rf"\b(?:Department|Institute|School|Faculty|Centre|Center){INLINE_WS_PATTERN}(?:of|for){INLINE_WS_PATTERN}{ORG_WORD_PATTERN}(?:{INLINE_WS_PATTERN}{ORG_WORD_PATTERN}){{0,5}}\b"
    ),
    "ORG_LEADING": re.compile(
        rf"\b(?:University|Institute|Instituto|Lab|Labs){INLINE_WS_PATTERN}(?:(?:of|for|de|del){INLINE_WS_PATTERN})?{ORG_WORD_PATTERN}(?:{INLINE_WS_PATTERN}{ORG_WORD_PATTERN}){{0,4}}\b"
    ),
    "ORG_SUFFIXED": re.compile(
        rf"\b{ORG_WORD_PATTERN}(?:{INLINE_WS_PATTERN}{ORG_WORD_PATTERN}){{0,5}}{INLINE_WS_PATTERN}(?:Ltd\.?|Limited|Inc\.?|LLC|Consulting|Initiative|University|Lab|Labs|Institute|School|Faculty|Foundation|Alliance|Group|Network|Agency|Council|Bank|Office|Department|Systems?|Analytics)\b"
    ),
    "ADDRESS_NUMBERED": re.compile(
        rf"\b\d{{1,5}}[A-Za-z]?{INLINE_WS_PATTERN}(?:{NAME_TOKEN_PATTERN}{INLINE_WS_PATTERN}){{0,4}}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd)\b"
    ),
    "ADDRESS_EU_NUMBERED": re.compile(
        rf"\b\d{{1,5}}[A-Za-z]?{INLINE_WS_PATTERN}(?:{ADDRESS_STREET_WORDS})(?:{INLINE_WS_PATTERN}(?:{ADDRESS_CONNECTOR_WORDS}|{CITY_TOKEN_PATTERN})){{1,6}}(?:,\s*\d{{4,5}}{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}})?\b"
    ),
    "ADDRESS_EU_TRAILING_NUMBER": re.compile(
        rf"\b(?:{ADDRESS_STREET_WORDS})(?:{INLINE_WS_PATTERN}(?:{ADDRESS_CONNECTOR_WORDS}|{CITY_TOKEN_PATTERN})){{1,6}}{INLINE_WS_PATTERN}\d{{1,5}}[A-Za-z]?(?:,\s*\d{{4,5}}{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}})?\b"
    ),
    "ADDRESS_POSTCODE_CITY": re.compile(
        rf"\b\d{{4,5}}{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}}\b"
    ),
    "ADDRESS_VIA": re.compile(rf"\bVia{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}){{0,2}}\b"),
    "COORDINATE": re.compile(r"\b\d{1,3}\.\d+\s*°?\s*[NS],\s*\d{1,3}\.\d+\s*°?\s*[EW]\b", re.IGNORECASE),
    "FILE_PATH": re.compile(r"(?<!https:)(?<!http:)/(?:[^\s/]+/)+[^\s/]*"),
    "PERSON_TITLED": re.compile(
        rf"\b{PERSON_TITLE_PATTERN}\.?{INLINE_WS_PATTERN}(?:{NAME_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN})?|{INITIAL_TOKEN_PATTERN}{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN})\b"
    ),
    "PERSON_FULL": re.compile(rf"\b{NAME_TOKEN_PATTERN}{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}\b"),
    "PERSON_INITIAL_LAST": re.compile(rf"\b{INITIAL_TOKEN_PATTERN}{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}\b"),
}

_REGEX_ENTITY_MAP = {
    "URL": "URL",
    "UK_REF": "ID",
    "PASSPORT": "ID",
    "EMAIL": "EMAIL",
    "PHONE": "PHONE",
    "DATE": "DATE",
    "IP_ADDRESS_V4": "IP_ADDRESS",
    "IP_ADDRESS_V6": "IP_ADDRESS",
    "ORG_PREFIXED": "ORG",
    "ORG_LEADING": "ORG",
    "ORG_SUFFIXED": "ORG",
    "ADDRESS_NUMBERED": "ADDRESS",
    "ADDRESS_EU_NUMBERED": "ADDRESS",
    "ADDRESS_EU_TRAILING_NUMBER": "ADDRESS",
    "ADDRESS_POSTCODE_CITY": "ADDRESS",
    "ADDRESS_VIA": "ADDRESS",
    "COORDINATE": "COORDINATE",
    "FILE_PATH": "FILE_PATH",
    "PERSON_TITLED": "PERSON",
    "PERSON_FULL": "PERSON",
    "PERSON_INITIAL_LAST": "PERSON",
}

SUPPORTED_TOGGLES = {"PERSON", "EMAIL", "PHONE", "ADDRESS", "ORG", "DATE", "URL", "IP_ADDRESS", "USERNAME", "COORDINATE", "FILE_PATH"}
ENTITY_PRIORITY = {
    "EMAIL": 0,
    "URL": 1,
    "IP_ADDRESS": 2,
    "PHONE": 3,
    "DATE": 4,
    "ADDRESS": 5,
    "ORG": 6,
    "PERSON": 7,
    "USERNAME": 9,
    "COORDINATE": 10,
    "FILE_PATH": 11,
}
SUPPORTED_LANGUAGE_CODE = "en"
SUPPORTED_LANGUAGE_LABEL = "English"
UNKNOWN_LANGUAGE_CODE = "unknown"
NON_ENGLISH_WARNING = "This text appears to be non-English. Entity detection may be less accurate."
NLP_ENTITY_MAP = {
    "PERSON": "PERSON",
    "ORG": "ORG",
    "LOCATION": "ADDRESS",
    "DATE_TIME": "DATE",
    "DATE": "DATE",
    "URL": "URL",
}

IMMIGRATION_KEYWORDS = re.compile(
    r"\b(visa|ukvi|uan|gwf|cas|cos|sponsor|brp|ilr|immigration|home office)\b",
    re.IGNORECASE,
)

LANGUAGE_HINTS = {
    "en": {"the", "and", "is", "are", "was", "were", "with", "from", "that", "this", "have", "has"},
    "es": {"el", "la", "de", "que", "hola", "gracias", "para", "con", "una", "por", "me", "llamo", "en", "y"},
    "fr": {"le", "la", "de", "bonjour", "merci", "avec", "pour", "une", "dans", "est", "et", "je", "vous"},
    "de": {"der", "die", "das", "und", "mit", "für", "ist", "nicht", "ich", "sie", "ein", "eine", "den"},
    "it": {"il", "lo", "la", "ciao", "grazie", "con", "per", "che", "una", "sono", "non", "nel", "gli"},
    "pt": {"olá", "ola", "obrigado", "com", "para", "que", "uma", "não", "voce", "você", "está", "em", "de"},
    "nl": {"de", "het", "een", "en", "met", "voor", "niet", "ik", "je", "dat", "dit", "van"},
}

LANGUAGE_ACCENT_HINTS = {
    "es": ("ñ", "á", "é", "í", "ó", "ú"),
    "fr": ("à", "â", "ç", "è", "é", "ê", "ë", "î", "ï", "ô", "ù", "û", "ü", "œ"),
    "de": ("ä", "ö", "ü", "ß"),
    "it": ("à", "è", "é", "ì", "ò", "ù"),
    "pt": ("ã", "â", "á", "à", "ç", "é", "ê", "í", "ó", "ô", "õ", "ú"),
}


class OptionalNlp:
    def __init__(self) -> None:
        self._analyzer = None
        self.available = False
        try:
            from presidio_analyzer import AnalyzerEngine

            self._analyzer = AnalyzerEngine()
            self.available = True
        except Exception:
            self.available = False

    def detect(self, text: str, enabled_types: Sequence[str]) -> List[Detection]:
        if not self.available or not self._analyzer:
            return []

        entities = []
        if "PERSON" in enabled_types:
            entities.append("PERSON")
        if "ORG" in enabled_types:
            entities.append("ORGANIZATION")
        if "ADDRESS" in enabled_types:
            entities.extend(["LOCATION", "ADDRESS"])
        if "DATE" in enabled_types:
            entities.extend(["DATE_TIME", "DATE"])

        if not entities:
            return []

        results = self._analyzer.analyze(text=text, entities=list(set(entities)), language="en")
        detections: List[Detection] = []
        for item in results:
            mapped = NLP_ENTITY_MAP.get(item.entity_type, item.entity_type)
            if mapped not in enabled_types:
                continue
            detections.append(
                Detection(
                    entity_type=mapped,
                    start=item.start,
                    end=item.end,
                    score=float(item.score or 0.6),
                )
            )
        return detections


def detect_language(text: str) -> str:
    cleaned = re.sub(r"https?://\S+|\b\S+@\S+\b|\d+", " ", text or "")
    letters = [char for char in cleaned if char.isalpha()]
    if not letters:
        return SUPPORTED_LANGUAGE_CODE

    script_counts = {
        "ru": len(re.findall(r"[Ѐ-ӿ]", cleaned)),
        "ar": len(re.findall(r"[\u0600-\u06FF]", cleaned)),
        "zh": len(re.findall(r"[\u4E00-\u9FFF]", cleaned)),
        "ja": len(re.findall(r"[\u3040-\u30FF]", cleaned)),
    }
    script_threshold = max(2, int(len(letters) * 0.2))
    for code, count in script_counts.items():
        if count >= script_threshold:
            return code

    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", cleaned.lower())
    if len(words) < 4:
        return UNKNOWN_LANGUAGE_CODE

    scores: Dict[str, int] = {}
    for code, hints in LANGUAGE_HINTS.items():
        score = sum(1 for word in words if word in hints)
        for marker in LANGUAGE_ACCENT_HINTS.get(code, ()):
            if marker in cleaned.lower():
                score += 1
        scores[code] = score

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_code, best_score = ranked[0]
    runner_up = ranked[1][1] if len(ranked) > 1 else 0
    if best_score >= 2 and best_score >= runner_up + 1:
        return best_code

    return UNKNOWN_LANGUAGE_CODE


def get_language_warning(text: str) -> Dict[str, Optional[str]]:
    detected_language = detect_language(text)
    warning = None
    if detected_language not in {SUPPORTED_LANGUAGE_CODE, UNKNOWN_LANGUAGE_CODE}:
        warning = NON_ENGLISH_WARNING

    return {
        "warning": warning,
        "detected_language": detected_language,
        "supported_language": SUPPORTED_LANGUAGE_LABEL,
    }


def _normalized_words(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", (text or "").lower())


def _strip_person_title(text: str) -> str:
    return re.sub(rf"^(?:{PERSON_TITLE_PATTERN})\.?\s+", "", (text or "").strip())


def _ascii_fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _is_org_like_phrase(text: str) -> bool:
    words = _normalized_words(text)
    if len(words) >= 2 and words[0] in ORG_PREFIX_WORDS and words[1] == "of":
        return True
    return any(word in ORG_HINT_WORDS or word in ORG_SUFFIX_WORDS for word in words)


def _is_ignored_entity_phrase(text: str) -> bool:
    words = _normalized_words(text)
    return any(all(len(words) > idx and words[idx] == token for idx, token in enumerate(prefix)) for prefix in IGNORED_ENTITY_PREFIXES)


def _is_street_like_phrase(text: str) -> bool:
    words = _normalized_words(text)
    if not words:
        return False
    return words[0] in STREET_PREFIX_WORDS or words[-1] in STREET_SUFFIX_WORDS


def _next_word_after(text: str, end: int) -> str:
    match = re.match(r"\s+([A-Za-zÀ-ÖØ-öø-ÿ]+)", text[end:])
    return match.group(1).lower() if match else ""


def _previous_word(text: str, start: int) -> str:
    match = re.search(r"([A-Za-zÀ-ÖØ-öø-ÿ]+)\W*$", text[:start])
    return match.group(1).lower() if match else ""


def _has_org_prefix_context(text: str, start: int) -> bool:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", text[:start].lower())
    return len(words) >= 2 and words[-2] in ORG_PREFIX_WORDS and words[-1] == "of"


def _has_ignored_entity_context(text: str, start: int) -> bool:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", text[:start].lower())
    return any(len(words) >= len(prefix) and tuple(words[-len(prefix) :]) == prefix for prefix in IGNORED_ENTITY_PREFIXES)


def _get_line_at(text: str, index: int) -> str:
    safe_index = max(0, min(index, max(len(text) - 1, 0)))
    start = text.rfind("\n", 0, safe_index) + 1
    end = text.find("\n", safe_index)
    if end == -1:
        end = len(text)
    return text[start:end]


def _is_likely_heading_line(line: str) -> bool:
    trimmed = (line or "").strip()
    if not trimmed:
        return False
    normalized = re.sub(r"^(?:subject|title)\s*:\s*", "", trimmed, flags=re.IGNORECASE)
    normalized = normalized.replace("–", " ").replace("—", " ").replace("-", " ").strip()
    if not normalized or len(normalized) > 140 or re.search(r"[.!?]", normalized):
        return False
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ'’&-]+", normalized)
    if len(words) < 2 or len(words) > 12:
        return False
    if words[0].lower() in {"hi", "hello", "dear"}:
        return False
    title_like = sum(1 for word in words if re.fullmatch(r"[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'’-]*", word))
    ratio = title_like / len(words)
    return (ratio >= 0.75 and len(words) >= 4) or (ratio >= 0.9 and len(words) >= 3)


def _is_likely_phone_value(text: str) -> bool:
    if IPV4_RE.fullmatch((text or "").strip()):
        return False
    digits = re.sub(r"\D", "", text or "")
    return 8 <= len(digits) <= 15 and (len(digits) >= 10 or "+" in (text or "") or bool(re.search(r"[\s.-]", text or "")))


def _is_valid_person_span(text: str, start: int, end: int, phrase: str) -> bool:
    cleaned = _strip_person_title(phrase)
    if not cleaned:
        return False

    parts = cleaned.split()
    next_word = _next_word_after(text, end)
    line = _get_line_at(text, start)
    if _is_likely_heading_line(line):
        return False
    if len(parts) == 1:
        token = parts[0]
        lowered = token.lower()
        if not NAME_TOKEN_RE.fullmatch(token):
            return False
        if lowered in ORG_HINT_WORDS or lowered in ORG_SUFFIX_WORDS:
            return False
        if lowered in STREET_PREFIX_WORDS:
            return False
        if _has_ignored_entity_context(text, start):
            return False
        if _has_org_prefix_context(text, start):
            return False
        if next_word in STREET_SUFFIX_WORDS or next_word in ORG_HINT_WORDS or next_word in ORG_SUFFIX_WORDS:
            return False
        return True

    if len(parts) != 2:
        return False
    if not (NAME_TOKEN_RE.fullmatch(parts[0]) or INITIAL_TOKEN_RE.fullmatch(parts[0])):
        return False
    if not NAME_TOKEN_RE.fullmatch(parts[1]):
        return False
    if parts[0].lower() in NON_PERSON_NAME_WORDS or parts[1].lower() in NON_PERSON_NAME_WORDS:
        return False
    if _is_org_like_phrase(cleaned) or _is_street_like_phrase(cleaned):
        return False
    if _has_ignored_entity_context(text, start):
        return False
    if _has_org_prefix_context(text, start):
        return False
    if next_word in ORG_SUFFIX_WORDS:
        return False
    return True


def _canonical_entity_key(entity_type: str, value: str) -> str:
    target = _strip_person_title(value) if entity_type == "PERSON" else (value or "")
    return f"{entity_type}:{_normalize_entity_value(target)}"


def _normalize_entity_value(value: str) -> str:
    folded = _ascii_fold((value or "").strip()).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", folded)).strip()


def _build_person_coreference_links(text: str, detections: Sequence[Detection]) -> tuple[list[Detection], dict[str, str]]:
    full_names = []
    for det in detections:
        if det.entity_type != "PERSON":
            continue
        raw = text[det.start : det.end].strip()
        cleaned = _strip_person_title(raw).strip()
        parts = cleaned.split()
        if len(parts) != 2:
            continue
        first, last = parts
        if not ((NAME_TOKEN_RE.fullmatch(first) or INITIAL_TOKEN_RE.fullmatch(first)) and NAME_TOKEN_RE.fullmatch(last)):
            continue
        full_names.append(
            {
                "first": first.lower(),
                "last": last.lower(),
                "first_is_initial": bool(INITIAL_TOKEN_RE.fullmatch(first)),
                "canonical": _canonical_entity_key("PERSON", cleaned),
            }
        )

    if not full_names:
        return [], {}

    first_name_map: Dict[str, str] = {}
    last_name_map: Dict[str, str] = {}
    initial_last_map: Dict[tuple[str, str], str] = {}
    ambiguous_first: set[str] = set()
    ambiguous_last: set[str] = set()
    ambiguous_initial_last: set[tuple[str, str]] = set()

    for full in full_names:
        if not full["first_is_initial"]:
            existing_first = first_name_map.get(full["first"])
            if not existing_first:
                first_name_map[full["first"]] = full["canonical"]
            elif existing_first != full["canonical"]:
                ambiguous_first.add(full["first"])

            initial_key = (full["first"][0], full["last"])
            existing_initial = initial_last_map.get(initial_key)
            if not existing_initial:
                initial_last_map[initial_key] = full["canonical"]
            elif existing_initial != full["canonical"]:
                ambiguous_initial_last.add(initial_key)

            existing_last = last_name_map.get(full["last"])
            if not existing_last:
                last_name_map[full["last"]] = full["canonical"]
            elif existing_last != full["canonical"]:
                ambiguous_last.add(full["last"])

    for key in ambiguous_first:
        first_name_map.pop(key, None)
    for key in ambiguous_last:
        last_name_map.pop(key, None)
    for key in ambiguous_initial_last:
        initial_last_map.pop(key, None)

    alias_map: Dict[str, str] = {}
    for name, canonical in first_name_map.items():
        alias_map[_canonical_entity_key("PERSON", name)] = canonical
    for name, canonical in last_name_map.items():
        alias_map[_canonical_entity_key("PERSON", name)] = canonical
    for det in detections:
        if det.entity_type != "PERSON":
            continue
        raw = text[det.start : det.end].strip()
        cleaned = _strip_person_title(raw).strip()
        parts = cleaned.split()
        if len(parts) != 2:
            continue
        first, last = parts
        if not (INITIAL_TOKEN_RE.fullmatch(first) and NAME_TOKEN_RE.fullmatch(last)):
            continue
        canonical = initial_last_map.get((first[0].lower(), last.lower()))
        if canonical:
            alias_map[_canonical_entity_key("PERSON", cleaned)] = canonical
            alias_map[_canonical_entity_key("PERSON", raw)] = canonical

    additions: List[Detection] = []
    for match in PERSON_SINGLE_NAME_RE.finditer(text):
        token = match.group(0)
        lowered = token.lower()
        if lowered not in first_name_map and lowered not in last_name_map:
            continue
        start = match.start()
        end = match.end()
        if any(not (end <= det.start or start >= det.end) for det in detections):
            continue
        if not _is_valid_person_span(text, start, end, token):
            continue
        if _previous_word(text, start) in STREET_SUFFIX_WORDS:
            continue
        additions.append(Detection(entity_type="PERSON", start=start, end=end, score=0.79))

    return additions, alias_map


def _extract_labeled_value(segment: str, entity_type: str) -> Optional[str]:
    if not segment:
        return None
    trimmed = segment.strip()
    trim_boundary = lambda value: re.sub(r"[),.;:]+$", "", (value or "").strip())
    if entity_type == "EMAIL":
        match = _REGEX_DETECTORS["EMAIL"].search(trimmed)
        return match.group(0) if match else None
    if entity_type == "URL":
        match = _REGEX_DETECTORS["URL"].search(trimmed)
        return match.group(0) if match else None
    if entity_type == "PHONE":
        match = _REGEX_DETECTORS["PHONE"].search(trimmed)
        return trim_boundary(match.group(0)) if match else None
    if entity_type == "PERSON":
        for key in ("PERSON_TITLED", "PERSON_FULL", "PERSON_INITIAL_LAST"):
            match = _REGEX_DETECTORS[key].search(trimmed)
            if match:
                return match.group(0)
        return None
    if entity_type == "IP_ADDRESS":
        match = IPV4_RE.search(trimmed) or IPV6_RE.search(trimmed)
        return match.group(0) if match else None
    if entity_type == "COORDINATE":
        match = _REGEX_DETECTORS["COORDINATE"].search(trimmed)
        return match.group(0) if match else None
    if entity_type == "FILE_PATH":
        match = _REGEX_DETECTORS["FILE_PATH"].search(trimmed)
        return match.group(0) if match else None
    if entity_type == "USERNAME":
        match = AT_USERNAME_RE.search(trimmed)
        if match:
            return match.group(0)
        generic = re.search(r"\b[a-z0-9]+-[a-z0-9-]+\b", trimmed)
        return generic.group(0) if generic else None
    return trim_boundary(trimmed)


def structured_detect(text: str, enabled_types: Sequence[str]) -> List[Detection]:
    label_map = {
        "person": "PERSON",
        "email": "EMAIL",
        "phone": "PHONE",
        "address": "ADDRESS",
        "organisation": "ORG",
        "organization": "ORG",
        "date": "DATE",
        "url": "URL",
        "website": "URL",
        "web address": "URL",
        "slack": "USERNAME",
        "github": "USERNAME",
        "username": "USERNAME",
        "handle": "USERNAME",
        "ip": "IP_ADDRESS",
        "server ip": "IP_ADDRESS",
        "ipv4": "IP_ADDRESS",
        "ipv6": "IP_ADDRESS",
        "backup ipv6": "IP_ADDRESS",
        "coordinate": "COORDINATE",
        "coordinates": "COORDINATE",
        "file path": "FILE_PATH",
        "filepath": "FILE_PATH",
        "path": "FILE_PATH",
    }
    detections: List[Detection] = []
    offset = 0
    for line in text.splitlines():
        match = LABELED_VALUE_RE.match(line)
        if match:
            label = re.sub(r"\s+", " ", match.group(1).strip().lower())
            mapped = label_map.get(label)
            if mapped and mapped in enabled_types:
                value = match.group(2)
                extracted = _extract_labeled_value(value, mapped)
                if extracted:
                    value_start = line.find(value)
                    extracted_start = line.find(extracted, value_start if value_start >= 0 else 0)
                    if extracted_start >= 0:
                        start = offset + extracted_start
                        end = start + len(extracted)
                        if mapped == "PHONE" and not _is_likely_phone_value(extracted):
                            continue
                        if mapped == "PERSON" and not _is_valid_person_span(text, start, end, extracted):
                            continue
                        detections.append(
                            Detection(
                                entity_type=mapped,
                                start=start,
                                end=end,
                                score=0.995,
                            )
                        )
        offset += len(line) + 1
    return detections


def regex_detect(text: str, enabled_types: Sequence[str]) -> List[Detection]:
    detections: List[Detection] = []
    for key, pattern in _REGEX_DETECTORS.items():
        mapped = _REGEX_ENTITY_MAP.get(key)
        if mapped and mapped not in enabled_types:
            continue
        for match in pattern.finditer(text):
            if mapped == "PHONE" and not _is_likely_phone_value(match.group(0)):
                continue
            if mapped == "ORG" and (_is_ignored_entity_phrase(match.group(0)) or _has_ignored_entity_context(text, match.start())):
                continue
            if mapped == "PERSON" and not _is_valid_person_span(text, match.start(), match.end(), match.group(0)):
                continue
            detections.append(
                Detection(entity_type=mapped or key, start=match.start(), end=match.end(), score=0.99)
            )
    if "USERNAME" in enabled_types:
        for match in AT_USERNAME_RE.finditer(text):
            detections.append(Detection(entity_type="USERNAME", start=match.start(), end=match.end(), score=0.97))
    return detections


def _resolve_overlaps(detections: Sequence[Detection]) -> List[Detection]:
    ranked = sorted(
        detections,
        key=lambda d: (ENTITY_PRIORITY.get(d.entity_type, 99), -(d.end - d.start), -d.score, d.start, d.end),
    )
    chosen: List[Detection] = []
    for det in ranked:
        has_overlap = any(not (det.end <= c.start or det.start >= c.end) for c in chosen)
        if not has_overlap:
            chosen.append(det)
    return sorted(chosen, key=lambda d: (d.start, d.end))


def apply_replacements(text: str, detections: Sequence[Detection], alias_map: Optional[Dict[str, str]] = None) -> Dict[str, object]:
    alias_map = alias_map or {}
    counters: Dict[str, int] = {}
    stable_map: Dict[str, str] = {}
    entities = []
    output_parts = []
    last_idx = 0

    for det in detections:
        label = det.entity_type
        original = text[det.start : det.end]
        own_canonical = _canonical_entity_key(label, original)
        canonical = alias_map.get(own_canonical, own_canonical)
        replacement = stable_map.get(canonical)
        if not replacement:
            counters[label] = counters.get(label, 0) + 1
            replacement = f"[{label}_{counters[label]}]"
            stable_map[canonical] = replacement

        output_parts.append(text[last_idx : det.start])
        output_parts.append(replacement)

        entities.append(
            {
                "type": label,
                "start": det.start,
                "end": det.end,
                "replacement": replacement,
                "confidence": round(det.score, 3),
            }
        )
        last_idx = det.end

    output_parts.append(text[last_idx:])
    return {
        "anonymized_text": "".join(output_parts),
        "entities": entities,
        "counts": counters,
    }


def anonymize_text(text: str, enabled_types: Sequence[str], nlp: OptionalNlp) -> Dict[str, object]:
    clean_types = [t for t in enabled_types if t in SUPPORTED_TOGGLES]
    structured_hits = structured_detect(text, clean_types)
    regex_hits = regex_detect(text, clean_types)
    nlp_hits = nlp.detect(text, clean_types)

    merged = _resolve_overlaps([*structured_hits, *regex_hits, *nlp_hits])
    alias_additions: List[Detection] = []
    alias_map: Dict[str, str] = {}
    if "PERSON" in clean_types:
        alias_additions, alias_map = _build_person_coreference_links(text, merged)
        merged = _resolve_overlaps([*merged, *alias_additions])
    replaced = apply_replacements(text, merged, alias_map=alias_map)
    replaced["cta_visaprep"] = bool(IMMIGRATION_KEYWORDS.search(text))
    return replaced
