from __future__ import annotations

import re
import unicodedata
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Sequence


@dataclass
class Detection:
    entity_type: str
    start: int
    end: int
    score: float


@dataclass(frozen=True)
class DetectorContext:
    text: str
    enabled_types: Sequence[str]
    structured_hits: Sequence[Detection]
    regex_hits: Sequence[Detection]
    nlp_hits: Sequence[Detection]


@dataclass(frozen=True)
class DetectorPlugin:
    name: str
    detect: Callable[[DetectorContext, Sequence[Detection]], List[Detection]]


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
PERSON_INITIAL_THREE_PATTERN = rf"{INITIAL_OPTIONAL_DOT_PATTERN}{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}"
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
    "bill",
    "reason",
    "pay",
    "method",
    "auth",
    "adult",
    "social",
    "care",
    "precept",
    "admin",
    "unit",
    "band",
    "property",
    "reference",
    "annual",
    "charge",
    "balance",
    "brought",
    "forward",
    "period",
    "payments",
    "received",
    "issue",
    "total",
    "outstanding",
    "instalment",
    "instalments",
    "debit",
    "monthly",
    "additional",
    "information",
    "government",
    "energy",
    "bills",
    "rebate",
    "borough",
    "authority",
    "account",
    "number",
    "attributable",
    "increase",
    "house",
    "save",
    "mint",
    "walk",
    "gp",
    "test",
    "tests",
    "result",
    "results",
    "printed",
    "requested",
    "attached",
    "returned",
    "clinician",
    "patient",
    "record",
    "specimen",
    "collected",
    "battery",
    "headers",
    "indicator",
    "follow",
    "action",
    "filing",
    "comments",
    "abnormal",
    "normal",
    "appointment",
    "doctor",
    "nurse",
    "full",
    "blood",
    "count",
    "white",
    "red",
    "cell",
    "below",
    "above",
    "range",
    "low",
    "high",
    "limit",
    "haemoglobin",
    "haematocrit",
    "mean",
    "volume",
    "platelet",
    "neutrophil",
    "lymphocyte",
    "monocyte",
    "eosinophil",
    "basophil",
    "textual",
    "clinical",
    "renal",
    "function",
    "serum",
    "sodium",
    "potassium",
    "creatinine",
    "urea",
    "protein",
    "transferase",
    "liver",
    "ferritin",
    "folate",
    "vitamin",
    "diagnosis",
    "hepatitis",
    "surface",
    "antigen",
    "antibody",
    "detected",
    "infection",
    "vaccinated",
    "immunisation",
    "microscopy",
    "reticulocyte",
    "macrocytosis",
    "hi",
    "hello",
    "dear",
    "best",
    "regards",
}
PERSON_CONNECTOR_WORDS = {
    "and",
    "or",
    "for",
    "of",
    "the",
    "to",
    "from",
    "at",
    "on",
    "in",
    "by",
    "with",
    "as",
    "into",
}
TABULAR_CONTEXT_HINT_WORDS = {
    "account",
    "number",
    "tax",
    "band",
    "property",
    "reference",
    "charge",
    "balance",
    "payments",
    "received",
    "period",
    "instalment",
    "instalments",
    "due",
    "outstanding",
    "annual",
    "admin",
    "unit",
    "increase",
    "greater",
    "invoice",
    "total",
    "income",
    "insurance",
    "paye",
    "payroll",
}
CLINICAL_CONTEXT_WORDS = {
    "specimen",
    "collected",
    "filed",
    "battery",
    "headers",
    "result",
    "results",
    "indicator",
    "follow-up",
    "follow",
    "action",
    "filing",
    "comments",
    "normal",
    "abnormal",
    "blood",
    "count",
    "serum",
    "renal",
    "liver",
    "clinical",
    "information",
    "haemoglobin",
    "haematocrit",
    "platelet",
    "neutrophil",
    "lymphocyte",
    "monocyte",
    "eosinophil",
    "basophil",
    "hepatitis",
    "antibody",
    "antigen",
    "bilirubin",
    "ferritin",
    "folate",
    "vitamin",
    "reticulocyte",
    "microscopy",
}
CLINICAL_MEASUREMENT_RE = re.compile(
    r"\b(?:10\^\d+/L|mmol/L|umol/L|g/L|g/dL|miu/L|iu/L|ng/ml|mL/min|fL|pg)\b",
    re.IGNORECASE,
)
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
SECRET_CONTEXT_BLOCK_WORDS = {
    "order",
    "booking",
    "ticket",
    "invoice",
    "case",
    "transaction",
    "employee",
    "staff",
    "personnel",
    "reference",
    "receipt",
    "id",
    "number",
    "phone",
    "mobile",
    "host",
    "ip",
    "date",
    "time",
    "paye",
    "nhs",
    "tax",
    "code",
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
    r"\b(?:github|slack)(?:"
    r"(?:\s+(?:username|user)\s*[:=]\s*|\s+(?:username|user)\s+|\s*[:=]\s*)(@?[a-z0-9][a-z0-9_.-]{2,})"
    r"|"
    r"\s+(@?[a-z0-9][a-z0-9_.-]{2,})(?=\s*(?:[,.;)\]\r\n]|$))"
    r")",
    re.IGNORECASE,
)
API_KEY_OPENAI_RE = re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")
API_KEY_AWS_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
API_KEY_GITHUB_RE = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{20,})\b")
API_KEY_GITLAB_RE = re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")
API_KEY_GOOGLE_RE = re.compile(r"\bAIza[0-9A-Za-z\-_]{31,35}\b")
API_KEY_SSH_PUBLIC_RE = re.compile(r"\b(?:ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp256)\s+[A-Za-z0-9+/=]{20,}(?:\s+\S+)?")
API_KEY_JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{2,}\.[A-Za-z0-9_-]{8,}\b")
API_KEY_BEARER_RE = re.compile(r"\bBearer\s+([A-Za-z0-9._-]{16,})\b", re.IGNORECASE)
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
    r"\b(?:[A-Z0-9_]*(?:OPENAI_KEY|AWS_SECRET|DATABASE_TOKEN|GITHUB_TOKEN|API_KEY|SECRET|TOKEN|ACCESS_KEY)[A-Z0-9_]*)\s*=\s*(?:['\"])?([^\s'\"\n]+)(?:['\"])?",
    re.IGNORECASE,
)
PASSWORD_LABELED_RE = re.compile(
    r"\b(?:password|passwd|passphrase|pwd)\b\s*(?:=|:|is)\s*(?:['\"])?([^\s'\"\n]{8,})(?:['\"])?",
    re.IGNORECASE,
)
API_KEY_STANDALONE_RE = re.compile(r"(?<![A-Za-z0-9._-])([A-Za-z0-9._-]{12,128})(?![A-Za-z0-9._-])")
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
    r"\bINV-[A-Z0-9]+(?:-[A-Z0-9]+)*\b|\binvoice(?:\s+number)?\s*#\s*[A-Z0-9-]+\b",
    re.IGNORECASE,
)
WINDOWS_FILE_PATH_RE = re.compile(r"\b[A-Z]:\\(?:[^\\\s]+\\)*[^\\\s]+\b")
STDNUM_IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}(?:[ -]?[A-Z0-9]{2,5}){3,8}\b")
STDNUM_US_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
STDNUM_US_ITIN_RE = re.compile(r"\b9\d{2}-\d{2}-\d{4}\b")
PRIVATE_KEY_BLOCK_RE = re.compile(
    r"-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA )?PRIVATE KEY-----",
    re.MULTILINE,
)
PRIVATE_KEY_HEADER_RE = re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----")
LABELED_VALUE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z ]{0,32})\s*(?::|->|→)\s*(.+?)\s*$")
PERSON_BOUNDARY_PATTERN = r"(?=\s|$|[),.;:\"'”’])"
DETECT_SECRETS_CONFIG: Dict[str, List[Dict[str, Any]]] = {
    "plugins_used": [
        {"name": "AWSKeyDetector"},
        {"name": "ArtifactoryDetector"},
        {"name": "AzureStorageKeyDetector"},
        {"name": "BasicAuthDetector"},
        {"name": "CloudantDetector"},
        {"name": "DiscordBotTokenDetector"},
        {"name": "GitHubTokenDetector"},
        {"name": "GitLabTokenDetector"},
        {"name": "IbmCloudIamDetector"},
        {"name": "IbmCosHmacDetector"},
        {"name": "JwtTokenDetector"},
        {"name": "MailchimpDetector"},
        {"name": "NpmDetector"},
        {"name": "OpenAIDetector"},
        {"name": "PrivateKeyDetector"},
        {"name": "PypiTokenDetector"},
        {"name": "SendGridDetector"},
        {"name": "SlackDetector"},
        {"name": "SoftlayerDetector"},
        {"name": "SquareOAuthDetector"},
        {"name": "StripeDetector"},
        {"name": "TelegramBotTokenDetector"},
        {"name": "TwilioKeyDetector"},
    ]
}

