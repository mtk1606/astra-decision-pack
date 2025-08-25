import os
import time
from typing import List, Tuple


class VectorStore:
    def upsert(self, vectors: List[Tuple[str, list, dict]]):
        raise NotImplementedError

    def query(self, vector: list, top_k: int = 8) -> List[dict]:
        raise NotImplementedError


class PineconeStore(VectorStore):
    def __init__(self, index_name: str):
        from pinecone import Pinecone
        api_key = os.environ.get("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY missing")
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)

    def upsert(self, vectors: List[Tuple[str, list, dict]]):
        # vectors: [(id, embedding, {"text":..., "domain":...})]
        items = [
            {"id": vid, "values": emb, "metadata": meta}
            for vid, emb, meta in vectors
        ]
        self.index.upsert(vectors=items)

    def query(self, vector: list, top_k: int = 8) -> List[dict]:
        t0 = time.time()
        res = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
        latency_ms = int((time.time() - t0) * 1000)
        return [{"text": m["metadata"].get("text", ""), "score": m.get("score", 0.0), "latency_ms": latency_ms} for m in res.get("matches", [])]


class FaissStore(VectorStore):
    def __init__(self, dim: int):
        import faiss  # type: ignore
        self.faiss = faiss
        self.index = faiss.IndexFlatIP(dim)
        self.texts: List[str] = []

    def upsert(self, vectors: List[Tuple[str, list, dict]]):
        import numpy as np
        mat = np.array([emb for _, emb, _ in vectors], dtype="float32")
        # normalize for cosine similarity with inner product
        faiss = self.faiss
        faiss.normalize_L2(mat)
        self.index.add(mat)
        for _, _, meta in vectors:
            self.texts.append(meta.get("text", ""))

    def query(self, vector: list, top_k: int = 8) -> List[dict]:
        import numpy as np
        q = np.array([vector], dtype="float32")
        self.faiss.normalize_L2(q)
        t0 = time.time()
        D, I = self.index.search(q, top_k)
        latency_ms = int((time.time() - t0) * 1000)
        results = []
        for idx, score in zip(I[0], D[0]):
            if 0 <= idx < len(self.texts):
                results.append({"text": self.texts[idx], "score": float(score), "latency_ms": latency_ms})
        return results


def get_store(embed_dim: int, index_name: str = "astra-signals-dev") -> VectorStore:
    if os.environ.get("PINECONE_API_KEY"):
        return PineconeStore(index_name=index_name)
    return FaissStore(dim=embed_dim)


