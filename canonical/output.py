from __future__ import annotations
import json
from pathlib import Path
from canonical.schema import Article


def save_canonical(article: Article, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "post.json"
    path.write_text(json.dumps(article.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def save_metadata(article: Article, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "title": article.title,
        "slug": article.slug,
        "excerpt": article.excerpt,
        "target_keyword": article.target_keyword,
        "secondary_keywords": article.secondary_keywords,
        "author": article.author,
        "status": article.status,
        "categories": article.categories,
        "tags": article.tags,
        "meta_title": article.meta_title,
        "meta_description": article.meta_description,
        "canonical_url": article.canonical_url,
        "featured_image": article.featured_image,
        "date": article.date,
        "last_updated": article.last_updated,
        "word_count_target": article.word_count_target,
        "reading_time_minutes": article.reading_time_minutes,
        "template_name": article.template_name,
        "language": article.language,
        "translated_from": article.translated_from,
        "review_scores": [
            {"category": s.category, "score": s.score, "max_score": s.max_score, "notes": s.notes}
            for s in article.review_scores
        ],
    }
    path = output_dir / "metadata.json"
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def save_schema(article: Article, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = article.schema_json_ld or _default_schema(article)
    path = output_dir / "schema.json"
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def save_rendered(article: Article, content: str, slug: str, extension: str, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{slug}.{extension}"
    path = output_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def save_all_artifacts(article: Article, rendered: dict[str, str], output_dir: str | Path) -> dict[str, str]:
    artifacts = {}
    artifacts["post.json"] = str(save_canonical(article, output_dir))
    artifacts["metadata.json"] = str(save_metadata(article, output_dir))
    artifacts["schema.json"] = str(save_schema(article, output_dir))
    for fmt, content in rendered.items():
        ext = _extension_for(fmt)
        path = save_rendered(article, content, article.slug, ext, output_dir)
        artifacts[f"{fmt}"] = str(path)
    return artifacts


def _extension_for(fmt: str) -> str:
    return {"markdown": "md", "mdx": "mdx", "html": "html", "wordpress": "wp.html", "wordpress-blocks": "blocks.html", "php": "php"}.get(fmt, fmt)


def _default_schema(article: Article) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": article.title,
        "description": article.meta_description or article.excerpt,
        "author": {"@type": "Person", "name": article.author} if article.author else {"@type": "Organization", "name": "Author"},
        "datePublished": article.date,
        "dateModified": article.last_updated or article.date,
        "mainEntityOfPage": {"@type": "WebPage", "@id": article.canonical_url or ""},
    }
