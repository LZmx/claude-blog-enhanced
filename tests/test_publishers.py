import json
import pytest
from canonical.schema import Article
from publishers.wordpress import WordPressPublisher, WordPressPayload


class TestWordPressPayload:
    def test_minimal_payload(self):
        payload = WordPressPayload(title="Test Post", content="<p>Hello</p>")
        d = payload.to_api_dict()
        assert d["title"] == "Test Post"
        assert d["content"] == "<p>Hello</p>"
        assert d["status"] == "draft"

    def test_full_payload(self):
        payload = WordPressPayload(
            title="Full Post",
            content="<p>Content</p>",
            status="publish",
            slug="full-post",
            excerpt="An excerpt",
            categories=[1, 2],
            tags=[3, 4],
            featured_media=42,
            date="2026-06-12T10:00:00",
        )
        d = payload.to_api_dict()
        assert d["slug"] == "full-post"
        assert d["categories"] == [1, 2]
        assert d["tags"] == [3, 4]
        assert d["date"] == "2026-06-12T10:00:00"

    def test_to_json(self):
        payload = WordPressPayload(title="JSON Test", content="<p>Test</p>")
        j = payload.to_json()
        parsed = json.loads(j)
        assert parsed["title"] == "JSON Test"


class TestWordPressPublisher:
    def test_build_payload_from_article(self):
        article = Article(
            title="WP Article",
            slug="wp-article",
            excerpt="WP excerpt",
            categories=["SEO", "AI"],
            tags=["seo", "ai", "rankings"],
            date="2026-06-12",
        )
        publisher = WordPressPublisher()
        payload = publisher.build_payload(article, "<p>Rendered content</p>")
        assert payload.title == "WP Article"
        assert payload.content == "<p>Rendered content</p>"
        assert payload.slug == "wp-article"

    def test_dry_run(self):
        article = Article(title="Dry Run Test", slug="dry-run")
        publisher = WordPressPublisher()
        payload = publisher.dry_run(article, "<p>Content</p>")
        assert payload.title == "Dry Run Test"

    def test_build_payload_with_category_map(self):
        article = Article(title="Mapped", slug="mapped", categories=["SEO"], tags=["ai"])
        publisher = WordPressPublisher()
        payload = publisher.build_payload(article, "<p>Content</p>", category_map={"SEO": 5}, tag_map={"ai": 10})
        assert payload.categories == [5]
        assert payload.tags == [10]

    def test_build_payload_with_platform_overrides(self):
        from canonical.schema import PlatformOverrides
        overrides = PlatformOverrides(wordpress_title="WP Title", wordpress_slug="wp-slug", wordpress_status="publish")
        article = Article(title="Original", slug="original", platform_overrides=overrides)
        publisher = WordPressPublisher()
        payload = publisher.build_payload(article, "<p>Content</p>")
        assert payload.title == "WP Title"
        assert payload.slug == "wp-slug"
        assert payload.status == "publish"

    def test_create_post_no_api_url(self):
        article = Article(title="No API", slug="no-api")
        publisher = WordPressPublisher()
        payload = publisher.build_payload(article, "<p>Content</p>")
        result = publisher.create_post(payload)
        assert "error" in result
        assert "not configured" in result["error"]
