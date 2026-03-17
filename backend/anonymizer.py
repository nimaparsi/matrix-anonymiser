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
NAME_SEGMENT_PATTERN = r"[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]+"
NAME_CAMEL_PATTERN = rf"(?:{NAME_SEGMENT_PATTERN}(?:{NAME_SEGMENT_PATTERN})*|[A-ZÀ-ÖØ-Ý](?:{NAME_SEGMENT_PATTERN})+)"
NAME_TOKEN_PATTERN = rf"(?:{NAME_CAMEL_PATTERN}|[A-ZÀ-ÖØ-Ý]['’]{NAME_SEGMENT_PATTERN})(?:[-'’]{NAME_SEGMENT_PATTERN})*"
INITIAL_TOKEN_PATTERN = r"[A-Z]\."
INITIAL_OPTIONAL_DOT_PATTERN = r"[A-Z]\.?"
PERSON_FULL_NAME_PATTERN = rf"{NAME_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}){{1,2}}"
PERSON_DOUBLE_INITIAL_LAST_PATTERN = rf"[A-Z]\.[A-Z]\.{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}"
PERSON_INITIAL_LAST_PATTERN = rf"{INITIAL_OPTIONAL_DOT_PATTERN}{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}"
PERSON_FIRST_INITIAL_PATTERN = rf"{NAME_TOKEN_PATTERN}{INLINE_WS_PATTERN}{INITIAL_OPTIONAL_DOT_PATTERN}"
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
    "rail",
    "west",
    "air",
    "transport",
    "group",
    "apple",
    "google",
    "visa",
    "mastercard",
    "paypal",
    "stripe",
    "american",
    "express",
    "amex",
    "pay",
}
ORG_SUFFIX_WORDS = {
    "ltd",
    "limited",
    "inc",
    "llc",
    "corp",
    "gmbh",
    "pte",
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
ORG_CONTEXT_WORDS = {
    "at",
    "with",
    "for",
    "from",
    "of",
    "into",
    "joined",
    "joining",
    "works",
    "worked",
    "working",
    "employed",
    "company",
    "organisation",
    "organization",
}
NON_PERSON_NAME_WORDS = {
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
    "sun",
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
    "coordination",
    "project",
    "regional",
    "sustainability",
    "pilot",
    "memo",
    "incident",
    "handover",
    "observed",
    "impacted",
    "accounts",
    "escalation",
    "owner",
    "reporter",
    "time",
    "ips",
    "note",
    "client",
    "intake",
    "form",
    "prepared",
    "contacts",
    "meeting",
    "schedule",
    "monitoring",
    "repository",
    "repositories",
    "file",
    "files",
    "slack",
    "payment",
    "agreement",
    "invoice",
    "employment",
    "verification",
    "document",
    "role",
    "product",
    "designer",
    "contact",
    "number",
    "personal",
    "email",
    "company",
    "consultant",
    "section",
    "signature",
    "background",
    "review",
    "report",
    "summary",
    "referral",
    "letter",
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
    "senior",
    "analyst",
    "manager",
    "engineer",
    "officer",
    "specialist",
    "coordinator",
    "associate",
    "lead",
    "head",
    "current",
    "employer",
    "european",
    "union",
    "economic",
    "area",
    "eea",
    "eu",
    "uk",
    "states",
    "state",
    "united",
    "kingdom",
    "financial",
    "centre",
    "center",
    "tower",
    "building",
    "hi",
    "hello",
    "dear",
    "best",
    "regards",
}
ADDRESS_STREET_WORDS = r"(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd|Rue|Calle|Via|Strasse|Strada)"
ADDRESS_CONNECTOR_WORDS = r"(?:de|del|de la|du|des|di|da|la)"
CITY_TOKEN_PATTERN = r"[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'’-]+"
MONTH_NAME_PATTERN = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
MONTH_WORDS = {
    "jan", "january", "feb", "february", "mar", "march", "apr", "april", "may", "jun", "june",
    "jul", "july", "aug", "august", "sep", "sept", "september", "oct", "october", "nov", "november",
    "dec", "december",
}
TIME_CONTEXT_WORDS = {"am", "pm", "gmt", "utc", "bst", "cet", "cest", "est", "edt", "pst", "pdt"}
USERNAME_CONTEXT_BLOCK_WORDS = {
    "thread",
    "threads",
    "message",
    "messages",
    "from",
    "earlier",
    "channel",
    "channels",
    "repo",
    "repos",
    "repository",
    "repositories",
    "issue",
    "issues",
    "commit",
    "commits",
    "notes",
    "logs",
}
PROTECTED_JURISDICTION_RE = re.compile(
    r"\b(?:England and Wales|United Kingdom|United States|European Union|European Economic Area|EEA|EU|UK|USA)\b",
    re.IGNORECASE,
)
ANALYTICS_ID_RE = re.compile(r"\b(?:G-[A-Z0-9]{8,12}|UA-\d+-\d+)\b")
NUMBERED_HEADING_RE = re.compile(r"^\s*\d+\.\s+[A-Z][A-Za-z\s]+\s*$")
EXISTING_PLACEHOLDER_RE = re.compile(
    r"^\s*(?:[^\w\s]{0,3}\s*)?(?:Person|Organisation|Organization|Email|Phone|Location|Date|Web Address|Username|Connection String|API Key|Analytics ID|Crypto Wallet|Employee ID|Order ID|Booking Reference|Ticket Reference|Transaction ID|Company Registration Number|Payment Card Number)\s+\d+\s*$",
    re.IGNORECASE,
)
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
INITIAL_OPTIONAL_DOT_RE = re.compile(rf"^{INITIAL_OPTIONAL_DOT_PATTERN}$")
PERSON_SINGLE_NAME_RE = re.compile(rf"\b{NAME_TOKEN_PATTERN}\b")
IPV4_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
IPV6_RE = re.compile(r"\b(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}\b")
AT_USERNAME_RE = re.compile(r"(?<![\w/])@\w[\w.-]+\b")
LABELED_USERNAME_RE = re.compile(
    r"\b(?:github|slack)(?:(?:\s+username)?\s*:|\s+username\s+|\s+)\s*(@?[a-z0-9][a-z0-9_.-]{2,})\b",
    re.IGNORECASE,
)
API_KEY_OPENAI_RE = re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")
API_KEY_AWS_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
API_KEY_GITHUB_RE = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{20,})\b")
API_KEY_GOOGLE_RE = re.compile(r"\bAIza[0-9A-Za-z\-_]{31,35}\b")
CRYPTO_WALLET_RE = re.compile(
    r"\b(?:0x[a-fA-F0-9]{40}|bc1[ac-hj-np-z02-9]{11,71}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|T[1-9A-HJ-NP-Za-km-z]{33}|r[1-9A-HJ-NP-Za-km-z]{24,34})\b",
    re.IGNORECASE,
)
HOSTNAME_RE = re.compile(r"(?<![@/])\b(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+(?:[A-Za-z]{2,}|internal|local|lan|corp|cluster|localhost)\b")
CONNECTION_STRING_RE = re.compile(
    r"\b[a-z][a-z0-9+.-]*://[^\s:@/]+:[^\s@/]+@(?:\[[0-9A-Fa-f:]+\]|[A-Za-z0-9.-]+)(?::\d+)?(?:/[^\s]*)?",
    re.IGNORECASE,
)
API_KEY_LABELED_RE = re.compile(
    r"\b(?:[A-Z0-9_]*(?:OPENAI_KEY|AWS_SECRET|DATABASE_TOKEN|GITHUB_TOKEN|API_KEY|SECRET|TOKEN|ACCESS_KEY)[A-Z0-9_]*)\s*=\s*(?:['\"])?([^\s'\"\n]+)(?:['\"])?"
)
BOOKING_REFERENCE_RE = re.compile(
    r"\b(?:booking(?:\s+(?:id|reference))?|reservation|pnr)(?:\s+(?:number|id|ref(?:erence)?))?\s*[:#-]?\s*([A-Z0-9-]{8,20})\b",
    re.IGNORECASE,
)
TICKET_REFERENCE_RE = re.compile(
    r"\b(?:ticket(?:\s+(?:number|reference))?)(?:\s+(?:number|id|ref(?:erence)?))?\s*[:#-]?\s*([A-Z0-9-]{8,20})\b",
    re.IGNORECASE,
)
ORDER_ID_RE = re.compile(
    r"\b(?:order(?:\s+id)?|receipt(?:\s+id)?|case(?:\s+id)?|reference(?:\s+id)?|ref(?:\s+id)?)\s*[:#-]?\s*([A-Z0-9]{10,20}|[A-Z0-9-]{8,24})\b",
    re.IGNORECASE,
)
EMPLOYEE_ID_RE = re.compile(
    r"\b(?:employee(?:\s+(?:id|number))?|staff(?:\s+(?:id|number))?|personnel(?:\s+(?:id|number))?)\s*[:#-]?\s*([A-Z0-9]{2,12}(?:-[A-Z0-9]{1,12}){1,4}|[A-Z0-9]{4,20})\b",
    re.IGNORECASE,
)
EMPLOYEE_ID_VALUE_RE = re.compile(r"(?:[A-Z0-9]{2,12}(?:-[A-Z0-9]{1,12}){1,4}|[A-Z0-9]{4,20})", re.IGNORECASE)
TRANSACTION_ID_RE = re.compile(
    r"\b(?:transaction(?:\s+id)?|payment(?:\s+id)?|charge(?:\s+id)?|alt\s+txn|txn)\s*[:#-]?\s*([A-Z0-9]{3,12}(?:-[A-Z0-9]{2,12}){1,4}|[A-Z0-9]{8,24})\b",
    re.IGNORECASE,
)
TRANSACTION_ID_DIRECT_RE = re.compile(r"\b(?:ch|txn)_[A-Za-z0-9]+\b")
COMPANY_REGISTRATION_NUMBER_RE = re.compile(
    r"\b(?:Company\s+No(?:\.|Number)?|Company\s+Number|GST(?:\s+Reg(?:istration)?\s+No)?|Registration(?:\s+No)?|Reg(?:istration)?\s+No)\s*[:#-]?\s*([A-Z0-9]{8,12})\b",
    re.IGNORECASE,
)
INVOICE_NUMBER_RE = re.compile(
    r"\bINV-[A-Z0-9]+\b|\binvoice(?:\s+number)?\s*#\s*[A-Z0-9-]+\b",
    re.IGNORECASE,
)
WINDOWS_FILE_PATH_RE = re.compile(r"\b[A-Z]:\\(?:[^\\\s]+\\)*[^\\\s]+\b")
PRIVATE_KEY_BLOCK_RE = re.compile(
    r"-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA )?PRIVATE KEY-----",
    re.MULTILINE,
)
PRIVATE_KEY_HEADER_RE = re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----")
LABELED_VALUE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z ]{0,32})\s*(?::|->|→)\s*(.+?)\s*$")
PERSON_BOUNDARY_PATTERN = r"(?=\s|$|[),.;:\"'”’])"