_REGEX_DETECTORS = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "PHONE": re.compile(r"(?:\+?\d[\d\s().-]{7,}\d|\(\d{2,5}\)[\d\s.-]{5,}\d)"),
    "URL": re.compile(r"\bhttps?://[^\s\"'<>]+\b", re.IGNORECASE),
    "URL_HOSTNAME": HOSTNAME_RE,
    "CONNECTION_STRING": CONNECTION_STRING_RE,
    "API_KEY_OPENAI": API_KEY_OPENAI_RE,
    "API_KEY_AWS": API_KEY_AWS_RE,
    "API_KEY_GITHUB": API_KEY_GITHUB_RE,
    "API_KEY_GITLAB": API_KEY_GITLAB_RE,
    "API_KEY_GOOGLE": API_KEY_GOOGLE_RE,
    "API_KEY_SSH_PUBLIC": API_KEY_SSH_PUBLIC_RE,
    "API_KEY_JWT": API_KEY_JWT_RE,
    "API_KEY_BEARER": API_KEY_BEARER_RE,
    "CRYPTO_WALLET": CRYPTO_WALLET_RE,
    "ANALYTICS_ID": ANALYTICS_ID_RE,
    "API_KEY_LABELED": API_KEY_LABELED_RE,
    "PASSWORD_LABELED": PASSWORD_LABELED_RE,
    "API_KEY_STANDALONE": API_KEY_STANDALONE_RE,
    "PRIVATE_KEY_BLOCK": PRIVATE_KEY_BLOCK_RE,
    "PRIVATE_KEY_HEADER": PRIVATE_KEY_HEADER_RE,
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "GOVERNMENT_ID_SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "GOVERNMENT_ID_UK_NI": re.compile(r"\b[A-Z]{2}\d{6}[A-Z]\b"),
    "GOVERNMENT_ID_NHS": re.compile(r"\b(?:NHS(?:\s*(?:no|number|#))?\s*[:#-]?\s*)(\d{3}\s?\d{3}\s?\d{4})\b", re.IGNORECASE),
    "GOVERNMENT_ID_PAYE": re.compile(r"\b(?:Employer\s+PAYE\s+reference|PAYE\s+reference)\s*[:#-]?\s*([0-9]{3}/[A-Z0-9]{1,10})\b", re.IGNORECASE),
    "GOVERNMENT_ID_TAX_CODE": re.compile(r"\bTax\s+code\s*[:#-]?\s*([A-Z0-9]{3,10})\b", re.IGNORECASE),
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
    "ADDRESS_UK_POSTCODE_TRAIL": re.compile(
        rf"\b\d{{1,5}}[A-Za-z]?{INLINE_WS_PATTERN}(?:{NAME_TOKEN_PATTERN}{INLINE_WS_PATTERN}){{0,4}}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd|View)\b"
        rf"(?:{INLINE_WS_PATTERN}(?:[A-Z][A-Za-z'’-]+|[A-Z])){{0,5}}{INLINE_WS_PATTERN}[A-Z]{{1,2}}\d[A-Z\d]?\s?\d[A-Z]{{2}}\b",
        re.IGNORECASE,
    ),
    "ADDRESS_NUMBERED": re.compile(
        rf"\b\d{{1,5}}[A-Za-z]?{INLINE_WS_PATTERN}(?:{NAME_TOKEN_PATTERN}{INLINE_WS_PATTERN}){{0,4}}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd|View)\b"
    ),
    "ADDRESS_SHORT_NUMBERED": re.compile(
        rf"\b\d{{1,5}}[A-Za-z]?{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}},\s*(?:{CITY_TOKEN_PATTERN}|[A-Z]{{2,}})(?:{INLINE_WS_PATTERN}(?:{CITY_TOKEN_PATTERN}|[A-Z]{{2,}})){{0,2}}\b"
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
        rf"\b(?!19\d{{2}}\b)(?!20\d{{2}}\b)\d{{4,5}}{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{CITY_TOKEN_PATTERN}){{0,2}}\b"
    ),
    "ADDRESS_VIA": re.compile(rf"\bVia{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}){{0,2}}\b"),
    "COORDINATE": re.compile(r"\b\d{1,3}\.\d+\s*°?\s*[NS],\s*\d{1,3}\.\d+\s*°?\s*[EW]\b", re.IGNORECASE),
    "FILE_PATH": re.compile(r"(?<!https:)(?<!http:)/(?:[^\s/]+/)+[^\s/]*"),
    "FILE_PATH_WINDOWS": WINDOWS_FILE_PATH_RE,
    "PERSON_TITLED": re.compile(
        rf"\b{PERSON_TITLE_PATTERN}\.?{INLINE_WS_PATTERN}(?:{PERSON_FULL_NAME_PATTERN}|{PERSON_DOUBLE_INITIAL_LAST_PATTERN}|{PERSON_INITIAL_THREE_PATTERN}|{PERSON_INITIAL_LAST_PATTERN}|{PERSON_FIRST_INITIAL_PATTERN}){PERSON_BOUNDARY_PATTERN}"
    ),
    "PERSON_GREETING": re.compile(
        rf"\b(?:Hi|Hello|Dear){INLINE_WS_PATTERN}({PERSON_FULL_NAME_PATTERN}|{PERSON_DOUBLE_INITIAL_LAST_PATTERN}|{PERSON_INITIAL_THREE_PATTERN}|{PERSON_INITIAL_LAST_PATTERN}|{PERSON_FIRST_INITIAL_PATTERN}){PERSON_BOUNDARY_PATTERN}",
        re.IGNORECASE,
    ),
    "PERSON_FULL": re.compile(rf"\b(?:{PERSON_FULL_NAME_PATTERN}|{PERSON_DOUBLE_INITIAL_LAST_PATTERN}|{PERSON_INITIAL_THREE_PATTERN}){PERSON_BOUNDARY_PATTERN}"),
    "PERSON_INITIAL_THREE": re.compile(rf"\b{PERSON_INITIAL_THREE_PATTERN}{PERSON_BOUNDARY_PATTERN}"),
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
    "API_KEY_GITLAB": "API_KEY",
    "API_KEY_GOOGLE": "API_KEY",
    "API_KEY_SSH_PUBLIC": "API_KEY",
    "API_KEY_JWT": "API_KEY",
    "API_KEY_BEARER": "API_KEY",
    "CRYPTO_WALLET": "CRYPTO_WALLET",
    "ANALYTICS_ID": "ANALYTICS_ID",
    "API_KEY_LABELED": "API_KEY",
    "PASSWORD_LABELED": "API_KEY",
    "API_KEY_STANDALONE": "API_KEY",
    "PRIVATE_KEY_BLOCK": "PRIVATE_KEY",
    "PRIVATE_KEY_HEADER": "PRIVATE_KEY",
    "CREDIT_CARD": "CREDIT_CARD",
    "GOVERNMENT_ID_SSN": "GOVERNMENT_ID",
    "GOVERNMENT_ID_UK_NI": "GOVERNMENT_ID",
    "GOVERNMENT_ID_NHS": "GOVERNMENT_ID",
    "GOVERNMENT_ID_PAYE": "GOVERNMENT_ID",
    "GOVERNMENT_ID_TAX_CODE": "GOVERNMENT_ID",
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
    "ADDRESS_UK_POSTCODE_TRAIL": "ADDRESS",
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
    "PERSON_INITIAL_THREE": "PERSON",
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
CORE_PRE_PLUGIN_TYPES: FrozenSet[str] = frozenset({"EMAIL", "URL", "CONNECTION_STRING"})
SECRET_PLUGIN_TYPES: FrozenSet[str] = frozenset(
    {"API_KEY", "CRYPTO_WALLET", "ANALYTICS_ID", "PRIVATE_KEY", "CREDIT_CARD", "GOVERNMENT_ID", "BANK_ACCOUNT"}
)
ID_PLUGIN_TYPES: FrozenSet[str] = frozenset(
    {"COMPANY_REGISTRATION_NUMBER", "INVOICE_NUMBER", "EMPLOYEE_ID", "BOOKING_REFERENCE", "TICKET_REFERENCE", "ORDER_ID", "TRANSACTION_ID"}
)
PHONE_PLUGIN_TYPES: FrozenSet[str] = frozenset({"PHONE"})
ADDRESS_PLUGIN_TYPES: FrozenSet[str] = frozenset({"ADDRESS"})
PERSON_ORG_PLUGIN_TYPES: FrozenSet[str] = frozenset({"PERSON", "ORG"})
SUPPORTED_LANGUAGE_CODE = "en"
SUPPORTED_LANGUAGE_LABEL = "English"
UNKNOWN_LANGUAGE_CODE = "unknown"
NON_ENGLISH_WARNING = "This text appears to be non-English. Entity detection may be less accurate."
STRUCTURED_PERSON_LABELS = {
    "person",
    "owner",
    "candidate",
    "patient",
    "applicant",
    "student",
    "assistant",
    "contact",
    "legal contact",
    "consultant",
    "engineer",
    "manager",
    "director",
    "supervisor",
    "employee",
    "applicant name",
    "name",
    "prepared by",
    "reporter",
    "escalation owner",
}
STRUCTURED_PERSON_LABELS_NORMALIZED = {re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", label.lower())).strip() for label in STRUCTURED_PERSON_LABELS}
STRUCTURED_LABEL_PREFIX_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 _/-]{1,64})\s*:\s*$")
NLP_ENTITY_MAP = {
    "PERSON": "PERSON",
    "ORG": "ORG",
    "ORGANIZATION": "ORG",
    "LOCATION": "ADDRESS",
    "DATE_TIME": "DATE",
    "DATE": "DATE",
    "EMAIL_ADDRESS": "EMAIL",
    "PHONE_NUMBER": "PHONE",
    "IP_ADDRESS": "IP_ADDRESS",
    "CREDIT_CARD": "CREDIT_CARD",
    "IBAN_CODE": "BANK_ACCOUNT",
    "US_SSN": "GOVERNMENT_ID",
    "US_ITIN": "GOVERNMENT_ID",
    "US_PASSPORT": "GOVERNMENT_ID",
    "PASSWORD": "API_KEY",
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
    "yesterday", "today", "tomorrow", "now", "later", "soon", "here", "back", "again", "via",
}


