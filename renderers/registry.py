from __future__ import annotations
from typing import Literal
from canonical.schema import Article
from renderers.base import BaseRenderer, RenderResult

RenderFormat = Literal["markdown", "mdx", "html", "wordpress", "wordpress-blocks", "php"]

_registry: dict[str, type[BaseRenderer]] = {}
_instances: dict[str, BaseRenderer] = {}


def register(format_name: str, renderer_cls: type[BaseRenderer]):
    _registry[format_name] = renderer_cls


def _ensure_registered():
    if not _registry:
        from renderers.markdown import MarkdownRenderer
        from renderers.mdx import MDXRenderer
        from renderers.generic_html import GenericHTMLRenderer
        from renderers.wordpress_classic import WordPressClassicRenderer
        from renderers.wordpress_blocks import WordPressBlocksRenderer
        from renderers.php_template import PHPTemplateRenderer
        for cls in [MarkdownRenderer, MDXRenderer, GenericHTMLRenderer, WordPressClassicRenderer, WordPressBlocksRenderer, PHPTemplateRenderer]:
            register(cls.format_name, cls)


def get_renderer(format_name: str) -> BaseRenderer:
    _ensure_registered()
    resolved = _resolve_format_alias(format_name)
    if resolved not in _instances:
        cls = _registry.get(resolved)
        if not cls:
            msg = f"Unknown renderer: {format_name}. Available: {list(_registry.keys())}"
            raise ValueError(msg)
        _instances[resolved] = cls()
    return _instances[resolved]


def _resolve_format_alias(name: str) -> str:
    alias_map = {
        "markdown": "markdown",
        "md": "markdown",
        "mdx": "mdx",
        "html": "html",
        "generic-html": "html",
        "wordpress": "wordpress",
        "wordpress-classic": "wordpress",
        "wordpress-blocks": "wordpress-blocks",
        "wp": "wordpress",
        "wp-blocks": "wordpress-blocks",
        "php": "php",
        "php-template": "php",
    }
    return alias_map.get(name, name)


def list_renderers() -> list[dict[str, str]]:
    _ensure_registered()
    return [
        {"format": fmt, "description": cls.description, "extension": cls.extension}
        for fmt, cls in _registry.items()
    ]


def render_article(article: Article, format_name: str) -> RenderResult:
    renderer = get_renderer(format_name)
    return renderer.render(article)
