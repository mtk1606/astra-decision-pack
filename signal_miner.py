# signal_miner.py
import argparse
import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

PRICE_RE = re.compile(r'(\$\s?\d{1,3}(?:[,\d{3}])*(?:\.\d{2})?)')

def now_utc_iso():
    return datetime.now(timezone.utc).isoformat()

def now_utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def safe_request(url, headers=None, timeout=12):
    headers = headers or DEFAULT_HEADERS
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        return {"error": str(e)}

def domain_from_url(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return "unknown"

def extract_generic(html):
    soup = BeautifulSoup(html, "html.parser")
    texts = []
    for tag in soup.find_all(["h1", "h2", "h3", "p"]):
        t = tag.get_text(strip=True)
        if t and len(t.split()) > 3:
            texts.append(t)
        if len(texts) >= 40:
            break
    lists = []
    for ul in soup.find_all(["ul","ol"]):
        items = [li.get_text(strip=True) for li in ul.find_all("li") if li.get_text(strip=True)]
        if items:
            lists.append(items)
        if len(lists) >= 10:
            break
    prices = sorted({m.strip() for m in PRICE_RE.findall(" ".join(texts))})
    return {
        "headlines_paragraphs": texts[:40],
        "lists": lists[:10],
        "prices": prices
    }

def extract_hackernews(html):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for a in soup.select("a.storylink, a.titlelink, span.titleline a"):
        t = a.get_text(strip=True)
        if t:
            items.append(t)
        if len(items) >= 20:
            break
    return {"hn_titles": items}

def snapshot_save(out_dir, domain, html):
    snapshots_dir = os.path.join(out_dir, "snapshots")
    os.makedirs(snapshots_dir, exist_ok=True)
    fname = f"{domain}_{now_utc_stamp()}.html"
    path = os.path.join(snapshots_dir, fname)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path
    except Exception:
        return None

def mine_site(url, limit):
    domain = domain_from_url(url)
    result = {
        "url": url,
        "domain": domain,
        "timestamp": now_utc_iso(),
        "error": None,
        "snapshot": None,
        "signals": {}
    }

    res = safe_request(url)
    if isinstance(res, dict) and res.get("error"):
        result["error"] = res["error"]
        return result

    html = res
    result["snapshot"] = snapshot_save("output", domain, html)

    if "news.ycombinator.com" in urlparse(url).netloc:
        parsed = extract_hackernews(html)
    else:
        parsed = extract_generic(html)

    for k, v in parsed.items():
        if isinstance(v, list):
            parsed[k] = v[:limit]

    result["signals"] = parsed
    return result

def pretty_markdown_report(all_results, md_path):
    lines = []
    lines.append("# Signals Report\n")
    lines.append(f"_Generated: {now_utc_iso()}_\n")
    for r in all_results:
        lines.append(f"## {r['domain']}\n")
        lines.append(f"- URL: {r['url']}\n")
        lines.append(f"- Timestamp: {r['timestamp']}\n")
        if r.get("error"):
            lines.append(f"- **Error:** {r['error']}\n")
            lines.append("\n---\n")
            continue

        signals = r.get("signals", {})
        for key, items in signals.items():
            if not items:
                continue
            lines.append(f"### {key}\n")
            for i, it in enumerate(items[:6], 1):
                # handle lists (e.g. UL/OL groups)
                if isinstance(it, list):
                    snippet = "; ".join(it)
                else:
                    snippet = str(it)
                snippet = snippet.replace("\n", " ")
                if len(snippet) > 220:
                    snippet = snippet[:217] + "..."
                lines.append(f"{i}. {snippet}\n")
        lines.append("\n---\n")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    parser = argparse.ArgumentParser(description="Signal Miner - extract signals from URLs")
    parser.add_argument("urls_file", nargs="?", default="url.txt", help="file with newline-separated urls")
    parser.add_argument("--limit", type=int, default=5, help="max items per signal type")
    parser.add_argument("--out", default="output/signals.json", help="output combined json")
    args = parser.parse_args()

    if not os.path.exists(args.urls_file):
        print(f"[ERROR] URLs file '{args.urls_file}' not found.")
        return

    with open(args.urls_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

    os.makedirs("output", exist_ok=True)
    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Mining: {url}")
        r = mine_site(url, limit=args.limit)
        results.append(r)
        domain = r.get("domain", f"site{i}")
        safe_name = re.sub(r'[^A-Za-z0-9_.-]', '_', domain)
        per_path = os.path.join("output", f"{safe_name}.json")
        with open(per_path, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    md_path = os.path.join("output", "signals.md")
    pretty_markdown_report(results, md_path)

    print(f"\n[INFO] Done. Combined JSON: {args.out}")
    print(f"[INFO] Per-site JSONs saved to: output/*.json")
    print(f"[INFO] Markdown report: {md_path}")
    print(f"[INFO] Raw HTML snapshots: output/snapshots/")

if __name__ == "__main__":
    main()
