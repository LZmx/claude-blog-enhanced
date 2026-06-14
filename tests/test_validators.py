import pytest
from validators.base import validate_output, list_validators
from validators.markdown import validate_markdown
from validators.html import validate_html, validate_wordpress, validate_wordpress_blocks, validate_php


class TestMarkdownValidator:
    def test_valid_markdown(self):
        content = "---\ntitle: Test\n---\n\n# Hello\n\nSome paragraph content."
        result = validate_markdown(content)
        assert result.valid

    def test_invalid_frontmatter(self):
        content = "---\ntitle: Test\n\n# Hello\n\nNo closing frontmatter."
        result = validate_markdown(content)
        assert not result.valid
        assert any("Unclosed" in e for e in result.errors)

    def test_unbalanced_code_fences(self):
        content = "---\ntitle: Test\n---\n\n```python\ncode block\n"
        result = validate_markdown(content)
        assert not result.valid
        assert any("Unbalanced" in e for e in result.errors)

    def test_heading_hierarchy_warning(self):
        content = "---\ntitle: Test\n---\n\n# H1\n\n### H3 (skipping H2)"
        result = validate_markdown(content)
        assert result.valid
        assert any("skipped" in w for w in result.warnings)

    def test_no_frontmatter_warning(self):
        content = "# Hello\n\nJust some content."
        result = validate_markdown(content)
        assert any("No YAML frontmatter" in w for w in result.warnings)


class TestHTMLValidator:
    def test_valid_html(self):
        content = "<!DOCTYPE html>\n<html><head><title>Test</title></head><body><article><h1>Hello</h1></article></body></html>"
        result = validate_html(content)
        assert result.valid

    def test_markdown_remnants(self):
        content = "<html><body>\n[Link text](http://example.com)\n</body></html>"
        result = validate_html(content)
        assert any("Markdown inline link" in w for w in result.warnings)

    def test_no_body_warning(self):
        content = "<h1>No HTML wrapper at all</h1>"
        result = validate_html(content)
        assert any("body" in w.lower() or "fragment" in w.lower() for w in result.warnings)


class TestWordPressValidator:
    def test_valid_wordpress(self):
        content = "<!-- wp:paragraph -->\n<p>Hello WordPress</p>\n<!-- /wp:paragraph -->"
        result = validate_wordpress(content)
        assert result.valid

    def test_markdown_remnants_are_errors(self):
        content = "<!-- wp:paragraph -->\n<p>Hello</p>\n<!-- /wp:paragraph -->\n---\n"
        result = validate_wordpress(content)
        assert not result.valid
        assert any("YAML" in e for e in result.errors)


class TestWordPressBlocksValidator:
    def test_balanced_blocks(self):
        content = "<!-- wp:paragraph -->\n<p>Hello</p>\n<!-- /wp:paragraph -->\n\n<!-- wp:heading -->\n<h2>Title</h2>\n<!-- /wp:heading -->"
        result = validate_wordpress_blocks(content)
        assert result.valid

    def test_unbalanced_blocks(self):
        content = "<!-- wp:paragraph -->\n<p>Hello</p>\n"
        result = validate_wordpress_blocks(content)
        assert not result.valid
        assert any("Unbalanced" in e for e in result.errors)


class TestPHPValidator:
    def test_valid_php(self):
        content = "<?php\n/** Template */\n?>\n<h1><?php echo esc_html( 'Hello' ); ?></h1>"
        result = validate_php(content)
        assert result.valid

    def test_no_php_tag(self):
        content = "<html><body>Hello</body></html>"
        result = validate_php(content)
        assert not result.valid
        assert any("<?php" in e for e in result.errors)

    def test_no_escaping_warning(self):
        content = "<?php echo 'Hello'; ?>"
        result = validate_php(content)
        assert result.valid
        assert any("No escaping" in w for w in result.warnings)


class TestValidateOutput:
    def test_validate_markdown(self):
        result = validate_output("---\ntitle: Test\n---\n\n# Content", "markdown")
        assert result.format_name == "markdown"

    def test_validate_html(self):
        result = validate_output("<html><body><p>Hi</p></body></html>", "html")
        assert result.format_name == "html"

    def test_validate_wordpress(self):
        result = validate_output("<!-- wp:paragraph -->\n<p>Hi</p>\n<!-- /wp:paragraph -->", "wordpress")
        assert result.format_name == "wordpress"

    def test_validate_unknown(self):
        with pytest.raises(ValueError):
            validate_output("test", "unknown-format")

    def test_list_validators(self):
        validators = list_validators()
        assert "markdown" in validators
        assert "html" in validators
        assert "wordpress" in validators
        assert "wordpress-blocks" in validators
        assert "php" in validators
