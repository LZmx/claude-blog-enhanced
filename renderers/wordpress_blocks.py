from __future__ import annotations
from html import escape
from canonical.schema import Article, ContentBlock
from renderers.base import BaseRenderer, RenderResult


class WordPressBlocksRenderer(BaseRenderer):
    format_name = "wordpress-blocks"
    description = "WordPress Block Editor (Gutenberg) HTML — full block markup for WP 5.0+"
    extension = "blocks.html"
    mime_type = "text/html"

    def render(self, article: Article) -> RenderResult:
        blocks: list[str] = []
        if article.summary_box_items:
            blocks.append(self._render_summary_box(article))
        for section in article.sections:
            blocks.append(self._render_section_heading(section))
            for block in section.blocks:
                rendered = self._render_block(block)
                if rendered:
                    blocks.append(rendered)
        if article.faq_items:
            blocks.append(self._render_faq(article))
        if article.cta:
            blocks.append(self._render_cta(article))
        content = "\n\n".join(blocks) + "\n"
        return self._result(content, article)

    def _render_section_heading(self, section) -> str:
        return (
            f"<!-- wp:heading {{\"level\":{section.heading_level}}} -->\n"
            f"<h{section.heading_level} class=\"wp-block-heading\">{escape(section.heading)}</h{section.heading_level}>\n"
            f"<!-- /wp:heading -->"
        )

    def _render_summary_box(self, article: Article) -> str:
        items = "\n".join(f"<li>{escape(item)}</li>" for item in article.summary_box_items)
        return (
            f"<!-- wp:group {{\"className\":\"summary-box\",\"backgroundColor\":\"pale-green\"}} -->\n"
            f"<div class=\"wp-block-group summary-box has-pale-green-background-color has-background\">\n"
            f"  <!-- wp:heading {{\"level\":3}} -->\n"
            f"  <h3 class=\"wp-block-heading\">{escape(article.summary_box_label)}</h3>\n"
            f"  <!-- /wp:heading -->\n"
            f"  <!-- wp:list -->\n"
            f"  <ul>{items}</ul>\n"
            f"  <!-- /wp:list -->\n"
            f"</div>\n"
            f"<!-- /wp:group -->"
        )

    def _render_block(self, block: ContentBlock) -> str:
        mapper = {
            "paragraph": (
                lambda b: f"<!-- wp:paragraph -->\n<p>{escape(b.content)}</p>\n<!-- /wp:paragraph -->"
            ),
            "heading": (
                lambda b: f"<!-- wp:heading {{\"level\":{b.level or 3}}} -->\n<h{b.level or 3} class=\"wp-block-heading\">{escape(b.content)}</h{b.level or 3}>\n<!-- /wp:heading -->"
            ),
            "list": (
                lambda b: "<!-- wp:list -->\n<ul class=\"wp-block-list\">\n"
                + "\n".join(f"<li>{escape(item)}</li>" for item in b.content.split("\n") if item.strip())
                + "\n</ul>\n<!-- /wp:list -->"
            ),
            "code": (
                lambda b: f"<!-- wp:code -->\n<pre class=\"wp-block-code\"><code>{escape(b.content)}</code></pre>\n<!-- /wp:code -->"
            ),
            "image": (
                lambda b: f"<!-- wp:image {{\"align\":\"center\"}} -->\n<figure class=\"wp-block-image aligncenter\"><img src=\"{escape(b.content)}\" alt=\"{escape(b.metadata.get('alt', ''))}\" /></figure>\n<!-- /wp:image -->"
            ),
            "chart": (
                lambda b: f"<!-- wp:html -->\n<figure>\n{b.content}\n<figcaption>{escape(b.metadata.get('caption', ''))}</figcaption>\n</figure>\n<!-- /wp:html -->"
            ),
            "video": (
                lambda b: f"<!-- wp:embed {{\"url\":\"{escape(b.content)}\"}} -->\n<figure class=\"wp-block-embed is-type-video\"><div class=\"wp-block-embed__wrapper\">\n{escape(b.content)}\n</div></figure>\n<!-- /wp:embed -->"
            ),
            "quote": (
                lambda b: f"<!-- wp:quote -->\n<blockquote class=\"wp-block-quote\"><p>{escape(b.content)}</p></blockquote>\n<!-- /wp:quote -->"
            ),
            "citation_capsule": (
                lambda b: f"<!-- wp:paragraph -->\n<p>{escape(b.content)}</p>\n<!-- /wp:paragraph -->"
            ),
            "info_gain_marker": (
                lambda b: f"<!-- {escape(b.content)} -->"
            ),
            "internal_link_zone": (
                lambda b: f"<!-- wp:paragraph -->\n<p>[Internal link: {escape(b.content)}]</p>\n<!-- /wp:paragraph -->"
            ),
            "table": (
                lambda b: f"<!-- wp:table -->\n<figure class=\"wp-block-table\"><table>{b.content}</table></figure>\n<!-- /wp:table -->"
            ),
            "html_embed": (
                lambda b: f"<!-- wp:html -->\n{b.content}\n<!-- /wp:html -->"
            ),
        }
        render_fn = mapper.get(block.type)
        return render_fn(block) if render_fn else f"<!-- wp:paragraph -->\n<p>{escape(block.content)}</p>\n<!-- /wp:paragraph -->"

    def _render_faq(self, article: Article) -> str:
        blocks = [
            "<!-- wp:heading -->",
            "<h2 class=\"wp-block-heading\">Frequently Asked Questions</h2>",
            "<!-- /wp:heading -->",
        ]
        for item in article.faq_items:
            blocks.extend([
                f"<!-- wp:heading {{\"level\":3}} -->",
                f"<h3 class=\"wp-block-heading\">{escape(item.question)}</h3>",
                f"<!-- /wp:heading -->",
                f"<!-- wp:paragraph -->",
                f"<p>{escape(item.answer)}</p>",
                f"<!-- /wp:paragraph -->",
            ])
        return "\n\n".join(blocks)

    def _render_cta(self, article: Article) -> str:
        return (
            f"<!-- wp:buttons -->\n"
            f"<div class=\"wp-block-buttons\">\n"
            f"  <!-- wp:button -->\n"
            f"  <div class=\"wp-block-button\"><a class=\"wp-block-button__link wp-element-button\">{escape(article.cta)}</a></div>\n"
            f"  <!-- /wp:button -->\n"
            f"</div>\n"
            f"<!-- /wp:buttons -->"
        )
