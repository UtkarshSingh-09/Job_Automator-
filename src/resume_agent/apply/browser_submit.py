import re
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

from resume_agent.models import JobModel, CompanyModel
from resume_agent.apply.models import ApplyResult, CandidateSubmissionPayload
from resume_agent.config import get_settings
from resume_agent.logging import logger


CAPTCHA_SELECTORS = [
    "iframe[src*='recaptcha']",
    "iframe[src*='hcaptcha']",
    "iframe[src*='turnstile']",
    "iframe[src*='arkoselabs']",
    "iframe[src*='client-api.arkoselabs.com']",
    "div.cf-turnstile",
    "div.g-recaptcha",
    "div.h-captcha",
    "[data-sitekey]",
]

LOGIN_SELECTORS = [
    "input[type='password']",
    "form[action*='login']",
    "form[action*='signin']",
    "button:has-text('Sign In to Apply')",
    "a:has-text('Sign In to Apply')",
]


def _clean_slug(text: str) -> str:
    """Sanitize string for file naming."""
    clean = re.sub(r"[^\w\-_]", "_", text)
    return re.sub(r"_+", "_", clean).strip("_")


def _get_screenshot_dir() -> Path:
    """Ensure and return screenshot output directory."""
    settings = get_settings()
    today_str = time.strftime("%Y-%m-%d")
    screenshot_dir = settings.output_dir / "screenshots" / today_str
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    return screenshot_dir


def check_captcha_present(page: Page) -> bool:
    """Detect presence of any CAPTCHA widget on the page."""
    for sel in CAPTCHA_SELECTORS:
        try:
            if page.locator(sel).count() > 0:
                return True
        except Exception:
            continue
    return False


def check_login_wall_present(page: Page, url: str) -> bool:
    """Detect if page requires user account login/creation."""
    if "myworkdayjobs.com" in url and "login" in url:
        return True

    for sel in LOGIN_SELECTORS:
        try:
            if page.locator(sel).count() > 0:
                # Check if password field is visible
                pw_elem = page.locator("input[type='password']")
                if pw_elem.count() > 0 and pw_elem.first.is_visible():
                    return True
        except Exception:
            continue
    return False


