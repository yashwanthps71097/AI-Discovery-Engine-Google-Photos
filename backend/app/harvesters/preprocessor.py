import re
import hashlib
from datetime import datetime
from typing import Tuple

class DataPreprocessor:
    """Sanitizes text, masks PII (emails, phones, IPs), and computes deduplication hashes."""

    # Regex patterns for PII detection
    EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_REGEX = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b')
    IP_REGEX = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
    HTML_REGEX = re.compile(r'<[^>]+>')
    EXCESS_WHITESPACE = re.compile(r'\s+')

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Strips HTML, normalizes whitespace, and masks Personally Identifiable Information (PII)."""
        if not text:
            return ""

        # Remove HTML tags
        cleaned = cls.HTML_REGEX.sub(' ', text)

        # Mask PII
        cleaned = cls.EMAIL_REGEX.sub('[EMAIL_REDACTED]', cleaned)
        cleaned = cls.PHONE_REGEX.sub('[PHONE_REDACTED]', cleaned)
        cleaned = cls.IP_REGEX.sub('[IP_REDACTED]', cleaned)

        # Normalize whitespace
        cleaned = cls.EXCESS_WHITESPACE.sub(' ', cleaned).strip()
        return cleaned

    @classmethod
    def sanitize_author(cls, author: str) -> str:
        """Sanitizes username/author to protect privacy."""
        if not author or author.lower() in ["anonymous", "none", "unknown"]:
            return "Anonymous User"
        # Mask emails if author is an email address
        if "@" in author:
            return cls.EMAIL_REGEX.sub('[EMAIL_REDACTED]', author)
        return author

    @classmethod
    def compute_deduplication_hash(cls, text: str, source_channel: str, post_date: datetime = None) -> str:
        """
        Computes SHA-256 hash across canonical parameters to guarantee zero duplicate processing.
        """
        normalized_text = " ".join(text.strip().lower().split())
        date_str = post_date.strftime("%Y-%m-%d") if post_date else "undated"
        composite = f"{source_channel.lower()}:{date_str}:{normalized_text}"
        return hashlib.sha256(composite.encode("utf-8")).hexdigest()

    @classmethod
    def process_raw_post(cls, raw_text: str, source_channel: str, author: str, post_date: datetime = None) -> Tuple[str, str, str]:
        """
        Runs full preprocessing pipeline.
        Returns: (sanitized_text, sanitized_author, deduplication_hash)
        """
        sanitized_text = cls.sanitize_text(raw_text)
        sanitized_author = cls.sanitize_author(author)
        dedup_hash = cls.compute_deduplication_hash(sanitized_text, source_channel, post_date)
        return sanitized_text, sanitized_author, dedup_hash
