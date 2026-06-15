<p align="center">
  <img src="assets/banner.svg" alt="Claude Blog: AI Blog Writing and SEO Optimization Skill for Claude Code. Animated terminal-style banner with pixel-art CLAUDE BLOG wordmark, breathing orange gradient, scanning command palette, and pulsing status indicators" width="100%">
</p>

# AI Blog Writing & SEO Optimization Skill for Claude Code (`claude-blog-enhanced`)

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent%20Skills-Compatible-blue" alt="Agent Skill"></a>
  <a href="https://github.com/LZmx/claude-blog-enhanced/releases"><img src="https://img.shields.io/github/v/release/LZmx/claude-blog-enhanced?label=release" alt="Version"></a>
  <a href="https://github.com/LZmx/claude-blog-enhanced/actions"><img src="https://img.shields.io/github/actions/workflow/status/LZmx/claude-blog-enhanced/ci.yml?branch=main&label=CI" alt="CI"></a>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License: MIT">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Sub--Skills-30-orange" alt="Sub-Skills">
  <img src="https://img.shields.io/badge/Tests-259%20passing-brightgreen" alt="Tests: 259 passing">
</p>

<p align="center">
  <a href="https://youtu.be/7Q4GaSgUFHo"><img src="https://img.youtube.com/vi/7Q4GaSgUFHo/maxresdefault.jpg" alt="Watch the Claude Blog v1.9.1 walkthrough on YouTube" width="640"></a>
</p>

<p align="center">
  <strong><a href="https://youtu.be/7Q4GaSgUFHo">Watch the 12:48 v1.9.1 walkthrough on YouTube</a></strong> · See the 5-gate Blog Delivery Contract run live, including a 6-minute live demo of the <a href="https://claude-blog.md/blog/chatgpt-codex-vs-claude-code-2026">Codex vs Claude sample blog</a> being generated end-to-end.
</p>

