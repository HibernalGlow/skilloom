from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("audit_topic_links.py")
SPEC = importlib.util.spec_from_file_location("audit_topic_links", MODULE_PATH)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


class AuditTopicLinksTest(unittest.TestCase):
    def write_markdown(self, root: Path, name: str, content: str) -> Path:
        path = root / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_inventory_links_question_and_multiple_providers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_markdown(
                root,
                "linked.md",
                """# Notes

## Confirmed receipt permits electronic service
{: custom-qb-note-topic-id="civil-procedure-summary-service-confirmed-receipt"}

**考点：电子送达**
{: custom-qb-note-topic-id="civil-procedure-summary-service-confirmed-receipt"}

## Question 1
{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-procedure-summary-service-confirmed-receipt" custom-qb-type="single"}
""",
            )

            report = audit.build_report([path], fanout_threshold=8)

            self.assertEqual(report["summary"]["errors"], 0)
            self.assertEqual(report["summary"]["warnings"], 0)
            topic = report["topic_index"]["civil-procedure-summary-service-confirmed-receipt"]
            self.assertEqual(topic["question_count"], 1)
            self.assertEqual(topic["provider_count"], 2)

    def test_reports_missing_invalid_duplicate_and_unbound_topics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_markdown(
                root,
                "broken.md",
                """## Missing topics
{: custom-qb-id="civil-question-1"}

## Broken topics
{: custom-qb-id="civil-question-2" custom-qb-question-topic-ids="civil-topic,civil-topic,Bad Topic"}

## Bad provider
{: custom-qb-note-topic-id="civil-one,civil-two"}
""",
            )

            report = audit.build_report([path], fanout_threshold=8)
            codes = {finding["code"] for finding in report["findings"]}

            self.assertIn("missing-question-topics", codes)
            self.assertIn("duplicate-question-topic", codes)
            self.assertIn("invalid-question-topic", codes)
            self.assertIn("invalid-provider-topic", codes)
            self.assertIn("topic-without-provider", codes)

    def test_duplicate_question_ids_and_high_fanout_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_markdown(
                root,
                "fanout.md",
                """## Provider
{: custom-qb-note-topic-id="civil-procedure-execution"}

## Question 1
{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-procedure-execution"}

## Question 1 duplicate
{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-procedure-execution"}
""",
            )

            report = audit.build_report([path], fanout_threshold=2)
            codes = [finding["code"] for finding in report["findings"]]

            self.assertEqual(codes.count("duplicate-question-id"), 2)
            self.assertIn("high-fanout-topic", codes)

    def test_provider_without_question_is_informational(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_markdown(
                root,
                "provider.md",
                """## Provider
{: custom-qb-note-topic-id="civil-property-registration"}
""",
            )

            report = audit.build_report([path])

            self.assertEqual(report["summary"]["errors"], 0)
            self.assertEqual(report["summary"]["info"], 1)
            self.assertEqual(report["findings"][0]["code"], "provider-without-question")

    def test_mixed_direction_question_does_not_count_as_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_markdown(
                root,
                "mixed.md",
                """## Question
{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-topic" custom-qb-note-topic-id="civil-topic"}

## Orphan topic direction
{: custom-qb-question-topic-ids="civil-orphan-topic"}
""",
            )

            report = audit.build_report([path])
            codes = {finding["code"] for finding in report["findings"]}

            self.assertEqual(report["summary"]["provider_blocks"], 0)
            self.assertIn("mixed-topic-directions", codes)
            self.assertIn("orphan-question-topics", codes)
            self.assertIn("topic-without-provider", codes)


if __name__ == "__main__":
    unittest.main()
