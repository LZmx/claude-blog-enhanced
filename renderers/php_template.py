from __future__ import annotations
from html import escape
from canonical.schema import Article, ContentBlock
from renderers.base import BaseRenderer, RenderResult


class PHPTemplateRenderer(BaseRenderer):
    format_name = "php"
    description = "PHP template — for WordPress theme integration, custom template files"
    extension = "php"
    mime_type = "text/x-php"

    def render(self, article: Article) -> RenderResult:
        lines: list[str] = []
        lines.append("<?php")
        lines.append("/**")
        lines.append(" * Template: Article")
        lines.append(f" * Title: {article.title}")
        lines.append(f" * Slug: {article.slug}")
        lines.append(" */")
        lines.append("?>")
        lines.append("")
        lines.append("<article class=\"blog-post\">")
        lines.append("  <header class=\"post-header\">")
        lines.append("    <h1><?php echo esc_html( get_the_title() ?: '" + self._esc_php_str(article.title) + "' ); ?></h1>")
        if article.author:
            lines.append(f"    <p class=\"byline\"><?php esc_html_e( 'By', 'textdomain' ); ?> {escape(article.author)}</p>")
        if article.date:
            lines.append(f"    <time datetime=\"{article.date}\"><?php echo get_the_date(); ?></time>")
        lines.append("  </header>")
        if article.summary_box_items:
            lines.append(self._render_summary_box(article))
        for section in article.sections:
            lines.append(self._render_section(section))
        if article.faq_items:
            lines.append(self._render_faq(article))
        if article.cta:
            lines.append(self._render_cta(article))
        lines.append("</article>")
        return self._result("\n".join(lines) + "\n", article)

    def _esc_php_str(self, s: str) -> str:
        return s.replace("'", "\\'")

    def _render_summary_box(self, article: Article) -> str:
        items = "\n".join(f"      <li><?php echo esc_html( '{self._esc_php_str(item)}' ); ?></li>" for item in article.summary_box_items)
        return (
            f"  <div class=\"summary-box\">\n"
            f"    <h3>{escape(article.summary_box_label)}</h3>\n"
            f"    <ul>\n{items}\n    </ul>\n"
            f"  </div>"
        )

    def _render_section(self, section) -> str:
        lines: list[str] = []
        tag = f"h{section.heading_level}"
        lines.append(f"  <section id=\"{self._esc_php_str(section.heading.lower().replace(' ', '-'))}\">")
        wp_heading = f"<?php echo esc_html( get_sub_field( '{self._esc_php_str(section.heading)}' ) ?: '{self._esc_php_str(section.heading)}' ); ?>"
        lines.append(f"    <{tag}>{wp_heading}</{tag}>")
        for block in section.blocks:
            rendered = self._render_block(block)
            if rendered:
                lines.append(rendered)
        lines.append("  </section>")
        return "\n".join(lines)

    def _render_block(self, block: ContentBlock) -> str:
        mapper = {
            "paragraph": lambda b: f"    <p><?php echo esc_html( '{self._esc_php_str(b.content)}' ); ?></p>",
            "heading": lambda b: f"    <h{b.level or 3}><?php echo esc_html( '{self._esc_php_str(b.content)}' ); ?></h{b.level or 3}>",
            "list": lambda b: "    <ul>\n" + "\n".join(f"      <li><?php echo esc_html( '{self._esc_php_str(item)}' ); ?></li>" for item in b.content.split("\n") if item.strip()) + "\n    </ul>",
            "code": lambda b: f"    <pre><code><?php echo esc_html( '{self._esc_php_str(b.content)}' ); ?></code></pre>",
            "image": lambda b: f"    <figure><img src=\"<?php echo esc_url( '{self._esc_php_str(b.content)}' ); ?>\" alt=\"{escape(b.metadata.get('alt', ''))}\" /></figure>",
            "chart": lambda b: f"    <figure>\n{b.content}\n    <figcaption>{escape(b.metadata.get('caption', ''))}</figcaption>\n    </figure>",
            "video": lambda b: f"    <figure><iframe src=\"<?php echo esc_url( '{self._esc_php_str(b.content)}' ); ?>\" title=\"{escape(b.metadata.get('title', ''))}\" loading=\"lazy\"></iframe></figure>",
            "quote": lambda b: f"    <blockquote><p><?php echo esc_html( '{self._esc_php_str(b.content)}' ); ?></p></blockquote>",
            "citation_capsule": lambda b: f"    <p><?php echo esc_html( '{self._esc_php_str(b.content)}' ); ?></p>",
            "info_gain_marker": lambda b: f"    <!-- {escape(b.content)} -->",
            "internal_link_zone": lambda b: f"    <p class=\"internal-link\">[Internal: {escape(b.content)}]</p>",
            "table": lambda b: f"    {b.content}",
            "html_embed": lambda b: f"    {b.content}",
        }
        render_fn = mapper.get(block.type)
        return render_fn(block) if render_fn else f"    <p><?php echo esc_html( '{self._esc_php_str(block.content)}' ); ?></p>"

    def _render_faq(self, article: Article) -> str:
        parts = ["  <section id=\"faq\" class=\"post-faq\">", "    <h2>Frequently Asked Questions</h2>"]
        for item in article.faq_items:
            parts.extend([
                f"    <div itemscope=\"\" itemprop=\"mainEntity\" itemtype=\"https://schema.org/Question\">",
                f"      <h3 itemprop=\"name\"><?php echo esc_html( '{self._esc_php_str(item.question)}' ); ?></h3>",
                f"      <div itemscope=\"\" itemprop=\"acceptedAnswer\" itemtype=\"https://schema.org/Answer\">",
                f"        <p itemprop=\"text\"><?php echo esc_html( '{self._esc_php_str(item.answer)}' ); ?></p>",
                f"      </div>",
                f"    </div>",
            ])
        parts.append("  </section>")
        return "\n".join(parts)

    def _render_cta(self, article: Article) -> str:
        return f"  <div class=\"post-cta\"><p><?php echo esc_html( '{self._esc_php_str(article.cta)}' ); ?></p></div>"
