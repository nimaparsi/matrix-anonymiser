from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence


@dataclass
class Detection:
    entity_type: str
    start: int
    end: int
    score: float


_REGEX_DETECTORS = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "PHONE": re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b"),
    "URL": re.compile(r"\bhttps?://[^\s]+\b", re.IGNORECASE),
    "UK_REF": re.compile(r"\b(?:UAN|GWF|CAS|COS|CoS)[-:\s]*[A-Z0-9]{5,16}\b", re.IGNORECASE),
    "PASSPORT": re.compile(r"\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b|\b\d{9}\b"),
    "DATE": re.compile(
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b",
        re.IGNORECASE,
    ),
}

_REGEX_ENTITY_MAP = {
    "URL": "URL",
    "UK_REF": "ID",
    "PASSPORT": "ID",
    "EMAIL": "EMAIL",
    "PHONE": "PHONE",
    "DATE": "DATE",
}

SUPPORTED_TOGGLES = {"PERSON", "EMAIL", "PHONE", "ADDRESS", "ORG", "DATE"}
NLP_ENTITY_MAP = {
    "PERSON": "PERSON",
    "ORG": "ORG",
    "LOCATION": "ADDRESS",
    "DATE_TIME": "DATE",
    "DATE": "DATE",
}

IMMIGRATION_KEYWORDS = re.compile(
    r"\b(visa|ukvi|uan|gwf|cas|cos|sponsor|brp|ilr|immigration|home office)\b",
    re.IGNORECASE,
)


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


def regex_detect(text: str, enabled_types: Sequence[str]) -> List[Detection]:
    detections: List[Detection] = []
    for key, pattern in _REGEX_DETECTORS.items():
        mapped = _REGEX_ENTITY_MAP.get(key)
        if mapped in {"EMAIL", "PHONE", "DATE"} and mapped not in enabled_types:
            continue
        for match in pattern.finditer(text):
            detections.append(
                Detection(entity_type=mapped or key, start=match.start(), end=match.end(), score=0.99)
            )
    return detections


def _resolve_overlaps(detections: Sequence[Detection]) -> List[Detection]:
    # Longest span first, then highest score, then earliest start.
    ranked = sorted(
        detections,
        key=lambda d: (-(d.end - d.start), -d.score, d.start, d.end),
    )
    chosen: List[Detection] = []
    for det in ranked:
        has_overlap = any(not (det.end <= c.start or det.start >= c.end) for c in chosen)
        if not has_overlap:
            chosen.append(det)
    return sorted(chosen, key=lambda d: (d.start, d.end))


def apply_replacements(text: str, detections: Sequence[Detection]) -> Dict[str, object]:
    counters: Dict[str, int] = {}
    entities = []
    output_parts = []
    last_idx = 0

    for det in detections:
        label = det.entity_type
        counters[label] = counters.get(label, 0) + 1
        replacement = f"[{label}_{counters[label]}]"

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
    regex_hits = regex_detect(text, clean_types)
    nlp_hits = nlp.detect(text, clean_types)

    merged = _resolve_overlaps([*regex_hits, *nlp_hits])
    replaced = apply_replacements(text, merged)
    replaced["cta_visaprep"] = bool(IMMIGRATION_KEYWORDS.search(text))
    return replaced

