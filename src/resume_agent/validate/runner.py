import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from resume_agent.db import get_db
from resume_agent.models import ProfileModel, JobModel, ProjectModel
from resume_agent.profile.service import get_profile
from resume_agent.jobs.service import get_job_by_id
from resume_agent.validate.parseback import extract_pdf_text, verify_parseback_fidelity
from resume_agent.validate.hygiene import (
    verify_section_order,
    verify_unicode_integrity,
    verify_zero_hyphenation,
    verify_page_geometry,
)
from resume_agent.validate.keywords import verify_keyword_coverage
from resume_agent.validate.audit import verify_grounding_audit
from resume_agent.logging import logger


@dataclass
class GateResult:
    gate_number: int
    name: str
    passed: bool
    score: float
    max_score: float
    details: Dict[str, Any] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    pdf_path: Path
    job_id: Optional[int]
    is_valid: bool
    ats_score: float
    gates: Dict[str, GateResult] = field(default_factory=dict)
    all_violations: List[str] = field(default_factory=list)

    def print_summary(self, console: Optional[Console] = None):
        """Render beautiful Rich terminal table summarizing 7 validation gates."""
        c = console or Console()

        table = Table(title="ATS 7-Gate Mechanical Verification Report", title_style="bold cyan", border_style="cyan")
        table.add_column("Gate #", style="dim", width=8, justify="center")
        table.add_column("Verification Gate", style="bold white", width=34)
        table.add_column("Status", width=12, justify="center")
        table.add_column("Score", width=10, justify="right")
        table.add_column("Diagnostics / Metrics", style="dim white")

        for key, g in sorted(self.gates.items(), key=lambda x: x[1].gate_number):
            status = "[bold green]✔ PASS[/bold green]" if g.passed else "[bold red]✘ FAIL[/bold red]"
            score_str = f"{g.score:.1f}/{g.max_score:.1f}"

            # Prepare succinct diagnostic
            diag = "All checks satisfied."
            if g.violations:
                diag = f"[red]{'; '.join(g.violations[:2])}[/red]"
            elif key == "gate_1":
                diag = f"Recovered {g.details.get('recovered_fields_count', 0)}/{g.details.get('total_fields_count', 0)} core fields"
            elif key == "gate_5":
                diag = f"Exact {g.details.get('page_count', 1)} page (Single-Page budget)"
            elif key == "gate_6":
                diag = f"Coverage: {g.details.get('coverage_score', 100.0):.1f}% (Found {g.details.get('found_terms_count', 0)} keywords)"
            elif key == "gate_7":
                diag = f"Audited {g.details.get('grounded_skills_count', 0)} grounded tools (0 hallucinations)"

            table.add_row(str(g.gate_number), g.name, status, score_str, diag)

        c.print()
        c.print(table)

        # Composite score panel
        status_color = "green" if self.is_valid else "red"
        status_text = "ATS COMPLIANT — READY FOR DISPATCH" if self.is_valid else "NON-COMPLIANT — REVIEW REQUIRED"

        summary_panel = Panel(
            f"[bold {status_color}]Overall Result: {status_text}[/bold {status_color}]\n"
            f"[bold white]Composite ATS Mechanical Score:[/bold white] [bold {status_color}]{self.ats_score:.1f} / 100.0[/bold {status_color}]\n"
            f"[dim]Artifact: {self.pdf_path}[/dim]",
            border_style=status_color,
            title="Mechanical ATS Evaluation",
            title_align="left",
        )
        c.print(summary_panel)
        c.print()


