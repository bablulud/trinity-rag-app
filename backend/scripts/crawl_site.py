"""Crawl a website from its XML sitemap and save each page as a Markdown file.

Built for www.trinityrail.com but works on any site with an XML sitemap (plain
or sitemap-index). Each page is fetched, stripped of chrome (nav/header/footer/
scripts), converted to lightweight Markdown, and written to the output dir with a
`Source URL:` / `Title:` header so the RAG pipeline can cite it.

Usage:
    python scripts/crawl_site.py \
        --sitemap https://www.trinityrail.com/sitemap.xml \
        --out ./content \
        --concurrency 8 --delay 0.1 [--max 0]

Point DOCS_DIR at the output dir (or pass --out backend/pdfs) so the crawled
pages are picked up on the next re-index.

--max 0 (default) means no limit (crawl the entire site).
"""
import argparse
import asyncio
import os
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "trinity-rag-crawler/1.0 (+https://www.trinityrail.com)"
# robots.txt disallows these path prefixes for all agents.
DISALLOWED = ("/search",)
BLOCK_TAGS = ["script", "style", "noscript", "svg", "form", "iframe"]
CHROME_ROLES = ["nav", "header", "footer", "aside"]


def _clean_ns(tag: str) -> str:
    return tag.split("}", 1)[-1]


async def fetch(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        r = await client.get(url, follow_redirects=True)
        if r.status_code == 200 and r.text:
            return r.text
        print(f"  [{r.status_code}] {url}", file=sys.stderr)
    except Exception as e:  # noqa: BLE001
        print(f"  [ERR] {url}: {e}", file=sys.stderr)
    return None


async def collect_urls(client: httpx.AsyncClient, sitemap_url: str) -> list[str]:
    """Recursively expand a sitemap (index or urlset) into a flat list of page URLs."""
    xml = await fetch(client, sitemap_url)
    if not xml:
        return []
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        print(f"  [XML ERR] {sitemap_url}: {e}", file=sys.stderr)
        return []

    tag = _clean_ns(root.tag)
    locs = [
        loc.text.strip()
        for loc in root.iter()
        if _clean_ns(loc.tag) == "loc" and loc.text
    ]

    if tag == "sitemapindex":
        urls: list[str] = []
        for child in locs:
            urls.extend(await collect_urls(client, child))
        return urls
    return locs


def allowed(url: str) -> bool:
    path = urlparse(url).path
    return not any(path.startswith(p) for p in DISALLOWED)


def slugify(url: str) -> str:
    p = urlparse(url)
    path = p.path.strip("/")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", path).strip("-") or "index"
    return slug[:180]


def html_to_markdown(html: str) -> tuple[str, str]:
    """Return (title, markdown-ish text) for a page, dropping site chrome."""
    soup = BeautifulSoup(html, "lxml")
    title = (soup.title.string or "").strip() if soup.title else ""

    for tag in soup(BLOCK_TAGS):
        tag.decompose()
    for role in CHROME_ROLES:
        for tag in soup.find_all(role):
            tag.decompose()

    root = soup.find("main") or soup.body or soup

    lines: list[str] = []
    for el in root.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote"]
    ):
        text = " ".join(el.get_text(" ", strip=True).split())
        if not text:
            continue
        name = el.name
        if name.startswith("h") and len(name) == 2 and name[1].isdigit():
            lines.append(f"{'#' * int(name[1])} {text}")
        elif name == "li":
            lines.append(f"* {text}")
        else:
            lines.append(text)

    # de-dupe consecutive identical lines (common with repeated CTAs)
    out: list[str] = []
    for ln in lines:
        if not out or out[-1] != ln:
            out.append(ln)
    return title, "\n\n".join(out)


async def crawl_page(
    client: httpx.AsyncClient, url: str, out_dir: str, sem: asyncio.Semaphore, delay: float
) -> bool:
    async with sem:
        html = await fetch(client, url)
        if delay:
            await asyncio.sleep(delay)
    if not html:
        return False
    title, body = html_to_markdown(html)
    if len(body) < 40:  # skip near-empty stubs
        return False
    path = os.path.join(out_dir, f"{slugify(url)}.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"Source URL: {url}\n")
        if title:
            fh.write(f"Title: {title}\n")
        fh.write("\n" + body + "\n")
    return True


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sitemap", default="https://www.trinityrail.com/sitemap.xml")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "content"))
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--delay", type=float, default=0.1)
    ap.add_argument("--max", type=int, default=0, help="0 = no limit")
    args = ap.parse_args()

    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    headers = {"User-Agent": USER_AGENT}
    limits = httpx.Limits(max_connections=args.concurrency * 2)
    async with httpx.AsyncClient(headers=headers, timeout=30.0, limits=limits) as client:
        print(f"Reading sitemap {args.sitemap} ...")
        urls = await collect_urls(client, args.sitemap)
        urls = [u for u in dict.fromkeys(urls) if allowed(u)]
        if args.max:
            urls = urls[: args.max]
        print(f"Crawling {len(urls)} pages -> {out_dir}")

        sem = asyncio.Semaphore(args.concurrency)
        saved = 0
        tasks = [crawl_page(client, u, out_dir, sem, args.delay) for u in urls]
        for i, coro in enumerate(asyncio.as_completed(tasks), 1):
            if await coro:
                saved += 1
            if i % 50 == 0:
                print(f"  {i}/{len(urls)} fetched, {saved} saved")
        print(f"done: {saved}/{len(urls)} pages saved to {out_dir}")


if __name__ == "__main__":
    asyncio.run(main())
