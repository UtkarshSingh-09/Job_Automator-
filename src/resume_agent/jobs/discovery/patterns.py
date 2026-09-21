import re
from typing import Dict, List, Tuple

# Mapping of ATS provider to regex pattern tuples: (compiled_regex, description)
ATS_SIGNATURES: Dict[str, List[re.Pattern]] = {
    "greenhouse": [
        re.compile(r"boards\.greenhouse\.io/(?:embed/job_board\?for=)?([a-zA-Z0-9_-]+)", re.IGNORECASE),
        re.compile(r"boards-api\.greenhouse\.io/v1/boards/([a-zA-Z0-9_-]+)", re.IGNORECASE),
        re.compile(r"api\.greenhouse\.io/v1/boards/([a-zA-Z0-9_-]+)", re.IGNORECASE),
        re.compile(r'data-board="([a-zA-Z0-9_-]+)"', re.IGNORECASE),
    ],
    "lever": [
        re.compile(r"jobs\.lever\.co/([a-zA-Z0-9_-]+)", re.IGNORECASE),
        re.compile(r"api\.lever\.co/v0/postings/([a-zA-Z0-9_-]+)", re.IGNORECASE),
    ],
    "ashby": [
        re.compile(r"jobs\.ashbyhq\.com/([a-zA-Z0-9_-]+)", re.IGNORECASE),
        re.compile(r"api\.ashbyhq\.com/posting-api/job-board/([a-zA-Z0-9_-]+)", re.IGNORECASE),
        re.compile(r"ashbyhq\.com/([a-zA-Z0-9_-]+)", re.IGNORECASE),
    ],
    "workable": [
        re.compile(r"apply\.workable\.com/([a-zA-Z0-9_-]+)", re.IGNORECASE),
        re.compile(r"([a-zA-Z0-9_-]+)\.workable\.com", re.IGNORECASE),
    ],
    "recruitee": [
        re.compile(r"([a-zA-Z0-9_-]+)\.recruitee\.com", re.IGNORECASE),
    ],
    "smartrecruiters": [
        re.compile(r"careers\.smartrecruiters\.com/([a-zA-Z0-9_-]+)", re.IGNORECASE),
        re.compile(r"api\.smartrecruiters\.com/v1/companies/([a-zA-Z0-9_-]+)", re.IGNORECASE),
    ],
}
