#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
CONF_MANIFEST_REL = Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json")
CONFDATA_MANIFEST_REL = Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json")
KCONFIG_CASES_REL = Path("zigux/tests/fixtures/kconfig_bridge/cases.json")

CONF_COUNT_PREFIX = "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT="
CONFDATA_CASE_COUNT_PREFIX = "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT="
CONFDATA_COUNT_PREFIX = "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT="

REQUIRED_SECTION_MARKERS = (
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def replace_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"marker not found: {old}")
    return text.replace(old, new, 1)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def extract_count_payload(text: str, prefix: str) -> int | None:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        candidate = line
        if candidate.startswith("- "):
            candidate = candidate[2:].strip()
        if candidate.startswith("`") and candidate.endswith("`"):
            candidate = candidate[1:-1]
        if candidate.startswith(prefix):
            payload = candidate[len(prefix) :].strip()
            if not payload:
                return None
            try:
                return int(payload)
            except ValueError as exc:
                raise SystemExit(f"invalid integer payload in closure note for {prefix}: {payload}") from exc
    return None


def expected_counts(root: Path) -> tuple[int, int, int]:
    conf_manifest = read_json(root / CONF_MANIFEST_REL)
    confdata_manifest = read_json(root / CONFDATA_MANIFEST_REL)
    cases_payload = read_json(root / KCONFIG_CASES_REL)

    if not isinstance(conf_manifest, dict):
        raise SystemExit(f"invalid manifest shape: {root / CONF_MANIFEST_REL}")
    if not isinstance(confdata_manifest, dict):
        raise SystemExit(f"invalid manifest shape: {root / CONFDATA_MANIFEST_REL}")
    if not isinstance(cases_payload, dict):
        raise SystemExit(f"invalid cases shape: {root / KCONFIG_CASES_REL}")

    conf_anchors = conf_manifest.get("helper_local_anchors")
    confdata_anchors = confdata_manifest.get("helper_local_anchors")
    confdata_cases = cases_payload.get("confdata_cases")

    if not isinstance(conf_anchors, list) or not all(isinstance(item, str) for item in conf_anchors):
        raise SystemExit(f"invalid helper_local_anchors in {root / CONF_MANIFEST_REL}")
    if not isinstance(confdata_anchors, list) or not all(isinstance(item, str) for item in confdata_anchors):
        raise SystemExit(f"invalid helper_local_anchors in {root / CONFDATA_MANIFEST_REL}")
    if not isinstance(confdata_cases, list):
        raise SystemExit(f"invalid confdata_cases in {root / KCONFIG_CASES_REL}")

    return len(conf_anchors), len(confdata_cases), len(confdata_anchors)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    closure_text = read_text(root / PHASE2_CLOSURE_REL)
    conf_count, confdata_case_count, confdata_count = expected_counts(root)
    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_SECTION_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_SECTION_MARKER", marker))

    expected_line_map = (
        (CONF_COUNT_PREFIX, conf_count),
        (CONFDATA_CASE_COUNT_PREFIX, confdata_case_count),
        (CONFDATA_COUNT_PREFIX, confdata_count),
    )
    for prefix, expected in expected_line_map:
        payload = extract_count_payload(closure_text, prefix)
        if payload is None:
            issues.append(("MISSING_COUNT_SENTINEL", prefix))
            continue
        if payload != expected:
            issues.append(("MISMATCHED_COUNT_SENTINEL", f"{prefix}{payload}"))
        sentinel_line = f"- `{prefix}{expected}`"
        count = count_exact_lines(closure_text, sentinel_line)
        if count != 1:
            issues.append(("EXACT_SENTINEL_COUNT", f"{count}::{sentinel_line}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_KCONFIG_BRIDGE_COUNTS=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    closure_text = """# Phase 2 Closure

## Current Closure Packet

- `scripts/zigux/check-kconfig-bridge.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=28`
- `PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=15`
- `PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=28`
"""
    write_text(root / PHASE2_CLOSURE_REL, closure_text)
    write_text(
        root / CONF_MANIFEST_REL,
        json.dumps(
            {
                "helper_local_anchors": [f"conf anchor {index}" for index in range(28)],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / CONFDATA_MANIFEST_REL,
        json.dumps(
            {
                "helper_local_anchors": [f"confdata anchor {index}" for index in range(28)],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / KCONFIG_CASES_REL,
        json.dumps(
            {
                "confdata_cases": [{"name": f"case-{index}"} for index in range(15)],
            },
            indent=2,
        )
        + "\n",
    )


def write_sample_root(root: Path) -> int:
    build_self_test_root(root)
    print(f"PHASE2_KCONFIG_BRIDGE_COUNTS_SAMPLE_ROOT={root}")
    return 0


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_bridge_counts_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_SECTION_MARKER",
            "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=28",
                "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=27",
            ),
            encoding="utf-8",
        )
        assert (
            "MISMATCHED_COUNT_SENTINEL",
            "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=27",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "- `PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=15`\n",
                "",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_COUNT_SENTINEL",
            CONFDATA_CASE_COUNT_PREFIX,
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                "- `PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=28`\n",
                "- `PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=28`\n"
                "- `PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=28`\n",
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "EXACT_SENTINEL_COUNT",
            "2::- `PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=28`",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        confdata_manifest_path = root / CONFDATA_MANIFEST_REL
        confdata_manifest_path.write_text(
            json.dumps({"helper_local_anchors": [f"confdata anchor {index}" for index in range(27)]}, indent=2)
            + "\n",
            encoding="utf-8",
        )
        assert (
            "MISMATCHED_COUNT_SENTINEL",
            "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=28",
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_KCONFIG_BRIDGE_COUNTS_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_BRIDGE_COUNTS_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 closure note kconfig bridge count contract aligned."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root.resolve())

    conf_count, confdata_case_count, confdata_count = expected_counts(args.root.resolve())
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_BRIDGE_COUNTS=pass")
    print(f"PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT={conf_count}")
    print(f"PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT={confdata_case_count}")
    print(f"PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT={confdata_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