def fill_form_fields(page: Page, candidate: CandidateSubmissionPayload, resume_pdf_path: Path) -> Dict[str, Any]:
    """
    Locates common job application fields and fills them with candidate data.
    Returns audit dictionary of matched fields.
    """
    matched = {
        "first_name": False,
        "last_name": False,
        "full_name": False,
        "email": False,
        "phone": False,
        "linkedin": False,
        "github": False,
        "portfolio": False,
        "resume": False,
    }

    # 1. Email (Most critical unique identifier)
    email_selectors = [
        "input[type='email']",
        "input[name*='email' i]",
        "input[id*='email' i]",
        "input[placeholder*='email' i]",
    ]
    for sel in email_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                loc.first.fill(candidate.email)
                matched["email"] = True
                break
            except Exception:
                pass

    # 2. First Name
    fn_selectors = [
        "input[name*='first_name' i]",
        "input[name*='firstname' i]",
        "input[id*='first_name' i]",
        "input[id*='firstname' i]",
        "input[autocomplete='given-name']",
        "input[placeholder*='first name' i]",
    ]
    for sel in fn_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                loc.first.fill(candidate.first_name)
                matched["first_name"] = True
                break
            except Exception:
                pass

    # 3. Last Name
    ln_selectors = [
        "input[name*='last_name' i]",
        "input[name*='lastname' i]",
        "input[id*='last_name' i]",
        "input[id*='lastname' i]",
        "input[autocomplete='family-name']",
        "input[placeholder*='last name' i]",
    ]
    for sel in ln_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                loc.first.fill(candidate.last_name)
                matched["last_name"] = True
                break
            except Exception:
                pass

    # 4. Full Name (if separate first/last fields don't exist)
    if not matched["first_name"]:
        name_selectors = [
            "input[name='name' i]",
            "input[name*='full_name' i]",
            "input[name*='fullname' i]",
            "input[placeholder*='full name' i]",
            "input[aria-label*='full name' i]",
            "input[id*='full_name' i]",
        ]
        for sel in name_selectors:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                try:
                    loc.first.fill(candidate.full_name)
                    matched["full_name"] = True
                    break
                except Exception:
                    pass

    # 5. Phone
    phone_selectors = [
        "input[type='tel']",
        "input[name*='phone' i]",
        "input[id*='phone' i]",
        "input[placeholder*='phone' i]",
    ]
    for sel in phone_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                loc.first.fill(candidate.phone)
                matched["phone"] = True
                break
            except Exception:
                pass

    # 6. LinkedIn URL
    li_selectors = [
        "input[name*='linkedin' i]",
        "input[id*='linkedin' i]",
        "input[placeholder*='linkedin' i]",
        "input[aria-label*='linkedin' i]",
    ]
    for sel in li_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                loc.first.fill(candidate.linkedin_url)
                matched["linkedin"] = True
                break
            except Exception:
                pass

    # 7. GitHub URL
    gh_selectors = [
        "input[name*='github' i]",
        "input[id*='github' i]",
        "input[placeholder*='github' i]",
        "input[aria-label*='github' i]",
    ]
    for sel in gh_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                loc.first.fill(candidate.github_url)
                matched["github"] = True
                break
            except Exception:
                pass

    # 8. Portfolio / Website
    port_selectors = [
        "input[name*='portfolio' i]",
        "input[name*='website' i]",
        "input[id*='website' i]",
        "input[placeholder*='portfolio' i]",
        "input[placeholder*='website' i]",
    ]
    for sel in port_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                loc.first.fill(candidate.portfolio_url)
                matched["portfolio"] = True
                break
            except Exception:
                pass

    # 9. Resume File Upload
    file_selectors = [
        "input[type='file'][accept*='pdf']",
        "input[type='file'][name*='resume' i]",
        "input[type='file'][id*='resume' i]",
        "input[type='file']",
    ]
    for sel in file_selectors:
        loc = page.locator(sel)
        if loc.count() > 0:
            try:
                loc.first.set_input_files(str(resume_pdf_path))
                matched["resume"] = True
                break
            except Exception as e:
                logger.warning(f"Failed to attach resume to {sel}: {e}")

    return matched


