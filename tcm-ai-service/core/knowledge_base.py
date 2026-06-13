"""
中医知识库 RAG 服务
封装 ChromaDB 向量检索 + Qwen text-embedding 生成。
支持知识库的查询、状态检查、重新索引。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional

import chromadb
import requests
from chromadb.config import Settings

# ── 配置 ──────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

EMBED_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
EMBED_MODEL = "text-embedding-v4"
CHROMA_PERSIST_DIR = BASE_DIR / "data" / "chroma_db"
COLLECTION_NAME = "tongue_knowledge"
DEFAULT_TOP_K = 5
BATCH_SIZE = 10
REQUEST_INTERVAL = 0.3


class KnowledgeBase:
    """中医知识库检索服务（ChromaDB + Qwen embedding）。"""

    def __init__(self):
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection: Optional[chromadb.Collection] = None

    # ── 初始化 ──────────────────────────────────────────────

    @property
    def collection(self) -> chromadb.Collection:
        if self._collection is None:
            CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(CHROMA_PERSIST_DIR),
                settings=Settings(anonymized_telemetry=False),
            )
            try:
                self._collection = self._client.get_collection(COLLECTION_NAME)
            except ValueError:
                self._collection = self._client.create_collection(
                    name=COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )
        return self._collection

    def ready(self) -> bool:
        try:
            return self.collection.count() > 0
        except Exception:
            return False

    def count(self) -> int:
        try:
            return self.collection.count()
        except Exception:
            return 0

    # ── 嵌入 ────────────────────────────────────────────────

    @staticmethod
    def embed_texts(texts: list[str]) -> list[list[float]]:
        """调用 Qwen text-embedding-v4 生成向量（绕过系统代理）。"""
        api_key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_API_KEY") or "sk-180e7f5a94824f6cb252e547896694ab"

        url = f"{EMBED_BASE_URL}/embeddings"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": EMBED_MODEL,
            "input": texts,
            "encoding_format": "float",
        }
        resp = requests.post(
            url, json=payload, headers=headers,
            timeout=120, proxies={"http": None, "https": None},
        )
        if resp.status_code != 200:
            raise RuntimeError(f"嵌入 API 返回 {resp.status_code}: {resp.text}")

        data = resp.json()
        embeddings = [None] * len(texts)
        for item in data.get("data", []):
            embeddings[item["index"]] = item["embedding"]
        if any(e is None for e in embeddings):
            raise RuntimeError("嵌入返回不完整，部分 index 缺失")
        return embeddings

    # ── 检索 ────────────────────────────────────────────────

    def search(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
        """向量检索，返回最相关的 top_k 条知识片段。"""
        query_emb = self.embed_texts([query])[0]
        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=top_k,
        )
        items = []
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )):
            items.append({
                "id": results["ids"][0][i],
                "text": doc,
                "section_title": meta.get("section_title", ""),
                "source_file": meta.get("source_file", ""),
                "paragraph_start": meta.get("paragraph_start"),
                "paragraph_end": meta.get("paragraph_end"),
                "score": round(1.0 - dist, 4),
            })
        items.sort(key=lambda x: x["score"], reverse=True)
        return items

    def search_with_context(self, query: str, top_k: int = DEFAULT_TOP_K) -> dict:
        """检索并拼接上下文文本，供大模型生成回答。"""
        items = self.search(query, top_k=top_k)
        context_parts = []
        for item in items:
            header = f"【{item['section_title']}】" if item["section_title"] else ""
            context_parts.append(f"{header}\n{item['text']}")
        return {
            "items": items,
            "context": "\n\n---\n\n".join(context_parts),
            "total": len(items),
        }

    # ── 索引管理 ────────────────────────────────────────────

    def reindex(self, chunks_dir: Optional[Path] = None) -> dict:
        """清空并重建向量库（从 knowledge_chunks 目录读取 chunk 文件）。"""
        if chunks_dir is None:
            chunks_dir = BASE_DIR / "data" / "knowledge_chunks"

        # 加载所有 chunk
        files = sorted(chunks_dir.glob("chunk_*.json"))
        chunks = []
        for f in files:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                text = data.get("text", "").strip()
                if text:
                    chunks.append(data)
            except Exception:
                continue

        if not chunks:
            return {"success": False, "msg": f"未找到有效 chunk（{chunks_dir}）"}

        # 删除旧集合，创建新集合
        try:
            if self._client:
                self._client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self._collection = self._client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        # 分批嵌入并写入
        total = len(chunks)
        success_count = 0
        for start in range(0, total, BATCH_SIZE):
            batch = chunks[start: start + BATCH_SIZE]
            texts = [item["text"] for item in batch]
            ids = [item["id"] for item in batch]
            metadatas = [
                {
                    "source_file": item.get("source_file", ""),
                    "section_title": item.get("section_title", ""),
                    "char_count": item.get("char_count", 0),
                    "paragraph_start": item.get("source_paragraph_range", [0, 0])[0],
                    "paragraph_end": item.get("source_paragraph_range", [0, 0])[1],
                    "md5": item.get("md5", ""),
                }
                for item in batch
            ]

            try:
                embeddings = self.embed_texts(texts)
                self.collection.add(
                    embeddings=embeddings, documents=texts,
                    metadatas=metadatas, ids=ids,
                )
                success_count += len(batch)
            except Exception as exc:
                # 重试一次
                time.sleep(2)
                try:
                    embeddings = self.embed_texts(texts)
                    self.collection.add(
                        embeddings=embeddings, documents=texts,
                        metadatas=metadatas, ids=ids,
                    )
                    success_count += len(batch)
                except Exception:
                    pass
            time.sleep(REQUEST_INTERVAL)

        return {
            "success": True,
            "total_chunks": total,
            "indexed": self.collection.count(),
            "success_count": success_count,
        }
