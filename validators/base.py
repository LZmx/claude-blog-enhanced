from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class ValidationResult:
    valid: bool
    format_name: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


ValidatorFn = Callable[[str], ValidationResult]

_registry: dict[str, ValidatorFn] = {}


def register(format_name: str, fn: ValidatorFn):
    _registry[format_name] = fn


def get_validator(format_name: str) -> ValidatorFn:
    resolved = _resolve_alias(format_name)
    if resolved not in _registry:
        raise ValueError(f"Unknown validator: {format_name}")
    return _registry[resolved]


def _resolve_alias(name: str) -> str:
    return {"md": "markdown", "mdx": "mdx", "html": "html", "generic-html": "html", "wordpress": "wordpress", "wordpress-classic": "wordpress", "wordpress-blocks": "wordpress-blocks", "wp": "wordpress", "php": "php", "php-template": "php"}.get(name, name)


def list_validators() -> list[str]:
    return list(_registry.keys())


def validate_output(output: str, format_name: str) -> ValidationResult:
    validator = get_validator(format_name)
    result = validator(output)
    result.format_name = format_name
    return result