def validate_resume_pdf(
    pdf_path: Path,
    job_id: Optional[int] = None,
    min_coverage: float = 80.0,
    update_db: bool = True
) -> ValidationReport:
    """
    Executes the 7-Step Automated Mechanical ATS Verification Suite on a generated PDF.
    
    Gates:
    1. Parse-Back Fidelity (20 pts)
    2. Section Boundary Order (10 pts)
    3. Unicode & Ligature Integrity (15 pts)
    4. Zero Hyphenation Mutilation (10 pts)
    5. Single-Page Physical Geometry (20 pts)
    6. Keyword Coverage Verification (15 pts)
    7. Anti-Hallucination Grounding Audit (10 pts)
    """
    pdf_p = Path(pdf_path)
    if not pdf_p.exists():
        raise FileNotFoundError(f"PDF file does not exist: {pdf_p}")

    logger.info(f"Running 7-Gate ATS Validation Suite on: {pdf_p.name}")

    # Extract text
    pdf_text = extract_pdf_text(pdf_p)
    profile = get_profile()

    # Retrieve job context if job_id provided or discoverable from DB
    target_job: Optional[JobModel] = None
    expected_bullets: List[str] = []

    if job_id:
        target_job = get_job_by_id(job_id)
        with get_db() as conn:
            row = conn.execute("SELECT bullets_json FROM matches WHERE job_id = ?;", (job_id,)).fetchone()
            if row and row["bullets_json"]:
                try:
                    payload = json.loads(row["bullets_json"])
                    for p in payload:
                        expected_bullets.extend(p.get("bullets", []))
                except Exception:
                    pass
    else:
        # Try to find match by pdf_path in DB
        with get_db() as conn:
            row = conn.execute("SELECT job_id, bullets_json FROM matches WHERE pdf_path = ?;", (str(pdf_p),)).fetchone()
            if row:
                job_id = row["job_id"]
                target_job = get_job_by_id(job_id)
                if row["bullets_json"]:
                    try:
                        payload = json.loads(row["bullets_json"])
                        for p in payload:
                            expected_bullets.extend(p.get("bullets", []))
                    except Exception:
                        pass

    gates = {}
    all_violations = []

    # Gate 1: Parse-Back Fidelity (Max 20 pts)
    p1_pass, p1_det, p1_viol = verify_parseback_fidelity(pdf_text, profile, expected_bullets)
    p1_score = 20.0 if p1_pass else 0.0
    gates["gate_1"] = GateResult(1, "Parse-Back Fidelity", p1_pass, p1_score, 20.0, p1_det, p1_viol)
    all_violations.extend(p1_viol)

    # Gate 2: Section Boundary Order (Max 10 pts)
    p2_pass, p2_det, p2_viol = verify_section_order(pdf_text)
    p2_score = 10.0 if p2_pass else 0.0
    gates["gate_2"] = GateResult(2, "Section Boundary Sequence", p2_pass, p2_score, 10.0, p2_det, p2_viol)
    all_violations.extend(p2_viol)

    # Gate 3: Unicode & Ligature Integrity (Max 15 pts)
    p3_pass, p3_det, p3_viol = verify_unicode_integrity(pdf_text)
    p3_score = 15.0 if p3_pass else 0.0
    gates["gate_3"] = GateResult(3, "Unicode & Ligature Integrity", p3_pass, p3_score, 15.0, p3_det, p3_viol)
    all_violations.extend(p3_viol)

    # Gate 4: Zero Hyphenation Mutilation (Max 10 pts)
    p4_pass, p4_det, p4_viol = verify_zero_hyphenation(pdf_text)
    p4_score = 10.0 if p4_pass else 0.0
    gates["gate_4"] = GateResult(4, "Zero Trailing Hyphenation", p4_pass, p4_score, 10.0, p4_det, p4_viol)
    all_violations.extend(p4_viol)

    # Gate 5: Single-Page Physical Geometry (Max 20 pts)
    p5_pass, p5_det, p5_viol = verify_page_geometry(pdf_p)
    p5_score = 20.0 if p5_pass else 0.0
    gates["gate_5"] = GateResult(5, "Single-Page Physical Budget", p5_pass, p5_score, 20.0, p5_det, p5_viol)
    all_violations.extend(p5_viol)

    # Gate 6: Keyword Coverage Verification (Max 15 pts)
    p6_pass, p6_det, p6_viol = verify_keyword_coverage(pdf_text, target_job, min_coverage_pct=min_coverage)
    cov_ratio = p6_det.get("coverage_score", 100.0) / 100.0
    p6_score = 15.0 * min(cov_ratio, 1.0)
    gates["gate_6"] = GateResult(6, "JD Keyword Coverage", p6_pass, p6_score, 15.0, p6_det, p6_viol)
    all_violations.extend(p6_viol)

    # Gate 7: Anti-Hallucination Grounding Audit (Max 10 pts)
    p7_pass, p7_det, p7_viol = verify_grounding_audit(pdf_text, profile)
    p7_score = 10.0 if p7_pass else 0.0
    gates["gate_7"] = GateResult(7, "Anti-Hallucination Audit", p7_pass, p7_score, 10.0, p7_det, p7_viol)
    all_violations.extend(p7_viol)

    # Composite evaluation
    # Knockout gates: 1, 2, 3, 4, 5, 7 must all pass. Gate 6 must meet min threshold.
    critical_pass = all(gates[f"gate_{i}"].passed for i in [1, 2, 3, 4, 5, 7])
    is_valid = critical_pass and p6_pass
    total_score = sum(g.score for g in gates.values())

    report = ValidationReport(
        pdf_path=pdf_p,
        job_id=job_id,
        is_valid=is_valid,
        ats_score=round(total_score, 1),
        gates=gates,
        all_violations=all_violations,
    )

    # Update SQLite database if job_id is bound
    if update_db and job_id:
        try:
            with get_db() as conn:
                conn.execute(
                    """
                    UPDATE matches
                    SET parse_ok = ?,
                        coverage_score = ?,
                        missing_terms_json = ?,
                        needs_review = ?
                    WHERE job_id = ?;
                    """,
                    (
                        1 if is_valid else 0,
                        p6_det.get("coverage_score", 100.0),
                        json.dumps(p6_det.get("missing_terms", [])),
                        0 if is_valid else 1,
                        job_id,
                    ),
                )
            logger.info(f"Updated matches record for Job #{job_id}: parse_ok={is_valid}, score={total_score:.1f}")
        except Exception as e:
            logger.warning(f"Could not update match record in DB: {e}")

    return report
