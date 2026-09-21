import re


def latex_escape(text: str) -> str:
    """
    Safely escape LaTeX special characters in dynamic text inputs.
    Converts reserved characters and smart typographical symbols into clean LaTeX representation.
    """
    if not text:
        return ""

    s = str(text)

    # 1. Normalize unicode typographical quotes and dashes
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("‘", "'").replace("’", "'")
    s = s.replace("—", "---").replace("–", "--")

    # 2. Backslash must be escaped first before introducing other backslashes
    s = s.replace("\\", r"\textbackslash{}")

    # 3. Special characters
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