**Fork of [`AgriciDaniel/claude-blog`](https://github.com/AgriciDaniel/claude-blog)** with multi-format renderer architecture. Same 30 sub-skills, 5 agents, delivery contract — plus canonical JSON content model and 6 output formats.

> - 🌐 **Original**: [`AgriciDaniel/claude-blog`](https://github.com/AgriciDaniel/claude-blog). MIT-licensed, public releases.
> - 🔧 **This fork**: [`LZmx/claude-blog-enhanced`](https://github.com/LZmx/claude-blog-enhanced). Adds multi-format output (markdown, MDX, HTML, WordPress, PHP) from a shared canonical article model. Always saves `post.json` regardless of format.

<p align="center">
  •
  <a href="#quick-start">Quick Start</a> •
  <a href="#commands">Commands</a> •
  <a href="#skills">Skills</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#faq">FAQ</a> •
</p>

> **Claude Blog** is a Tier 4 Claude Code skill for blog content creation, optimization, and management. 30 sub-skills, 5 specialized subagents, 12 content templates, and 21 reference docs — dual-optimized for Google rankings (December 2025 Core Update, E-E-A-T) and AI citations (GEO/AEO).

## Quick Start

### 1. Prerequisites

- **Claude Code** (`npm install -g @anthropic-ai/claude-code` or via [VS Code extension](https://docs.anthropic.com/en/docs/claude-code/overview))
- **Python 3.11+** for quality scoring scripts
- **Optional but recommended:** Patchright (`pip install patchright`) for visual verification and PDF generation in the Blog Delivery Contract

### 2. Install the Skill

Via curl (easiest):

```bash
curl -sL https://raw.githubusercontent.com/LZmx/claude-blog-enhanced/main/install.sh | bash
```

Or if you have the repo locally:

```bash
git clone https://github.com/LZmx/claude-blog-enhanced.git
cd claude-blog-enhanced
mkdir -p ~/.claude/skills/
ln -sf "$PWD" ~/.claude/skills/claude-blog
```

Via plugin marketplace:

```bash
/plugin marketplace add LZmx/claude-blog-enhanced
/plugin install claude-blog-enhanced@LZmx-claude-blog-enhanced
```

Verify:

```bash
claude "When I type /blog, what happens?"
```

If you see the blog skill description, it worked. Start with `/blog write "your topic"`.

### 3. (Optional) Configure Google API

Some features (Search Console, GA4, PageSpeed, YouTube, NLP) require Google API access.

See [skills/blog-google/references/auth-setup.md](skills/blog-google/references/auth-setup.md) for setup instructions. Things work without it — the skill degrades gracefully.

## Commands

Every `/blog` command supports `--format` for output format selection. Default is `markdown`.

| Command | Description |
|---------|-------------|
| `/blog write "AI SEO trends" --format markdown` | Write new article (markdown, default) |
| `/blog write "How to" --format html` | Write as generic HTML |
| `/blog write "WordPress guide" --format wordpress` | Write as WordPress Classic HTML |
| `/blog write "Gutenberg tutorial" --format wordpress-blocks` | Write as WordPress Block Editor HTML |
| `/blog write "PHP template" --format php` | Write as PHP template |
| `/blog write "MDX post" --format mdx` | Write as MDX for Next.js/Astro |
| `/blog rewrite` | Optimize existing posts |
| `/blog analyze` | 5-category 100-point scoring |
| `/blog brief` | Detailed content briefs |
| `/blog outline` | SERP-informed outlines |
| `/blog calendar` | Editorial calendars |
| `/blog strategy` | Blog positioning |
| `/blog seo-check` | Post-writing SEO validation |
| `/blog schema` | JSON-LD schema generation |
| `/blog chart` | Inline SVG charts |
| `/blog repurpose` | Multi-platform repurposing |
| `/blog geo` | AI citation optimization |
| `/blog image` | AI image generation |
| `/blog audit` | Full-site blog health assessment |
| `/blog cannibalization` | Keyword overlap detection |
| `/blog factcheck` | Statistics verification |
| `/blog persona` | Writing persona management |
| `/blog taxonomy` | CMS taxonomy management |
| `/blog notebooklm` | NotebookLM research |
| `/blog audio` | Audio narration |
| `/blog google` | Google API data |
| `/blog cluster` | Topic cluster execution |
| `/blog multilingual` | Multi-language publishing |
| `/blog translate` | SEO-optimized translation |
| `/blog localize` | Cultural adaptation |
| `/blog locale-audit` | Multilingual QA |
| `/blog flow` | FLOW framework prompts |
| `/blog brand` | Brand/Voice context |
| `/blog discourse` | Discourse research |

See [full reference](https://github.com/LZmx/claude-blog-enhanced/blob/main/skills/blog/SKILL.md) for details.

## Skills

The engine is organized as 30 sub-skills under `skills/` — each a focused module with its own directives, references, scripts, and sometimes assets:

```
skills/
  blog/                        # Orchestrator: routing, scoring, templates, references
  blog-write/                  # Write new articles
  blog-rewrite/                # Optimize existing posts
  blog-analyze/                # 5-category 100-point scoring
  blog-brief/                  # Detailed content briefs
  blog-outline/                # SERP-informed outlines
  blog-calendar/               # Editorial calendars
  blog-strategy/               # Blog positioning
  blog-seo-check/              # Post-writing SEO validation
  blog-schema/                 # JSON-LD schema generation
  blog-chart/                  # Inline SVG charts
  blog-repurpose/              # Multi-platform repurposing
  blog-geo/                    # AI citation optimization
  blog-audit/                  # Full-site blog health
  blog-image/                  # AI image generation
  blog-cannibalization/        # Keyword overlap detection
  blog-factcheck/              # Statistics verification
  blog-persona/                # Writing persona management
  blog-taxonomy/               # CMS taxonomy management
  blog-notebooklm/             # NotebookLM research
  blog-audio/                  # Audio narration
  blog-google/                 # Google API integration
  blog-cluster/                # Topic cluster execution
  blog-flow/                   # FLOW framework prompts
  blog-multilingual/           # Multi-language publishing
  blog-translate/              # SEO-optimized translation
  blog-localize/               # Cultural adaptation
  blog-locale-audit/           # Multilingual QA
  blog-discourse/              # Practitioner discourse research
  blog-brand/                  # Brand/Voice context
```

## Architecture

### Multi-Format Output Architecture (v2.0.0)

```
prompts → canonical JSON model → renderer → output file + WordPress REST payload
```

Key components:
- **`canonical/`**: Article schema (`Article`, `ArticleSection`, `ContentBlock`) + builder + output helpers
- **`renderers/`**: 6 format renderers (markdown, mdx, html, wordpress, wordpress-blocks, php)
- **`validators/`**: Format-aware validators (markdown, html, wordpress, wordpress-blocks, php)
- **`publishers/`**: WordPress REST API adapter with dry-run, create, update

Always saved: `post.json` (canonical model), `metadata.json`, `schema.json`

### Original v1.9.0 Architecture

```
  scripts/
    blog_render.py              # Render blog post to HTML + PDF
    blog_preflight.py           # 5-gate delivery contract runner
    lint_prose.py               # Fence-aware prose-hygiene linter
    analyze_blog.py             # 5-category quality scoring
    discourse_research.py       # Discourse brief synthesis
    generate_hero.py            # Hero image ladder
    cognitive_load.py           # Concept-density analysis
    load_untrusted_root.py      # Fence helper for BRAND/VOICE/DISCOURSE
    sync_flow.py                # FLOW references sync
  agents/
    blog-researcher.md          # Statistics and source research
    blog-writer.md              # Content generation
    blog-seo.md                 # SEO validation
    blog-reviewer.md            # Quality scoring (blocking)
    blog-translator.md          # Multilingual translation
```

### Two Paths Through blog_render.py

```
Legacy:  --md article.md → output.html + output.pdf
Canonical: --json post.json --format <fmt> → article.<ext> + post.json + metadata.json + schema.json
```

---

## FAQ

### What's new in v2.0.0 (this fork)?

Multi-format renderer architecture with a canonical JSON content model. Choose output format per article:

- **markdown**: Obsidian, GitHub, static sites, editorial review
- **html**: Generic CMS, rich text fields, email, RSS
- **wordpress/wordpress-blocks**: Direct WordPress publish workflows
- **php**: WordPress theme integration
- **mdx**: Next.js, Astro, Gatsby pipelines

Always saves `post.json` regardless of format. See the full [format documentation](skills/blog/SKILL.md).

### Is this compatible with the original claude-blog?

Yes. All 30 sub-skills, 5 agents, 12 templates, 21 reference docs, and the 5-gate Blog Delivery Contract are fully preserved. The `--md` legacy path in `blog_render.py` still works. This is additive — no existing feature was removed.

### Can I still run tests?

```bash
python -m pytest tests/
```

### Do I need Claude Code Pro?

No. The public open-source version at [`AgriciDaniel/claude-blog`](https://github.com/AgriciDaniel/claude-blog) is MIT-licensed. This fork is also MIT-licensed.

### /release-blog support?

The `/release-blog` command (blog post + cover + SEO + Vercel deploy) is not included in this fork. It was specific to the original author's deployment pipeline.

---

## References

- **[Blog Delivery Contract](skills/blog/references/blog-delivery-contract.md)**: 5-gate enforcement with canonical model, format completeness, visual verification, content review, and asset integrity.
- **[FLOW framework](https://github.com/AgriciDaniel/flow)**: Evidence-led Find, Optimize, Win prompts (CC BY 4.0). Integrated as a sub-skill via `/blog flow`.
- **[Claude Ads](https://github.com/AgriciDaniel/claude-ads)** and **[Claude SEO](https://github.com/AgriciDaniel/claude-seo)**: sibling skills from the original author.

## History

<a href="https://star-history.com/#AgriciDaniel/claude-blog&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=AgriciDaniel/claude-blog&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=AgriciDaniel/claude-blog&type=Date" />
    <img alt="Star history of AgriciDaniel/claude-blog on GitHub" src="https://api.star-history.com/svg?repos=AgriciDaniel/claude-blog&type=Date" />
  </picture>
</a>

*Star history of the original `AgriciDaniel/claude-blog` — the upstream repo this fork is based on.*

---

## License

MIT — see [LICENSE](LICENSE).

## Author

- **Original**: [AgriciDaniel](https://github.com/AgriciDaniel) — [YouTube](https://www.youtube.com/@AgriciDaniel)
- **This fork**: [LZmx](https://github.com/LZmx/claude-blog-enhanced)
