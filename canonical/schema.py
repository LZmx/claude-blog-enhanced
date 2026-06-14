from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional
from enum import Enum


BlockType = Literal[
    "paragraph",
    "heading",
    "list",
    "code",
    "image",
    "chart",
    "video",
    "quote",
    "faq_section",
    "cta",
    "citation_capsule",
    "info_gain_marker",
    "internal_link_zone",
    "summary_box",
    "table",
    "html_embed",
]


@dataclass
class ContentBlock:
    type: BlockType
    content: str
    level: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class Citation:
    statistic: str
    source_name: str
    source_url: str
    year: str
    methodology: str = ""


@dataclass
class FAQItem:
    question: str
    answer: str


@dataclass
class ReviewScore:
    category: str
    score: float
    max_score: float
    notes: str = ""


@dataclass
class DeliveryContractData:
    iteration_count: int = 0
    preflight_report: dict = field(default_factory=dict)
    nonce: str = ""


@dataclass
class PlatformOverrides:
    wordpress_title: str = ""
    wordpress_excerpt: str = ""
    wordpress_slug: str = ""
    wordpress_status: str = "draft"
    html_title: str = ""
    html_meta_robots: str = ""
    mdx_imports: list[str] = field(default_factory=list)


@dataclass
class ArticleSection:
    heading: str
    heading_level: int = 2
    blocks: list[ContentBlock] = field(default_factory=list)

    def add(self, block_type: BlockType, content: str, level: int = 0, metadata: dict | None = None) -> ArticleSection:
        self.blocks.append(ContentBlock(type=block_type, content=content, level=level, metadata=metadata or {}))
        return self


@dataclass
class Article:
    title: str
    slug: str
    excerpt: str = ""
    summary: str = ""
    summary_box_label: str = "Key Takeaways"
    summary_box_items: list[str] = field(default_factory=list)
    target_keyword: str = ""
    secondary_keywords: list[str] = field(default_factory=list)
    author: str = ""
    status: str = "draft"
    categories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    meta_title: str = ""
    meta_description: str = ""
    canonical_url: str = ""
    featured_image: str = ""
    featured_image_alt: str = ""
    og_image: str = ""
    date: str = ""
    last_updated: str = ""
    schema_json_ld: dict = field(default_factory=dict)
    sections: list[ArticleSection] = field(default_factory=list)
    faq_items: list[FAQItem] = field(default_factory=list)
    cta: str = ""
    internal_link_suggestions: list[str] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    review_scores: list[ReviewScore] = field(default_factory=list)
    delivery_contract: DeliveryContractData = field(default_factory=DeliveryContractData)
    platform_overrides: PlatformOverrides = field(default_factory=PlatformOverrides)
    word_count_target: int = 0
    reading_time_minutes: int = 0
    template_name: str = ""
    language: str = "en"
    translated_from: str = ""
    translated_date: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Article:
        if "delivery_contract" in data and isinstance(data["delivery_contract"], dict):
            data["delivery_contract"] = DeliveryContractData(**data["delivery_contract"])
        if "platform_overrides" in data and isinstance(data["platform_overrides"], dict):
            data["platform_overrides"] = PlatformOverrides(**data["platform_overrides"])
        if "sections" in data:
            sections = []
            for s in data["sections"]:
                if "blocks" in s:
                    s["blocks"] = [ContentBlock(**b) if isinstance(b, dict) else b for b in s["blocks"]]
                sections.append(ArticleSection(**s) if isinstance(s, dict) else s)
            data["sections"] = sections
        if "faq_items" in data:
            data["faq_items"] = [FAQItem(**f) if isinstance(f, dict) else f for f in data["faq_items"]]
        if "citations" in data:
            data["citations"] = [Citation(**c) if isinstance(c, dict) else c for c in data["citations"]]
        if "review_scores" in data:
            data["review_scores"] = [ReviewScore(**r) if isinstance(r, dict) else r for r in data["review_scores"]]
        if "summary_box_items" not in data:
            data["summary_box_items"] = []
        return cls(**data)
