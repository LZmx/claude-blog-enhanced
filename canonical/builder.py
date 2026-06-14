from __future__ import annotations
from canonical.schema import Article, ArticleSection, ContentBlock, Citation, FAQItem, BlockType


class ArticleBuilder:
    _article: Article

    def __init__(self, title: str, slug: str):
        self._article = Article(title=title, slug=slug)

    @classmethod
    def from_topic(cls, topic: str, slug: str = "") -> ArticleBuilder:
        if not slug:
            slug = topic.lower().replace(" ", "-").replace("'", "").replace('"', "")
            import re
            slug = re.sub(r"[^a-z0-9-]", "", slug)
        return cls(title=topic, slug=slug)

    def with_excerpt(self, excerpt: str) -> ArticleBuilder:
        self._article.excerpt = excerpt
        return self

    def with_summary(self, summary: str) -> ArticleBuilder:
        self._article.summary = summary
        return self

    def with_summary_box(self, label: str, items: list[str]) -> ArticleBuilder:
        self._article.summary_box_label = label
        self._article.summary_box_items = items
        return self

    def with_keyword(self, keyword: str, secondary: list[str] | None = None) -> ArticleBuilder:
        self._article.target_keyword = keyword
        if secondary:
            self._article.secondary_keywords = secondary
        return self

    def with_author(self, author: str) -> ArticleBuilder:
        self._article.author = author
        return self

    def with_meta(self, meta_title: str, meta_description: str) -> ArticleBuilder:
        self._article.meta_title = meta_title
        self._article.meta_description = meta_description
        return self

    def with_image(self, url: str, alt: str = "", og_url: str = "") -> ArticleBuilder:
        self._article.featured_image = url
        self._article.featured_image_alt = alt or ""
        self._article.og_image = og_url or url
        return self

    def with_dates(self, date: str, last_updated: str = "") -> ArticleBuilder:
        self._article.date = date
        self._article.last_updated = last_updated or date
        return self

    def with_canonical(self, url: str) -> ArticleBuilder:
        self._article.canonical_url = url
        return self

    def add_section(self, heading: str, heading_level: int = 2) -> ArticleSection:
        section = ArticleSection(heading=heading, heading_level=heading_level)
        self._article.sections.append(section)
        return section

    def add_faq(self, question: str, answer: str) -> ArticleBuilder:
        self._article.faq_items.append(FAQItem(question=question, answer=answer))
        return self

    def add_citation(self, statistic: str, source_name: str, source_url: str, year: str) -> ArticleBuilder:
        self._article.citations.append(
            Citation(statistic=statistic, source_name=source_name, source_url=source_url, year=year)
        )
        return self

    def with_cta(self, cta: str) -> ArticleBuilder:
        self._article.cta = cta
        return self

    def with_schema(self, schema: dict) -> ArticleBuilder:
        self._article.schema_json_ld = schema
        return self

    def with_template(self, name: str) -> ArticleBuilder:
        self._article.template_name = name
        return self

    def with_language(self, lang: str, translated_from: str = "", translated_date: str = "") -> ArticleBuilder:
        self._article.language = lang
        self._article.translated_from = translated_from
        self._article.translated_date = translated_date
        return self

    def with_categories_tags(self, categories: list[str], tags: list[str]) -> ArticleBuilder:
        self._article.categories = categories
        self._article.tags = tags
        return self

    def build(self) -> Article:
        return self._article
