import argparse
import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from .pinecone_helper import get_store

# Expose OpenAI symbol for tests so it can be patched.
# Prefer real OpenAI class if available, otherwise provide a simple wrapper.
try:
    from openai import OpenAI  # modern imports (if available)
except Exception:
    import openai as _openai
    class OpenAI:
        def __init__(self, **kwargs):
            # wrap the openai module so tests can patch the OpenAI symbol
            self._client = _openai
        def __getattr__(self, name):
            return getattr(self._client, name)


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_signals(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # combined file is a list of per-site dicts
    if isinstance(data, list):
        return data
    # allow a single site dict too
    return [data]


def collect_snippets(per_site: Dict[str, Any], k: int = 10) -> Tuple[str, List[str]]:
    domain = per_site.get("domain", "unknown")
    snippets: List[str] = []
    signals = per_site.get("signals", {})
    for key, items in signals.items():
        for it in items:
            text = "; ".join(it) if isinstance(it, list) else str(it)
            if text and len(text.split()) >= 4:
                snippets.append(text)
            if len(snippets) >= k:
                break
        if len(snippets) >= k:
            break
    return domain, snippets


def make_embeddings(client, texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    if not texts:
        return []
    resp = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]


def build_prompt(template_path: str, retrieved_texts: List[str]) -> str:
    with open(template_path, "r", encoding="utf-8") as f:
        tpl = f.read()
    joined = "\n- " + "\n- ".join(retrieved_texts[:8]) if retrieved_texts else "\n- (no snippets)"
    return tpl.replace("{{SNIPPETS}}", joined)


def call_llm_json(client, model: str, prompt: str) -> Dict[str, Any]:
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful, precise assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content
    return json.loads(content)


def find_latest_output(base_output: str) -> str:
    # if base_output contains per-run folders, pick latest; else fallback to base_output/signals.json
    candidates: List[Tuple[float, str]] = []
    if os.path.isdir(base_output):
        for name in os.listdir(base_output):
            candidate = os.path.join(base_output, name, "signals.json")
            if os.path.exists(candidate):
                candidates.append((os.path.getmtime(candidate), candidate))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    # default
    default_path = os.path.join(base_output, "signals.json")
    return default_path


def generate_pack_for_run(run_path: str, model: str = "gpt-4o-mini", embed_model: str = "text-embedding-3-small") -> Dict[str, Any]:
    """Generate Decision Pack for a specific run file, returns pack + metadata"""
    from openai import OpenAI
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY env var is required")
    client = OpenAI()

    if not os.path.exists(run_path):
        raise RuntimeError(f"Run file not found: {run_path}")

    # load single run
    with open(run_path, "r", encoding="utf-8") as f:
        site = json.load(f)

    domain, top_snippets = collect_snippets(site, k=10)

    # embed
    t0 = time.time()
    embeds = make_embeddings(client, top_snippets, model=embed_model)
    embed_ms = int((time.time() - t0) * 1000)

    if embeds:
        dim = len(embeds[0])
    else:
        dim = 1536  # default for model

    store = get_store(embed_dim=dim, index_name="astra-signals-dev")
    vectors = [(f"{domain}-{i}", emb, {"text": txt, "domain": domain}) for i, (emb, txt) in enumerate(zip(embeds, top_snippets))]
    if vectors:
        store.upsert(vectors)

    # retrieval using centroid of embeddings as query
    if embeds:
        import numpy as np
        q = (sum(embeds) / len(embeds)) if isinstance(embeds, list) else embeds[0]
        if not isinstance(q, list):
            q = (np.array(embeds).mean(axis=0)).tolist()
    else:
        q = [0.0] * dim
    results = store.query(q, top_k=8)
    retrieved_texts = [r.get("text", "") for r in results]

    # prompt
    tpl_path = os.path.join(os.path.dirname(__file__), "prompts", "decision_pack_template.txt")
    prompt = build_prompt(tpl_path, retrieved_texts)

    # llm
    pack = call_llm_json(client, model, prompt)

    # ensure keys
    required_keys = [
        "title", "hypothesis", "expected_lift", "confidence",
        "confidence_justification", "risks", "assets_needed", "suggested_execution_steps"
    ]
    for k in required_keys:
        pack.setdefault(k, [] if k.endswith("s") or k.endswith("steps") else "")

    # build citations
    citations = []
    for i, (text, result) in enumerate(zip(retrieved_texts[:5], results[:5])):
        citations.append({
            "snippet": text[:100] + "..." if len(text) > 100 else text,
            "score": result.get("score", 0.0),
            "latency_ms": result.get("latency_ms", 0)
        })

    return {
        "pack": pack,
        "metadata": {
            "model": model,
            "embed_model": embed_model,
            "domain": domain,
            "embed_ms": embed_ms,
            "citations": citations,
            "run_path": run_path
        }
    }


def save_pack(pack: Dict[str, Any], domain: str, outdir: str = None) -> str:
    """Save a Decision Pack to file"""
    if outdir is None:
        outdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output", "decision_packs"))
    os.makedirs(outdir, exist_ok=True)
    stamp = now_stamp()
    outfile = os.path.join(outdir, f"{domain}__{stamp}.json")
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)
    return outfile


