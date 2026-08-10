#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("audit_topic_granularity.py")
SPEC = importlib.util.spec_from_file_location("audit_topic_granularity", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TopicGranularityGateTests(unittest.TestCase):
    def write(self, text: str) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        path = Path(temp.name) / "topics.md"
        path.write_text(text, encoding="utf-8")
        return temp, path

    def test_rejects_parent_topic_on_question(self) -> None:
        temp, path = self.write('''### 专题\n{: custom-qb-note-topic-id="civil-procedure"}\n\n### 细考点\n{: custom-qb-note-topic-id="civil-procedure-service" custom-qb-note-topic-parent-id="civil-procedure"}\n\n##### 1.\n{: custom-qb-id="q-1" custom-qb-question-topic-ids="civil-procedure" custom-qb-type="subjective"}\n''')
        try:
            self.assertIn("307", {item.code for item in MODULE.audit([path])})
        finally:
            temp.cleanup()

    def test_allows_explicit_exception_with_reason(self) -> None:
        temp, path = self.write('''### 专题\n{: custom-qb-note-topic-id="civil-procedure"}\n\n### 细考点\n{: custom-qb-note-topic-id="civil-procedure-service" custom-qb-note-topic-parent-id="civil-procedure"}\n\n##### 1.\n{: custom-qb-id="q-1" custom-qb-question-topic-ids="civil-procedure" custom-qb-topic-granularity-exception="本题仅考专题整体框架，无可复用细点" custom-qb-type="subjective"}\n''')
        try:
            self.assertNotIn("307", {item.code for item in MODULE.audit([path])})
        finally:
            temp.cleanup()

    def test_rejects_orphan_parent_declaration(self) -> None:
        temp, path = self.write('''### 细考点\n{: custom-qb-note-topic-id="civil-procedure-service" custom-qb-note-topic-parent-id="civil-procedure"}\n''')
        try:
            self.assertIn("308", {item.code for item in MODULE.audit([path])})
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