class OptionalNlp:
    def __init__(self) -> None:
        self._analyzer = None
        self.available = False
        self._supported_entities: set[str] = set()
        self._phone_lib = None
        self.phone_available = False
        self._detect_secrets_scan_line = None
        self._detect_secrets_transient_settings = None
        self.detect_secrets_available = False
        self._stdnum_iban = None
        self._stdnum_us_ssn = None
        self._stdnum_us_itin = None
        self.stdnum_available = False
        self._presidio_enabled = os.getenv("ENABLE_PRESIDIO_NLP", "false").strip().lower() in {"1", "true", "yes", "on"}
        if self._presidio_enabled:
            try:
                from presidio_analyzer import AnalyzerEngine

                self._analyzer = AnalyzerEngine()
                try:
                    for recognizer in getattr(self._analyzer.registry, "recognizers", []):
                        for entity in getattr(recognizer, "supported_entities", []) or []:
                            self._supported_entities.add(str(entity))
                except Exception:
                    self._supported_entities = set()
                self.available = True
            except Exception:
                self.available = False
        try:
            import phonenumbers

            self._phone_lib = phonenumbers
            self.phone_available = True
        except Exception:
            self.phone_available = False
        try:
            from detect_secrets.core.scan import scan_line
            from detect_secrets.settings import transient_settings

            self._detect_secrets_scan_line = scan_line
            self._detect_secrets_transient_settings = transient_settings
            self.detect_secrets_available = True
        except Exception:
            self.detect_secrets_available = False
        try:
            from stdnum import iban as stdnum_iban
            from stdnum.us import itin as stdnum_us_itin
            from stdnum.us import ssn as stdnum_us_ssn

            self._stdnum_iban = stdnum_iban
            self._stdnum_us_ssn = stdnum_us_ssn
            self._stdnum_us_itin = stdnum_us_itin
            self.stdnum_available = True
        except Exception:
            self.stdnum_available = False

    @staticmethod
    def _looks_like_plugin_secret(value: str) -> bool:
        candidate = (value or "").strip().lstrip("=:'\"")
        if not candidate or len(candidate) < 16:
            return False
        if any(ch.isspace() for ch in candidate):
            return False
        if candidate.isalpha() or candidate.isdigit():
            return False
        return bool(re.fullmatch(r"[A-Za-z0-9._:/+=-]{16,}", candidate))

    @staticmethod
    def _find_secret_span_in_line(line: str, secret_value: str, start_at: int = 0) -> tuple[int, int]:
        raw = secret_value or ""
        for candidate in (raw, raw.strip(), raw.strip().lstrip("=:'\"")):
            if not candidate:
                continue
            idx = line.find(candidate, start_at)
            if idx != -1:
                return idx, idx + len(candidate)
        return -1, -1

    def _detect_with_detect_secrets(
        self,
        text: str,
        enabled_types: Sequence[str],
        seen_spans: set[tuple[str, int, int]],
    ) -> List[Detection]:
        if not self.detect_secrets_available or not self._detect_secrets_scan_line or not self._detect_secrets_transient_settings:
            return []
        if "API_KEY" not in enabled_types and "PRIVATE_KEY" not in enabled_types:
            return []

        detections: List[Detection] = []
        line_offset = 0
        for raw_line in text.splitlines(keepends=True):
            line = raw_line.rstrip("\r\n")
            if not line:
                line_offset += len(raw_line)
                continue
            try:
                with self._detect_secrets_transient_settings(DETECT_SECRETS_CONFIG):
                    plugin_hits = list(self._detect_secrets_scan_line(line))
            except Exception:
                line_offset += len(raw_line)
                continue
            if not plugin_hits:
                line_offset += len(raw_line)
                continue

            span_cursor: Dict[str, int] = {}
            for hit in plugin_hits:
                secret_kind = str(getattr(hit, "type", "") or "").strip().lower()
                secret_value = str(getattr(hit, "secret_value", "") or "").strip()
                if not secret_value:
                    continue

                mapped = "PRIVATE_KEY" if "private key" in secret_kind else "API_KEY"
                if mapped not in enabled_types:
                    continue

                cursor_key = f"{mapped}:{secret_value}"
                line_start, line_end = self._find_secret_span_in_line(line, secret_value, span_cursor.get(cursor_key, 0))
                if line_start == -1 and "json web token" in secret_kind:
                    jwt_match = API_KEY_JWT_RE.search(line)
                    if jwt_match:
                        line_start, line_end = jwt_match.start(), jwt_match.end()
                if line_start == -1:
                    continue
                span_cursor[cursor_key] = line_end

                start = line_offset + line_start
                end = line_offset + line_end
                if _inside_existing_token(text, start, end):
                    continue
                if _is_protected_heading_line(text, start):
                    continue
                candidate = text[start:end]

                if mapped == "API_KEY":
                    extracted = _extract_api_key_candidate(candidate)
                    if extracted:
                        rel = candidate.find(extracted)
                        if rel >= 0:
                            start += rel
                            end = start + len(extracted)
                            candidate = extracted
                    elif not self._looks_like_plugin_secret(candidate):
                        continue
                else:
                    if "BEGIN" not in candidate and len(candidate.strip()) < 24:
                        continue

                key = (mapped, start, end)
                if key in seen_spans:
                    continue
                seen_spans.add(key)
                detections.append(Detection(entity_type=mapped, start=start, end=end, score=0.992))

            line_offset += len(raw_line)
        return detections

    def _detect_with_stdnum(
        self,
        text: str,
        enabled_types: Sequence[str],
        seen_spans: set[tuple[str, int, int]],
    ) -> List[Detection]:
        if not self.stdnum_available:
            return []

        detections: List[Detection] = []
        if "BANK_ACCOUNT" in enabled_types and self._stdnum_iban:
            for match in STDNUM_IBAN_RE.finditer(text):
                start, end = match.start(), match.end()
                candidate = match.group(0)
                compact = re.sub(r"[\s-]+", "", candidate)
                if len(compact) < 15 or len(compact) > 34:
                    continue
                try:
                    if not self._stdnum_iban.is_valid(compact):
                        continue
                except Exception:
                    continue
                if _inside_existing_token(text, start, end) or _is_protected_heading_line(text, start):
                    continue
                key = ("BANK_ACCOUNT", start, end)
                if key in seen_spans:
                    continue
                seen_spans.add(key)
                detections.append(Detection(entity_type="BANK_ACCOUNT", start=start, end=end, score=0.99))

        if "GOVERNMENT_ID" in enabled_types:
            for pattern, validator in (
                (STDNUM_US_SSN_RE, self._stdnum_us_ssn),
                (STDNUM_US_ITIN_RE, self._stdnum_us_itin),
            ):
                if not validator:
                    continue
                for match in pattern.finditer(text):
                    start, end = match.start(), match.end()
                    candidate = match.group(0)
                    try:
                        if not validator.is_valid(candidate):
                            continue
                    except Exception:
                        continue
                    if _inside_existing_token(text, start, end) or _is_protected_heading_line(text, start):
                        continue
                    key = ("GOVERNMENT_ID", start, end)
                    if key in seen_spans:
                        continue
                    seen_spans.add(key)
                    detections.append(Detection(entity_type="GOVERNMENT_ID", start=start, end=end, score=0.99))

        return detections

    def detect(self, text: str, enabled_types: Sequence[str]) -> List[Detection]:
        detections: List[Detection] = []
        seen_spans: set[tuple[str, int, int]] = set()

        if self.available and self._analyzer:
            entities = []
            if "PERSON" in enabled_types:
                entities.append("PERSON")
            if "ORG" in enabled_types:
                entities.append("ORGANIZATION")
            if "ADDRESS" in enabled_types:
                entities.extend(["LOCATION", "ADDRESS"])
            if "DATE" in enabled_types:
                entities.extend(["DATE_TIME", "DATE"])
            if "EMAIL" in enabled_types:
                entities.append("EMAIL_ADDRESS")
            if "PHONE" in enabled_types:
                entities.append("PHONE_NUMBER")
            if "IP_ADDRESS" in enabled_types:
                entities.append("IP_ADDRESS")
            if "URL" in enabled_types:
                entities.append("URL")
            if "CREDIT_CARD" in enabled_types:
                entities.append("CREDIT_CARD")
            if "BANK_ACCOUNT" in enabled_types:
                entities.append("IBAN_CODE")
            if "GOVERNMENT_ID" in enabled_types:
                entities.extend(["US_SSN", "US_ITIN", "US_PASSPORT"])
            if "API_KEY" in enabled_types:
                entities.append("PASSWORD")

            if entities:
                unique_entities = list(set(entities))
                if self._supported_entities:
                    unique_entities = [entity for entity in unique_entities if entity in self._supported_entities]
                if unique_entities:
                    results = self._analyzer.analyze(text=text, entities=unique_entities, language="en")
                    for item in results:
                        mapped = NLP_ENTITY_MAP.get(item.entity_type, item.entity_type)
                        if mapped not in enabled_types:
                            continue
                        span = text[item.start : item.end]
                        if mapped == "ADDRESS" and re.fullmatch(r"[A-Z]{3}", span or ""):
                            continue
                        if mapped == "PHONE":
                            if not _is_likely_phone_value(span):
                                continue
                            if _has_booking_or_order_context(text, item.start) or _has_government_id_context(text, item.start):
                                continue
                        key = (mapped, item.start, item.end)
                        if key in seen_spans:
                            continue
                        seen_spans.add(key)
                        detections.append(
                            Detection(
                                entity_type=mapped,
                                start=item.start,
                                end=item.end,
                                score=float(item.score or 0.6),
                            )
                        )

        if self.phone_available and self._phone_lib and "PHONE" in enabled_types:
            for region in ("GB", "US", "CA", "AU", "SG", "FR", "DE", "ES", "IT", "NL"):
                try:
                    matcher = self._phone_lib.PhoneNumberMatcher(text, region)
                except Exception:
                    continue
                for item in matcher:
                    start, end = item.start, item.end
                    span = text[start:end]
                    if not _is_likely_phone_value(span):
                        continue
                    if _has_booking_or_order_context(text, start) or _has_government_id_context(text, start):
                        continue
                    key = ("PHONE", start, end)
                    if key in seen_spans:
                        continue
                    seen_spans.add(key)
                    detections.append(
                        Detection(
                            entity_type="PHONE",
                            start=start,
                            end=end,
                            score=0.985,
                        )
                    )
        detections.extend(self._detect_with_detect_secrets(text, enabled_types, seen_spans))
        detections.extend(self._detect_with_stdnum(text, enabled_types, seen_spans))
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


