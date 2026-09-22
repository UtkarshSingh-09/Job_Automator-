import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
import fitz  # PyMuPDF


def verify_section_order(pdf_text: str) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Gate 2: Section Boundary Order.
    Asserts exact chronological reading sequence:
    EDUCATION -> TECHNICAL SKILLS -> TECHNICAL PROJECTS -> HONORS & ACHIEVEMENTS
    """
    violations = []
    text_lower = pdf_text.lower()

    # Define standard headings and their regex patterns
    sections = [
        ("education", r"\b(education)\b"),
        ("skills", r"\b(technical skills|skills)\b"),
        ("projects", r"\b(technical projects|featured projects|projects)\b"),
        ("honors", r"\b(honors & achievements|honors and achievements|achievements|honors)\b"),
    ]

    positions = {}
    last_pos = -1

    for name, pat in sections:
        match = re.search(pat, text_lower)
        if not match:
            violations.append(f"Gate 2: Expected section '{name.upper()}' was not detected in resume text")
            positions[name] = -1
        else:
            pos = match.start()
            positions[name] = pos
            if pos < last_pos:
                violations.append(
                    f"Gate 2: Section order violation: '{name.upper()}' appears out of chronological order"
                )
            last_pos = pos

    is_pass = len(violations) == 0
    return is_pass, {"section_positions": positions}, violations


def verify_unicode_integrity(pdf_text: str) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Gate 3: Unicode & Ligature Integrity.
    Asserts zero occurrences of '\\ufffd' (unmapped glyphs) or Private Use Area codes.
    Verifies that ligatures ('fi', 'fl', 'ffi') decode cleanly into standard ASCII.
    """
    violations = []

    # 1. Unmapped replacement character
    ufffd_count = pdf_text.count("\ufffd")
    if ufffd_count > 0:
        violations.append(
            f"Gate 3: Detected {ufffd_count} unmapped glyph(s) ('\\ufffd') in extracted text stream"
        )

    # 2. Private Use Area (FontAwesome / custom icon fonts)
    pua_chars = []
    for idx, ch in enumerate(pdf_text):
        code = ord(ch)
        # Unicode PUA ranges: \uE000-\uF8FF, \U000F0000-\U000FFFFD, \U00100000-\U0010FFFD
        if (0xE000 <= code <= 0xF8FF) or (0xF0000 <= code <= 0xFFFFD) or (0x100000 <= code <= 0x10FFFD):
            pua_chars.append((ch, hex(code)))

    if pua_chars:
        violations.append(
            f"Gate 3: Detected {len(pua_chars)} Unicode Private Use Area icon glyph(s) (e.g. {pua_chars[0][1]})"
        )

    # 3. Check for typical broken ligature symptoms (e.g., 'Veri  cation', 'E  cient')
    broken_ligature_pattern = re.compile(r"\b[a-zA-Z]+\s{2,}[a-zA-Z]+\b")
    broken_ligatures = broken_ligature_pattern.findall(pdf_text)
    if broken_ligatures:
        violations.append(
            f"Gate 3: Suspected broken ligature gaps detected: {broken_ligatures[:3]}"
        )

    is_pass = len(violations) == 0
    details = {
        "unmapped_glyph_count": ufffd_count,
        "pua_icon_count": len(pua_chars),
        "broken_ligature_count": len(broken_ligatures),
    }
    return is_pass, details, violations


def verify_zero_hyphenation(pdf_text: str) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Gate 4: Zero Hyphenation Mutilation.
    Asserts that no technical keywords or words end with a trailing hyphen across a line break.
    """
    violations = []
    lines = pdf_text.splitlines()

    trailing_hyphens = []
    for idx, line in enumerate(lines[:-1]):
        stripped = line.rstrip()
        # Look for a word ending with a hyphen right at line boundary
        match = re.search(r"\b([a-zA-Z0-9_]+)-\s*$", stripped)
        if match:
            word_part = match.group(1)
            next_line = lines[idx + 1].lstrip()
            next_word_part = next_line.split()[0] if next_line.split() else ""
            reconstructed = f"{word_part}-{next_word_part}"
            trailing_hyphens.append({
                "line_number": idx + 1,
                "severed_token": reconstructed,
            })
            violations.append(
                f"Gate 4: Word severed across line break: '{reconstructed}' on line {idx + 1}"
            )

    is_pass = len(violations) == 0
    details = {
        "trailing_hyphen_count": len(trailing_hyphens),
        "severed_tokens": trailing_hyphens,
    }
    return is_pass, details, violations


def verify_page_geometry(pdf_path: Path) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Gate 5: Single-Page Physical Geometry.
    Asserts document page count == exactly 1 page.
    Flags any multi-page spillover (e.g., Page 1.05).
    """
    violations = []
    if not Path(pdf_path).exists():
        violations.append(f"Gate 5: PDF file not found at {pdf_path}")
        return False, {}, violations

    doc = fitz.open(pdf_path)
    page_count = doc.page_count

    if page_count != 1:
        violations.append(
            f"Gate 5: Document has {page_count} pages (must be strictly 1 page, zero spillover)"
        )

    page = doc[0] if page_count >= 1 else None
    rect = (page.rect.width, page.rect.height) if page else (0, 0)
    doc.close()

    is_pass = page_count == 1
    details = {
        "page_count": page_count,
        "page_width_pt": rect[0],
        "page_height_pt": rect[1],
        "is_single_page": page_count == 1,
    }
    return is_pass, details, violations
