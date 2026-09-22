import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import fitz  # PyMuPDF
from resume_agent.models import ProfileModel


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract raw text from PDF using PyMuPDF."""
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    text_chunks = []
    for page in doc:
        text_chunks.append(page.get_text())
    doc.close()
    return "\n".join(text_chunks)


def verify_parseback_fidelity(
    pdf_text: str,
    profile: Optional[ProfileModel] = None,
    expected_bullets: Optional[List[str]] = None
) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Gate 1: Parse-Back Fidelity.
    Asserts that candidate core identity fields and project bullet sentences
    are fully recovered from the PDF text stream without parsing dropouts or corruption.
    
    Returns:
        (is_pass: bool, details: Dict[str, Any], violations: List[str])
    """
    violations = []
    norm_text = " ".join(pdf_text.split()).lower()

    # Core identity fields to verify
    target_name = (profile.full_name if profile else "Utkarsh Singh").lower()
    target_email = (profile.email if profile else "thakurutkarsh2212@gmail.com").lower()
    raw_phone = profile.phone if profile else "+91-7565960168"
    phone_digits = re.sub(r"\D", "", raw_phone)[-10:]  # Last 10 digits
    target_college = (profile.college if profile else "SRM University Amaravati").lower()
    target_cgpa = f"{profile.cgpa:.2f}" if profile and profile.cgpa else "8.78"
    target_grad = str(profile.grad_year if profile and profile.grad_year else "2028")

    checks = {
        "candidate_name": target_name in norm_text,
        "email_address": target_email in norm_text,
        "phone_number": phone_digits in re.sub(r"\D", "", norm_text),
        "institution": "srm university" in norm_text,
        "degree_major": ("computer science" in norm_text) or ("bachelor" in norm_text),
        "cgpa_metric": target_cgpa in norm_text,
        "graduation_year": target_grad in norm_text,
    }

    for field, passed in checks.items():
        if not passed:
            violations.append(f"Gate 1: Critical identity field '{field}' was not recovered in PDF text stream")

    # Verify bullet recovery if expected bullets are provided
    bullet_checks = []
    if expected_bullets:
        for idx, bullet in enumerate(expected_bullets, 1):
            # Extract prominent words (>= 5 chars) to test lexical recovery
            clean_b = re.sub(r"[\*\`]", "", bullet)
            test_words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{5,}\b", clean_b)]
            if test_words:
                found_count = sum(1 for w in test_words if w in norm_text)
                recovery_pct = (found_count / len(test_words)) * 100
                passed = recovery_pct >= 85.0
                bullet_checks.append({
                    "bullet_index": idx,
                    "recovery_pct": round(recovery_pct, 1),
                    "passed": passed,
                })
                if not passed:
                    violations.append(
                        f"Gate 1: Bullet #{idx} text recovery failed ({recovery_pct:.1f}% recovered, threshold >= 85%)"
                    )

    is_pass = len(violations) == 0
    details = {
        "identity_checks": checks,
        "bullet_checks": bullet_checks,
        "recovered_fields_count": sum(1 for v in checks.values() if v),
        "total_fields_count": len(checks),
    }

    return is_pass, details, violations
