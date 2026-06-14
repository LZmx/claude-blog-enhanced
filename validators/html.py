from __future__ import annotations
import re
from validators.base import ValidationResult, register


def validate_html(content: str) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    # Check for markdown remnants in HTML output
    md_patterns = [
        (r"^---\s*$", "YAML frontmatter delimiter '---'"),
        (r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", "Markdown inline link format [text](url)"),
        (r"^#{1,6}\s", "Markdown heading format (#) at line start"),
        (r"^>\s", "Markdown blockquote format (>) at line start"),
        (r"```", "Markdown code fence (```)"),
        (r"^\s*[-*+]\s", "Markdown unordered list format at line start"),
    ]
    for line in content.split("\n"):
        stripped = line.strip()
        for pattern, desc in md_patterns:
            if re.match(pattern, stripped):
                warnings.append(f"{desc}: '{stripped[:60]}'")

    # Check for basic HTML structure
    if "<!DOCTYPE html>" not in content and "<html" not in content:
        if "<body" not in content:
            warnings.append("No <body> tag found - may be a fragment rather than full HTML")

    # Check for heading hierarchy
    h_levels = []
    for m in re.finditer(r"<h(\d)", content):
        h_levels.append(int(m.group(1)))
    for i in range(1, len(h_levels)):
        if h_levels[i] > h_levels[i - 1] + 1:
            warnings.append(f"Heading level skipped: h{h_levels[i-1]} -> h{h_levels[i]}")

    # Check for semantic elements
    if "<article" not in content:
        warnings.append("No <article> tag - consider semantic HTML")
    if "<main" not in content and "<article" not in content:
        warnings.append("No <main> or <article> landmark element")

    # Check for common issues
    unclosed_img = content.count("<img") - content.count("/>")
    if unclosed_img > 0:
        warnings.append(f"Found {unclosed_img} unclosed <img> tags (missing />)")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_wordpress(content: str) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    # Same md remnants check
    md_patterns = [
        (r"^---\s*$", "YAML frontmatter delimiter '---'"),
        (r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", "Markdown inline link format [text](url)"),
        (r"^#{1,6}\s", "Markdown heading format (#) at line start"),
        (r"```", "Markdown code fence (```)"),
    ]
    for line in content.split("\n"):
        for pattern, desc in md_patterns:
            if re.match(pattern, line.strip()):
                errors.append(f"{desc} found in WordPress output: '{line.strip()[:60]}'")

    # Check safe tags
    safe_tags = {"p", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "a", "img", "figure", "figcaption", "blockquote", "pre", "code", "table", "tr", "td", "th", "thead", "tbody", "em", "strong", "br", "hr", "div", "span", "sup", "sub", "section", "header", "footer"}
    found_tags = set(re.findall(r"<\/?(\w+)", content))
    unsafe = found_tags - safe_tags
    if unsafe:
        warnings.append(f"Potentially unsafe tags for WordPress: {', '.join(sorted(unsafe))}")

    # Check for wp-block comments
    if "<!-- wp:" not in content:
        warnings.append("No WordPress block comments found - content may not render in Block Editor")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_wordpress_blocks(content: str) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    # Check balanced block comments
    open_blocks = content.count("<!-- wp:")
    close_blocks = content.count("<!-- /wp:")
    if open_blocks != close_blocks:
        errors.append(f"Unbalanced block comments: {open_blocks} open vs {close_blocks} close")

    # Check no markdown remnants (same as wordpress)
    for line in content.split("\n"):
        if re.match(r"^---\s*$", line.strip()):
            errors.append(f"YAML frontmatter in block content: '{line.strip()[:60]}'")

    # Readability check - should be readable when comments removed
    import re as regex
    without_comments = regex.sub(r"<!--\s*(?:/)?wp:[^>]+-->", "", content).strip()
    if len(without_comments) < 50:
        warnings.append("Content appears empty after removing block comments")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_php(content: str) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    # Check for valid PHP open tag
    if "<?php" not in content:
        errors.append("No <?php opening tag found")
    if "?>" not in content and not content.strip().endswith("?>"):
        if content.strip().endswith(".php"):
            pass  # pure PHP file doesn't need closing tag
        warnings.append("No ?> closing tag - valid for pure PHP files")

    # Check for escaped output
    php_echo = re.findall(r"<\?php\s+echo\s+", content)
    if not php_echo:
        warnings.append("No echo statements - template may not output anything")

    # Check for escaping functions
    has_esc = "esc_html" in content or "esc_url" in content or "esc_attr" in content
    if not has_esc:
        warnings.append("No escaping functions (esc_html/esc_url/esc_attr) found - XSS risk")

    # Check no markdown remnants
    for line in content.split("\n"):
        if re.match(r"^---\s*$", line.strip()):
            errors.append(f"YAML frontmatter delimiter in PHP output")
            break

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


register("html", validate_html)
register("wordpress", validate_wordpress)
register("wordpress-blocks", validate_wordpress_blocks)
register("php", validate_php)