_REGEX_DETECTORS = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "PHONE": re.compile(r"(?:\+?\d[\d\s().-]{7,}\d|\(\d{2,5}\)[\d\s.-]{5,}\d)"),
    "URL": re.compile(r"\bhttps?://[^\s\"'<>]+\b", re.IGNORECASE),
    "URL_HOSTNAME": HOSTNAME_RE,
    "CONNECTION_STRING": CONNECTION_STRING_RE,
    "API_KEY_OPENAI": API_KEY_OPENAI_RE,
    "API_KEY_AWS": API_KEY_AWS_RE,
    "API_KEY_GITHUB": API_KEY_GITHUB_RE,
    "API_KEY_GOOGLE": API_KEY_GOOGLE_RE,
    "CRYPTO_WALLET": CRYPTO_WALLET_RE,
    "ANALYTICS_ID": ANALYTICS_ID_RE,
    "API_KEY_LABELED": API_KEY_LABELED_RE,
    "PRIVATE_KEY_BLOCK": PRIVATE_KEY_BLOCK_RE,
    "PRIVATE_KEY_HEADER": PRIVATE_KEY_HEADER_RE,
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "GOVERNMENT_ID_SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "GOVERNMENT_ID_UK_NI": re.compile(r"\b[A-Z]{2}\d{6}[A-Z]\b"),
    "BANK_ACCOUNT_IBAN": re.compile(r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b"),
    "BOOKING_REFERENCE": BOOKING_REFERENCE_RE,
    "TICKET_REFERENCE": TICKET_REFERENCE_RE,
    "ORDER_ID": ORDER_ID_RE,
    "EMPLOYEE_ID": EMPLOYEE_ID_RE,
    "TRANSACTION_ID": TRANSACTION_ID_RE,
    "TRANSACTION_ID_DIRECT": TRANSACTION_ID_DIRECT_RE,
    "COMPANY_REGISTRATION_NUMBER": COMPANY_REGISTRATION_NUMBER_RE,
    "INVOICE_NUMBER": INVOICE_NUMBER_RE,
    "IP_ADDRESS_V4": IPV4_RE,
    "IP_ADDRESS_V6": IPV6_RE,
    "UK_REF": re.compile(r"\b(?:UAN|GWF|CAS|COS|CoS)[-:\s]*[A-Z0-9]{5,16}\b", re.IGNORECASE),
    "PASSPORT": re.compile(r"\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b|\b\d{9}\b"),
    "DATE": re.compile(
        rf"\b(?:\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}/\d{{1,2}}/\d{{2,4}}|\d{{1,2}}-\d{{1,2}}-\d{{2,4}}|\d{{1,2}}(?:st|nd|rd|th)?{INLINE_WS_PATTERN}{MONTH_NAME_PATTERN}{INLINE_WS_PATTERN}\d{{4}}|{MONTH_NAME_PATTERN}{INLINE_WS_PATTERN}\d{{1,2}}(?:st|nd|rd|th)?(?:,{INLINE_WS_PATTERN}|\s+)\d{{4}})\b",
        re.IGNORECASE,
    ),
    "ORG_PREFIXED": re.compile(
        rf"\b(?:Department|Institute|School|Faculty|Centre|Center){INLINE_WS_PATTERN}(?:of|for){INLINE_WS_PATTERN}{ORG_WORD_PATTERN}(?:{INLINE_WS_PATTERN}{ORG_WORD_PATTERN}){{0,5}}\b"
    ),
    "ORG_LEADING": re.compile(
        rf"\b(?:University|Institute|Instituto|Lab|Labs){INLINE_WS_PATTERN}(?:(?:of|for|de|del){INLINE_WS_PATTERN})?{ORG_WORD_PATTERN}(?:{INLINE_WS_PATTERN}{ORG_WORD_PATTERN}){{0,4}}\b"
    ),
    "ORG_SUFFIXED": re.compile(
        rf"\b{ORG_WORD_PATTERN}(?:{INLINE_WS_PATTERN}{ORG_WORD_PATTERN}){{0,5}}(?:{INLINE_WS_PATTERN}Pte\.?{INLINE_WS_PATTERN}Ltd\.?|{INLINE_WS_PATTERN}(?:Ltd\.?|Limited|Inc\.?|LLC|Corp\.?|GmbH|Consulting|Initiative|University|Lab|Labs|Institute|School|Faculty|Foundation|Alliance|Group|Network|Agency|Council|Bank|Office|Department|Systems?|Analytics|Research))\b"
    ),
    "ORG_SUFFIXED_DOTTED": re.compile(
        rf"\b[A-Z][A-Za-z0-9.-]*(?:{INLINE_WS_PATTERN}[A-Z][A-Za-z0-9&.'’-]*){{0,5}}(?:{INLINE_WS_PATTERN}Pte\.?{INLINE_WS_PATTERN}Ltd\.?|{INLINE_WS_PATTERN}(?:Ltd\.?|Limited|Inc\.?|LLC|Corp\.?|GmbH))\b"
    ),
    "ADDRESS_UK_FULL": re.compile(
        rf"\b\d{{1,5}}[A-Za-z]?{INLINE_WS_PATTERN}(?:{NAME_TOKEN_PATTERN}{INLINE_WS_PATTERN}){{0,4}}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd|View)\b"
        rf"(?:\s*(?:\r?\n|,\s*)\s*[A-Z][A-Za-z' -]{{1,40}}{INLINE_WS_PATTERN}[A-Z]{{1,2}}\d[A-Z\d]?\s?\d[A-Z]{{2}}\b)?"
        rf"(?:\s*(?:\r?\n|,\s*)\s*(?:United{INLINE_WS_PATTERN}Kingdom|UK|England{INLINE_WS_PATTERN}and{INLINE_WS_PATTERN}Wales))?",
        re.IGNORECASE,
    ),
    "ADDRESS_NUMBERED": re.compile(
        rf"\b\d{{1,5}}[A-Za-z]?{INLINE_WS_PATTERN}(?:{NAME_TOKEN_PATTERN}{INLINE_WS_PATTERN}){{0,4}}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd|View)\b"
    ),
    "ADDRESS_SHORT_NUMBERED": re.compile(
        rf"\b\d{{1,5}}[A-Za-z]?{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}}(?:,\s*{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}})?\b"
    ),
    "ADDRESS_EU_NUMBERED": re.compile(
        rf"\b\d{{1,5}}[A-Za-z]?{INLINE_WS_PATTERN}(?:{ADDRESS_STREET_WORDS})(?:{INLINE_WS_PATTERN}(?:{ADDRESS_CONNECTOR_WORDS}|{CITY_TOKEN_PATTERN})){{1,6}}(?:,\s*\d{{4,5}}{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}})?\b"
    ),
    "ADDRESS_EU_TRAILING_NUMBER": re.compile(
        rf"\b(?:{ADDRESS_STREET_WORDS})(?:{INLINE_WS_PATTERN}(?:{ADDRESS_CONNECTOR_WORDS}|{CITY_TOKEN_PATTERN})){{1,6}}{INLINE_WS_PATTERN}\d{{1,5}}[A-Za-z]?(?:,\s*\d{{4,5}}{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}})?\b"
    ),
    "ADDRESS_SG_BLOCK": re.compile(
        rf"\b(?:{ORG_WORD_PATTERN}|{CITY_TOKEN_PATTERN})(?:{INLINE_WS_PATTERN}(?:{ORG_WORD_PATTERN}|{CITY_TOKEN_PATTERN}|Financial|Centre|Center|Tower|Building|Plaza|Bay)){{1,6}}(?:\s*(?:\r?\n|,\s*)\s*(?:Tower{INLINE_WS_PATTERN}\d+|#{INLINE_WS_PATTERN}?\d{{1,2}}-\d{{2}}|Tower{INLINE_WS_PATTERN}\d+{INLINE_WS_PATTERN}#\d{{1,2}}-\d{{2}}))?(?:\s*(?:\r?\n|,\s*)\s*Singapore{INLINE_WS_PATTERN}\d{{6}})\b",
        re.IGNORECASE,
    ),
    "ADDRESS_INTL_BLOCK": re.compile(
        rf"\b(?:{ORG_WORD_PATTERN}|{CITY_TOKEN_PATTERN})(?:{INLINE_WS_PATTERN}(?:{ORG_WORD_PATTERN}|{CITY_TOKEN_PATTERN}|Financial|Centre|Center|Tower|Building|Plaza|Bay|Suite|Floor|Level|Unit|Block)){{1,8}}"
        rf"(?:\s*(?:\r?\n|,\s*)\s*(?:Tower{INLINE_WS_PATTERN}\d+|Suite{INLINE_WS_PATTERN}[A-Za-z0-9-]+|Floor{INLINE_WS_PATTERN}\d+|Level{INLINE_WS_PATTERN}\d+|Unit{INLINE_WS_PATTERN}[A-Za-z0-9-]+|#{INLINE_WS_PATTERN}?\d{{1,3}}-\d{{2}}))?"
        rf"(?:\s*(?:\r?\n|,\s*)\s*(?:{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,3}}{INLINE_WS_PATTERN}\d{{4,6}}|\d{{4,6}}{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,3}}|{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,3}}))"
        rf"(?:\s*(?:\r?\n|,\s*)\s*(?:Singapore|United{INLINE_WS_PATTERN}Kingdom|UK|England{INLINE_WS_PATTERN}and{INLINE_WS_PATTERN}Wales|France|Spain|Germany|Italy|Netherlands|Portugal|United{INLINE_WS_PATTERN}States|USA|European{INLINE_WS_PATTERN}Union))?\b",
        re.IGNORECASE,
    ),
    "ADDRESS_TOWER_BLOCK": re.compile(
        rf"\b(?:{CITY_TOKEN_PATTERN}|{ORG_WORD_PATTERN})(?:{INLINE_WS_PATTERN}(?:{CITY_TOKEN_PATTERN}|{ORG_WORD_PATTERN}|Centre|Center|Tower|Suite|Floor|Level|Unit|Block)){{0,5}}{INLINE_WS_PATTERN}Tower{INLINE_WS_PATTERN}\d+{INLINE_WS_PATTERN}#\d{{1,3}}-\d{{2}}(?:,\s*Singapore{INLINE_WS_PATTERN}\d{{6}})?\b",
        re.IGNORECASE,
    ),
    "ADDRESS_POSTCODE_CITY": re.compile(
        rf"\b\d{{4,5}}{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}}\b"
    ),
    "ADDRESS_VIA": re.compile(rf"\bVia{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}){{0,2}}\b"),
    "COORDINATE": re.compile(r"\b\d{1,3}\.\d+\s*°?\s*[NS],\s*\d{1,3}\.\d+\s*°?\s*[EW]\b", re.IGNORECASE),
    "FILE_PATH": re.compile(r"(?<!https:)(?<!http:)/(?:[^\s/]+/)+[^\s/]*"),
    "FILE_PATH_WINDOWS": WINDOWS_FILE_PATH_RE,
    "PERSON_TITLED": re.compile(
        rf"\b{PERSON_TITLE_PATTERN}\.?{INLINE_WS_PATTERN}(?:{PERSON_FULL_NAME_PATTERN}|{PERSON_DOUBLE_INITIAL_LAST_PATTERN}|{PERSON_INITIAL_LAST_PATTERN}|{PERSON_FIRST_INITIAL_PATTERN}){PERSON_BOUNDARY_PATTERN}"
    ),
    "PERSON_GREETING": re.compile(
        rf"\b(?:Hi|Hello|Dear){INLINE_WS_PATTERN}({PERSON_FULL_NAME_PATTERN}|{PERSON_DOUBLE_INITIAL_LAST_PATTERN}|{PERSON_INITIAL_LAST_PATTERN}|{PERSON_FIRST_INITIAL_PATTERN}){PERSON_BOUNDARY_PATTERN}",
        re.IGNORECASE,
    ),
    "PERSON_FULL": re.compile(rf"\b(?:{PERSON_FULL_NAME_PATTERN}|{PERSON_DOUBLE_INITIAL_LAST_PATTERN}){PERSON_BOUNDARY_PATTERN}"),
    "PERSON_INITIAL_LAST": re.compile(rf"\b{PERSON_INITIAL_LAST_PATTERN}{PERSON_BOUNDARY_PATTERN}"),
    "PERSON_FIRST_INITIAL": re.compile(rf"\b{PERSON_FIRST_INITIAL_PATTERN}{PERSON_BOUNDARY_PATTERN}"),
}

