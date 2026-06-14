"""
End-to-end test: build an article with the builder, render it in all 6 formats,
validate each output, and verify format-specific rules.
"""
import pytest
from canonical.builder import ArticleBuilder
from renderers.registry import render_article, list_renderers
from validators.base import validate_output


@pytest.fixture
def full_article():
    builder = ArticleBuilder.from_topic(
        "The Complete Guide to AI Citation Optimization in 2026",
        "ai-citation-optimization-guide",
    )
    builder.with_excerpt("A comprehensive guide to optimizing content for AI citation platforms including ChatGPT, Perplexity, and Google AI Overviews.")
    builder.with_summary_box("Key Takeaways", [
        "AI citations increase content visibility by 3.2x across ChatGPT, Perplexity, and Gemini (BrightEdge, 2026)",
        "Content with answer-first formatting sees 2.7x higher AI citation rates",
        "30-day freshness updates improve AI citation probability by 40%",
    ])
    builder.with_keyword("AI citation optimization", ["GEO optimization", "AI content visibility", "answer engine optimization"])
    builder.with_author("Dr. Sarah Chen")
    builder.with_meta("AI Citation Optimization Guide 2026: Complete Strategy for GEO",
                     "Learn how to optimize content for AI citations. Data-driven strategies for ChatGPT, Perplexity, and Google AI Overviews visibility in 2026.")
    builder.with_image("https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200", "AI citation optimization concept")
    builder.with_dates("2026-06-12", "2026-06-12")
    builder.with_canonical("https://example.com/ai-citation-optimization")
    builder.with_schema({
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": "AI Citation Optimization Guide 2026",
        "description": "Complete guide to optimizing content for AI citations",
    })
    builder.with_categories_tags(["SEO", "AI", "Content Marketing"], ["ai citations", "geo", "content optimization"])
    builder.with_cta("Download our AI Citation Readiness Checklist")
    builder.add_citation("Content with citation capsules sees 3.2x more AI citations", "BrightEdge", "https://brightedge.com", "2026")
    builder.add_citation("73% of enterprise buyers consult AI before purchase", "Gartner", "https://gartner.com", "2026")
    builder.add_citation("Answer-first format improves AI extraction by 2.7x", "Search Engine Land", "https://searchengineland.com", "2026")

    sec1 = builder.add_section("What Is AI Citation Optimization?", 2)
    sec1.add("paragraph", "AI citation optimization, also known as Generative Engine Optimization (GEO), is the practice of structuring content so AI assistants like ChatGPT, Perplexity, and Google AI Overviews can easily extract, cite, and recommend it in their responses.")
    sec1.add("citation_capsule", "AI citation optimization (GEO) is the practice of structuring content for AI assistant extraction. According to BrightEdge (2026), content optimized with citation capsules sees 3.2x more AI citations than unoptimized content.")

    sec2 = builder.add_section("The 5 Pillars of AI Citation Readiness", 2)
    sec2.add("paragraph", "Our research identifies five key pillars that determine whether an AI system will cite your content. Each pillar maps to a specific scoring criterion in our quality framework.")
    sec2.add("list", "Answer-First Formatting with sourced statistics\nCitation Capsules for direct AI extraction\nInformation Gain Markers signaling original value\nTechnical Accessibility (schema, crawlability)\nFreshness Signals with regular updates")

    sec3 = builder.add_section("Measuring Your AI Citation Score", 2)
    sec3.add("paragraph", "We developed a standardized 100-point scoring system for AI citation readiness. Here is how the scores break down:")
    sec3.add("chart", "<svg viewBox=\"0 0 560 380\"><rect x=\"50\" y=\"200\" width=\"60\" height=\"120\" fill=\"#4CAF50\"/><text x=\"80\" y=\"190\">30</text><rect x=\"160\" y=\"160\" width=\"60\" height=\"160\" fill=\"#2196F3\"/><text x=\"190\" y=\"150\">25</text><rect x=\"270\" y=\"240\" width=\"60\" height=\"80\" fill=\"#FF9800\"/><text x=\"300\" y=\"230\">15</text><rect x=\"380\" y=\"240\" width=\"60\" height=\"80\" fill=\"#9C27B0\"/><text x=\"410\" y=\"230\">15</text><rect x=\"490\" y=\"240\" width=\"60\" height=\"80\" fill=\"#E91E63\"/><text x=\"520\" y=\"230\">15</text></svg>", metadata={"caption": "AI Citation Readiness scoring breakdown by category"})

    builder.add_faq("How long does it take to optimize for AI citations?",
                    "Most content can be optimized for AI citations in 30-60 minutes by adding citation capsules, answer-first formatting, and schema markup. Full GEO optimization typically takes 2-4 hours per article.")
    builder.add_faq("Does AI citation optimization help Google rankings too?",
                    "Yes. The same signals that help AI citation (answer-first formatting, sourced statistics, fresh content, clear structure) also align with Google's December 2025 Core Update emphasis on E-E-A-T and original value.")

    return builder.build()


