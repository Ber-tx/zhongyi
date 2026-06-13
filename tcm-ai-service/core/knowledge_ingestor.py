"""
知识文档导入服务
将 Markdown 文档按"段落感知 + 字符上限"策略切分为 chunk，
写入 data/knowledge_chunks/ 目录，供 KnowledgeBase 索引。
支持增量添加与全量重建。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


def md5_text(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def is_heading(text: str) -> bool:
    return bool(re.match(r"^\s{0,3}#{1,6}\s+", text))


def heading_text(text: str) -> str:
    return re.sub(r"^\s{0,3}#{1,6}\s+", "", text).strip()


def heading_level(title: str) -> int:
    t = title.strip()
    if re.match(r"^第.+章", t): return 1
    if re.match(r"^第.+节", t): return 2
    if re.match(r"^[一二三四五六七八九十]+、", t): return 3
    if re.match(r"^（[一二三四五六七八九十]+）", t): return 4
    return 5


def paragraph_split(text: str) -> List[str]:
    parts = re.split(r"\n{2,}", text)
    parts = [p.strip() for p in parts if p and p.strip()]
    if len(parts) == 1:
        text = parts[0]
        lines = re.split(r"\n", text)
        parts = []
        cur = []
        for ln in lines:
            ln = ln.strip()
            if not ln:
                if cur:
                    parts.append("\n".join(cur).strip())
                    cur = []
                continue
            if is_heading(ln):
                if cur:
                    parts.append("\n".join(cur).strip())
                    cur = []
                parts.append(ln)
                continue
            cur.append(ln)
            if sum(len(x) for x in cur) > 4000:
                parts.append("\n".join(cur).strip())
                cur = []
        if cur:
            parts.append("\n".join(cur).strip())
    return parts


def split_long_paragraphs(paragraphs: List[str], max_len: int) -> List[str]:
    out = []
    for p in paragraphs:
        if is_heading(p) or len(p) <= max_len:
            out.append(p)
            continue
        sentences = re.split(r"(?<=[。！？；])", p)
        buf = ""
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            if len(buf) + len(s) <= max_len:
                buf = f"{buf}{s}" if buf else s
            else:
                if buf:
                    out.append(buf)
                buf = s
        if buf:
            out.append(buf)
    return out


def group_sections_strict(paragraphs: List[str]) -> List[Dict]:
    blocks = []
    current_heading = ""
    current_parts = []
    start_idx = 0
    for idx, p in enumerate(paragraphs):
        if is_heading(p):
            if current_parts:
                blocks.append({
                    "heading": current_heading,
                    "parts": current_parts,
                    "range": [start_idx + 1, idx],
                })
            current_heading = heading_text(p)
            current_parts = [p]
            start_idx = idx
        else:
            if not current_parts:
                start_idx = idx
            current_parts.append(p)
    if current_parts:
        blocks.append({
            "heading": current_heading,
            "parts": current_parts,
            "range": [start_idx + 1, len(paragraphs)],
        })
    return blocks


def make_chunks(
    paragraphs: List[str],
    chunk_size: int = 1800,
    overlap: int = 0,
    min_chars: int = 1400,
    strict_headings: bool = True,
) -> List[Dict]:
    chunks = []
    paragraphs = split_long_paragraphs(paragraphs, max_len=max(600, chunk_size // 2))
    blocks = group_sections_strict(paragraphs) if strict_headings else group_sections_strict(paragraphs)

    for block in blocks:
        parts = block["parts"]
        heading = block["heading"]
        i, n = 0, len(parts)
        while i < n:
            start_idx = i
            current = []
            cur_len = 0
            while i < n and cur_len < chunk_size:
                part = parts[i]
                if cur_len > 0 and cur_len + len(part) > chunk_size and cur_len >= min_chars:
                    break
                if cur_len == 0:
                    current.append(part)
                    cur_len += len(part)
                else:
                    current.append("\n\n" + part)
                    cur_len += len(part) + 2
                i += 1
            text = "".join(current).strip()
            if not text:
                break

            chunk_id = f"chunk_{len(chunks)+1:04d}"
            global_start = block["range"][0] + start_idx - 1
            global_end = block["range"][0] + i - 1

            if len(text) < min_chars and chunks and chunks[-1]["section_title"] == heading:
                merged = chunks[-1]["text"] + "\n\n" + text
                chunks[-1]["text"] = merged
                chunks[-1]["char_count"] = len(merged)
                chunks[-1]["md5"] = md5_text(merged)
                chunks[-1]["source_paragraph_range"][1] = global_end
            else:
                chunks.append({
                    "id": chunk_id,
                    "text": text,
                    "char_count": len(text),
                    "section_title": heading,
                    "md5": md5_text(text),
                    "source_paragraph_range": [global_start, global_end],
                })
            if strict_headings or overlap <= 0 or i >= n:
                continue
            tail_needed = overlap
            j = i - 1
            cum = 0
            while j >= start_idx and cum < tail_needed:
                cum += len(parts[j]) + (2 if cum > 0 else 0)
                j -= 1
            i = max(start_idx, j + 1)
    return chunks


def ingest_markdown(
    md_path: str,
    out_dir: Optional[str] = None,
    chunk_size: int = 1800,
) -> dict:
    """
    将 Markdown 文档导入知识库 chunk 目录。

    Args:
        md_path: Markdown 文件路径
        out_dir: chunk 输出目录（默认 data/knowledge_chunks）
        chunk_size: 每个 chunk 的目标字符数

    Returns:
        导入结果统计
    """
    if out_dir is None:
        out_dir = str(Path(__file__).resolve().parent.parent / "data" / "knowledge_chunks")

    md_file = Path(md_path)
    if not md_file.exists():
        return {"success": False, "msg": f"文件不存在: {md_path}"}

    text = md_file.read_text(encoding="utf-8")
    paras = paragraph_split(text)
    all_chunks = make_chunks(paras, chunk_size=chunk_size)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 加载已有 index
    index_path = out_path / "index.json"
    existing_index = []
    if index_path.exists():
        try:
            existing_index = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    new_entries = []
    for c in all_chunks:
        fname = f"{c['id']}.json"
        payload = {
            "id": c["id"],
            "source_file": str(md_file.resolve()),
            "section_title": c.get("section_title", ""),
            "char_count": c.get("char_count", 0),
            "md5": c.get("md5"),
            "source_paragraph_range": c.get("source_paragraph_range"),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "text": c.get("text"),
        }
        (out_path / fname).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        new_entries.append({k: payload[k] for k in (
            "id", "source_file", "section_title", "char_count", "md5",
            "source_paragraph_range", "created_at",
        )})

    # 更新 index（新文件在前）
    combined = new_entries + existing_index
    index_path.write_text(
        json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return {
        "success": True,
        "chunks_created": len(all_chunks),
        "output_dir": str(out_path),
        "source_file": str(md_file.resolve()),
    }


def main():
    parser = argparse.ArgumentParser(description="导入 Markdown 文档到知识库")
    parser.add_argument("--input", "-i", required=True, help="Markdown 文件路径")
    parser.add_argument("--out_dir", "-o", default=None, help="chunk 输出目录")
    parser.add_argument("--chunk_size", type=int, default=1800, help="分块字符数")
    args = parser.parse_args()

    result = ingest_markdown(args.input, args.out_dir, args.chunk_size)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
