from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from canonical.schema import Article


@dataclass
class RenderResult:
    content: str
    extension: str
    mime_type: str = "text/plain"
    warnings: list[str] = field(default_factory=list)
    _article_slug: str = ""

    def default_filename(self, slug: str = "") -> str:
        used = slug or self._article_slug
        return f"{used}.{self.extension}"


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class BaseRenderer(ABC):
    format_name: str = ""
    description: str = ""
    extension: str = ""
    mime_type: str = "text/plain"

    @abstractmethod
    def render(self, article: Article) -> RenderResult:
        ...

    def render_to_string(self, article: Article) -> str:
        return self.render(article).content

    def validate(self, output: str) -> ValidationResult:
        return ValidationResult(valid=True)

    def default_filename(self, slug: str) -> str:
        return f"{slug}.{self.extension}"

    def _result(self, content: str, article: Article) -> RenderResult:
        result = RenderResult(content=content, extension=self.extension, mime_type=self.mime_type)
        result._article_slug = article.slug
        return result
