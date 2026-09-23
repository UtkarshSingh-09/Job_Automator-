import re
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

from resume_agent.models import JobModel, CompanyModel
from resume_agent.apply.models import ApplyResult, CandidateSubmissionPayload
from resume_agent.apply.qa_generator import QAGenerator
from resume_agent.config import get_settings
from resume_agent.logging import logger


CAPTCHA_SELECTORS = [
    "iframe[title*='challenge' i]",
    "iframe[src*='bframe' i]",
    "iframe[src*='recaptcha/api2/bframe' i]",
    "iframe[src*='arkoselabs' i]",
    "iframe[src*='client-api.arkoselabs.com' i]",
    "div.g-recaptcha:not([data-size='invisible'])",
    "div.h-captcha:not([data-size='invisible'])",
    "div.cf-turnstile:not([data-size='invisible'])",
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


def resolve_custom_form_questions(
    page: Page,
    job: Optional[JobModel],
    candidate: CandidateSubmissionPayload
) -> Dict[str, str]:
    """
    Scans the page for custom textareas, select dropdowns, and unhandled inputs.
    Resolves each with QAGenerator and fills them in.
    Returns audit dictionary: {question_label: answered_value}
    """
    qa = QAGenerator()
    filled_answers = {}

    # 0. Handle standard custom text inputs and textareas (excluding comboboxes and file inputs)
    try:
        q_elements = page.locator('input[id^="question_"]:not([type="file"]):not([type="hidden"]):not([type="checkbox"]):not([type="radio"]), textarea[id^="question_"]')
        count = q_elements.count()
        for i in range(count):
            elem = q_elements.nth(i)
            if not elem.is_visible():
                continue

            input_type = (elem.get_attribute("type") or "").lower()
            if input_type in ("file", "hidden", "checkbox", "radio", "submit", "button"):
                continue

            role = elem.get_attribute("role") or ""
            cls = elem.get_attribute("class") or ""
            if role == "combobox" or "select__input" in cls:
                continue  # Handled by combobox section

            current_val = elem.input_value() or ""
            if current_val.strip():
                continue

            eid = elem.get_attribute("id") or ""
            lbl_elem = page.locator(f'label[for="{eid}"], [id="{eid}-label"]')
            lbl = lbl_elem.first.inner_text().strip().split("\n")[0] if lbl_elem.count() > 0 else eid
            tag = elem.evaluate("e => e.tagName.toLowerCase()")

            logger.info(f"Resolving custom question field: '{lbl[:50]}' ({tag})")
            res = qa.resolve_question(lbl, field_type=tag, job=job, candidate=candidate)
            ans = res.get("answer", "")
            if ans:
                elem.fill(ans)
                clean_lbl = lbl.strip("*").strip()
                filled_answers[clean_lbl] = ans
    except Exception as e:
        logger.warning(f"Error resolving custom question inputs: {e}")

    # 1. Handle Generic Textarea fields (Essays, Why company, Project descriptions)
    try:
        textareas = page.locator("textarea:not([id^='question_'])")
        count = textareas.count()
        for i in range(count):
            ta = textareas.nth(i)
            if not ta.is_visible():
                continue

            current_val = ta.input_value() or ""
            if current_val.strip():
                continue

            label_text = ""
            ta_id = ta.get_attribute("id")
            if ta_id:
                label_elem = page.locator(f"label[for='{ta_id}']")
                if label_elem.count() > 0:
                    label_text = label_elem.first.inner_text()

            if not label_text:
                label_text = ta.get_attribute("aria-label") or ta.get_attribute("placeholder") or ""

            if not label_text:
                parent = ta.locator("xpath=..")
                label_text = parent.inner_text() if parent.count() > 0 else ""

            if not label_text.strip():
                label_text = "Tell us about your background and why you are interested in this role."

            clean_label = label_text.split("\n")[0].strip()[:200]
            logger.info(f"Resolving custom textarea prompt: '{clean_label}'")
            res = qa.resolve_question(clean_label, field_type="textarea", job=job, candidate=candidate)
            answer_text = res.get("answer", "")
            if answer_text:
                ta.fill(answer_text)
                filled_answers[clean_label] = answer_text
    except Exception as e:
        logger.warning(f"Error resolving custom textareas: {e}")

    # 2. Handle Standard HTML <select> Dropdown fields
    try:
        selects = page.locator("select")
        count = selects.count()
        for i in range(count):
            sel = selects.nth(i)
            if not sel.is_visible():
                continue

            label_text = ""
            sel_id = sel.get_attribute("id")
            if sel_id:
                label_elem = page.locator(f"label[for='{sel_id}']")
                if label_elem.count() > 0:
                    label_text = label_elem.first.inner_text()

            if not label_text:
                label_text = sel.get_attribute("aria-label") or ""

            if not label_text:
                parent = sel.locator("xpath=..")
                label_text = parent.inner_text() if parent.count() > 0 else ""

            clean_label = label_text.split("\n")[0].strip()[:200]
            if not clean_label:
                continue

            options = []
            try:
                opt_locs = sel.locator("option")
                for o_idx in range(opt_locs.count()):
                    o_text = opt_locs.nth(o_idx).inner_text().strip()
                    if o_text:
                        options.append(o_text)
            except Exception:
                pass

            if not options:
                continue

            logger.info(f"Resolving custom select dropdown: '{clean_label}'")
            res = qa.resolve_question(clean_label, field_type="select", job=job, candidate=candidate, options=options)
            chosen_opt = res.get("answer", "")
            if chosen_opt:
                try:
                    sel.select_option(label=chosen_opt)
                    filled_answers[clean_label] = chosen_opt
                except Exception:
                    try:
                        sel.select_option(value=chosen_opt)
                        filled_answers[clean_label] = chosen_opt
                    except Exception as e:
                        logger.warning(f"Could not select option '{chosen_opt}' for '{clean_label}': {e}")
    except Exception as e:
        logger.warning(f"Error resolving standard selects: {e}")

    # 3. Handle Modern Comboboxes (Greenhouse react-select, dynamic dropdowns)
    # Run 2 passes to capture cascading fields that appear after an answer (e.g. race after Hispanic: No)
    try:
        for _pass in range(2):
            combos = page.locator('input.select__input, input[role="combobox"]').all()
            for cinp in combos:
                cid = cinp.get_attribute("id") or ""
                if cid in ["country", "candidate-location", "iti-0__search-input"]:
                    continue
                if not cinp.is_visible():
                    continue

                # Check if this react-select already has an active selection
                parent_container = cinp.locator("xpath=../../..")
                single_val = parent_container.locator(".select__single-value")
                if single_val.count() > 0 and single_val.inner_text().strip():
                    continue  # Already selected

                lbl_elem = page.locator(f'label[for="{cid}"], [id="{cid}-label"]')
                lbl = lbl_elem.first.inner_text().strip().replace("\n", " ") if lbl_elem.count() > 0 else cid

                try:
                    cinp.click(timeout=2000)
                    page.keyboard.press("ArrowDown")
                    page.wait_for_timeout(300)
                    opts = [o.inner_text().strip() for o in page.locator('div[id*="-option-"], .select__option').all()]
                    if not opts:
                        page.keyboard.press("Escape")
                        continue

                    res = qa.resolve_question(lbl, field_type="select", job=job, candidate=candidate, options=opts)
                    chosen = res.get("answer", "")
                    if chosen:
                        clean_lbl = lbl.strip("*").strip()
                        filled_answers[clean_lbl] = chosen

                    matched = page.locator('div[id*="-option-"], .select__option').filter(has_text=chosen).first
                    if matched.count() > 0:
                        matched.click()
                    else:
                        page.keyboard.press("Enter")
                    page.wait_for_timeout(300)
                except Exception as ce:
                    logger.debug(f"Combobox interaction warning on '{cid}': {ce}")
                    page.keyboard.press("Escape")
    except Exception as e:
        logger.warning(f"Error resolving modern comboboxes: {e}")

    return filled_answers


def fill_form_fields(
    page: Page,
    candidate: CandidateSubmissionPayload,
    resume_pdf_path: Path,
    job: Optional[JobModel] = None
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Locates common job application fields and fills them with candidate data,
    then automatically resolves custom textareas and select fields using QAGenerator.
    Returns: (matched_summary, filled_answers)
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

    # 8.5 Country Combobox (Greenhouse Phone & Country selection)
    country_selectors = [
        "#country",
        "input[name='country']",
        "input[id*='country' i]",
    ]
    for sel in country_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                loc.first.click()
                page.keyboard.type("India", delay=80)
                page.wait_for_timeout(600)
                opts = page.locator("div[id*='-option-'], .select__option").all()
                for o in opts:
                    t = o.inner_text().strip()
                    if t == "India +91" or t.startswith("India +") or t == "India":
                        o.click()
                        matched["country"] = True
                        break
                page.wait_for_timeout(300)
                break
            except Exception as ce:
                logger.debug(f"Country selection error: {ce}")

    # 9. City / Location / Address (handles standard text and react-select comboboxes)
    loc_selectors = [
        "#candidate-location",
        "input[name*='location' i]",
        "input[name*='city' i]",
        "input[placeholder*='location' i]",
        "input[placeholder*='city' i]",
        "input[id*='city' i]",
        "input[id*='location' i]",
    ]
    for sel in loc_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                role = loc.first.get_attribute("role") or ""
                cls = loc.first.get_attribute("class") or ""
                if role == "combobox" or "select__input" in cls:
                    loc.first.click()
                    # For autocomplete comboboxes, type primary city name rather than full address string
                    target_city = candidate.location.split(",")[0].strip() if candidate.location else "Ayodhya"
                    page.keyboard.type(target_city, delay=80)
                    page.wait_for_timeout(1200)
                    opts = page.locator("div[id*='-option-'], .select__option").all()
                    if opts:
                        opts[0].click()
                    else:
                        page.keyboard.press("Enter")
                    page.wait_for_timeout(400)
                else:
                    loc.first.fill(candidate.location)
                matched["location"] = True
                break
            except Exception:
                pass

    # 10. School / University
    school_selectors = [
        "input[name*='school' i]",
        "input[name*='university' i]",
        "input[name*='college' i]",
        "input[placeholder*='school' i]",
        "input[placeholder*='university' i]",
    ]
    for sel in school_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                loc.first.fill(candidate.college)
                matched["school"] = True
                break
            except Exception:
                pass

    # 11. Degree / Major
    degree_selectors = [
        "input[name*='degree' i]",
        "input[name*='major' i]",
        "input[placeholder*='degree' i]",
        "input[placeholder*='major' i]",
    ]
    for sel in degree_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            try:
                loc.first.fill(candidate.degree)
                matched["degree"] = True
                break
            except Exception:
                pass

    # 12. Resume File Upload
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

    # 13. Automatically resolve custom employer questions & dropdowns
    filled_answers = resolve_custom_form_questions(page, job, candidate)

    return matched, filled_answers


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
            matched_fields, filled_answers = fill_form_fields(page, candidate, resume_pdf_path, job=job)
            logger.info(f"Form field matching summary: {matched_fields}")
            logger.info(f"Custom questions answered ({len(filled_answers)}): {list(filled_answers.keys())}")

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
                    response_data={"matched_fields": matched_fields, "filled_answers": filled_answers}
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

            # 7. Verification Gate: Confirm actual submission
            # Poll for up to 10 seconds for navigation or confirmation/error states
            verified_success = False
            validation_errors = []
            captcha_challenge = False

            for _ in range(10):
                page.wait_for_timeout(1000)

                # Check if CAPTCHA challenge popped up
                if check_captcha_present(page):
                    captcha_challenge = True
                    break

                # Check for visible validation error messages on page
                error_locs = page.locator(
                    ".field-error, "
                    "div[aria-invalid='true'], "
                    "input[aria-invalid='true'], "
                    "[class*='error-message'], "
                    "[class*='errorMessage'], "
                    "span:has-text('This field is required'), "
                    "div:has-text('This field is required'), "
                    "span:has-text('Please enter your location')"
                )
                err_texts = []
                for e_idx in range(error_locs.count()):
                    try:
                        e_elem = error_locs.nth(e_idx)
                        if e_elem.is_visible():
                            txt = e_elem.inner_text().strip()
                            if txt and txt not in err_texts and len(txt) < 100:
                                err_texts.append(txt)
                    except Exception:
                        pass

                if err_texts:
                    validation_errors = err_texts
                    break

                # Check for confirmation indicators in URL
                curr_url = page.url.lower()
                if any(ind in curr_url for ind in ["confirmation", "thank_you", "submitted", "applied"]):
                    verified_success = True
                    break

                # Check for confirmation text in DOM
                body_text = page.inner_text("body").lower() if page.locator("body").count() > 0 else ""
                if any(conf in body_text for conf in [
                    "thank you for applying",
                    "application submitted",
                    "your application has been received",
                    "thanks for applying",
                    "we've received your application",
                    "application received"
                ]):
                    verified_success = True
                    break

            # Handle CAPTCHA challenge
            if captcha_challenge:
                ss_file = screenshot_dir / f"{comp_slug}__{title_slug}_captcha.png"
                page.screenshot(path=str(ss_file), full_page=True)
                browser.close()
                return ApplyResult(
                    success=False,
                    status="captcha_blocked",
                    method="playwright_form",
                    screenshot_path=ss_file,
                    notes="Interactive CAPTCHA challenge presented upon submit. Human interaction required.",
                    response_data={"matched_fields": matched_fields, "filled_answers": filled_answers}
                )

            # Handle Form Validation Errors
            if validation_errors:
                ss_file = screenshot_dir / f"{comp_slug}__{title_slug}_validation_failed.png"
                page.screenshot(path=str(ss_file), full_page=True)
                logger.warning(f"Form validation errors detected: {validation_errors}")
                browser.close()
                return ApplyResult(
                    success=False,
                    status="validation_blocked",
                    method="playwright_form",
                    screenshot_path=ss_file,
                    notes=f"Submission blocked by form validation errors: {', '.join(validation_errors)}",
                    response_data={"validation_errors": validation_errors, "matched_fields": matched_fields}
                )

            # Handle Confirmed Submission
            if verified_success:
                ss_file = screenshot_dir / f"{comp_slug}__{title_slug}_confirmed.png"
                page.screenshot(path=str(ss_file), full_page=True)
                logger.info(f"Application confirmed! Confirmation screenshot saved to: {ss_file}")
                browser.close()
                return ApplyResult(
                    success=True,
                    status="submitted",
                    method="playwright_form",
                    screenshot_path=ss_file,
                    notes="Application submission verified on employer confirmation screen.",
                    response_data={"matched_fields": matched_fields, "filled_answers": filled_answers}
                )

            # Fallback: Timeout / Ambiguous state
            ss_file = screenshot_dir / f"{comp_slug}__{title_slug}_ambiguous.png"
            page.screenshot(path=str(ss_file), full_page=True)
            logger.warning("Submission state unconfirmed after waiting 10 seconds.")
            browser.close()
            return ApplyResult(
                success=False,
                status="manual_required",
                method="playwright_form",
                screenshot_path=ss_file,
                notes="Submit clicked, but page did not transition to a verified confirmation screen. Manual verification required.",
                response_data={"matched_fields": matched_fields, "filled_answers": filled_answers}
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
