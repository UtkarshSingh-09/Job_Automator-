import hashlib
import re


def generate_content_hash(company_name: str, title: str, location: str = "") -> str:
    """
    Generate deterministic SHA-256 content hash for deduplication.
    Normalizes company, title, and location into a canonical key.
    """
    def clean(s: str) -> str:
        s = s.lower().strip()
        s = re.sub(r"[^\w\s]", "", s)
        return " ".join(s.split())

    key = f"{clean(company_name)}|{clean(title)}|{clean(location)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()
