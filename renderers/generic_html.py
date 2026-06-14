from __future__ import annotations
import json
from html import escape
from canonical.schema import Article, ContentBlock
from renderers.base import BaseRenderer, RenderResult


class GenericHTMLRenderer(BaseRenderer):
    format_name = "html"
    description = "Generic semantic HTML — for CMS rich-text fields, email, RSS"
    extension = "html"
    mime_type = "text/html"

    def render(self, article: Article) -> RenderResult:
        body = self._render_body(article)
        head = self._render_head(article)
        html = f"<!DOCTYPE html>\n<html lang=\"{article.language}\">\n<head>\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n"
        return self._result(html, article)

    def render_body_only(self, article: Article) -> str:
        return self._render_body(article)

    def _render_head(self, article: Article) -> str:
        lines = [f"  <meta charset=\"utf-8\">"]
        lines.append(f"  <title>{escape(article.meta_title or article.title)}</title>")
        lines.append(f"  <meta name=\"description\" content=\"{escape(article.meta_description or article.excerpt)}\">")
        if article.canonical_url:
            lines.append(f"  <link rel=\"canonical\" href=\"{escape(article.canonical_url)}\">")
        if article.featured_image:
            lines.append(f"  <meta property=\"og:image\" content=\"{escape(article.og_image or article.featured_image)}\">")
        lines.append(f"  <meta property=\"og:title\" content=\"{escape(article.meta_title or article.title)}\">")
        lines.append(f"  <meta property=\"og:description\" content=\"{escape(article.meta_description or article.excerpt)}\">")
        lines.append(f"  <meta name=\"twitter:card\" content=\"summary_large_image\">")
        lines.append(f"  <meta name=\"twitter:title\" content=\"{escape(article.meta_title or article.title)}\">")
        lines.append(f"  <meta name=\"twitter:description\" content=\"{escape(article.meta_description or article.excerpt)}\">")
        if article.schema_json_ld:
            schema_html = json.dumps(article.schema_json_ld, ensure_ascii=False)
            lines.append(f"  <script type=\"application/ld+json\">{schema_html}</script>")
        lines.append(f"  <style>")
        lines.append(f"    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 1rem; color: #1a1a1a; }}")
        lines.append(f"    h1, h2, h3, h4 {{ line-height: 1.3; }}")
        lines.append(f"    img {{ max-width: 100%; height: auto; }}")
        lines.append(f"    figure {{ margin: 2rem 0; text-align: center; }}")
        lines.append(f"    figcaption {{ font-size: 0.9rem; color: #666; margin-top: 0.5rem; }}")
        lines.append(f"    blockquote {{ border-left: 4px solid #0066cc; margin: 1.5rem 0; padding: 0.5rem 1rem; background: #f5f8ff; }}")
        lines.append(f"    .summary-box {{ background: #e8f4e8; border-left: 4px solid #2d8a2d; padding: 1rem 1.5rem; margin: 1.5rem 0; }}")
        lines.append(f"    .summary-box h3 {{ margin-top: 0; }}")
        lines.append(f"    @media (prefers-color-scheme: dark) {{ body {{ background: #1a1a1a; color: #e0e0e0; }} blockquote {{ background: #1a2a1a; }} .summary-box {{ background: #1a2a1a; border-left-color: #4caf50; }} }}")
        lines.append(f"  </style>")
        return "\n".join(lines)

    def _render_body(self, article: Article) -> str:
        parts: list[str] = []
        parts.append(f"  <article>")
        parts.append(f"    <header>")
        parts.append(f"      <h1>{escape(article.title)}</h1>")
        if article.author:
            parts.append(f"      <p class=\"byline\">By {escape(article.author)}</p>")
        if article.date:
            parts.append(f"      <time datetime=\"{article.date}\">{article.date}</time>")
        parts.append(f"    </header>")
        if article.summary_box_items:
            parts.append(self._render_summary_box(article))
        if article.featured_image:
            parts.append(f"    <img src=\"{escape(article.featured_image)}\" alt=\"{escape(article.featured_image_alt)}\" class=\"featured-image\" />")
        for section in article.sections:
            parts.append(self._render_section(section))
        if article.faq_items:
            parts.append(self._render_faq(article))
        if article.cta:
            parts.append(self._render_cta(article))
        if article.citations:
            parts.append(self._render_citations(article))
        parts.append(f"  </article>")
        return "\n\n".join(parts)

    def _render_summary_box(self, article: Article) -> str:
        items = "\n".join(f"      <li>{escape(item)}</li>" for item in article.summary_box_items)
        return (
            f"    <div class=\"summary-box\">\n"
            f"      <h3>{escape(article.summary_box_label)}</h3>\n"
            f"      <ul>\n{items}\n      </ul>\n"
            f"    </div>"
        )

    def _render_section(self, section) -> str:
        parts: list[str] = []
        tag = f"h{section.heading_level}"
        parts.append(f"    <section>")
        parts.append(f"      <{tag}>{escape(section.heading)}</{tag}>")
        for block in section.blocks:
            rendered = self._render_block(block)
            if rendered:
                parts.append(rendered)
        parts.append(f"    </section>")
        return "\n\n".join(parts)

    def _render_block(self, block: ContentBlock) -> str:
        mapper = {
            "paragraph": lambda b: f"      <p>{escape(b.content)}</p>",
            "heading": lambda b: f"      <h{b.level or 3}>{escape(b.content)}</h{b.level or 3}>",
            "list": lambda b: "      <ul>\n" + "\n".join(f"        <li>{escape(item)}</li>" for item in b.content.split("\n") if item.strip()) + "\n      </ul>",
            "code": lambda b: f"      <pre><code>{escape(b.content)}</code></pre>",
            "image": lambda b: f"      <figure><img src=\"{escape(b.content)}\" alt=\"{escape(b.metadata.get('alt', ''))}\" /><figcaption>{escape(b.metadata.get('caption', ''))}</figcaption></figure>",
            "chart": lambda b: f"      <figure>\n{b.content}\n        <figcaption>{escape(b.metadata.get('caption', ''))}</figcaption>\n      </figure>",
            "video": lambda b: f"      <figure><iframe src=\"{escape(b.content)}\" title=\"{escape(b.metadata.get('title', ''))}\" loading=\"lazy\"></iframe><figcaption>{escape(b.metadata.get('title', ''))}</figcaption></figure>",
            "quote": lambda b: f"      <blockquote><p>{escape(b.content)}</p></blockquote>" + (f"<p>— {escape(b.metadata.get('source', ''))}</p>" if b.metadata.get("source") else ""),
            "citation_capsule": lambda b: f"      <p>{escape(b.content)}</p>",
            "info_gain_marker": lambda b: f"      <!-- [{escape(b.content)}] -->",
            "internal_link_zone": lambda b: f"      <p class=\"internal-link\">[Internal link: {escape(b.content)}]</p>",
            "table": lambda b: f"      {b.content}",
            "html_embed": lambda b: f"      {b.content}",
        }
        render_fn = mapper.get(block.type)
        return render_fn(block) if render_fn else f"      <p>{escape(block.content)}</p>"

    def _render_faq(self, article: Article) -> str:
        parts = [f"    <section id=\"faq\">", f"      <h2>Frequently Asked Questions</h2>"]
        for item in article.faq_items:
            parts.append(f"      <div itemscope=\"\" itemprop=\"mainEntity\" itemtype=\"https://schema.org/Question\">")
            parts.append(f"        <h3 itemprop=\"name\">{escape(item.question)}</h3>")
            parts.append(f"        <div itemscope=\"\" itemprop=\"acceptedAnswer\" itemtype=\"https://schema.org/Answer\">")
            parts.append(f"          <p itemprop=\"text\">{escape(item.answer)}</p>")
            parts.append(f"        </div>")
            parts.append(f"      </div>")
        parts.append(f"    </section>")
        return "\n".join(parts)

    def _render_cta(self, article: Article) -> str:
        return f"    <div class=\"cta-box\"><p>{escape(article.cta)}</p></div>"

    def _render_citations(self, article: Article) -> str:
        parts = [f"    <section id=\"sources\">", f"      <h2>Sources</h2>", f"      <ul>"]
        for c in article.citations:
            parts.append(f"        <li><a href=\"{escape(c.source_url)}\">{escape(c.source_name)}</a> — {escape(c.statistic)} ({escape(c.year)})</li>")
        parts.append(f"      </ul>")
        parts.append(f"    </section>")
        return "\n".join(parts)