def _is_likely_code_identifier(value: str) -> bool:
    candidate = (value or "").strip().strip("()[]{}")
    if not candidate or " " in candidate:
        return False
    if re.fullmatch(r"X[A-Za-z0-9.]{2,8}", candidate):
        return True
    if re.fullmatch(r"[A-Za-z]{1,3}\d[A-Za-z0-9.]{1,8}", candidate):
        return True
    if "." in candidate and re.fullmatch(r"[A-Za-z0-9.]{3,10}", candidate):
        return True
    if re.fullmatch(r"[A-Z0-9]{2,8}\.\.?", candidate):
        return True
    return False


def _is_clinical_or_tabular_line(line: str) -> bool:
    raw = (line or "").strip()
    if not raw:
        return False
    lowered = raw.lower()
    digit_tokens = re.findall(r"\b\d[\d,./:-]*\b", raw)
    has_measurement = bool(CLINICAL_MEASUREMENT_RE.search(raw))
    has_code = bool(re.search(r"\([A-Za-z0-9.]{3,10}\)", raw))
    keyword_hits = sum(1 for word in CLINICAL_CONTEXT_WORDS if word in lowered)
    if has_measurement and keyword_hits >= 1:
        return True
    if has_code and keyword_hits >= 1:
        return True
    if len(digit_tokens) >= 3 and keyword_hits >= 2:
        return True
    return False


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


