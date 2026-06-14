from __future__ import annotations
from canonical.schema import Article, ContentBlock
from renderers.base import BaseRenderer, RenderResult


class MDXRenderer(BaseRenderer):
    format_name = "mdx"
    description = "MDX (Markdown + JSX) — for Next.js, Astro, Gatsby MDX pipelines"
    extension = "mdx"
    mime_type = "text/mdx"

    def render(self, article: Article) -> RenderResult:
        parts: list[str] = []
        parts.append(self._render_frontmatter(article))
        parts.append("")
        for imp in article.platform_overrides.mdx_imports:
            parts.append(imp)
            parts.append("")
        parts.append(self._render_summary_box(article))
        for section in article.sections:
            parts.append(self._render_section(section))
        parts.append(self._render_faq(article))
        if article.cta:
            parts.append(self._render_cta(article))
        parts.append(self._render_citations(article))
        content = "\n\n".join(p for p in parts if p.strip()) + "\n"
        return self._result(content, article)

    def _render_frontmatter(self, article: Article) -> str:
        import json
        lines = ["---"]
        lines.append(f"title: '{article.title}'")
        lines.append(f"description: '{article.meta_description or article.excerpt}'")
        if article.featured_image:
            lines.append(f"coverImage: '{article.featured_image}'")
        if article.featured_image_alt:
            lines.append(f"coverImageAlt: '{article.featured_image_alt}'")
        if article.og_image:
            lines.append(f"ogImage: '{article.og_image}'")
        if article.date:
            lines.append(f"date: '{article.date}'")
        if article.last_updated:
            lines.append(f"lastUpdated: '{article.last_updated}'")
        if article.author:
            lines.append(f"author: '{article.author}'")
        if article.canonical_url:
            lines.append(f"canonicalURL: '{article.canonical_url}'")
        if article.tags:
            lines.append(f"tags: {json.dumps(article.tags)}")
        if article.categories:
            lines.append(f"categories: {json.dumps(article.categories)}")
        lines.append("---")
        return "\n".join(lines)

    def _render_summary_box(self, article: Article) -> str:
        if not article.summary_box_items:
            return ""
        items = "\n".join(f"- {item}" for item in article.summary_box_items)
        return f"<Callout type=\"summary\">\n\n**{article.summary_box_label}**\n\n{items}\n\n</Callout>"

    def _render_section(self, section) -> str:
        lines: list[str] = []
        marker = "#" * section.heading_level
        lines.append(f"{marker} {section.heading}")
        for block in section.blocks:
            rendered = self._render_block(block)
            if rendered:
                lines.append(rendered)
        return "\n\n".join(lines)

    def _render_block(self, block: ContentBlock) -> str:
        mapper = {
            "paragraph": lambda b: b.content,
            "heading": lambda b: f"{'#' * (b.level or 3)} {b.content}",
            "list": lambda b: "\n".join(f"- {item}" for item in b.content.split("\n") if item.strip()),
            "code": lambda b: f"```{b.metadata.get('language', '')}\n{b.content}\n```",
            "image": lambda b: f"<Image src=\"{b.content}\" alt=\"{b.metadata.get('alt', '')}\" />",
            "chart": lambda b: f"<figure>\n{b.content}\n  <figcaption>{b.metadata.get('caption', '')}</figcaption>\n</figure>",
            "video": lambda b: f"<Video src=\"{b.content}\" title=\"{b.metadata.get('title', '')}\" />",
            "quote": lambda b: f"> {b.content}" + (f"\n> — {b.metadata.get('source', '')}" if b.metadata.get("source") else ""),
            "citation_capsule": lambda b: b.content,
            "info_gain_marker": lambda b: f"{{/* [{b.content}] */}}",
            "internal_link_zone": lambda b: f"<InternalLink to=\"{b.content}\" />",
            "table": lambda b: b.content,
            "html_embed": lambda b: b.content,
        }
        render_fn = mapper.get(block.type)
        return render_fn(block) if render_fn else block.content

    def _render_faq(self, article: Article) -> str:
        if not article.faq_items:
            return ""
        items_json = []
        for item in article.faq_items:
            items_json.append(f"    {{ question: '{item.question}', answer: '{item.answer}' }}")
        return (
            f"<FAQSchema faqs={{\n"
            + ",\n".join(items_json) +
            f"\n}} />\n\n"
            f"## Frequently Asked Questions\n"
            + "\n".join(f"### {item.question}\n\n{item.answer}" for item in article.faq_items)
        )

    def _render_cta(self, article: Article) -> str:
        return f"\n<Callout type=\"cta\">\n\n{article.cta}\n\n</Callout>\n"

    def _render_citations(self, article: Article) -> str:
        if not article.citations:
            return ""
        parts = ["## Sources", ""]
        for c in article.citations:
            parts.append(f"- [{c.source_name}]({c.source_url}) — {c.statistic} ({c.year})")
        return "\n".join(parts)
