from typing import Optional, Tuple, List
import httpx
from resume_agent.jobs.discovery.patterns import ATS_SIGNATURES
from resume_agent.jobs.discovery.validator import validate_ats_slug
from resume_agent.logging import logger


def detect_ats(domain: str, timeout: float = 10.0) -> Optional[Tuple[str, str]]:
    """
    Attempt to auto-detect ATS provider and slug for a given company domain.
    Probes common career URLs, follows redirects, and analyzes HTML signatures.
    """
    cleaned_domain = domain.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]

    candidate_urls = [
        f"https://{cleaned_domain}/careers",
        f"https://{cleaned_domain}/jobs",
        f"https://careers.{cleaned_domain}",
        f"https://jobs.{cleaned_domain}",
        f"https://{cleaned_domain}",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True, max_redirects=5) as client:
        for url in candidate_urls:
            try:
                resp = client.get(url)
                if resp.status_code >= 400:
                    continue

                # 1. Check final redirected URL
                final_url = str(resp.url)
                detected = _match_signatures(final_url)
                if detected:
                    provider, slug = detected
                    if validate_ats_slug(provider, slug):
                        return provider, slug

                # 2. Check HTML body for iframes, links, and embedded scripts
                html_text = resp.text
                detected = _match_signatures(html_text)
                if detected:
                    provider, slug = detected
                    if validate_ats_slug(provider, slug):
                        return provider, slug

            except Exception as e:
                logger.debug(f"Probing {url} failed: {e}")
                continue

    return None


def _match_signatures(text: str) -> Optional[Tuple[str, str]]:
    """Check text against all ATS signature regexes in priority order."""
    for provider, patterns in ATS_SIGNATURES.items():
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                slug = match.group(1).strip("/").split("?")[0].split("#")[0]
                if slug and len(slug) > 1 and not slug.startswith("http"):
                    return provider, slug
    return None
