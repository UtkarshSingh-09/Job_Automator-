import html
import re
from typing import Optional


def html_to_markdown(raw_html: str) -> str:
    """
    Convert raw HTML job description into clean, readable Markdown text.
    Handles headings, paragraphs, lists, bold/italic, and breaks.
    """
    if not raw_html:
        return ""

    # 0. Unescape first in case API returned escaped HTML entities (&lt;div&gt;)
    text = html.unescape(raw_html)

    # 1. Strip script and style blocks
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # 2. Convert common HTML structural elements to Markdown
    text = re.sub(r"<h[1-3][^>]*>(.*?)</h[1-3]>", r"\n\n### \1\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<h[4-6][^>]*>(.*?)</h[4-6]>", r"\n\n#### \1\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>(.*?)</p>", r"\n\n\1\n\n", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"\n• \1", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", r"\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<(strong|b)[^>]*>(.*?)</\1>", r"**\2**", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<(em|i)[^>]*>(.*?)</\1>", r"*\2*", text, flags=re.DOTALL | re.IGNORECASE)

    # 3. Strip all remaining HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # 4. Unescape HTML entities (e.g. &amp;, &nbsp;, &#39;)
    text = html.unescape(text)

    # 5. Clean whitespace: collapse multiple blank lines into max 2
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                cleaned_lines.append("")
                prev_blank = True
        else:
            cleaned_lines.append(line)
            prev_blank = False

    return "\n".join(cleaned_lines).strip()


def detect_remote_type(title: str, location: str, description: str) -> str:
    """Classify remote status: remote, hybrid, or onsite."""
    combined = f"{title} {location} {description[:500]}".lower()

    if "remote" in combined or "work from anywhere" in combined or "telecommute" in combined:
        return "remote"
    elif "hybrid" in combined or "flexible" in combined:
        return "hybrid"
    return "onsite"
