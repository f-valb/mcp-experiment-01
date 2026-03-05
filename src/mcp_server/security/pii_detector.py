import re
from dataclasses import dataclass


@dataclass
class PIIPattern:
    name: str
    pattern: re.Pattern
    description: str


PII_PATTERNS: list[PIIPattern] = [
    # --- Personal Identifiers ---
    PIIPattern(
        name="email_address",
        pattern=re.compile(
            r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
        ),
        description="Email addresses",
    ),
    PIIPattern(
        name="us_phone_number",
        pattern=re.compile(
            r"\b(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        ),
        description="US phone numbers",
    ),
    PIIPattern(
        name="ssn",
        pattern=re.compile(
            r"\b(?!000|666|9\d{2})[0-8]\d{2}[-\s]\d{2}[-\s]\d{4}\b"
        ),
        description="Social Security Numbers",
    ),
    PIIPattern(
        name="credit_card",
        pattern=re.compile(
            r"\b(?:4[0-9]{12}(?:[0-9]{3})?"
            r"|5[1-5][0-9]{14}"
            r"|3[47][0-9]{13}"
            r"|3(?:0[0-5]|[68][0-9])[0-9]{11}"
            r"|6(?:011|5[0-9]{2})[0-9]{12}"
            r"|(?:2131|1800|35\d{3})\d{11})\b"
        ),
        description="Credit card numbers",
    ),
    # --- Network Identifiers ---
    PIIPattern(
        name="ipv4_address",
        pattern=re.compile(
            r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
            r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
        ),
        description="IPv4 addresses",
    ),
    # --- Secrets and Credentials ---
    PIIPattern(
        name="api_key_generic",
        pattern=re.compile(
            r"(?i)(?:api[_-]?key|apikey|api[_-]?secret)"
            r"\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}['\"]?"
        ),
        description="API keys",
    ),
    PIIPattern(
        name="aws_access_key",
        pattern=re.compile(r"\b(?:AKIA|ABIA|ACCA)[A-Z0-9]{16}\b"),
        description="AWS access key IDs",
    ),
    PIIPattern(
        name="aws_secret_key",
        pattern=re.compile(
            r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*['\"]?"
            r"[A-Za-z0-9/+=]{40}['\"]?"
        ),
        description="AWS secret access keys",
    ),
    PIIPattern(
        name="password_in_text",
        pattern=re.compile(
            r"(?i)(?:password|passwd|pwd)\s*[:=]\s*['\"]?\S{6,}['\"]?"
        ),
        description="Passwords",
    ),
    PIIPattern(
        name="bearer_token",
        pattern=re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}"),
        description="Bearer tokens",
    ),
    PIIPattern(
        name="private_key_header",
        pattern=re.compile(r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----"),
        description="Private key content",
    ),
    PIIPattern(
        name="github_token",
        pattern=re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}\b"),
        description="GitHub tokens",
    ),
    PIIPattern(
        name="slack_token",
        pattern=re.compile(r"\bxox[boaprs]-[A-Za-z0-9\-]{10,}\b"),
        description="Slack tokens",
    ),
    PIIPattern(
        name="generic_secret",
        pattern=re.compile(
            r"(?i)(?:secret|token|credential|auth[_-]?key)"
            r"\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{20,}['\"]?"
        ),
        description="Generic secrets/tokens",
    ),
]

# IPs to ignore (localhost, broadcast, common non-PII)
_TRIVIAL_IPS = frozenset({
    "0.0.0.0", "127.0.0.1", "255.255.255.255",
    "192.168.0.1", "192.168.1.1", "10.0.0.1",
})


def _luhn_check(number_str: str) -> bool:
    """Validate a number string using the Luhn algorithm."""
    digits = [int(d) for d in number_str if d.isdigit()]
    if len(digits) < 13:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def _is_non_trivial_ip(ip: str) -> bool:
    """Check if an IP address is non-trivial (not localhost/broadcast/common)."""
    return ip not in _TRIVIAL_IPS


def scan_for_pii(text: str) -> dict[str, int]:
    """Scan text for PII and sensitive data patterns.

    Returns a dict mapping category descriptions to match counts.
    Empty dict means no PII detected.
    """
    findings: dict[str, int] = {}

    for pii_pattern in PII_PATTERNS:
        matches = pii_pattern.pattern.findall(text)
        if not matches:
            continue

        # Additional validation for specific types
        if pii_pattern.name == "credit_card":
            matches = [m for m in matches if _luhn_check(m)]
        elif pii_pattern.name == "ipv4_address":
            matches = [m for m in matches if _is_non_trivial_ip(m)]

        if matches:
            findings[pii_pattern.description] = len(matches)

    return findings