_REGEX_ENTITY_MAP = {
    "URL": "URL",
    "URL_HOSTNAME": "URL",
    "CONNECTION_STRING": "CONNECTION_STRING",
    "UK_REF": "ID",
    "PASSPORT": "ID",
    "EMAIL": "EMAIL",
    "API_KEY_OPENAI": "API_KEY",
    "API_KEY_AWS": "API_KEY",
    "API_KEY_GITHUB": "API_KEY",
    "API_KEY_GOOGLE": "API_KEY",
    "CRYPTO_WALLET": "CRYPTO_WALLET",
    "ANALYTICS_ID": "ANALYTICS_ID",
    "API_KEY_LABELED": "API_KEY",
    "PRIVATE_KEY_BLOCK": "PRIVATE_KEY",
    "PRIVATE_KEY_HEADER": "PRIVATE_KEY",
    "CREDIT_CARD": "CREDIT_CARD",
    "GOVERNMENT_ID_SSN": "GOVERNMENT_ID",
    "GOVERNMENT_ID_UK_NI": "GOVERNMENT_ID",
    "BANK_ACCOUNT_IBAN": "BANK_ACCOUNT",
    "BOOKING_REFERENCE": "BOOKING_REFERENCE",
    "TICKET_REFERENCE": "TICKET_REFERENCE",
    "ORDER_ID": "ORDER_ID",
    "EMPLOYEE_ID": "EMPLOYEE_ID",
    "TRANSACTION_ID": "TRANSACTION_ID",
    "TRANSACTION_ID_DIRECT": "TRANSACTION_ID",
    "COMPANY_REGISTRATION_NUMBER": "COMPANY_REGISTRATION_NUMBER",
    "INVOICE_NUMBER": "INVOICE_NUMBER",
    "PHONE": "PHONE",
    "DATE": "DATE",
    "IP_ADDRESS_V4": "IP_ADDRESS",
    "IP_ADDRESS_V6": "IP_ADDRESS",
    "ORG_PREFIXED": "ORG",
    "ORG_LEADING": "ORG",
    "ORG_SUFFIXED": "ORG",
    "ORG_SUFFIXED_DOTTED": "ORG",
    "ADDRESS_UK_FULL": "ADDRESS",
    "ADDRESS_NUMBERED": "ADDRESS",
    "ADDRESS_SHORT_NUMBERED": "ADDRESS",
    "ADDRESS_EU_NUMBERED": "ADDRESS",
    "ADDRESS_EU_TRAILING_NUMBER": "ADDRESS",
    "ADDRESS_SG_BLOCK": "ADDRESS",
    "ADDRESS_INTL_BLOCK": "ADDRESS",
    "ADDRESS_TOWER_BLOCK": "ADDRESS",
    "ADDRESS_POSTCODE_CITY": "ADDRESS",
    "ADDRESS_VIA": "ADDRESS",
    "COORDINATE": "COORDINATE",
    "FILE_PATH": "FILE_PATH",
    "FILE_PATH_WINDOWS": "FILE_PATH",
    "PERSON_TITLED": "PERSON",
    "PERSON_GREETING": "PERSON",
    "PERSON_FULL": "PERSON",
    "PERSON_INITIAL_LAST": "PERSON",
    "PERSON_FIRST_INITIAL": "PERSON",
}

