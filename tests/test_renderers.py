import json
import pytest
from canonical.schema import Article, ArticleSection, ContentBlock, FAQItem, Citation
from canonical.builder import ArticleBuilder
from renderers.registry import get_renderer, list_renderers, render_article, _resolve_format_alias


@pytest.fixture
def sample_article():
    builder = ArticleBuilder.from_topic("AI SEO Trends 2026", "ai-seo-trends-2026")
    builder.with_excerpt("How AI is transforming SEO in 2026")
    builder.with_summary_box("Key Takeaways", [
        "AI overviews appear in 58% of searches (Search Engine Land, 2026)",
        "E-E-A-T signals are now required for AI citation ranking",
        "Content freshness within 30 days improves AI citation rate by 40%",
    ])
    builder.with_keyword("AI SEO trends", ["artificial intelligence SEO", "SEO 2026 trends"])
    builder.with_author("Jane Doe")
    builder.with_meta("AI SEO Trends 2026: What Changes for Rankings", "AI overviews appear in 58% of searches. Learn how to optimize for both Google rankings and AI citations in 2026.")
    builder.with_image("https://example.com/cover.jpg", "AI SEO trends illustration")
    builder.with_dates("2026-06-12")
    builder.with_canonical("https://example.com/ai-seo-trends-2026")
    builder.with_categories_tags(["SEO", "AI", "Digital Marketing"], ["ai seo", "seo trends", "ai citations"])
    builder.with_schema({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": "AI SEO Trends 2026",
    })
    builder.add_citation("58% of searches show AI overviews", "Search Engine Land", "https://searchengineland.com", "2026")
    builder.add_citation("73% of users click AI-assisted results", "Gartner", "https://gartner.com", "2026")
    builder.add_faq("What is AI SEO?", "AI SEO means optimizing content for both traditional search engines and AI assistants like ChatGPT, Perplexity, and Google AI Overviews.")
    builder.add_faq("How do I optimize for AI citations?", "Use answer-first formatting, include citation capsules with sourced statistics, and maintain a 30-day freshness update cycle.")

    section = builder.add_section("How AI Overviews Changed Search Results", 2)
    section.add("paragraph", "In 2026, AI overviews have fundamentally reshaped the search landscape. According to Search Engine Land, 58% of all searches now display an AI-generated overview before any organic result.")
    section.add("citation_capsule", "According to a 2026 Search Engine Land study, 58% of searches now display AI overviews, reducing traditional organic CTR by 61% for position-one results.")
    section.add("info_gain_marker", "ORIGINAL DATA")
    section.add("internal_link_zone", "complete guide to AI citation optimization → reference doc on AI citation readiness scoring")

    section2 = builder.add_section("E-E-A-T Signals for AI Ranking", 2)
    section2.add("paragraph", "Experience, expertise, authoritativeness, and trustworthiness remain critical. Gartner reports 73% of enterprise buyers now consult AI assistants before contacting vendors.")
    section2.add("chart", "<svg viewBox=\"0 0 560 380\"><text>AI Overview Growth 2024-2026</text></svg>", metadata={"caption": "Search Engine Land, 2026"})

    section3 = builder.add_section("Content Freshness Requirements", 2)
    section3.add("paragraph", "AI citation platforms prioritize recently updated content. Posts updated within 30 days of a query see 40% higher citation rates.")
    section3.add("list", "Update statistics quarterly\nRefresh examples annually\nReview internal links monthly")
    section3.add("code", "const freshnessCheck = (post) => { return post.lastUpdated > Date.now() - 30 * 86400000; }", metadata={"language": "javascript"})

    return builder.build()


class TestRendererRegistry:
    def test_list_renderers(self):
        renderers = list_renderers()
        formats = [r["format"] for r in renderers]
        assert "markdown" in formats
        assert "mdx" in formats
        assert "html" in formats
        assert "wordpress" in formats
        assert "wordpress-blocks" in formats
        assert "php" in formats

    def test_alias_resolution(self):
        assert _resolve_format_alias("markdown") == "markdown"
        assert _resolve_format_alias("md") == "markdown"
        assert _resolve_format_alias("html") == "html"
        assert _resolve_format_alias("generic-html") == "html"
        assert _resolve_format_alias("wordpress") == "wordpress"
        assert _resolve_format_alias("wordpress-classic") == "wordpress"
        assert _resolve_format_alias("wp") == "wordpress"
        assert _resolve_format_alias("php") == "php"
        assert _resolve_format_alias("php-template") == "php"


