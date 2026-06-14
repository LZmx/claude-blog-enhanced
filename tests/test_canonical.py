import json
import tempfile
from pathlib import Path
from canonical.schema import Article, ArticleSection, ContentBlock, FAQItem, Citation
from canonical.builder import ArticleBuilder
from canonical.output import save_canonical, save_metadata, save_schema, save_all_artifacts


class TestArticleSchema:
    def test_create_empty_article(self):
        article = Article(title="Test Post", slug="test-post")
        assert article.title == "Test Post"
        assert article.slug == "test-post"
        assert article.status == "draft"
        assert article.sections == []
        assert article.summary_box_items == []

    def test_article_with_sections(self):
        section = ArticleSection(heading="Introduction", heading_level=2)
        section.add("paragraph", "Hello world")
        article = Article(title="Test", slug="test", sections=[section])
        assert len(article.sections) == 1
        assert article.sections[0].blocks[0].content == "Hello world"

    def test_article_to_dict_roundtrip(self):
        article = Article(
            title="Original",
            slug="original",
            excerpt="An excerpt",
            target_keyword="test",
            secondary_keywords=["test2", "test3"],
            author="Tester",
        )
        d = article.to_dict()
        restored = Article.from_dict(d)
        assert restored.title == "Original"
        assert restored.slug == "original"
        assert restored.target_keyword == "test"
        assert restored.secondary_keywords == ["test2", "test3"]

    def test_article_with_faq_items(self):
        article = Article(
            title="FAQ Post",
            slug="faq-post",
            faq_items=[FAQItem(question="Q1?", answer="A1"), FAQItem(question="Q2?", answer="A2")],
        )
        d = article.to_dict()
        restored = Article.from_dict(d)
        assert len(restored.faq_items) == 2
        assert restored.faq_items[0].question == "Q1?"

    def test_article_with_citations(self):
        article = Article(
            title="Cited Post",
            slug="cited-post",
            citations=[Citation(statistic="58%", source_name="Gartner", source_url="https://gartner.com", year="2026")],
        )
        d = article.to_dict()
        restored = Article.from_dict(d)
        assert len(restored.citations) == 1
        assert restored.citations[0].source_name == "Gartner"


class TestArticleBuilder:
    def test_builder_minimal(self):
        article = ArticleBuilder.from_topic("Hello World").build()
        assert article.title == "Hello World"
        assert article.slug == "hello-world"

    def test_builder_full_flow(self):
        builder = ArticleBuilder.from_topic("How AI Changes SEO", "ai-seo-changes")
        builder.with_excerpt("AI is transforming SEO")
        builder.with_summary_box("Key Takeaways", ["AI changes rankings", "Focus on E-E-A-T"])
        builder.with_keyword("AI SEO", ["artificial intelligence SEO", "SEO AI tools"])
        builder.with_author("Jane Doe")
        builder.with_meta("AI SEO Guide 2026", "How AI changes SEO in 2026")
        builder.with_image("https://example.com/image.jpg", "AI SEO", "https://example.com/og.jpg")
        builder.with_dates("2026-06-01")
        builder.with_canonical("https://example.com/ai-seo")
        builder.with_cta("Subscribe for more AI SEO tips")
        builder.with_categories_tags(["SEO", "AI"], ["seo", "ai", "rankings"])
        builder.add_citation("73% of searches use AI", "Search Engine Land", "https://searchengineland.com", "2026")

        section = builder.add_section("How AI Changes Search Results", 2)
        section.add("paragraph", "AI is reshaping how users find information.")
        section.add("citation_capsule", "According to a 2026 study, 73% of searches now involve AI.")

        builder.add_faq("What is AI SEO?", "AI SEO is search optimization for AI assistants.")

        article = builder.build()
        assert article.title == "How AI Changes SEO"
        assert len(article.sections) == 1
        assert article.sections[0].blocks[0].content == "AI is reshaping how users find information."
        assert len(article.faq_items) == 1
        assert len(article.citations) == 1

    def test_builder_slug_generation(self):
        article = ArticleBuilder.from_topic("What's New in AI?").build()
        assert article.slug == "whats-new-in-ai"

    def test_builder_fluent_api(self):
        section = ArticleBuilder.from_topic("Test").add_section("Intro", 2)
        section.add("paragraph", "Para 1").add("paragraph", "Para 2")
        article = ArticleBuilder.from_topic("Test").build()
        article.sections.append(section)
        assert len(article.sections) == 1
        assert len(article.sections[0].blocks) == 2
        assert section.blocks[0].content == "Para 1"
        assert section.blocks[1].content == "Para 2"


class TestOutput:
    def test_save_canonical(self, tmp_path):
        article = Article(title="Save Test", slug="save-test")
        path = save_canonical(article, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["title"] == "Save Test"

    def test_save_metadata(self, tmp_path):
        article = Article(title="Meta Test", slug="meta-test", author="Me")
        path = save_metadata(article, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["title"] == "Meta Test"
        assert data["author"] == "Me"

    def test_save_schema(self, tmp_path):
        article = Article(title="Schema Test", slug="schema-test")
        path = save_schema(article, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["@type"] == "BlogPosting"
        assert data["headline"] == "Schema Test"

    def test_save_all_artifacts(self, tmp_path):
        article = Article(title="All Artifacts", slug="all-artifacts")
        rendered = {"markdown": "# Hello"}
        artifacts = save_all_artifacts(article, rendered, tmp_path)
        assert "post.json" in artifacts
        assert "metadata.json" in artifacts
        assert "schema.json" in artifacts
        assert "markdown" in artifacts
        assert Path(artifacts["post.json"]).exists()
        assert Path(artifacts["markdown"]).exists()