SUPPORTED_TOGGLES = {
    "PERSON",
    "EMAIL",
    "PHONE",
    "ADDRESS",
    "ORG",
    "DATE",
    "URL",
    "CONNECTION_STRING",
    "IP_ADDRESS",
    "USERNAME",
    "COORDINATE",
    "FILE_PATH",
    "API_KEY",
    "CRYPTO_WALLET",
    "ANALYTICS_ID",
    "BOOKING_REFERENCE",
    "TICKET_REFERENCE",
    "ORDER_ID",
    "EMPLOYEE_ID",
    "TRANSACTION_ID",
    "COMPANY_REGISTRATION_NUMBER",
    "INVOICE_NUMBER",
    "CREDIT_CARD",
    "GOVERNMENT_ID",
    "BANK_ACCOUNT",
    "PRIVATE_KEY",
}
ENTITY_PRIORITY = {
    "EMAIL": 0,
    "URL": 1,
    "CONNECTION_STRING": 1,
    "API_KEY": 2,
    "ANALYTICS_ID": 2,
    "CRYPTO_WALLET": 3,
    "PRIVATE_KEY": 4,
    "CREDIT_CARD": 5,
    "GOVERNMENT_ID": 6,
    "BANK_ACCOUNT": 7,
    "COMPANY_REGISTRATION_NUMBER": 8,
    "INVOICE_NUMBER": 9,
    "EMPLOYEE_ID": 10,
    "BOOKING_REFERENCE": 11,
    "TICKET_REFERENCE": 12,
    "ORDER_ID": 13,
    "TRANSACTION_ID": 14,
    "IP_ADDRESS": 15,
    "PHONE": 16,
    "ADDRESS": 17,
    "DATE": 18,
    "PERSON": 19,
    "ORG": 20,
    "FILE_PATH": 21,
    "USERNAME": 22,
    "COORDINATE": 23,
}
SUPPORTED_LANGUAGE_CODE = "en"
SUPPORTED_LANGUAGE_LABEL = "English"
UNKNOWN_LANGUAGE_CODE = "unknown"
NON_ENGLISH_WARNING = "This text appears to be non-English. Entity detection may be less accurate."
STRUCTURED_PERSON_LABELS = {
    "person",
    "assistant",
    "contact",
    "manager",
    "director",
    "employee",
    "applicant name",
    "name",
    "prepared by",
    "reporter",
    "escalation owner",
}
NLP_ENTITY_MAP = {
    "PERSON": "PERSON",
    "ORG": "ORG",
    "LOCATION": "ADDRESS",
    "DATE_TIME": "DATE",
    "DATE": "DATE",
    "URL": "URL",
    "ANALYTICS_ID": "ANALYTICS_ID",
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

PRONOUN_REVERSE_MAP = {
    "she": "he",
    "he": "she",
    "him": "her",
    "her": "him",
    "his": "her",
    "hers": "his",
}
PRONOUN_REVERSE_RE = re.compile(r"\b(hers|his|him|her|she|he)\b", re.IGNORECASE)
PRONOUN_PROTECTED_RE = re.compile(
    r"```[\s\S]*?```|`[^`\n]+`|\[[^\]\n]{1,120}\]|\bhttps?://[^\s]+\b|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)
PRONOUN_ENGLISH_HINTS = set(PRONOUN_REVERSE_MAP)
NON_POSSESSIVE_HER_FOLLOWERS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but", "by",
    "can", "could", "did", "do", "does", "for", "from", "had", "has", "have",
    "if", "in", "into", "is", "may", "might", "must", "nor", "not", "of", "on",
    "or", "should", "than", "that", "the", "their", "them", "then", "there",
    "these", "they", "this", "those", "to", "was", "were", "will", "with", "would",
    "yesterday", "today", "tomorrow", "now", "later", "soon", "here", "back", "again",
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
            span = text[item.start : item.end]
            if mapped == "ADDRESS" and re.fullmatch(r"[A-Z]{3}", span or ""):
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


def should_apply_pronoun_reversal(text: str) -> bool:
    language = detect_language(text)
    if language == SUPPORTED_LANGUAGE_CODE:
        return True
    if language != UNKNOWN_LANGUAGE_CODE:
        return False

    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", (text or "").lower())
    if not words:
        return False

    english_score = sum(1 for word in words if word in LANGUAGE_HINTS["en"] or word in PRONOUN_ENGLISH_HINTS)
    foreign_score = 0
    for code, hints in LANGUAGE_HINTS.items():
        if code == SUPPORTED_LANGUAGE_CODE:
            continue
        foreign_score = max(foreign_score, sum(1 for word in words if word in hints))
    return english_score > 0 and english_score >= foreign_score + 1


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


def _has_immediate_capitalized_next_word(text: str, end: int) -> bool:
    return bool(re.match(rf"\s+{NAME_TOKEN_PATTERN}\b", text[end:]))


def _has_address_signal(value: str) -> bool:
    candidate = (value or "").strip()
    if not candidate:
        return False
    if re.search(rf"\b(?:{ADDRESS_STREET_WORDS})\b", candidate, re.IGNORECASE):
        return True
    if re.search(r"\b(?:tower|suite|floor|level|unit|block)\b|#\s*\d{1,3}-\d{2}\b", candidate, re.IGNORECASE):
        return True
    if re.search(
        rf"\b(?:Singapore|United{INLINE_WS_PATTERN}Kingdom|UK|England{INLINE_WS_PATTERN}and{INLINE_WS_PATTERN}Wales|France|Spain|Germany|Italy|Netherlands|Portugal|United{INLINE_WS_PATTERN}States|USA|European{INLINE_WS_PATTERN}Union)\b",
        candidate,
        re.IGNORECASE,
    ):
        return True
    if re.search(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", candidate):
        return True
    if re.search(r"\b\d{4,6}\b", candidate):
        return True
    if re.match(rf"^\d{{1,5}}[A-Za-z]?(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{1,4}}(?:,\s*{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}})?$", candidate):
        return True
    if re.match(rf"^(?:Via|Rue|Calle|Strasse|Strada){INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,3}}$", candidate, re.IGNORECASE):
        return True
    return False


def _has_conversational_from_context(text: str, start: int) -> bool:
    return bool(
        re.search(
            rf"\b(?:notes|message|comment){INLINE_WS_PATTERN}from{INLINE_WS_PATTERN}$",
            text[:start],
            re.IGNORECASE,
        )
    )


def _has_booking_or_order_context(text: str, start: int) -> bool:
    line_start = text.rfind("\n", 0, start) + 1
    line_prefix = text[line_start:start]
    if re.search(
        rf"\b(?:order(?:{INLINE_WS_PATTERN}id)?|receipt(?:{INLINE_WS_PATTERN}id)?|case(?:{INLINE_WS_PATTERN}id)?|reference(?:{INLINE_WS_PATTERN}id)?|ref(?:{INLINE_WS_PATTERN}id)?|booking(?:{INLINE_WS_PATTERN}(?:id|reference))?|ticket(?:{INLINE_WS_PATTERN}(?:number|reference))?|reservation|pnr|transaction(?:{INLINE_WS_PATTERN}id)?|payment(?:{INLINE_WS_PATTERN}id)?|employee(?:{INLINE_WS_PATTERN}(?:id|number))?|staff(?:{INLINE_WS_PATTERN}(?:id|number))?|personnel(?:{INLINE_WS_PATTERN}(?:id|number))?)\b",
        line_prefix,
        re.IGNORECASE,
    ):
        return True
    return bool(
        re.search(
            rf"\b(?:order(?:{INLINE_WS_PATTERN}id)?|receipt(?:{INLINE_WS_PATTERN}id)?|case(?:{INLINE_WS_PATTERN}id)?|reference(?:{INLINE_WS_PATTERN}id)?|ref(?:{INLINE_WS_PATTERN}id)?|booking(?:{INLINE_WS_PATTERN}(?:id|reference))?|ticket(?:{INLINE_WS_PATTERN}(?:number|reference))?|reservation|pnr|transaction(?:{INLINE_WS_PATTERN}id)?|payment(?:{INLINE_WS_PATTERN}id)?|employee(?:{INLINE_WS_PATTERN}(?:id|number))?|staff(?:{INLINE_WS_PATTERN}(?:id|number))?|personnel(?:{INLINE_WS_PATTERN}(?:id|number))?){INLINE_WS_PATTERN}$",
            text[:start],
            re.IGNORECASE,
        )
    )


def _inside_existing_token(text: str, start: int, end: int) -> bool:
    token_start = text.rfind("[", 0, start + 1)
    token_end = text.find("]", start)
    return token_start != -1 and token_end != -1 and token_start <= start and end <= token_end


def _inside_file_path(text: str, start: int, end: int) -> bool:
    return any(
        match.start() <= start and end <= match.end()
        for match in list(_REGEX_DETECTORS["FILE_PATH"].finditer(text)) + list(_REGEX_DETECTORS["FILE_PATH_WINDOWS"].finditer(text))
    )


def _inside_connection_string(text: str, start: int, end: int) -> bool:
    return any(match.start() <= start and end <= match.end() for match in CONNECTION_STRING_RE.finditer(text or ""))


def _looks_like_existing_placeholder(value: str) -> bool:
    return bool(EXISTING_PLACEHOLDER_RE.fullmatch((value or "").strip()))


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
    if NUMBERED_HEADING_RE.fullmatch(trimmed):
        return True
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


def _is_protected_heading_line(text: str, start: int) -> bool:
    return bool(NUMBERED_HEADING_RE.fullmatch(_get_line_at(text, start).strip()))


def _is_likely_phone_value(text: str) -> bool:
    if IPV4_RE.fullmatch((text or "").strip()):
        return False
    digits = re.sub(r"\D", "", text or "")
    return 8 <= len(digits) <= 15 and (len(digits) >= 10 or "+" in (text or "") or bool(re.search(r"[\s.-]", text or "")))


def _is_api_key_value(text: str) -> bool:
    candidate = (text or "").strip()
    return any(
        regex.fullmatch(candidate)
        for regex in (API_KEY_OPENAI_RE, API_KEY_AWS_RE, API_KEY_GITHUB_RE, API_KEY_GOOGLE_RE)
    )


def _is_likely_hostname_value(text: str) -> bool:
    candidate = (text or "").strip().strip(".,;:")
    if not candidate or any(char in candidate for char in "/@\\"):
        return False
    match = HOSTNAME_RE.fullmatch(candidate)
    if not match:
        return False
    labels = candidate.lower().split(".")
    if len(labels) < 2:
        return False
    last = labels[-1]
    fileish_suffixes = {"txt", "csv", "json", "md", "log", "pdf", "doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg", "gif", "zip", "tar", "gz"}
    if last in fileish_suffixes:
        return False
    if last in {"internal", "local", "lan", "corp", "cluster", "localhost"}:
        return True
    return len(labels) >= 3 or any("-" in label or any(char.isdigit() for char in label) for label in labels[:-1])


def _extract_url_candidate(text: str) -> Optional[str]:
    candidate = (text or "").strip()
    if not candidate:
        return None
    match = CONNECTION_STRING_RE.search(candidate)
    if match:
        return match.group(0)
    match = _REGEX_DETECTORS["URL"].search(candidate)
    if match:
        return match.group(0)
    match = HOSTNAME_RE.search(candidate)
    if match and _is_likely_hostname_value(match.group(0)):
        return match.group(0)
    return None


def _extract_api_key_candidate(text: str) -> Optional[str]:
    candidate = (text or "").strip()
    if not candidate:
        return None
    labeled_match = API_KEY_LABELED_RE.search(candidate)
    if labeled_match:
        return labeled_match.group(1)
    for regex in (API_KEY_OPENAI_RE, API_KEY_AWS_RE, API_KEY_GITHUB_RE, API_KEY_GOOGLE_RE):
        match = regex.search(candidate)
        if match:
            return match.group(0)
    return None


def _is_protected_region_phrase(value: str) -> bool:
    raw = (value or "").strip()
    candidate = re.sub(r"[(),.;:\s]+", " ", raw)
    candidate = re.sub(r"\s+", " ", candidate).strip()
    if candidate and PROTECTED_JURISDICTION_RE.fullmatch(candidate):
        return True
    parts = [part.strip() for part in re.split(r",", raw) if part.strip()]
    if len(parts) > 1:
        return all(_is_protected_region_phrase(part) for part in parts)
    return False


def _passes_luhn(text: str) -> bool:
    digits = re.sub(r"\D", "", text or "")
    if not 13 <= len(digits) <= 16:
        return False
    total = 0
    parity = len(digits) % 2
    for idx, char in enumerate(digits):
        num = int(char)
        if idx % 2 == parity:
            num *= 2
            if num > 9:
                num -= 9
        total += num
    return total % 10 == 0


def _is_address_false_positive(text: str, start: int, value: str) -> bool:
    if not _has_address_signal(value):
        return True
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+|\d+", (value or "").lower())
    if not words:
        return False
    if len(words[0]) <= 2 and start > 0 and text[start - 1] == ":":
        return True
    if len(words) in {2, 3} and words[0].isdigit() and words[1] in MONTH_WORDS:
        return len(words) == 2 or words[2].isdigit()
    if words[0].isdigit() and all(word in TIME_CONTEXT_WORDS for word in words[1:]):
        return True
    return False


def _apply_case_style(source: str, target: str) -> str:
    if not source:
        return target
    if source.isupper():
        return target.upper()
    if source.islower():
        return target.lower()
    if source[:1].isupper() and source[1:] == source[1:].lower():
        return target[:1].upper() + target[1:].lower()
    return target


def _replacement_for_reversed_pronoun(segment: str, match: re.Match[str]) -> str:
    source = match.group(0)
    lowered = source.lower()
    if lowered == "her":
        next_match = re.match(r"\s+([A-Za-zÀ-ÖØ-öø-ÿ']+)", segment[match.end() :])
        next_word = next_match.group(1).lower() if next_match else ""
        replacement = "his" if next_word and next_word not in NON_POSSESSIVE_HER_FOLLOWERS else "him"
    else:
        replacement = PRONOUN_REVERSE_MAP.get(lowered)

    if not replacement:
        return source
    return _apply_case_style(source, replacement)


def reverse_gendered_pronouns(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return _replacement_for_reversed_pronoun(match.string, match)

    output_parts: List[str] = []
    last_idx = 0
    for protected in PRONOUN_PROTECTED_RE.finditer(text):
        output_parts.append(PRONOUN_REVERSE_RE.sub(replace, text[last_idx : protected.start()]))
        output_parts.append(protected.group(0))
        last_idx = protected.end()
    output_parts.append(PRONOUN_REVERSE_RE.sub(replace, text[last_idx:]))
    return "".join(output_parts)


def _person_signature(cleaned: str) -> Optional[Dict[str, str]]:
    parts = [part for part in (cleaned or "").split() if part]
    if len(parts) == 2 and re.fullmatch(r"[A-Z]\.[A-Z]\.", parts[0]) and NAME_TOKEN_RE.fullmatch(parts[1]):
        return {"kind": "double_initial_last", "initials": parts[0][:3].lower(), "last": parts[1].lower()}
    if len(parts) == 2:
        first, last = parts
        if NAME_TOKEN_RE.fullmatch(first) and NAME_TOKEN_RE.fullmatch(last):
            return {"kind": "full", "first": first.lower(), "last": last.lower()}
        if INITIAL_OPTIONAL_DOT_RE.fullmatch(first) and NAME_TOKEN_RE.fullmatch(last):
            return {"kind": "initial_last", "first_initial": first[0].lower(), "last": last.lower()}
        if NAME_TOKEN_RE.fullmatch(first) and INITIAL_OPTIONAL_DOT_RE.fullmatch(last):
            return {"kind": "first_initial", "first": first.lower(), "last_initial": last[0].lower()}
        return None
    if len(parts) == 3 and all(NAME_TOKEN_RE.fullmatch(part) for part in parts):
        return {"kind": "full", "first": parts[0].lower(), "last": parts[-1].lower()}
    return None


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

    signature = _person_signature(cleaned)
    if not signature:
        return False
    normalized_parts = [part.lower().rstrip(".") for part in parts]
    if any(part in NON_PERSON_NAME_WORDS for part in normalized_parts):
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


COUNTRY_LINE_RE = re.compile(
    rf"^\s*(?:Singapore|United{INLINE_WS_PATTERN}Kingdom|UK|France|Spain|Germany|Italy|Netherlands|Portugal|United{INLINE_WS_PATTERN}States|USA)\s*$",
    re.IGNORECASE,
)


def _build_person_coreference_links(text: str, detections: Sequence[Detection]) -> tuple[list[Detection], dict[str, str]]:
    parsed_people = []
    for det in detections:
        if det.entity_type != "PERSON":
            continue
        raw = text[det.start : det.end].strip()
        cleaned = _strip_person_title(raw).strip()
        signature = _person_signature(cleaned)
        if not signature:
            continue
        parsed_people.append(
            {
                "raw": raw,
                "cleaned": cleaned,
                "canonical": _canonical_entity_key("PERSON", cleaned),
                **signature,
            }
        )

    full_names = [item for item in parsed_people if item["kind"] == "full"]
    if not full_names:
        return [], {}

    first_name_map: Dict[str, str] = {}
    last_name_map: Dict[str, str] = {}
    initial_last_map: Dict[tuple[str, str], str] = {}
    first_last_initial_map: Dict[tuple[str, str], str] = {}
    ambiguous_first: set[str] = set()
    ambiguous_last: set[str] = set()
    ambiguous_initial_last: set[tuple[str, str]] = set()
    ambiguous_first_last_initial: set[tuple[str, str]] = set()

    for full in full_names:
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

        first_initial_key = (full["first"], full["last"][0])
        existing_first_initial = first_last_initial_map.get(first_initial_key)
        if not existing_first_initial:
            first_last_initial_map[first_initial_key] = full["canonical"]
        elif existing_first_initial != full["canonical"]:
            ambiguous_first_last_initial.add(first_initial_key)

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
    for key in ambiguous_first_last_initial:
        first_last_initial_map.pop(key, None)

    alias_map: Dict[str, str] = {}
    for name, canonical in first_name_map.items():
        alias_map[_canonical_entity_key("PERSON", name)] = canonical
    for name, canonical in last_name_map.items():
        alias_map[_canonical_entity_key("PERSON", name)] = canonical
    for person in parsed_people:
        if person["kind"] == "initial_last":
            canonical = initial_last_map.get((person["first_initial"], person["last"]))
        elif person["kind"] == "first_initial":
            canonical = first_last_initial_map.get((person["first"], person["last_initial"]))
        else:
            canonical = None
        if canonical:
            alias_map[_canonical_entity_key("PERSON", person["cleaned"])] = canonical
            alias_map[_canonical_entity_key("PERSON", person["raw"])] = canonical

    additions: List[Detection] = []
    seen_spans = {(det.start, det.end) for det in detections if det.entity_type == "PERSON"}
    for key in ("PERSON_INITIAL_LAST", "PERSON_FIRST_INITIAL"):
        for match in _REGEX_DETECTORS[key].finditer(text):
            token = match.group(0)
            start = match.start()
            end = match.end()
            if (start, end) in seen_spans:
                continue
            signature = _person_signature(_strip_person_title(token).strip())
            if not signature:
                continue
            canonical = None
            if signature["kind"] == "initial_last":
                canonical = initial_last_map.get((signature["first_initial"], signature["last"]))
            elif signature["kind"] == "first_initial":
                canonical = first_last_initial_map.get((signature["first"], signature["last_initial"]))
            if not canonical:
                continue
            if any(not (end <= det.start or start >= det.end) for det in detections):
                continue
            if not _is_valid_person_span(text, start, end, token):
                continue
            alias_map[_canonical_entity_key("PERSON", token)] = canonical
            additions.append(Detection(entity_type="PERSON", start=start, end=end, score=0.8))
            seen_spans.add((start, end))

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
    if _looks_like_existing_placeholder(trimmed):
        return None
    trim_boundary = lambda value: re.sub(r"[),.;:]+$", "", (value or "").strip())
    if entity_type == "EMAIL":
        match = _REGEX_DETECTORS["EMAIL"].search(trimmed)
        return match.group(0) if match else None
    if entity_type == "URL":
        return _extract_url_candidate(trimmed)
    if entity_type == "CONNECTION_STRING":
        match = CONNECTION_STRING_RE.search(trimmed)
        return match.group(0) if match else None
    if entity_type == "API_KEY":
        return _extract_api_key_candidate(trimmed)
    if entity_type == "CRYPTO_WALLET":
        match = CRYPTO_WALLET_RE.search(trimmed)
        return match.group(0) if match else None
    if entity_type == "ANALYTICS_ID":
        match = ANALYTICS_ID_RE.search(trimmed)
        return match.group(0) if match else None
    if entity_type == "PRIVATE_KEY":
        match = PRIVATE_KEY_BLOCK_RE.search(trimmed) or PRIVATE_KEY_HEADER_RE.search(trimmed)
        return match.group(0) if match else None
    if entity_type == "CREDIT_CARD":
        match = _REGEX_DETECTORS["CREDIT_CARD"].search(trimmed)
        return match.group(0) if match and _passes_luhn(match.group(0)) else None
    if entity_type == "GOVERNMENT_ID":
        match = _REGEX_DETECTORS["GOVERNMENT_ID_SSN"].search(trimmed) or _REGEX_DETECTORS["GOVERNMENT_ID_UK_NI"].search(trimmed)
        return match.group(0) if match else None
    if entity_type == "BANK_ACCOUNT":
        match = _REGEX_DETECTORS["BANK_ACCOUNT_IBAN"].search(trimmed)
        return match.group(0) if match else None
    if entity_type == "BOOKING_REFERENCE":
        match = _REGEX_DETECTORS["BOOKING_REFERENCE"].search(trimmed)
        return match.group(1) if match else None
    if entity_type == "TICKET_REFERENCE":
        match = _REGEX_DETECTORS["TICKET_REFERENCE"].search(trimmed)
        return match.group(1) if match else None
    if entity_type == "ORDER_ID":
        match = _REGEX_DETECTORS["ORDER_ID"].search(trimmed)
        return match.group(1) if match else None
    if entity_type == "EMPLOYEE_ID":
        match = _REGEX_DETECTORS["EMPLOYEE_ID"].search(trimmed)
        if match:
            return match.group(1)
        candidate = trim_boundary(trimmed)
        return candidate if EMPLOYEE_ID_VALUE_RE.fullmatch(candidate) else None
    if entity_type == "TRANSACTION_ID":
        match = _REGEX_DETECTORS["TRANSACTION_ID"].search(trimmed)
        if match:
            return match.group(1)
        direct = _REGEX_DETECTORS["TRANSACTION_ID_DIRECT"].search(trimmed)
        return direct.group(0) if direct else None
    if entity_type == "COMPANY_REGISTRATION_NUMBER":
        match = _REGEX_DETECTORS["COMPANY_REGISTRATION_NUMBER"].search(trimmed)
        return match.group(1) if match else None
    if entity_type == "PHONE":
        match = _REGEX_DETECTORS["PHONE"].search(trimmed)
        return trim_boundary(match.group(0)) if match else None
    if entity_type == "PERSON":
        for key in ("PERSON_TITLED", "PERSON_FULL", "PERSON_INITIAL_LAST", "PERSON_FIRST_INITIAL"):
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
        match = _REGEX_DETECTORS["FILE_PATH"].search(trimmed) or _REGEX_DETECTORS["FILE_PATH_WINDOWS"].search(trimmed)
        return match.group(0) if match else None
    if entity_type == "USERNAME":
        match = AT_USERNAME_RE.search(trimmed)
        if match:
            return match.group(0)
        labeled = LABELED_USERNAME_RE.search(trimmed)
        if labeled and labeled.group(1).lower().lstrip("@") not in USERNAME_CONTEXT_BLOCK_WORDS:
            return labeled.group(1)
        return None
    if entity_type == "INVOICE_NUMBER":
        match = _REGEX_DETECTORS["INVOICE_NUMBER"].search(trimmed)
        return match.group(0) if match else None
    return trim_boundary(trimmed)


def structured_detect(text: str, enabled_types: Sequence[str]) -> List[Detection]:
    label_map = {
        "person": "PERSON",
        "assistant": "PERSON",
        "contact": "PERSON",
        "contact number": "PHONE",
        "contact no": "PHONE",
        "employee": "PERSON",
        "applicant name": "PERSON",
        "name": "PERSON",
        "prepared by": "PERSON",
        "reporter": "PERSON",
        "escalation owner": "PERSON",
        "manager": "PERSON",
        "director": "PERSON",
        "email": "EMAIL",
        "phone": "PHONE",
        "address": "ADDRESS",
        "organisation": "ORG",
        "organization": "ORG",
        "employer": "ORG",
        "current employer": "ORG",
        "date": "DATE",
        "url": "URL",
        "website": "URL",
        "web address": "URL",
        "api key": "API_KEY",
        "apikey": "API_KEY",
        "wallet": "CRYPTO_WALLET",
        "wallet address": "CRYPTO_WALLET",
        "walletaddress": "CRYPTO_WALLET",
        "crypto wallet": "CRYPTO_WALLET",
        "cryptowallet": "CRYPTO_WALLET",
        "crypto address": "CRYPTO_WALLET",
        "cryptoaddress": "CRYPTO_WALLET",
        "eth address": "CRYPTO_WALLET",
        "eth wallet": "CRYPTO_WALLET",
        "btc address": "CRYPTO_WALLET",
        "btc wallet": "CRYPTO_WALLET",
        "bitcoin address": "CRYPTO_WALLET",
        "bitcoin wallet": "CRYPTO_WALLET",
        "analytics id": "ANALYTICS_ID",
        "analyticsid": "ANALYTICS_ID",
        "measurement id": "ANALYTICS_ID",
        "measurementid": "ANALYTICS_ID",
        "credit card": "CREDIT_CARD",
        "creditcard": "CREDIT_CARD",
        "government id": "GOVERNMENT_ID",
        "governmentid": "GOVERNMENT_ID",
        "bank account": "BANK_ACCOUNT",
        "bankaccount": "BANK_ACCOUNT",
        "booking reference": "BOOKING_REFERENCE",
        "bookingreference": "BOOKING_REFERENCE",
        "ticket number": "TICKET_REFERENCE",
        "ticketnumber": "TICKET_REFERENCE",
        "ticket reference": "TICKET_REFERENCE",
        "ticketreference": "TICKET_REFERENCE",
        "pnr": "BOOKING_REFERENCE",
        "reservation": "BOOKING_REFERENCE",
        "order id": "ORDER_ID",
        "orderid": "ORDER_ID",
        "case id": "ORDER_ID",
        "caseid": "ORDER_ID",
        "booking id": "BOOKING_REFERENCE",
        "bookingid": "BOOKING_REFERENCE",
        "receipt id": "ORDER_ID",
        "receiptid": "ORDER_ID",
        "employee id": "EMPLOYEE_ID",
        "employeeid": "EMPLOYEE_ID",
        "employee number": "EMPLOYEE_ID",
        "employeenumber": "EMPLOYEE_ID",
        "staff id": "EMPLOYEE_ID",
        "staffid": "EMPLOYEE_ID",
        "staff number": "EMPLOYEE_ID",
        "staffnumber": "EMPLOYEE_ID",
        "personnel id": "EMPLOYEE_ID",
        "personnelid": "EMPLOYEE_ID",
        "personnel number": "EMPLOYEE_ID",
        "personnelnumber": "EMPLOYEE_ID",
        "transaction id": "TRANSACTION_ID",
        "transactionid": "TRANSACTION_ID",
        "payment id": "TRANSACTION_ID",
        "paymentid": "TRANSACTION_ID",
        "charge id": "TRANSACTION_ID",
        "chargeid": "TRANSACTION_ID",
        "company no": "COMPANY_REGISTRATION_NUMBER",
        "companyno": "COMPANY_REGISTRATION_NUMBER",
        "company number": "COMPANY_REGISTRATION_NUMBER",
        "companynumber": "COMPANY_REGISTRATION_NUMBER",
        "gst": "COMPANY_REGISTRATION_NUMBER",
        "gst reg no": "COMPANY_REGISTRATION_NUMBER",
        "gst regno": "COMPANY_REGISTRATION_NUMBER",
        "registration": "COMPANY_REGISTRATION_NUMBER",
        "registration no": "COMPANY_REGISTRATION_NUMBER",
        "registrationno": "COMPANY_REGISTRATION_NUMBER",
        "reg no": "COMPANY_REGISTRATION_NUMBER",
        "regno": "COMPANY_REGISTRATION_NUMBER",
        "invoice": "INVOICE_NUMBER",
        "invoice number": "INVOICE_NUMBER",
        "invoicenumber": "INVOICE_NUMBER",
        "private key": "PRIVATE_KEY",
        "privatekey": "PRIVATE_KEY",
        "slack": "USERNAME",
        "github": "USERNAME",
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
        if NUMBERED_HEADING_RE.fullmatch(line.strip()):
            offset += len(line) + 1
            continue
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
                            pass
                        elif mapped == "PERSON":
                            if label in STRUCTURED_PERSON_LABELS:
                                cleaned = _strip_person_title(extracted).strip()
                                is_structured_person = bool(_person_signature(cleaned) or NAME_TOKEN_RE.fullmatch(cleaned))
                                if not is_structured_person:
                                    pass
                                else:
                                    detections.append(
                                        Detection(
                                            entity_type=mapped,
                                            start=start,
                                            end=end,
                                            score=0.995,
                                        )
                                    )
                            elif _is_valid_person_span(text, start, end, extracted):
                                detections.append(
                                    Detection(
                                        entity_type=mapped,
                                        start=start,
                                        end=end,
                                        score=0.995,
                                    )
                                )
                        else:
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
        if key == "CONNECTION_STRING":
            if "CONNECTION_STRING" not in enabled_types and "URL" not in enabled_types:
                continue
        elif mapped and mapped not in enabled_types:
            continue
        for match in pattern.finditer(text):
            start = match.start()
            end = match.end()
            if key == "API_KEY_LABELED":
                start = match.start(1)
                end = match.end(1)
            if key == "PERSON_GREETING":
                start = match.start(1)
                end = match.end(1)
            if key in {"BOOKING_REFERENCE", "TICKET_REFERENCE", "ORDER_ID", "EMPLOYEE_ID", "TRANSACTION_ID"}:
                start = match.start(1)
                end = match.end(1)
            if key == "COMPANY_REGISTRATION_NUMBER":
                start = match.start(1)
                end = match.end(1)
            value = text[start:end]
            if _looks_like_existing_placeholder(value):
                continue
            if _inside_existing_token(text, start, end):
                continue
            if _is_protected_heading_line(text, start):
                continue
            if mapped == "CREDIT_CARD" and not _passes_luhn(match.group(0)):
                continue
            if mapped == "PHONE" and not _is_likely_phone_value(value):
                continue
            if mapped == "PHONE" and _has_booking_or_order_context(text, start):
                continue
            if mapped == "EMAIL" and _inside_connection_string(text, start, end):
                continue
            if mapped == "URL" and not _extract_url_candidate(value):
                continue
            if key == "CONNECTION_STRING" and not CONNECTION_STRING_RE.fullmatch(value):
                continue
            if mapped == "ADDRESS" and _is_address_false_positive(text, start, value):
                continue
            if mapped == "ADDRESS" and _is_protected_region_phrase(value):
                continue
            if mapped == "ORG" and (_is_ignored_entity_phrase(value) or _has_ignored_entity_context(text, start)):
                continue
            if mapped == "PERSON" and not _is_valid_person_span(text, start, end, value):
                continue
            detections.append(
                Detection(entity_type=("CONNECTION_STRING" if key == "CONNECTION_STRING" else (mapped or key)), start=start, end=end, score=0.99)
            )
    if "USERNAME" in enabled_types:
        for match in AT_USERNAME_RE.finditer(text):
            if _is_protected_heading_line(text, match.start()):
                continue
            if _inside_existing_token(text, match.start(), match.end()) or _inside_file_path(text, match.start(), match.end()):
                continue
            detections.append(Detection(entity_type="USERNAME", start=match.start(), end=match.end(), score=0.97))
        for match in LABELED_USERNAME_RE.finditer(text):
            handle = match.group(1)
            if not handle:
                continue
            if _is_protected_heading_line(text, match.start(1)):
                continue
            if handle.lower().lstrip("@") in USERNAME_CONTEXT_BLOCK_WORDS:
                continue
            start = match.start(1)
            end = match.end(1)
            if _is_api_key_value(handle):
                continue
            if _inside_existing_token(text, start, end) or _inside_file_path(text, start, end):
                continue
            detections.append(Detection(entity_type="USERNAME", start=start, end=end, score=0.975))
    return detections


def org_heuristic_detect(text: str, enabled_types: Sequence[str], locked: Sequence[Detection]) -> List[Detection]:
    if "ORG" not in enabled_types:
        return []

    detections: List[Detection] = []
    locked_spans = [(det.start, det.end) for det in locked]

    def overlaps(start: int, end: int) -> bool:
        return any(not (end <= left or start >= right) for left, right in locked_spans)

    def provider_followed_by_masked_card(end: int) -> bool:
        return bool(re.match(rf"{INLINE_WS_PATTERN}\*{{4}}(?:{INLINE_WS_PATTERN}\*{{4}}){{2}}{INLINE_WS_PATTERN}\d{{4}}\b", text[end:]))

    contextual_single = re.compile(
        rf"\b(?:at|with|for|from|of|into|joined|joining|works(?:{INLINE_WS_PATTERN}at)?|worked(?:{INLINE_WS_PATTERN}at)?|working(?:{INLINE_WS_PATTERN}at)?|employed(?:{INLINE_WS_PATTERN}at)?)"
        rf"{INLINE_WS_PATTERN}([A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ0-9&.'’-]{{2,}}|[A-Z]{{2,}})\b"
    )
    for match in contextual_single.finditer(text):
        candidate = match.group(1)
        start = match.start(1)
        end = match.end(1)
        lowered = candidate.lower()
        if overlaps(start, end):
            continue
        if _is_protected_heading_line(text, start):
            continue
        if _has_conversational_from_context(text, start):
            continue
        if lowered in NON_PERSON_NAME_WORDS or lowered in STREET_SUFFIX_WORDS or lowered in STREET_PREFIX_WORDS:
            continue
        if lowered in ORG_CONTEXT_WORDS or lowered in {"he", "she", "they", "them"}:
            continue
        if lowered in {"london", "paris", "singapore", "madrid", "manchester", "oxford"}:
            continue
        if _has_ignored_entity_context(text, start):
            continue
        if _is_ignored_entity_phrase(candidate) or _is_street_like_phrase(candidate):
            continue
        if _has_immediate_capitalized_next_word(text, end) and not _is_org_like_phrase(candidate):
            continue
        if _is_likely_heading_line(_get_line_at(text, start)):
            continue
        detections.append(Detection(entity_type="ORG", start=start, end=end, score=0.86))

    contextual_at = re.compile(
        rf"(?<!\w)@{INLINE_WS_PATTERN}([A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ0-9&.'’-]{{2,}}(?:{INLINE_WS_PATTERN}[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ0-9&.'’-]{{2,}}){{0,3}})"
    )
    for match in contextual_at.finditer(text):
        candidate = match.group(1)
        start = match.start(1)
        end = match.end(1)
        lowered = candidate.lower()
        if overlaps(start, end):
            continue
        if _is_protected_heading_line(text, start):
            continue
        if lowered in NON_PERSON_NAME_WORDS or lowered in STREET_SUFFIX_WORDS or lowered in STREET_PREFIX_WORDS:
            continue
        if lowered in ORG_CONTEXT_WORDS or lowered in {"he", "she", "they", "them"}:
            continue
        if lowered in {"london", "paris", "singapore", "madrid", "manchester", "oxford"}:
            continue
        if _has_ignored_entity_context(text, start):
            continue
        if _is_ignored_entity_phrase(candidate) or _is_street_like_phrase(candidate):
            continue
        detections.append(Detection(entity_type="ORG", start=start, end=end, score=0.87))

    parenthetical_proper = re.compile(rf"\(([A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ0-9&.'’-]*(?:{INLINE_WS_PATTERN}[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ0-9&.'’-]*){{0,3}})\)")
    for match in parenthetical_proper.finditer(text):
        candidate = match.group(1)
        start = match.start(1)
        end = match.end(1)
        lowered = candidate.lower()
        if overlaps(start, end):
            continue
        if _is_protected_heading_line(text, start):
            continue
        if lowered in NON_PERSON_NAME_WORDS or lowered in STREET_SUFFIX_WORDS or lowered in STREET_PREFIX_WORDS:
            continue
        if lowered in {"london", "paris", "singapore", "madrid", "manchester", "oxford"}:
            continue
        if _is_street_like_phrase(candidate) or _is_ignored_entity_phrase(candidate):
            continue
        if _has_immediate_capitalized_next_word(text, end) and not _is_org_like_phrase(candidate):
            continue
        detections.append(Detection(entity_type="ORG", start=start, end=end, score=0.84))

    transport_brand = re.compile(r"\b[A-Z][A-Za-z]*(?:rail|west|air|transport|group)[A-Za-z]*\b", re.IGNORECASE)
    for match in transport_brand.finditer(text):
        candidate = match.group(0)
        start = match.start()
        end = match.end()
        if overlaps(start, end):
            continue
        if _is_protected_heading_line(text, start):
            continue
        if _is_ignored_entity_phrase(candidate) or _is_street_like_phrase(candidate):
            continue
        detections.append(Detection(entity_type="ORG", start=start, end=end, score=0.83))

    dotted_legal_org = re.compile(
        rf"\b[A-Z][A-Za-z0-9.-]*(?:{INLINE_WS_PATTERN}[A-Z][A-Za-z0-9&.'’-]*){{0,5}}(?:{INLINE_WS_PATTERN}Pte\.?{INLINE_WS_PATTERN}Ltd\.?|{INLINE_WS_PATTERN}(?:Ltd\.?|Limited|Inc\.?|LLC|Corp\.?|GmbH))\b"
    )
    for match in dotted_legal_org.finditer(text):
        candidate = match.group(0)
        start = match.start()
        end = match.end()
        if overlaps(start, end):
            continue
        if _is_protected_heading_line(text, start):
            continue
        if _is_ignored_entity_phrase(candidate) or _is_street_like_phrase(candidate):
            continue
        detections.append(Detection(entity_type="ORG", start=start, end=end, score=0.9))

    payment_provider = re.compile(r"\b(?:Apple Pay|Google Pay|Visa|Mastercard|Amex|American Express|PayPal|Stripe)\b", re.IGNORECASE)
    for match in payment_provider.finditer(text):
        start = match.start()
        end = match.end()
        if overlaps(start, end):
            continue
        if _is_protected_heading_line(text, start):
            continue
        if provider_followed_by_masked_card(end):
            continue
        detections.append(Detection(entity_type="ORG", start=start, end=end, score=0.9))

    return detections


def person_conversational_detect(text: str, enabled_types: Sequence[str], locked: Sequence[Detection]) -> List[Detection]:
    if "PERSON" not in enabled_types:
        return []

    detections: List[Detection] = []
    locked_spans = [(det.start, det.end) for det in locked]

    def overlaps(start: int, end: int) -> bool:
        return any(not (end <= left or start >= right) for left, right in locked_spans)

    pattern = re.compile(
        rf"\b(?:notes|message|comment){INLINE_WS_PATTERN}from{INLINE_WS_PATTERN}((?:{PERSON_FULL_NAME_PATTERN}|{NAME_TOKEN_PATTERN}))\b",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        candidate = match.group(1)
        start = match.start(1)
        end = match.end(1)
        if overlaps(start, end):
            continue
        if _is_protected_heading_line(text, start):
            continue
        if _is_org_like_phrase(candidate) or _is_ignored_entity_phrase(candidate) or _is_street_like_phrase(candidate):
            continue
        if not _is_valid_person_span(text, start, end, candidate):
            continue
        detections.append(Detection(entity_type="PERSON", start=start, end=end, score=0.88))

    quoted_name = re.compile(rf"[\"“]((?:{PERSON_FULL_NAME_PATTERN}|{PERSON_DOUBLE_INITIAL_LAST_PATTERN}|{PERSON_INITIAL_LAST_PATTERN}|{PERSON_FIRST_INITIAL_PATTERN}))(?=\s|$|[\"”])")
    for match in quoted_name.finditer(text):
        candidate = match.group(1)
        start = match.start(1)
        end = match.end(1)
        if overlaps(start, end):
            continue
        if _is_protected_heading_line(text, start):
            continue
        if _is_org_like_phrase(candidate) or _is_ignored_entity_phrase(candidate) or _is_street_like_phrase(candidate):
            continue
        if not _is_valid_person_span(text, start, end, candidate):
            continue
        detections.append(Detection(entity_type="PERSON", start=start, end=end, score=0.84))

    return detections


def late_location_cue_detect(text: str, enabled_types: Sequence[str], locked: Sequence[Detection]) -> List[Detection]:
    if "ADDRESS" not in enabled_types:
        return []

    detections: List[Detection] = []
    locked_spans = [(det.start, det.end) for det in locked]

    def overlaps(start: int, end: int) -> bool:
        return any(not (end <= left or start >= right) for left, right in locked_spans)

    pattern = re.compile(r"\b(?:from|in|at|location called)\s+([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2})\b")
    for match in pattern.finditer(text):
        place = match.group(1)
        start = match.start(1)
        end = match.end(1)
        lowered = place.lower()
        if overlaps(start, end):
            continue
        if _is_protected_heading_line(text, start):
            continue
        if _is_protected_region_phrase(place):
            continue
        if lowered in NON_PERSON_NAME_WORDS or lowered in STREET_SUFFIX_WORDS or lowered in STREET_PREFIX_WORDS:
            continue
        if _is_org_like_phrase(place):
            continue
        detections.append(Detection(entity_type="ADDRESS", start=start, end=end, score=0.69))
    return detections


def trailing_person_tail_detect(text: str, enabled_types: Sequence[str], locked: Sequence[Detection]) -> List[Detection]:
    if "PERSON" not in enabled_types:
        return []

    detections: List[Detection] = []
    locked_spans = [(det.start, det.end) for det in locked]

    def overlaps(start: int, end: int) -> bool:
        return any(not (end <= left or start >= right) for left, right in locked_spans)

    pattern = re.compile(rf"(?:[\"“]|note{INLINE_WS_PATTERN}[\"“])((?:{PERSON_FULL_NAME_PATTERN}|{PERSON_DOUBLE_INITIAL_LAST_PATTERN}|{PERSON_INITIAL_LAST_PATTERN}|{PERSON_FIRST_INITIAL_PATTERN}))\s*$")
    match = pattern.search(text)
    if not match:
        return detections
    candidate = match.group(1)
    start = match.start(1)
    end = match.end(1)
    if overlaps(start, end):
        return detections
    if _is_protected_heading_line(text, start):
        return detections
    if _is_org_like_phrase(candidate) or _is_ignored_entity_phrase(candidate) or _is_street_like_phrase(candidate):
        return detections
    if not _person_signature(_strip_person_title(candidate)):
        return detections
    normalized_parts = [part.lower().rstrip(".") for part in candidate.split()]
    if any(part in NON_PERSON_NAME_WORDS for part in normalized_parts):
        return detections
    if _has_ignored_entity_context(text, start) or _has_org_prefix_context(text, start):
        return detections
    detections.append(Detection(entity_type="PERSON", start=start, end=end, score=0.83))
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


def _merge_address_blocks(text: str, detections: Sequence[Detection]) -> List[Detection]:
    merged: List[Detection] = []
    ordered = sorted(detections, key=lambda d: (d.start, d.end))
    idx = 0
    while idx < len(ordered):
        current = ordered[idx]
        if current.entity_type != "ADDRESS":
            merged.append(current)
            idx += 1
            continue
        start = current.start
        end = current.end
        score = current.score
        j = idx + 1
        while j < len(ordered):
            nxt = ordered[j]
            if nxt.entity_type != "ADDRESS":
                break
            bridge = text[end:nxt.start]
            if not re.fullmatch(r"(?:\s|,|\r?\n)+", bridge):
                break
            end = nxt.end
            score = max(score, nxt.score)
            j += 1
        tail = text[end:]
        country = re.match(
            r"(?:\s*(?:,|\r?\n)\s*)(Singapore|United Kingdom|UK|England and Wales|France|Spain|Germany|Italy|Netherlands|Portugal|United States|USA|European Union)\b",
            tail,
            re.IGNORECASE,
        )
        if country:
            end += country.end()
        merged.append(Detection(entity_type="ADDRESS", start=start, end=end, score=score))
        idx = j
    return merged


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
    raw_text = "".join(output_parts)
    cleaned_text = re.sub(r"(\[[A-Z_]+_\d+\])(?:\s+\1)+", r"\1", raw_text)
    return {
        "anonymized_text": cleaned_text,
        "entities": entities,
        "counts": counters,
    }


def anonymize_text(
    text: str,
    enabled_types: Sequence[str],
    nlp: OptionalNlp,
    reverse_pronouns: bool = False,
) -> Dict[str, object]:
    clean_types = [t for t in enabled_types if t in SUPPORTED_TOGGLES]
    structured_hits = structured_detect(text, clean_types)
    regex_hits = regex_detect(text, clean_types)
    nlp_hits = nlp.detect(text, clean_types)
    org_hits = org_heuristic_detect(text, clean_types, [*structured_hits, *regex_hits, *nlp_hits])
    person_hits = person_conversational_detect(text, clean_types, [*structured_hits, *regex_hits, *nlp_hits, *org_hits])
    tail_person_hits = trailing_person_tail_detect(text, clean_types, [*structured_hits, *regex_hits, *nlp_hits, *org_hits, *person_hits])
    location_hits = late_location_cue_detect(text, clean_types, [*structured_hits, *regex_hits, *nlp_hits, *org_hits, *person_hits, *tail_person_hits])

    merged = _resolve_overlaps([*structured_hits, *regex_hits, *nlp_hits, *org_hits, *person_hits, *tail_person_hits, *location_hits])
    merged = _merge_address_blocks(text, merged)
    alias_additions: List[Detection] = []
    alias_map: Dict[str, str] = {}
    if "PERSON" in clean_types:
        alias_additions, alias_map = _build_person_coreference_links(text, merged)
        merged = _resolve_overlaps([*merged, *alias_additions])
    replaced = apply_replacements(text, merged, alias_map=alias_map)
    if reverse_pronouns and should_apply_pronoun_reversal(text):
        replaced["anonymized_text"] = reverse_gendered_pronouns(replaced["anonymized_text"])
    replaced["cta_visaprep"] = bool(IMMIGRATION_KEYWORDS.search(text))
    return replaced
