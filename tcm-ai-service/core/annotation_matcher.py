"""
舌象标注匹配服务
从标注规范表 (xlsx) 加载标注规则，将 YOLO 检测结果匹配到标注解释。
适配自项目2的 AnnotationService。
"""

import os
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional


class AnnotationMatcher:
    """从 Excel 标注规范表加载规则，匹配 YOLO 检测标签。"""

    def __init__(self, workbook_path: str):
        self.workbook_path = workbook_path
        self.rules = self._load_rules(workbook_path)
        self._rule_index = {}
        for r in self.rules:
            label = str(r.get("label") or r.get("标签选项") or "").strip()
            if label:
                self._rule_index[label.lower()] = r

    def match_detections(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """将 YOLO 检测结果匹配到标注规则。"""
        matched_items = []
        unmatched_labels = []

        for detection in detections:
            raw_label = detection.get("class", "未知")
            rule = self.match_label(raw_label)
            if rule:
                matched_items.append({
                    **rule,
                    "source_label": raw_label,
                    "confidence": detection.get("confidence", 0),
                })
            else:
                unmatched_labels.append(raw_label)

        if not detections:
            summary = "未识别到明确舌象标签，请重新上传清晰舌像。"
            risk_level = "unknown"
        elif not matched_items:
            summary = "模型有识别结果，但未能在标注表中找到对应解释。"
            risk_level = "unknown"
        else:
            labels = "、".join(item["label"] for item in matched_items[:4])
            summary = f"识别到 {labels}。"
            risk_level = self._risk_level(matched_items)

        return {
            "items": matched_items,
            "unmatched_labels": unmatched_labels,
            "summary": summary,
            "risk_level": risk_level,
        }

    def match_label(self, label: str) -> Optional[Dict[str, str]]:
        if not label:
            return None
        key = str(label).strip().lower()
        if key in self._rule_index:
            return self._rule_index[key]
        for rule in self.rules:
            rlabel = str(rule.get("label") or rule.get("标签选项") or "").strip().lower()
            if not rlabel:
                continue
            if key == rlabel or key in rlabel or rlabel in key:
                return rule
        return None

    def knowledge_cards(self) -> List[Dict[str, str]]:
        return self.rules

    def _load_rules(self, workbook_path: str) -> List[Dict[str, str]]:
        if not os.path.exists(workbook_path):
            return []

        rows = self._read_xlsx_first_sheet(workbook_path)
        if not rows:
            return []

        headers = rows[0]
        rules = []
        current_dimension = ""
        for row in rows[1:]:
            values = dict(zip(headers, row))
            if values.get("维度"):
                current_dimension = values["维度"]
            label = values.get("标签选项")
            if not label:
                continue
            rule = {"dimension": current_dimension, "label": label}
            for h in headers:
                if h and h not in rule:
                    rule[h] = values.get(h, "")
            rules.append(rule)
        return rules

    def _read_xlsx_first_sheet(self, path: str) -> List[List[str]]:
        ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        with zipfile.ZipFile(path) as archive:
            shared_strings = self._read_shared_strings(archive, ns)
            sheet_xml = archive.read("xl/worksheets/sheet1.xml")

        root = ET.fromstring(sheet_xml)
        rows = []
        for row_el in root.findall(".//main:sheetData/main:row", ns):
            values_by_col = {}
            max_col = 0
            for cell in row_el.findall("main:c", ns):
                ref = cell.attrib.get("r", "")
                col_index = self._column_index(ref)
                max_col = max(max_col, col_index)
                values_by_col[col_index] = self._cell_value(cell, shared_strings, ns)
            rows.append([values_by_col.get(idx, "") for idx in range(1, max_col + 1)])
        return rows

    def _read_shared_strings(self, archive, ns):
        try:
            xml = archive.read("xl/sharedStrings.xml")
        except KeyError:
            return []
        root = ET.fromstring(xml)
        strings = []
        for item in root.findall("main:si", ns):
            text_parts = [node.text or "" for node in item.findall(".//main:t", ns)]
            strings.append("".join(text_parts))
        return strings

    def _cell_value(self, cell, shared_strings, ns):
        value_el = cell.find("main:v", ns)
        if value_el is None:
            t_el = cell.find(".//main:t", ns)
            return t_el.text if t_el is not None and t_el.text else ""
        raw = value_el.text or ""
        if cell.attrib.get("t") == "s":
            return shared_strings[int(raw)] if raw.isdigit() else ""
        return raw

    def _column_index(self, ref: str) -> int:
        letters = re.sub(r"[^A-Z]", "", ref.upper())
        total = 0
        for letter in letters:
            total = total * 26 + ord(letter) - ord("A") + 1
        return total

    def _risk_level(self, matched_items: List[Dict]) -> str:
        for item in matched_items:
            for key in ("风险等级", "risk_level", "risk"):
                rv = item.get(key) or item.get(key.lower())
                if rv:
                    rv = str(rv).strip().lower()
                    if "关注" in rv or "高" in rv or "attention" in rv:
                        return "attention"
                    if "观察" in rv or "中" in rv or "observe" in rv:
                        return "observe"
                    if "正常" in rv or "低" in rv or "normal" in rv:
                        return "normal"
        return "unknown"
