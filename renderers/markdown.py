from __future__ import annotations
from canonical.schema import Article, ContentBlock
from renderers.base import BaseRenderer, RenderResult


class MarkdownRenderer(BaseRenderer):
    format_name = "markdown"
    description = "Standard Markdown (GitHub Flavored) — for Obsidian, GitHub, static sites, editorial review"
    extension = "md"
    mime_type = "text/markdown"

    def render(self, article: Article) -> RenderResult:
        parts: list[str] = []
        parts.append(self._render_frontmatter(article))
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
        lines = ["---"]
        lines.append(f"title: \"{article.title}\"")
        lines.append(f"description: \"{article.meta_description or article.excerpt}\"")
        if article.featured_image:
            lines.append(f"coverImage: \"{article.featured_image}\"")
        if article.featured_image_alt:
            lines.append(f"coverImageAlt: \"{article.featured_image_alt}\"")
        if article.og_image:
            lines.append(f"ogImage: \"{article.og_image}\"")
        if article.date:
            lines.append(f"date: \"{article.date}\"")
        if article.last_updated:
            lines.append(f"lastUpdated: \"{article.last_updated}\"")
        if article.author:
            lines.append(f"author: \"{article.author}\"")
        if article.tags:
            lines.append(f"tags: [{', '.join(f'\"{t}\"' for t in article.tags)}]")
        if article.categories:
            lines.append(f"categories: [{', '.join(f'\"{c}\"' for c in article.categories)}]")
        if article.canonical_url:
            lines.append(f"canonicalURL: \"{article.canonical_url}\"")
        if article.language and article.language != "en":
            lines.append(f"lang: \"{article.language}\"")
        if article.translated_from:
            lines.append(f"translatedFrom: \"{article.translated_from}\"")
        if article.translated_date:
            lines.append(f"translatedDate: \"{article.translated_date}\"")
        lines.append("---")
        return "\n".join(lines)

    def _render_summary_box(self, article: Article) -> str:
        if not article.summary_box_items:
            return ""
        items = "\n".join(f"- {item}" for item in article.summary_box_items)
        return f"> **{article.summary_box_label}**\n{items}"

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
            "paragraph": self._render_paragraph,
            "heading": self._render_block_heading,
            "list": self._render_list,
            "code": self._render_code,
            "image": self._render_image,
            "chart": self._render_chart,
            "video": self._render_video,
            "quote": self._render_quote,
            "citation_capsule": self._render_citation_capsule,
            "info_gain_marker": self._render_info_gain,
            "internal_link_zone": self._render_internal_link,
            "table": self._render_table,
            "html_embed": self._render_html_embed,
        }
        render_fn = mapper.get(block.type)
        if render_fn:
            return render_fn(block)
        return block.content

    def _render_paragraph(self, block: ContentBlock) -> str:
        return block.content

    def _render_block_heading(self, block: ContentBlock) -> str:
        level = block.level or 3
        return f"{'#' * level} {block.content}"

    def _render_list(self, block: ContentBlock) -> str:
        items = block.content.split("\n")
        return "\n".join(f"- {item}" for item in items if item.strip())

    def _render_code(self, block: ContentBlock) -> str:
        lang = block.metadata.get("language", "")
        return f"```{lang}\n{block.content}\n```"

    def _render_image(self, block: ContentBlock) -> str:
        alt = block.metadata.get("alt", "")
        url = block.content
        return f"![{alt}]({url})"

    def _render_chart(self, block: ContentBlock) -> str:
        caption = block.metadata.get("caption", "")
        svg = block.content
        result = f"<figure>\n{svg}\n"
        if caption:
            result += f"  <figcaption>{caption}</figcaption>\n"
        result += "</figure>"
        return result

    def _render_video(self, block: ContentBlock) -> str:
        url = block.content
        title = block.metadata.get("title", "")
        return (
            f'<figure>\n'
            f'  <iframe src="{url}" title="{title}" loading="lazy"></iframe>\n'
            f'  <figcaption>{title}</figcaption>\n'
            f'</figure>'
        )

    def _render_quote(self, block: ContentBlock) -> str:
        source = block.metadata.get("source", "")
        text = block.content
        result = f"> {text}"
        if source:
            result += f"\n> — {source}"
        return result

    def _render_citation_capsule(self, block: ContentBlock) -> str:
        return block.content

    def _render_info_gain(self, block: ContentBlock) -> str:
        return f"<!-- [{block.content}] -->"

    def _render_internal_link(self, block: ContentBlock) -> str:
        return f"[INTERNAL-LINK: {block.content}]"

    def _render_table(self, block: ContentBlock) -> str:
        return block.content

    def _render_html_embed(self, block: ContentBlock) -> str:
        return block.content

    def _render_faq(self, article: Article) -> str:
        if not article.faq_items:
            return ""
        parts = ["## Frequently Asked Questions", ""]
        for item in article.faq_items:
            parts.append(f"### {item.question}")
            parts.append("")
            parts.append(item.answer)
            parts.append("")
        return "\n".join(parts)

    def _render_cta(self, article: Article) -> str:
        return f"\n> **{article.cta}**\n"

    def _render_citations(self, article: Article) -> str:
        if not article.citations:
            return ""
        parts = ["## Sources", ""]
        for c in article.citations:
            parts.append(f"- [{c.source_name}]({c.source_url}) - {c.statistic} ({c.year})")
            parts.append("")
        return "\n".join(parts)