class TestMarkdownRenderer:
    def test_render_minimal(self):
        article = Article(title="Minimal", slug="minimal")
        renderer = get_renderer("markdown")
        result = renderer.render(article)
        assert "Minimal" in result.content
        assert result.content.startswith("---")

    def test_render_full_article(self, sample_article):
        renderer = get_renderer("markdown")
        result = renderer.render(sample_article)
        content = result.content
        assert "---" in content
        assert "AI SEO Trends 2026" in content
        assert "Key Takeaways" in content
        assert "## How AI Overviews Changed Search Results" in content
        assert "## E-E-A-T Signals for AI Ranking" in content
        assert "## Content Freshness Requirements" in content
        assert "## Frequently Asked Questions" in content
        assert "## Sources" in content
        assert "58%" in content
        assert "```javascript" in content
        assert result.extension == "md"

    def test_render_summary_box(self, sample_article):
        renderer = get_renderer("markdown")
        result = renderer.render(sample_article)
        assert "> **Key Takeaways**" in result.content
        assert "-" in result.content.split("Key Takeaways")[1].split("\n")[1]


class TestMDXRenderer:
    def test_render_full_article(self, sample_article):
        renderer = get_renderer("mdx")
        result = renderer.render(sample_article)
        content = result.content
        assert "---" in content
        assert "AI SEO Trends 2026" in content
        assert "<Callout type=\"summary\">" in content
        assert "Key Takeaways" in content
        assert "## How AI Overviews Changed Search Results" in content
        assert result.extension == "mdx"


class TestGenericHTMLRenderer:
    def test_render_full_article(self, sample_article):
        renderer = get_renderer("html")
        result = renderer.render(sample_article)
        content = result.content
        assert "<!DOCTYPE html>" in content
        assert "<html lang=\"en\">" in content
        assert "<article>" in content
        assert "<h1>AI SEO Trends 2026</h1>" in content
        assert "<h2>How AI Overviews Changed Search Results</h2>" in content
        assert "class=\"summary-box\"" in content
        assert "application/ld+json" in content
        assert result.extension == "html"

    def test_render_body_only(self, sample_article):
        renderer = get_renderer("html")
        body = renderer.render_body_only(sample_article)
        assert "<h1>AI SEO Trends 2026</h1>" in body
        assert "<!DOCTYPE html>" not in body


class TestWordPressClassicRenderer:
    def test_render_full_article(self, sample_article):
        renderer = get_renderer("wordpress")
        result = renderer.render(sample_article)
        content = result.content
        assert "<!-- wp:post-content -->" in content
        assert "<!-- wp:group" in content
        assert "class=\"summary-box\"" in content
        assert "<!-- wp:heading" in content
        assert "<h2>How AI Overviews Changed Search Results</h2>" in content
        assert "<!-- /wp:post-content -->" in content
        assert result.extension == "wp.html"

    def test_no_markdown_remnants(self, sample_article):
        renderer = get_renderer("wordpress")
        result = renderer.render(sample_article)
        assert "---" not in result.content
        assert "[INTERNAL-LINK:" not in result.content  # Should be rendered as WP paragraph


class TestWordPressBlocksRenderer:
    def test_render_full_article(self, sample_article):
        renderer = get_renderer("wordpress-blocks")
        result = renderer.render(sample_article)
        content = result.content
        assert "<!-- wp:heading" in content
        assert "class=\"wp-block-heading\"" in content
        assert "<!-- wp:group" in content
        assert "has-pale-green-background-color" in content
        assert result.extension == "blocks.html"


class TestPHPRenderer:
    def test_render_full_article(self, sample_article):
        renderer = get_renderer("php")
        result = renderer.render(sample_article)
        content = result.content
        assert "<?php" in content
        assert "?>" in content
        assert "esc_html" in content
        assert "<article class=\"blog-post\">" in content
        assert "get_the_title" in content
        assert result.extension == "php"

    def test_escaped_output(self, sample_article):
        renderer = get_renderer("php")
        result = renderer.render(sample_article)
        assert "esc_html" in result.content


class TestRenderArticle:
    def test_render_article_function(self, sample_article):
        result = render_article(sample_article, "markdown")
        assert "AI SEO Trends 2026" in result.content
        assert result.extension == "md"

    def test_render_all_formats(self, sample_article):
        for fmt in ["markdown", "mdx", "html", "wordpress", "wordpress-blocks", "php"]:
            result = render_article(sample_article, fmt)
            assert result.content
            assert len(result.content) > 50

    def test_render_unknown_format(self):
        article = Article(title="Test", slug="test")
        with pytest.raises(ValueError, match="Unknown renderer"):
            render_article(article, "unknown-format")
