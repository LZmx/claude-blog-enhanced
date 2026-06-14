from __future__ import annotations
import re
from validators.base import ValidationResult, register


def validate_markdown(content: str) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    # Check frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end == -1:
            errors.append("Unclosed YAML frontmatter (no closing '---')")
        else:
            fm = content[3:end]
            if "title:" not in fm:
                warnings.append("Frontmatter missing 'title' field")
            if "description:" not in fm:
                warnings.append("Frontmatter missing 'description' field")
    else:
        warnings.append("No YAML frontmatter found (content should start with '---')")

    # Check heading hierarchy
    heading_levels = []
    for line in content.split("\n"):
        m = re.match(r"^(#{1,6})\s", line)
        if m:
            heading_levels.append(len(m.group(1)))
    for i in range(1, len(heading_levels)):
        if heading_levels[i] > heading_levels[i - 1] + 1:
            warnings.append(f"Heading level skipped: h{heading_levels[i-1]} -> h{heading_levels[i]}")

    if heading_levels and heading_levels[0] != 1:
        if not content.startswith("---"):
            errors.append("First heading must be H1 (# Title)")

    # Check for raw HTML that should be markdown
    html_patterns = [
        (r"<div[^>]*>", "<div> tags in markdown"),
        (r"<span[^>]*>", "<span> tags in markdown"),
        (r"<section[^>]*>", "<section> tags in markdown"),
    ]
    for pattern, desc in html_patterns:
        if re.search(pattern, content):
            warnings.append(f"{desc} - prefer markdown syntax")

    # Check for balanced code fences
    fences = content.count("```")
    if fences % 2 != 0:
        errors.append("Unbalanced code fences (odd count of ```)")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


register("markdown", validate_markdown)
