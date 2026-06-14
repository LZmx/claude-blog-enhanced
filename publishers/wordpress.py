from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from canonical.schema import Article


@dataclass
class WordPressPayload:
    title: str
    content: str
    status: str = "draft"
    slug: str = ""
    excerpt: str = ""
    categories: list[int] = field(default_factory=list)
    tags: list[int] = field(default_factory=list)
    featured_media: int = 0
    meta: dict = field(default_factory=dict)
    date: Optional[str] = None

    def to_api_dict(self) -> dict:
        d = {
            "title": self.title,
            "content": self.content,
            "status": self.status,
        }
        if self.slug:
            d["slug"] = self.slug
        if self.excerpt:
            d["excerpt"] = self.excerpt
        if self.categories:
            d["categories"] = self.categories
        if self.tags:
            d["tags"] = self.tags
        if self.featured_media:
            d["featured_media"] = self.featured_media
        if self.meta:
            d["meta"] = self.meta
        if self.date:
            d["date"] = self.date
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_api_dict(), indent=indent, ensure_ascii=False)


class WordPressPublisher:
    def __init__(self, api_url: str = "", auth_token: str = "", username: str = "", password: str = ""):
        self.api_url = api_url.rstrip("/")
        self.auth_token = auth_token
        self.username = username
        self.password = password

    @classmethod
    def from_article(cls, article: Article, rendered_content: str) -> WordPressPublisher:
        publisher = cls()
        return publisher

    def build_payload(
        self,
        article: Article,
        rendered_content: str,
        category_map: dict[str, int] | None = None,
        tag_map: dict[str, int] | None = None,
    ) -> WordPressPayload:
        wp_slug = article.platform_overrides.wordpress_slug or article.slug
        wp_title = article.platform_overrides.wordpress_title or article.title
        wp_status = article.platform_overrides.wordpress_status
        wp_excerpt = article.platform_overrides.wordpress_excerpt or article.excerpt

        payload = WordPressPayload(
            title=wp_title,
            content=rendered_content,
            status=wp_status,
            slug=wp_slug,
            excerpt=wp_excerpt,
        )

        if category_map:
            for cat in article.categories:
                if cat in category_map:
                    payload.categories.append(category_map[cat])
        if tag_map:
            for tag in article.tags:
                if tag in tag_map:
                    payload.tags.append(tag_map[tag])

        if article.date:
            payload.date = article.date

        return payload

    def dry_run(self, article: Article, rendered_content: str, category_map: dict[str, int] | None = None, tag_map: dict[str, int] | None = None) -> WordPressPayload:
        return self.build_payload(article, rendered_content, category_map, tag_map)

    def create_post(self, payload: WordPressPayload) -> dict:
        if not self.api_url:
            return {"error": "WordPress API URL not configured. Set api_url."}
        import urllib.request
        import base64

        url = f"{self.api_url}/wp/v2/posts"
        data = json.dumps(payload.to_api_dict()).encode("utf-8")
        credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {credentials}",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.read().decode('utf-8')[:500]}"}
        except Exception as e:
            return {"error": str(e)}

    def update_post(self, post_id: int, payload: WordPressPayload) -> dict:
        if not self.api_url:
            return {"error": "WordPress API URL not configured"}
        import urllib.request
        import base64

        url = f"{self.api_url}/wp/v2/posts/{post_id}"
        data = json.dumps(payload.to_api_dict()).encode("utf-8")
        credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {credentials}",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.read().decode('utf-8')[:500]}"}
        except Exception as e:
            return {"error": str(e)}
