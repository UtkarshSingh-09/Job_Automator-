import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import fitz  # PyMuPDF
import jinja2

from resume_agent.config import get_settings
from resume_agent.render.escape import latex_escape
from resume_agent.logging import logger


def find_latex_compiler() -> Optional[str]:
    """Detect available LaTeX compiler on the system (tectonic or pdflatex)."""
    # 1. Check tectonic
    tectonic_path = shutil.which("tectonic")
    if tectonic_path:
        return tectonic_path

    # 2. Check standard Mac TeX Live location
    mac_pdflatex = "/Library/TeX/texbin/pdflatex"
    if os.path.exists(mac_pdflatex) and os.access(mac_pdflatex, os.X_OK):
        return mac_pdflatex

    # 3. Check PATH pdflatex
    pdflatex_path = shutil.which("pdflatex")
    if pdflatex_path:
        return pdflatex_path

    return None


def render_latex_template(context: Dict[str, Any]) -> str:
    """Render templates/resume.tex.j2 with safe character escaping."""
    settings = get_settings()
    template_dir = settings.project_root / "templates"
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["latex_escape"] = latex_escape

    template = env.get_template("resume.tex.j2")
    return template.render(**context)


def compile_resume_pdf(
    context: Dict[str, Any],
    company_name: str,
    job_title: str
) -> Path:
    """
    Compile single-page ATS-proof resume to PDF.
    Verifies page count strictly equals 1 using PyMuPDF (fitz).
    Saves PDF to data/output/{YYYY-MM-DD}/{company}__{title}.pdf.
    """
    compiler = find_latex_compiler()
    if not compiler:
        raise RuntimeError(
            "No LaTeX compiler found on system! Please install tectonic ('brew install tectonic') "
            "or TeX Live ('/Library/TeX/texbin/pdflatex')."
        )

    tex_content = render_latex_template(context)
    settings = get_settings()

    # Destination directory
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = settings.output_dir / date_str
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_comp = re.sub(r"[^\w\-]", "_", company_name.strip())
    safe_title = re.sub(r"[^\w\-]", "_", job_title.strip())
    dest_pdf_path = out_dir / f"{safe_comp}__{safe_title}.pdf"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        tex_file = tmp_path / "resume.tex"
        tex_file.write_text(tex_content, encoding="utf-8")

        # Compile
        logger.info(f"Compiling resume PDF using '{compiler}'...")
        if "tectonic" in compiler.lower():
            cmd = [compiler, str(tex_file), "--outdir", str(tmp_path)]
        else:
            cmd = [
                compiler,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-output-directory",
                str(tmp_path),
                str(tex_file),
            ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        compiled_pdf = tmp_path / "resume.pdf"

        if not compiled_pdf.exists():
            log_preview = res.stdout[-1500:] if res.stdout else res.stderr[-1500:]
            logger.error(f"LaTeX compilation failed:\n{log_preview}")
            raise RuntimeError(f"LaTeX compilation failed to produce PDF:\n{log_preview}")

        # Verify page count with PyMuPDF
        doc = fitz.open(compiled_pdf)
        page_count = doc.page_count
        doc.close()

        if page_count != 1:
            logger.warning(
                f"Generated PDF has {page_count} pages (must be strictly 1 page for ATS budget)!"
            )
        else:
            logger.info("Verified single-page constraint: 1/1 pages.")

        # Copy to output destination
        shutil.copy2(compiled_pdf, dest_pdf_path)
        logger.info(f"Resume PDF saved successfully to: {dest_pdf_path}")

    return dest_pdf_path
