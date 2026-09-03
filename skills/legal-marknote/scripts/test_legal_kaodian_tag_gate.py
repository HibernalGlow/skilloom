#!/usr/bin/env python3
"""Tests for the shared kaodian-tag gate (E820/E821/E822/W823)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from legal_kaodian_tag_gate import validate_kaodian_tags


def codes(findings):
    return [(finding.level, finding.code) for finding in findings]


def test_marknote_heading_tag_passes():
    text = "\n".join([
        "# 民法专题",
        "",
        "## 善意取得 #法考/民法/所有权/善意取得#",
        '{: custom-qb-note-topic-id="civil-property-good-faith-acquisition"}',
        "",
        "善意取得是 **所有权** 取得制度的一种。",
    ])
    assert codes(validate_kaodian_tags(text, "legal-marknote")) == []


def test_marknote_missing_tag_reports_e820():
    text = "\n".join([
        "## 善意取得",
        '{: custom-qb-note-topic-id="civil-property-good-faith-acquisition"}',
        "",
        "正文。",
    ])
    assert ("E", "820") in codes(validate_kaodian_tags(text, "legal-marknote"))


def test_marknote_anchor_with_standalone_tag_paragraph_passes():
    text = "\n".join([
        "**考点：占有改定**",
        '{: custom-qb-note-topic-id="civil-property-possession-agreement"}',
        "",
        "#法考/民法/占有/定义#",
        "",
        "正文。",
    ])
    assert codes(validate_kaodian_tags(text, "legal-marknote")) == []


def test_marknote_gate_silent_without_require_tags():
    text = "## 善意取得\n{: custom-qb-note-topic-id=\"civil-x\"}\n"
    assert validate_kaodian_tags(text, "legal-marknote", require_tags=False) == []


def test_goldquest_heading_tag_passes():
    text = "\n".join([
        "##### [合同解释·选择] 1. #法考/民法/合同法/合同解释#",
        '{: custom-qb-id="civil-gold-2020-001" custom-qb-question-topic-ids="civil-contract-validity" custom-qb-answer="A"}',
        "* 甲与乙签订合同。",
    ])
    assert codes(validate_kaodian_tags(text, "legal-goldquest")) == []


def test_goldquest_missing_tag_reports_e820():
    text = "\n".join([
        "##### [合同解释·选择] 1.",
        '{: custom-qb-id="civil-gold-2020-001" custom-qb-question-topic-ids="civil-contract-validity" custom-qb-answer="A"}',
        "* 甲与乙签订合同。",
    ])
    assert ("E", "820") in codes(validate_kaodian_tags(text, "legal-goldquest"))


def test_goldquest_tag_inside_stem_reports_e822():
    text = "\n".join([
        "##### [合同解释·选择] 1. #法考/民法/合同法/合同解释#",
        '{: custom-qb-id="civil-gold-2020-001" custom-qb-question-topic-ids="civil-contract-validity" custom-qb-answer="A"}',
        "* 甲与乙签订合同 #法考/民法/合同法/合同解释#。",
    ])
    findings = codes(validate_kaodian_tags(text, "legal-goldquest"))
    assert ("E", "822") in findings


def test_unclosed_tag_reports_e821():
    text = "见 #法考/民法/合同法/合同解释 的讨论。"
    assert ("E", "821") in codes(validate_kaodian_tags(text, "legal-marknote"))


def test_tag_inside_fence_reports_e822():
    text = "\n".join([
        "```md",
        "#法考/民法/物权#",
        "```",
    ])
    findings = codes(validate_kaodian_tags(text, "legal-goldquest"))
    assert ("E", "822") in findings


def test_tag_outside_vocabulary_reports_w823():
    text = "\n".join([
        "## 临时考点 #法考/不存在科目/不存在考点#",
        '{: custom-qb-note-topic-id="civil-temp"}',
    ])
    assert ("W", "823") in codes(validate_kaodian_tags(text, "legal-marknote"))


def test_vocabulary_tag_has_no_w823():
    text = "\n".join([
        "## 物权 #法考/民法/物权#",
        '{: custom-qb-note-topic-id="civil-property"}',
    ])
    assert ("W", "823") not in codes(validate_kaodian_tags(text, "legal-marknote"))