def main():
    parser = argparse.ArgumentParser(description="Generate Decision Pack from mined signals (RAG)")
    parser.add_argument("--input", default=None, help="Path to combined signals.json (defaults to latest output/signals.json)")
    parser.add_argument("--outdir", default=os.path.join("output", "decision_packs"))
    parser.add_argument("--embed_model", default="text-embedding-3-small")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--index", default="astra-signals-dev")
    args = parser.parse_args()

    from openai import OpenAI
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY env var is required")
    client = OpenAI()

    base_output = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
    input_path = args.input or find_latest_output(base_output)
    if not os.path.exists(input_path):
        raise SystemExit(f"Input not found: {input_path}")

    combined = load_signals(input_path)
    # choose first site for MVP; later iterate all
    site = combined[0] if combined else {}
    domain, top_snippets = collect_snippets(site, k=10)

    # embed
    t0 = time.time()
    embeds = make_embeddings(client, top_snippets, model=args.embed_model)
    embed_ms = int((time.time() - t0) * 1000)
    print(f"[INFO] Embedded {len(embeds)} snippets in {embed_ms} ms")

    if embeds:
        dim = len(embeds[0])
    else:
        dim = 1536  # default for model

    store = get_store(embed_dim=dim, index_name=args.index)
    vectors = [(f"{domain}-{i}", emb, {"text": txt, "domain": domain}) for i, (emb, txt) in enumerate(zip(embeds, top_snippets))]
    if vectors:
        store.upsert(vectors)

    # retrieval using centroid of embeddings as query
    if embeds:
        import numpy as np
        q = (sum(embeds) / len(embeds)) if isinstance(embeds, list) else embeds[0]
        if not isinstance(q, list):
            q = (np.array(embeds).mean(axis=0)).tolist()
    else:
        q = [0.0] * dim
    results = store.query(q, top_k=8)
    retrieved_texts = [r.get("text", "") for r in results]

    # prompt
    tpl_path = os.path.join(os.path.dirname(__file__), "prompts", "decision_pack_template.txt")
    prompt = build_prompt(tpl_path, retrieved_texts)

    # llm
    pack = call_llm_json(client, args.model, prompt)

    # ensure keys
    required_keys = [
        "title", "hypothesis", "expected_lift", "confidence",
        "confidence_justification", "risks", "assets_needed", "suggested_execution_steps"
    ]
    for k in required_keys:
        pack.setdefault(k, [] if k.endswith("s") or k.endswith("steps") else "")

    # write
    outdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output", "decision_packs"))
    os.makedirs(outdir, exist_ok=True)
    stamp = now_stamp()
    outfile = os.path.join(outdir, f"{domain}__{stamp}.json")
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Decision Pack written: {outfile}")


if __name__ == "__main__":
    main()


