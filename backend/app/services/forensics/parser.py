import email
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import getaddresses, parsedate_to_datetime
from html.parser import HTMLParser
from typing import Any


class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ("script", "style"):
            self.skip = True

    def handle_endtag(self, tag):
        if tag.lower() in ("script", "style"):
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)

    def get_text(self) -> str:
        return "".join(self.text).strip()


def _decode_header_value(value: str) -> str:
    """Decode RFC 2047 encoded header fragments."""
    if not value:
        return ""
    fragments = email.header.decode_header(value)
    parts = []
    for fragment, charset in fragments:
        if isinstance(fragment, bytes):
            try:
                parts.append(fragment.decode(charset or "utf-8", errors="replace"))
            except LookupError:
                parts.append(fragment.decode("utf-8", errors="replace"))
        else:
            parts.append(fragment)
    return "".join(parts)


def _extract_first_address(raw: str | None) -> tuple[str | None, str | None]:
    """Return (display_name, address) for the first address in a header."""
    if not raw:
        return None, None
    addresses = getaddresses([_decode_header_value(raw)])
    if not addresses:
        return None, None
    display, addr = addresses[0]
    return display or None, addr or None


def _extract_address_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    addresses = getaddresses([_decode_header_value(raw)])
    return [addr for _, addr in addresses if addr]


def _parse_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _get_body_text(msg: Any) -> tuple[str | None, str | None]:
    """Return (plain_text, sanitized_html)."""
    plain_parts = []
    html_parts = []

    def walk(part: Any):
        content_type = part.get_content_type()
        disposition = part.get_content_disposition() or ""
        if "attachment" in disposition:
            return
        if content_type == "text/plain":
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or "utf-8"
                try:
                    plain_parts.append(payload.decode(charset, errors="replace"))
                except LookupError:
                    plain_parts.append(payload.decode("utf-8", errors="replace"))
        elif content_type == "text/html":
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or "utf-8"
                try:
                    html = payload.decode(charset, errors="replace")
                except LookupError:
                    html = payload.decode("utf-8", errors="replace")
                html_parts.append(html)

    if msg.is_multipart():
        for part in msg.walk():
            if part is msg:
                continue
            walk(part)
    else:
        walk(msg)

    plain = "\n".join(plain_parts).strip() or None
    html = "\n".join(html_parts).strip() if html_parts else None

    if html:
        extractor = _HTMLTextExtractor()
        try:
            extractor.feed(html)
            sanitized_text = extractor.get_text()
        except Exception:
            sanitized_text = re.sub(r"<[^>]+>", "", html)
        # Escape remaining HTML so it cannot render as active markup.
        from html import escape

        sanitized_html = escape(sanitized_text)
    else:
        sanitized_html = None

    return plain, sanitized_html


@dataclass
class ParsedEmail:
    from_address: str | None = None
    from_display_name: str | None = None
    to_addresses: list[str] = field(default_factory=list)
    cc_addresses: list[str] = field(default_factory=list)
    reply_to: str | None = None
    return_path: str | None = None
    subject: str | None = None
    date: datetime | None = None
    message_id: str | None = None
    authentication_results: list[str] = field(default_factory=list)
    dkim_signatures: list[str] = field(default_factory=list)
    received: list[str] = field(default_factory=list)
    raw_headers: str = ""
    body_text: str | None = None
    body_html_sanitized: str | None = None


def parse_email_bytes(raw_bytes: bytes) -> ParsedEmail:
    """Parse raw email bytes into a structured representation.

    Treats the input as attacker-controlled data and never executes attachments.
    """
    try:
        msg = email.message_from_bytes(raw_bytes)
    except Exception as exc:
        # If the standard parser completely fails, return an empty parse.
        return ParsedEmail(raw_headers=f"# parse error: {exc}")

    raw_headers = ""
    for key, value in msg.items():
        raw_headers += f"{key}: {_decode_header_value(value)}\n"

    display, addr = _extract_first_address(msg.get("From", ""))
    body_text, body_html = _get_body_text(msg)

    return ParsedEmail(
        from_address=addr,
        from_display_name=display,
        to_addresses=_extract_address_list(msg.get("To", "")),
        cc_addresses=_extract_address_list(msg.get("Cc", "")),
        reply_to=_extract_first_address(msg.get("Reply-To", ""))[1],
        return_path=_extract_first_address(msg.get("Return-Path", ""))[1],
        subject=_decode_header_value(msg.get("Subject", "")),
        date=_parse_date(msg.get("Date", "")),
        message_id=msg.get("Message-ID", "").strip() or None,
        authentication_results=[
            v.strip() for v in msg.get_all("Authentication-Results", [])
        ],
        dkim_signatures=[v.strip() for v in msg.get_all("DKIM-Signature", [])],
        received=[v.strip() for v in msg.get_all("Received", [])],
        raw_headers=raw_headers,
        body_text=body_text,
        body_html_sanitized=body_html,
    )