def submit_via_browser(
    job: JobModel,
    candidate: CandidateSubmissionPayload,
    resume_pdf_path: Path,
    company: Optional[CompanyModel] = None,
    dry_run: bool = False,
    timeout: float = 40.0
) -> ApplyResult:
    """
    Tier 2 Browser Automation via Headless Chromium.
    Navigates to job application form, verifies safety conditions (no CAPTCHA, no login),
    maps candidate fields, attaches resume, and either captures verification screenshot
    (dry-run) or completes live submission.
    """
    apply_url = job.apply_url
    comp_slug = _clean_slug(job.company_name)
    title_slug = _clean_slug(job.title)
    screenshot_dir = _get_screenshot_dir()

    logger.info(f"Starting Playwright browser session for {job.company_name} - {job.title}")
    logger.info(f"Navigating to URL: {apply_url} (Dry Run: {dry_run})")

    if not resume_pdf_path.exists():
        return ApplyResult(
            success=False,
            status="failed",
            method="playwright_form",
            error=f"Resume PDF does not exist at {resume_pdf_path}"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        page = context.new_page()

        try:
            # 1. Navigate to target URL
            page.goto(apply_url, wait_until="networkidle", timeout=int(timeout * 1000))
            page.wait_for_timeout(1500)  # Settle dynamic JS rendering

            # 2. Check for Login Wall / Account Creation requirement
            if check_login_wall_present(page, apply_url):
                logger.warning(f"Login wall detected at {apply_url}. Bypassing auto-apply per safety policy.")
                ss_file = screenshot_dir / f"{comp_slug}__{title_slug}_login_wall.png"
                page.screenshot(path=str(ss_file), full_page=True)
                browser.close()
                return ApplyResult(
                    success=False,
                    status="needs_login",
                    method="playwright_form",
                    screenshot_path=ss_file,
                    notes="Account login/creation required. Manual submission required."
                )

            # 3. Check for CAPTCHA
            if check_captcha_present(page):
                logger.warning(f"CAPTCHA challenge detected at {apply_url}. Bypassing auto-apply per safety policy.")
                ss_file = screenshot_dir / f"{comp_slug}__{title_slug}_captcha.png"
                page.screenshot(path=str(ss_file), full_page=True)
                browser.close()
                return ApplyResult(
                    success=False,
                    status="captcha_blocked",
                    method="playwright_form",
                    screenshot_path=ss_file,
                    notes="CAPTCHA detected. Human interaction required."
                )

            # 4. Fill Application Form
            matched_fields = fill_form_fields(page, candidate, resume_pdf_path)
            logger.info(f"Form field matching summary: {matched_fields}")

            # Confidence gate: Must find email and either full_name or (first_name and last_name)
            has_identity = matched_fields["email"] and (matched_fields["full_name"] or (matched_fields["first_name"] and matched_fields["last_name"]))
            has_resume = matched_fields["resume"]

            if not has_identity or not has_resume:
                logger.warning(f"Low confidence form detection (<80%) at {apply_url}. Identity: {has_identity}, Resume: {has_resume}")
                ss_file = screenshot_dir / f"{comp_slug}__{title_slug}_form_mismatch.png"
                page.screenshot(path=str(ss_file), full_page=True)
                browser.close()
                return ApplyResult(
                    success=False,
                    status="form_error",
                    method="playwright_form",
                    screenshot_path=ss_file,
                    notes="Could not confidently bind required form inputs (email/name/resume).",
                    response_data={"matched_fields": matched_fields}
                )

            # 5. Handle Dry-Run Mode (Simulation only — no submit click)
            if dry_run:
                ss_file = screenshot_dir / f"{comp_slug}__{title_slug}_dryrun.png"
                page.screenshot(path=str(ss_file), full_page=True)
                logger.info(f"[DRY-RUN] Form filled successfully! Verification screenshot saved to: {ss_file}")
                browser.close()
                return ApplyResult(
                    success=True,
                    status="dry_run",
                    method="playwright_form",
                    screenshot_path=ss_file,
                    notes=f"Form inputs populated cleanly. Verified with screenshot.",
                    response_data={"matched_fields": matched_fields}
                )

            # 6. Live Submission Mode (Click Submit)
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Submit Application')",
                "button:has-text('Submit')",
                "button:has-text('Apply')",
            ]

            submitted = False
            for sel in submit_selectors:
                loc = page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    logger.info(f"Clicking submit button selector: {sel}")
                    loc.first.click()
                    submitted = True
                    break

            if not submitted:
                ss_file = screenshot_dir / f"{comp_slug}__{title_slug}_no_submit_btn.png"
                page.screenshot(path=str(ss_file), full_page=True)
                browser.close()
                return ApplyResult(
                    success=False,
                    status="form_error",
                    method="playwright_form",
                    screenshot_path=ss_file,
                    notes="Could not locate visible submit button on form."
                )

            # Wait for response / confirmation
            page.wait_for_timeout(4000)
            ss_file = screenshot_dir / f"{comp_slug}__{title_slug}_confirmed.png"
            page.screenshot(path=str(ss_file), full_page=True)
            logger.info(f"Application submitted! Confirmation screenshot saved to: {ss_file}")

            browser.close()
            return ApplyResult(
                success=True,
                status="submitted",
                method="playwright_form",
                screenshot_path=ss_file,
                notes="Submitted via headless browser.",
                response_data={"matched_fields": matched_fields}
            )

        except PlaywrightTimeoutError as te:
            logger.error(f"Navigation/interaction timeout for {apply_url}: {te}")
            browser.close()
            return ApplyResult(
                success=False,
                status="failed",
                method="playwright_form",
                error=f"Timeout interacting with application page: {te}"
            )
        except Exception as e:
            logger.error(f"Error during browser submission: {e}")
            browser.close()
            return ApplyResult(
                success=False,
                status="failed",
                method="playwright_form",
                error=str(e)
            )
