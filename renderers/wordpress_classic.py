from __future__ import annotations
from html import escape
from canonical.schema import Article, ContentBlock
from renderers.base import BaseRenderer, RenderResult


class WordPressClassicRenderer(BaseRenderer):
    format_name = "wordpress"
    description = "WordPress Classic Editor HTML — semantic, safe tags, suitable for post_content via REST API"
    extension = "wp.html"
    mime_type = "text/html"

    SAFE_TAGS = {"p", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "a", "img", "figure", "figcaption", "blockquote", "pre", "code", "table", "thead", "tbody", "tr", "th", "td", "em", "strong", "br", "hr", "div", "span", "sup", "sub"}

    def render(self, article: Article) -> RenderResult:
        body = self._render_body(article)
        html = f"<!-- wp:post-content -->\n{body}\n<!-- /wp:post-content -->\n"
        return self._result(html, article)

    def render_body_only(self, article: Article) -> str:
        return self._render_body(article)

    def _render_body(self, article: Article) -> str:
        parts: list[str] = []
        if article.summary_box_items:
            parts.append(self._render_summary_box(article))
        if article.featured_image:
            parts.append(self._render_wp_image(article.featured_image, article.featured_image_alt, is_featured=True))
        for section in article.sections:
            parts.append(self._render_section(section))
        if article.faq_items:
            parts.append(self._render_faq(article))
        if article.cta:
            parts.append(self._render_cta(article))
        return "\n\n".join(parts)

    def _render_summary_box(self, article: Article) -> str:
        items = "\n".join(f"<li>{escape(item)}</li>" for item in article.summary_box_items)
        return f"<!-- wp:group {{\"className\":\"summary-box\"}} -->\n<div class=\"summary-box\">\n<h3>{escape(article.summary_box_label)}</h3>\n<ul>{items}</ul>\n</div>\n<!-- /wp:group -->"

    def _render_wp_image(self, url: str, alt: str, is_featured: bool = False) -> str:
        if is_featured:
            attrs = '{"align":"center","sizeSlug":"large"}'
            return f"<!-- wp:image {attrs} -->\n<figure class=\"wp-block-image aligncenter size-large\"><img src=\"{escape(url)}\" alt=\"{escape(alt)}\" /></figure>\n<!-- /wp:image -->"
        return f"<!-- wp:image -->\n<figure class=\"wp-block-image\"><img src=\"{escape(url)}\" alt=\"{escape(alt)}\" /></figure>\n<!-- /wp:image -->"

    def _render_section(self, section) -> str:
        parts: list[str] = []
        tag = f"h{section.heading_level}"
        parts.append(f"<!-- wp:heading {{\"level\":{section.heading_level}}} -->")
        parts.append(f"<{tag}>{escape(section.heading)}</{tag}>")
        parts.append(f"<!-- /wp:heading -->")
        for block in section.blocks:
            rendered = self._render_block(block)
            if rendered:
                parts.append(rendered)
        return "\n".join(parts)

    def _render_block(self, block: ContentBlock) -> str:
        mapper = {
            "paragraph": lambda b: f"<!-- wp:paragraph -->\n<p>{escape(b.content)}</p>\n<!-- /wp:paragraph -->",
            "heading": lambda b: f"<!-- wp:heading {{\"level\":{b.level or 3}}} -->\n<h{b.level or 3}>{escape(b.content)}</h{b.level or 3}>\n<!-- /wp:heading -->",
            "list": lambda b: "<!-- wp:list -->\n<ul>\n" + "\n".join(f"<li>{escape(item)}</li>" for item in b.content.split("\n") if item.strip()) + "\n</ul>\n<!-- /wp:list -->",
            "code": lambda b: f"<!-- wp:code -->\n<pre class=\"wp-block-code\"><code>{escape(b.content)}</code></pre>\n<!-- /wp:code -->",
            "image": lambda b: self._render_wp_image(b.content, b.metadata.get("alt", "")),
            "chart": lambda b: f"<!-- wp:html -->\n<figure>\n{b.content}\n<figcaption>{escape(b.metadata.get('caption', ''))}</figcaption>\n</figure>\n<!-- /wp:html -->",
            "video": lambda b: f"<!-- wp:embed {{\"url\":\"{escape(b.content)}\"}} -->\n<figure class=\"wp-block-embed\"><iframe src=\"{escape(b.content)}\" title=\"{escape(b.metadata.get('title', ''))}\"></iframe></figure>\n<!-- /wp:embed -->",
            "quote": lambda b: f"<!-- wp:quote -->\n<blockquote class=\"wp-block-quote\"><p>{escape(b.content)}</p></blockquote>\n<!-- /wp:quote -->",
            "citation_capsule": lambda b: f"<!-- wp:paragraph -->\n<p>{escape(b.content)}</p>\n<!-- /wp:paragraph -->",
            "info_gain_marker": lambda b: f"<!-- {escape(b.content)} -->",
            "internal_link_zone": lambda b: f"<!-- wp:paragraph -->\n<p>[Internal link: {escape(b.content)}]</p>\n<!-- /wp:paragraph -->",
            "table": lambda b: f"<!-- wp:table -->\n<figure class=\"wp-block-table\"><table>{b.content}</table></figure>\n<!-- /wp:table -->",
            "html_embed": lambda b: f"<!-- wp:html -->\n{b.content}\n<!-- /wp:html -->",
        }
        render_fn = mapper.get(block.type)
        return render_fn(block) if render_fn else f"<!-- wp:paragraph -->\n<p>{escape(block.content)}</p>\n<!-- /wp:paragraph -->"

    def _render_faq(self, article: Article) -> str:
        parts = ["<!-- wp:heading -->", "<h2>Frequently Asked Questions</h2>", "<!-- /wp:heading -->"]
        for item in article.faq_items:
            parts.append(f"<!-- wp:heading {{\"level\":3}} -->")
            parts.append(f"<h3>{escape(item.question)}</h3>")
            parts.append(f"<!-- /wp:heading -->")
            parts.append(f"<!-- wp:paragraph -->")
            parts.append(f"<p>{escape(item.answer)}</p>")
            parts.append(f"<!-- /wp:paragraph -->")
        return "\n".join(parts)

    def _render_cta(self, article: Article) -> str:
        return f"<!-- wp:paragraph -->\n<p><strong>{escape(article.cta)}</strong></p>\n<!-- /wp:paragraph -->"