class TestEndToEndFormatPipeline:
    def test_all_formats_produce_content(self, full_article):
        formats = ["markdown", "mdx", "html", "wordpress", "wordpress-blocks", "php"]
        results = {}
        for fmt in formats:
            result = render_article(full_article, fmt)
            assert result.content
            assert len(result.content) > 100
            results[fmt] = result
        assert results["markdown"].content != results["html"].content

    def test_markdown_has_frontmatter(self, full_article):
        result = render_article(full_article, "markdown")
        assert result.content.startswith("---")
        assert "title:" in result.content.split("---")[1]

    def test_html_has_doctype(self, full_article):
        result = render_article(full_article, "html")
        assert "<!DOCTYPE html>" in result.content
        assert "<html" in result.content

    def test_wordpress_has_block_comments(self, full_article):
        result = render_article(full_article, "wordpress")
        assert "<!-- wp:" in result.content

    def test_wordpress_blocks_has_class_names(self, full_article):
        result = render_article(full_article, "wordpress-blocks")
        assert "wp-block-heading" in result.content
        assert "wp-block-list" in result.content
        assert "wp-block-buttons" in result.content

    def test_php_has_escaping(self, full_article):
        result = render_article(full_article, "php")
        assert "esc_html" in result.content

    def test_mdx_has_callout(self, full_article):
        result = render_article(full_article, "mdx")
        assert "<Callout type=\"summary\">" in result.content


class TestValidatorIntegration:
    def test_markdown_passes_validation(self, full_article):
        result = render_article(full_article, "markdown")
        v = validate_output(result.content, "markdown")
        assert v.valid

    def test_html_passes_validation(self, full_article):
        result = render_article(full_article, "html")
        v = validate_output(result.content, "html")
        assert v.valid

    def test_wordpress_passes_validation(self, full_article):
        result = render_article(full_article, "wordpress")
        v = validate_output(result.content, "wordpress")
        assert v.valid

    def test_wordpress_blocks_passes_validation(self, full_article):
        result = render_article(full_article, "wordpress-blocks")
        v = validate_output(result.content, "wordpress-blocks")
        assert v.valid

    def test_php_passes_validation(self, full_article):
        result = render_article(full_article, "php")
        v = validate_output(result.content, "php")
        assert v.valid


class TestFormatUniqueness:
    def test_markdown_vs_html_different(self, full_article):
        md = render_article(full_article, "markdown").content
        html = render_article(full_article, "html").content
        assert md != html
        assert md.startswith("---")
        assert not html.startswith("---")

    def test_wordpress_vs_generic_html_different(self, full_article):
        html = render_article(full_article, "html").content
        wp = render_article(full_article, "wordpress").content
        assert html != wp
        assert "<!-- wp:" in wp

    def test_mdx_vs_markdown_different_summary_boxes(self, full_article):
        md = render_article(full_article, "markdown").content
        mdx = render_article(full_article, "mdx").content
        assert "> **Key Takeaways**" in md
        assert "<Callout type=\"summary\">" in mdx
