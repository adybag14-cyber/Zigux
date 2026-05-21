#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from collections import Counter
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")
START_HERE_HEADING = "Start here"
START_HERE_LINES = (
    "- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)",
    "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
    "- [Live Product Docs](../Documentation/zigux/README.md)",
    "- [Review Checklist](../Documentation/zigux/review-checklist.md)",
    "- [Freeze Map](../Documentation/zigux/freeze-map.md)",
    "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)",
)


def extract_start_here_block(readme: str) -> list[str] | None:
    lines = readme.splitlines()
    try:
        heading_index = lines.index(START_HERE_HEADING)
    except ValueError:
        return None

    block: list[str] = []
    started = False
    for line in lines[heading_index + 1 :]:
        if line.startswith("- "):
            block.append(line)
            started = True
            continue
        if not started and not line.strip():
            continue
        break
    return block


def collect_failures(root: Path) -> list[str]:
    readme = (root / README_PATH).read_text(encoding="utf-8")
    block = extract_start_here_block(readme)
    if block is None:
        return [f"missing-heading:{START_HERE_HEADING}"]

    failures: list[str] = []
    expected_counter = Counter(START_HERE_LINES)
    actual_counter = Counter(block)

    for line, expected_count in expected_counter.items():
        actual_count = actual_counter.get(line, 0)
        for _ in range(expected_count - actual_count):
            failures.append(f"missing-link:{line}")

    for line, actual_count in actual_counter.items():
        extra_count = actual_count - expected_counter.get(line, 0)
        for _ in range(extra_count):
            failures.append(f"unexpected-link:{line}")

    if not failures and tuple(block) != START_HERE_LINES:
        failures.append("wrong-order:start-here")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

Start here
- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)
- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)
- [Live Product Docs](../Documentation/zigux/README.md)
- [Review Checklist](../Documentation/zigux/review-checklist.md)
- [Freeze Map](../Documentation/zigux/freeze-map.md)
- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_start_here_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        if collect_failures(root):
            raise AssertionError("baseline Lane 01 Start here fixture should pass")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Start here\n", "", 1))
        failures = collect_failures(root)
        expected = [f"missing-heading:{START_HERE_HEADING}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing heading failures: {failures}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- [Live Product Docs](../Documentation/zigux/README.md)\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing-link:- [Live Product Docs](../Documentation/zigux/README.md)"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected live docs failures: {failures}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- [Review Checklist](../Documentation/zigux/review-checklist.md)\n",
                "- [Bootstrap Notes](../Documentation/zigux/phase2-toolchain-bootstrap-notes.md)\n",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing-link:- [Review Checklist](../Documentation/zigux/review-checklist.md)",
            "unexpected-link:- [Bootstrap Notes](../Documentation/zigux/phase2-toolchain-bootstrap-notes.md)",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected review checklist failures: {failures}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- [Freeze Map](../Documentation/zigux/freeze-map.md)\n"
                "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)\n",
                "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)\n"
                "- [Freeze Map](../Documentation/zigux/freeze-map.md)\n",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = ["wrong-order:start-here"]
        if failures != expected:
            raise AssertionError(f"unexpected ordering failures: {failures}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)\n",
                "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)\n"
                "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)\n",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "unexpected-link:- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected duplicate-link failures: {failures}")
        case_count += 1

    print("LANE01_BOOTSTRAP_START_HERE_LINKS_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_START_HERE_LINKS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 bootstrap README keeps its Start here links aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Start here fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Lane 01 bootstrap Start here link check passed.")
    print(f"LANE01_BOOTSTRAP_START_HERE_LINK_COUNT={len(START_HERE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