def _has_government_id_context(text: str, start: int) -> bool:
    line_start = text.rfind("\n", 0, start) + 1
    line_prefix = text[line_start:start]
    if re.search(
        rf"\b(?:nhs(?:{INLINE_WS_PATTERN}(?:no|number|#))?|paye(?:{INLINE_WS_PATTERN}reference)?|tax{INLINE_WS_PATTERN}code|ssn|national{INLINE_WS_PATTERN}insurance|ni)\b",
        line_prefix,
        re.IGNORECASE,
    ):
        return True
    return bool(
        re.search(
            rf"\b(?:nhs(?:{INLINE_WS_PATTERN}(?:no|number|#))?|paye(?:{INLINE_WS_PATTERN}reference)?|tax{INLINE_WS_PATTERN}code|ssn|national{INLINE_WS_PATTERN}insurance|ni){INLINE_WS_PATTERN}$",
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


def _is_non_person_structured_value_context(text: str, start: int) -> bool:
    line_start = text.rfind("\n", 0, start) + 1
    prefix = text[line_start:start]
    match = STRUCTURED_LABEL_PREFIX_RE.match(prefix)
    if not match:
        return False
    label = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", match.group(1).lower())).strip()
    return bool(label and label not in STRUCTURED_PERSON_LABELS_NORMALIZED)


def _is_person_structured_value_context(text: str, start: int) -> bool:
    line_start = text.rfind("\n", 0, start) + 1
    prefix = text[line_start:start]
    match = STRUCTURED_LABEL_PREFIX_RE.match(prefix)
    if not match:
        return False
    label = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", match.group(1).lower())).strip()
    return bool(label and label in STRUCTURED_PERSON_LABELS_NORMALIZED)


def _is_tabular_context_near_span(text: str, start: int, end: int) -> bool:
    left = max(0, start - 48)
    right = min(len(text), end + 64)
    window = text[left:right]
    lowered = window.lower()
    digit_tokens = re.findall(r"\b\d[\d,./-]*\b", window)
    has_currency = bool(re.search(r"[£$€]", window))
    has_percent = "%" in window
    has_hint = any(word in lowered for word in TABULAR_CONTEXT_HINT_WORDS)
    if has_currency and len(digit_tokens) >= 1:
        return True
    if has_percent and len(digit_tokens) >= 2:
        return True
    if has_hint and len(digit_tokens) >= 2:
        return True
    return False


def _is_likely_phone_value(text: str) -> bool:
    if IPV4_RE.fullmatch((text or "").strip()):
        return False
    digits = re.sub(r"\D", "", text or "")
    return 8 <= len(digits) <= 15 and (len(digits) >= 10 or "+" in (text or "") or bool(re.search(r"[\s.-]", text or "")))


def _is_api_key_value(text: str) -> bool:
    candidate = (text or "").strip()
    if not candidate:
        return False
    direct_patterns = (
        API_KEY_OPENAI_RE,
        API_KEY_AWS_RE,
        API_KEY_GITHUB_RE,
        API_KEY_GITLAB_RE,
        API_KEY_GOOGLE_RE,
        API_KEY_SSH_PUBLIC_RE,
        API_KEY_JWT_RE,
    )
    if any(regex.fullmatch(candidate) for regex in direct_patterns):
        return True
    if API_KEY_BEARER_RE.fullmatch(candidate):
        return True
    return bool(PASSWORD_LABELED_RE.fullmatch(candidate))


def _is_likely_standalone_secret(text: str, start: int, end: int, value: str) -> bool:
    candidate = (value or "").strip().strip("`'\"()[]{}<>")
    if not candidate:
        return False
    if len(candidate) < 12 or len(candidate) > 128:
        return False
    if _looks_like_existing_placeholder(candidate):
        return False
    if not re.search(r"[A-Za-z]", candidate) or not re.search(r"\d", candidate):
        return False
    if IPV4_RE.fullmatch(candidate) or IPV6_RE.fullmatch(candidate):
        return False
    if candidate.lower().startswith(("http://", "https://")):
        return False
    if _inside_connection_string(text, start, end):
        return False
    if _is_likely_hostname_value(candidate):
        return False
    if _has_booking_or_order_context(text, start) or _has_government_id_context(text, start):
        return False

    previous_word = _previous_word(text, start)
    if previous_word in SECRET_CONTEXT_BLOCK_WORDS:
        return False

    # Common booking/order style identifiers should remain with ID classifiers.
    if re.fullmatch(r"[A-Z0-9-]{8,24}", candidate):
        return False

    letters = sum(char.isalpha() for char in candidate)
    digits = sum(char.isdigit() for char in candidate)
    symbols = sum(not char.isalnum() for char in candidate)
    if symbols == 0 and (letters < 8 or digits < 2):
        return False
    if candidate.islower() and symbols == 0 and digits < 3 and len(candidate) < 16:
        return False
    return True


def _is_likely_hostname_value(text: str) -> bool:
    candidate = (text or "").strip().strip(".,;:")
    if not candidate or any(char in candidate for char in "/@\\"):
        return False
    if API_KEY_JWT_RE.fullmatch(candidate):
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
    password_match = PASSWORD_LABELED_RE.search(candidate)
    if password_match:
        return password_match.group(1)
    for regex in (
        API_KEY_OPENAI_RE,
        API_KEY_AWS_RE,
        API_KEY_GITHUB_RE,
        API_KEY_GITLAB_RE,
        API_KEY_GOOGLE_RE,
        API_KEY_SSH_PUBLIC_RE,
        API_KEY_JWT_RE,
    ):
        match = regex.search(candidate)
        if match:
            return match.group(0)
    bearer_match = API_KEY_BEARER_RE.search(candidate)
    if bearer_match:
        return bearer_match.group(1)
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
    if start > 0 and text[start - 1] in {".", "/", ":"} and re.match(r"^\d{1,2}\b", value or ""):
        return True
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+|\d+", (value or "").lower())
    if not words:
        return False
    first_number = re.match(r"^\s*(\d{1,5})\b", value or "")
    if first_number:
        number_text = first_number.group(1)
        number_value = int(number_text)
        if len(number_text) == 4 and 1900 <= number_value <= 2100:
            return True
        if (
            number_value < 20
            and not re.search(rf"\b(?:{ADDRESS_STREET_WORDS})\b", value or "", re.IGNORECASE)
            and not re.search(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", value or "")
            and "," not in (value or "")
        ):
            return True
    if re.match(
        rf"^\s*Dr\.?{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}(?:{INLINE_WS_PATTERN}{NAME_TOKEN_PATTERN}){{0,2}}(?:\s|$)",
        value or "",
    ) and not re.search(r"\d", value or ""):
        return True
    if len(words[0]) <= 2 and start > 0 and text[start - 1] == ":":
        return True
    if len(words) in {2, 3} and words[0].isdigit() and words[1] in MONTH_WORDS:
        return len(words) == 2 or words[2].isdigit()
    if words[0].isdigit() and all(word in TIME_CONTEXT_WORDS for word in words[1:]):
        return True
    if any(word in TABULAR_CONTEXT_HINT_WORDS for word in words):
        if not re.search(rf"\b(?:{ADDRESS_STREET_WORDS})\b", value or "", re.IGNORECASE) and "," not in (value or ""):
            return True
    street_tokens = re.findall(rf"\b(?:{ADDRESS_STREET_WORDS})\b", value or "", re.IGNORECASE)
    if re.search(r"\b(?:or|and)\b", (value or "").lower()) and len(street_tokens) >= 2:
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
    if len(parts) == 3 and INITIAL_OPTIONAL_DOT_RE.fullmatch(parts[0]) and all(NAME_TOKEN_RE.fullmatch(part) for part in parts[1:]):
        return {"kind": "full", "first": parts[0][0].lower(), "last": parts[-1].lower()}
    return None


def _is_valid_person_span(text: str, start: int, end: int, phrase: str) -> bool:
    cleaned = _strip_person_title(phrase)
    if not cleaned:
        return False
    if _is_likely_code_identifier(cleaned):
        return False

    parts = cleaned.split()
    has_explicit_title = bool(re.match(rf"^(?:{PERSON_TITLE_PATTERN})\.?\s+", (phrase or "").strip(), re.IGNORECASE))
    prev_word = _previous_word(text, start)
    is_greeting_context = prev_word in {"dear", "hi", "hello"}
    next_word = _next_word_after(text, end)
    line = _get_line_at(text, start)
    is_person_structured_context = _is_person_structured_value_context(text, start)
    if _is_likely_heading_line(line) and not has_explicit_title:
        return False
    if _is_non_person_structured_value_context(text, start):
        return False
    if _is_tabular_context_near_span(text, start, end) and not is_person_structured_context and not has_explicit_title:
        return False
    if _is_clinical_or_tabular_line(line) and not is_person_structured_context and not has_explicit_title and not is_greeting_context:
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
    if any(len(part.rstrip(".")) == 1 and not part.endswith(".") for part in parts):
        if not is_greeting_context and not is_person_structured_context:
            return False
    normalized_parts = [part.lower().rstrip(".") for part in parts]
    if any(part in PERSON_CONNECTOR_WORDS for part in normalized_parts):
        return False
    if any(part in CLINICAL_CONTEXT_WORDS for part in normalized_parts):
        return False
    if any(part in NON_PERSON_NAME_WORDS for part in normalized_parts):
        return False
    if normalized_parts[-1] in {"house", "tower", "building", "centre", "center"} and re.match(r"\s*,\s*\d{1,5}\b", text[end:]):
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
        for key in (
            "GOVERNMENT_ID_SSN",
            "GOVERNMENT_ID_UK_NI",
            "GOVERNMENT_ID_NHS",
            "GOVERNMENT_ID_PAYE",
            "GOVERNMENT_ID_TAX_CODE",
        ):
            match = _REGEX_DETECTORS[key].search(trimmed)
            if match:
                return match.group(1) if match.lastindex else match.group(0)
        return None
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
        if labeled:
            handle = labeled.group(1) or labeled.group(2)
            if handle and handle.lower().lstrip("@") not in USERNAME_CONTEXT_BLOCK_WORDS:
                return handle
        plain = re.search(r"^@?[a-z0-9][a-z0-9_.-]{2,}$", trimmed.strip(), re.IGNORECASE)
        if plain:
            candidate = plain.group(0)
            if not _is_api_key_value(candidate) and candidate.lower().lstrip("@") not in USERNAME_CONTEXT_BLOCK_WORDS:
                return candidate
        return None
    if entity_type == "INVOICE_NUMBER":
        match = _REGEX_DETECTORS["INVOICE_NUMBER"].search(trimmed)
        return match.group(0) if match else None
    return trim_boundary(trimmed)


def structured_detect(text: str, enabled_types: Sequence[str]) -> List[Detection]:
    label_map = {
        "person": "PERSON",
        "applicant": "PERSON",
        "patient": "PERSON",
        "student": "PERSON",
        "assistant": "PERSON",
        "contact": "PERSON",
        "engineer": "PERSON",
        "primary contact": "EMAIL",
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
        "supervisor": "PERSON",
        "owner": "PERSON",
        "candidate": "PERSON",
        "legal contact": "PERSON",
        "consultant": "PERSON",
        "email": "EMAIL",
        "university email": "EMAIL",
        "phone": "PHONE",
        "address": "ADDRESS",
        "correspondence address": "ADDRESS",
        "reference address": "ADDRESS",
        "organisation": "ORG",
        "organization": "ORG",
        "sponsor organisation": "ORG",
        "sponsor organization": "ORG",
        "employer": "ORG",
        "current employer": "ORG",
        "placement company": "ORG",
        "date": "DATE",
        "url": "URL",
        "website": "URL",
        "web address": "URL",
        "api key": "API_KEY",
        "apikey": "API_KEY",
        "password": "API_KEY",
        "passwd": "API_KEY",
        "passphrase": "API_KEY",
        "pwd": "API_KEY",
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
        "nhs no": "GOVERNMENT_ID",
        "nhs number": "GOVERNMENT_ID",
        "nhs": "GOVERNMENT_ID",
        "paye reference": "GOVERNMENT_ID",
        "employer paye reference": "GOVERNMENT_ID",
        "tax code": "GOVERNMENT_ID",
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
        "slack user": "USERNAME",
        "slack username": "USERNAME",
        "username": "USERNAME",
        "user": "USERNAME",
        "github": "USERNAME",
        "github user": "USERNAME",
        "github username": "USERNAME",
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
            if key in {"API_KEY_LABELED", "PASSWORD_LABELED", "API_KEY_BEARER", "API_KEY_STANDALONE"}:
                start = match.start(1)
                end = match.end(1)
            if key == "PERSON_GREETING":
                start = match.start(1)
                end = match.end(1)
            if key in {
                "BOOKING_REFERENCE",
                "TICKET_REFERENCE",
                "ORDER_ID",
                "EMPLOYEE_ID",
                "TRANSACTION_ID",
                "GOVERNMENT_ID_NHS",
                "GOVERNMENT_ID_PAYE",
                "GOVERNMENT_ID_TAX_CODE",
            }:
                start = match.start(1)
                end = match.end(1)
            if key == "COMPANY_REGISTRATION_NUMBER":
                start = match.start(1)
                end = match.end(1)
            if mapped == "PHONE" and start > 0 and text[start - 1] == "+":
                start -= 1
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
            if mapped == "PHONE" and _has_government_id_context(text, start):
                continue
            if mapped == "EMAIL" and _inside_connection_string(text, start, end):
                continue
            if mapped == "URL" and not _extract_url_candidate(value):
                continue
            if mapped == "URL" and _is_api_key_value(value):
                continue
            if key == "API_KEY_STANDALONE" and not _is_likely_standalone_secret(text, start, end, value):
                continue
            if key == "CONNECTION_STRING" and not CONNECTION_STRING_RE.fullmatch(value):
                continue
            if mapped == "ADDRESS" and _is_address_false_positive(text, start, value):
                continue
            if mapped == "ADDRESS" and _is_protected_region_phrase(value):
                continue
            if mapped == "ORG" and (_is_ignored_entity_phrase(value) or _has_ignored_entity_context(text, start)):
                continue
            if mapped == "ORG":
                words = _normalized_words(value)
                if words and words[0] in TABULAR_CONTEXT_HINT_WORDS:
                    continue
                if _is_likely_code_identifier(value):
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
            handle = match.group(1) or match.group(2)
            if not handle:
                continue
            group_index = 1 if match.group(1) else 2
            handle_start = match.start(group_index)
            handle_end = match.end(group_index)
            if _is_protected_heading_line(text, handle_start):
                continue
            if handle.lower().lstrip("@") in USERNAME_CONTEXT_BLOCK_WORDS:
                continue
            start = handle_start
            end = handle_end
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
        if _is_likely_code_identifier(candidate):
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
        if _is_likely_code_identifier(candidate):
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
        if _is_likely_code_identifier(candidate):
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
        if _is_likely_code_identifier(candidate):
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
        if _is_likely_code_identifier(candidate):
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

    quoted_name = re.compile(rf"[\"“]((?:{PERSON_FULL_NAME_PATTERN}|{PERSON_DOUBLE_INITIAL_LAST_PATTERN}|{PERSON_INITIAL_THREE_PATTERN}|{PERSON_INITIAL_LAST_PATTERN}|{PERSON_FIRST_INITIAL_PATTERN}))(?=\s|$|[\"”])")
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

    pattern = re.compile(rf"(?:[\"“]|note{INLINE_WS_PATTERN}[\"“])((?:{PERSON_FULL_NAME_PATTERN}|{PERSON_DOUBLE_INITIAL_LAST_PATTERN}|{PERSON_INITIAL_THREE_PATTERN}|{PERSON_INITIAL_LAST_PATTERN}|{PERSON_FIRST_INITIAL_PATTERN}))\s*$")
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


def _collect_stage_hits(context: DetectorContext, target_types: FrozenSet[str]) -> List[Detection]:
    active_targets = {entity for entity in context.enabled_types if entity in target_types}
    if "URL" in context.enabled_types and ("URL" in target_types or "CONNECTION_STRING" in target_types):
        active_targets.add("CONNECTION_STRING")
    if not active_targets:
        return []
    return [
        *(det for det in context.structured_hits if det.entity_type in active_targets),
        *(det for det in context.regex_hits if det.entity_type in active_targets),
        *(det for det in context.nlp_hits if det.entity_type in active_targets),
    ]


def _overlaps_any(det: Detection, existing: Sequence[Detection]) -> bool:
    return any(not (det.end <= item.start or det.start >= item.end) for item in existing)


def context_guard_detector(context: DetectorContext, locked: Sequence[Detection]) -> List[Detection]:
    # Context guarding is applied inline across regex/heuristics (`_is_protected_heading_line`,
    # table suppression, protected regions). This plugin intentionally contributes no spans.
    return []


def secret_detector(context: DetectorContext, locked: Sequence[Detection]) -> List[Detection]:
    return _collect_stage_hits(context, SECRET_PLUGIN_TYPES)


def id_detector(context: DetectorContext, locked: Sequence[Detection]) -> List[Detection]:
    return _collect_stage_hits(context, ID_PLUGIN_TYPES)


def phone_detector(context: DetectorContext, locked: Sequence[Detection]) -> List[Detection]:
    return _collect_stage_hits(context, PHONE_PLUGIN_TYPES)


def address_detector(context: DetectorContext, locked: Sequence[Detection]) -> List[Detection]:
    return _collect_stage_hits(context, ADDRESS_PLUGIN_TYPES)


def person_org_detector(context: DetectorContext, locked: Sequence[Detection]) -> List[Detection]:
    base_hits = _collect_stage_hits(context, PERSON_ORG_PLUGIN_TYPES)
    org_hits = org_heuristic_detect(context.text, context.enabled_types, [*locked, *base_hits])
    person_hits = person_conversational_detect(context.text, context.enabled_types, [*locked, *base_hits, *org_hits])
    tail_hits = trailing_person_tail_detect(context.text, context.enabled_types, [*locked, *base_hits, *org_hits, *person_hits])
    return [*base_hits, *org_hits, *person_hits, *tail_hits]


DETECTOR_PLUGINS: Sequence[DetectorPlugin] = (
    DetectorPlugin(name="ContextGuardDetector", detect=context_guard_detector),
    DetectorPlugin(name="SecretDetector", detect=secret_detector),
    DetectorPlugin(name="IdDetector", detect=id_detector),
    DetectorPlugin(name="PhoneDetector", detect=phone_detector),
    DetectorPlugin(name="AddressDetector", detect=address_detector),
    DetectorPlugin(name="PersonOrgDetector", detect=person_org_detector),
)


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
    context = DetectorContext(
        text=text,
        enabled_types=clean_types,
        structured_hits=structured_hits,
        regex_hits=regex_hits,
        nlp_hits=nlp_hits,
    )

    resolved: List[Detection] = []

    def add_stage(detections: Sequence[Detection]) -> None:
        stage = _resolve_overlaps(detections)
        for det in stage:
            if not _overlaps_any(det, resolved):
                resolved.append(det)

    # Priority order:
    # Email -> URL/Connection -> SecretDetector -> IdDetector -> IP -> PhoneDetector -> AddressDetector
    # -> Date -> PersonOrgDetector -> late location cues -> Username -> Coordinate -> File Path.
    add_stage(_collect_stage_hits(context, CORE_PRE_PLUGIN_TYPES))
    plugin_by_name = {plugin.name: plugin for plugin in DETECTOR_PLUGINS}
    for name in ("ContextGuardDetector", "SecretDetector", "IdDetector"):
        add_stage(plugin_by_name[name].detect(context, resolved))
    add_stage(_collect_stage_hits(context, frozenset({"IP_ADDRESS"})))
    for name in ("PhoneDetector", "AddressDetector"):
        add_stage(plugin_by_name[name].detect(context, resolved))
    add_stage(_collect_stage_hits(context, frozenset({"DATE"})))
    add_stage(plugin_by_name["PersonOrgDetector"].detect(context, resolved))
    add_stage(late_location_cue_detect(text, clean_types, resolved))
    add_stage(_collect_stage_hits(context, frozenset({"USERNAME"})))
    add_stage(_collect_stage_hits(context, frozenset({"COORDINATE"})))
    add_stage(_collect_stage_hits(context, frozenset({"FILE_PATH"})))

    merged = _merge_address_blocks(text, resolved)
    merged = _resolve_overlaps(merged)
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
