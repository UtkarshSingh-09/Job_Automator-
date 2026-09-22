import re


def _escape_latex_plain(text: str) -> str:
    """Helper to escape raw plain text for LaTeX reserved characters."""
    if not text:
        return ""
    s = str(text)

    # Normalize unicode typographical quotes and dashes
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("‘", "'").replace("’", "'")
    s = s.replace("—", "---").replace("–", "--")

    # Backslash must be escaped first before introducing other backslashes
    s = s.replace("\\", r"\textbackslash{}")

    # Reserved special characters
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]

    for char, rep in replacements:
        s = s.replace(char, rep)

    return s


def latex_escape(text: str) -> str:
    """
    Safely escape LaTeX special characters in dynamic text inputs.
    Supports markdown bold (**text** -> \\textbf{text}) and inline code (`code` -> \\texttt{code})
    to enable recruiter eye-tracking bolding while protecting against LaTeX syntax corruption.
    """
    if not text:
        return ""

    pattern = re.compile(r"(\*\*.*?\*\*|`.*?`)")
    parts = pattern.split(str(text))
    out = []

    for part in parts:
        if part.startswith("**") and part.endswith("**") and len(part) >= 4:
            inner = part[2:-2]
            out.append(r"\textbf{" + _escape_latex_plain(inner) + "}")
        elif part.startswith("`") and part.endswith("`") and len(part) >= 2:
            inner = part[1:-1]
            out.append(r"\texttt{" + _escape_latex_plain(inner) + "}")
        else:
            out.append(_escape_latex_plain(part))

    return "".join(out)

