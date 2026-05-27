#!/usr/bin/env python3
"""Guard the current Phase 1 reminder packet shared by closure, scripts, and tests notes."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")

CURRENT_REMINDER_PACKET = [
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
]

EXPECTED_CLOSURE_PACKET_LINE = (
    "- `PHASE1_CURRENT_REMINDER_PACKET="
    + ",".join(CURRENT_REMINDER_PACKET)
    + "`"
)

EXPECTED_SCRIPTS_LINES = [
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bitmap-direct-anchors.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bitmap direct-anchor, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zigux/tests/phase1_host_tools_smoke.zig` remain the current reminder-surface companions for that packet",
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
]

EXPECTED_TESTS_ROUTE_LINES = [
    "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "  * current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
]

TESTS_PACKET_HEADER = "  * current direct-readback Phase 1 reminder packet:"
TESTS_PACKET_FOOTER = "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`"


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative: Path) -> str:
    path = root / relative
    return path.read_text(encoding="utf-8")


def exact_count_failures(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    if count == 1:
        return []
    return [f"{label}:expected=1:actual={count}"]


def extract_bullet_block(text: str, start_marker: str, end_marker: str) -> list[str]:
    try:
        start = text.index(start_marker) + len(start_marker)
        end = text.index(end_marker, start)
    except ValueError as exc:
        raise ValueError(f"missing_block_marker:{exc}") from exc

    items: list[str] = []
    for raw_line in text[start:end].splitlines():
        line = raw_line.strip()
        if line.startswith("- `") and line.endswith("`") and "=" not in line:
            items.append(line[3:-1])
    return items


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative in (CLOSURE_REL, SCRIPTS_README_REL, TESTS_README_REL):
        if not (root / relative).is_file():
            failures.append(f"missing_file:{relative.as_posix()}")
    if failures:
        return failures

    closure_text = read_text(root, CLOSURE_REL)
    scripts_text = read_text(root, SCRIPTS_README_REL)
    tests_text = read_text(root, TESTS_README_REL)

    failures.extend(
        exact_count_failures(
            closure_text,
            f"{CLOSURE_REL.as_posix()}:current_reminder_packet_line",
            EXPECTED_CLOSURE_PACKET_LINE,
        )
    )

    try:
        closure_items = extract_bullet_block(
            closure_text,
            "## Current Reminder Packet",
            "## Helper-Local Direct Anchor Reminder",
        )
    except ValueError as exc:
        failures.append(f"{CLOSURE_REL.as_posix()}:{exc}")
        closure_items = []
    if closure_items and closure_items != CURRENT_REMINDER_PACKET:
        failures.append(f"{CLOSURE_REL.as_posix()}:current_reminder_packet_items_drift")

    for line in EXPECTED_SCRIPTS_LINES:
        failures.extend(
            exact_count_failures(
                scripts_text,
                f"{SCRIPTS_README_REL.as_posix()}:marker",
                line,
            )
        )

    try:
        tests_items = extract_bullet_block(tests_text, TESTS_PACKET_HEADER, TESTS_PACKET_FOOTER)
    except ValueError as exc:
        failures.append(f"{TESTS_README_REL.as_posix()}:{exc}")
        tests_items = []
    expected_tests_items = CURRENT_REMINDER_PACKET[:-1] + ["zigux/tests/README.md"]
    if tests_items and tests_items != expected_tests_items:
        failures.append(f"{TESTS_README_REL.as_posix()}:current_direct_readback_packet_items_drift")

    for line in EXPECTED_TESTS_ROUTE_LINES:
        failures.extend(
            exact_count_failures(
                tests_text,
                f"{TESTS_README_REL.as_posix()}:route_marker",
                line,
            )
        )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_closure_text() -> str:
    bullet_lines = "\n".join(f"- `{item}`" for item in CURRENT_REMINDER_PACKET)
    return (
        "# Phase 1 Closure\n\n"
        "## Current Reminder Packet\n\n"
        f"{bullet_lines}\n\n"
        f"{EXPECTED_CLOSURE_PACKET_LINE}\n\n"
        "## Helper-Local Direct Anchor Reminder\n\n"
        "placeholder\n"
    )


def sample_scripts_text() -> str:
    return "# scripts/zigux\n\n## Phase 1\n\n" + "\n".join(EXPECTED_SCRIPTS_LINES) + "\n"


def sample_tests_text() -> str:
    test_items = CURRENT_REMINDER_PACKET[:-1] + ["zigux/tests/README.md"]
    bullet_lines = "\n".join(f"- `{item}`" for item in test_items)
    return (
        "# zigux/tests\n\n"
        "## Phase 1 host-tools review packet\n\n"
        f"{TESTS_PACKET_HEADER}\n"
        f"{bullet_lines}\n\n"
        f"{EXPECTED_TESTS_ROUTE_LINES[0]}\n"
        f"{EXPECTED_TESTS_ROUTE_LINES[1]}\n"
    )


def write_sample_root(root: Path) -> None:
    write_text(root / CLOSURE_REL, sample_closure_text())
    write_text(root / SCRIPTS_README_REL, sample_scripts_text())
    write_text(root / TESTS_README_REL, sample_tests_text())


def run_self_test() -> int:
    cases = 0

    with tempfile.TemporaryDirectory(prefix="phase1-reminder-packet-") as tmp:
        root = Path(tmp)
        write_sample_root(root)

        baseline_failures = collect_failures(root)
        if baseline_failures:
            raise AssertionError(("baseline", baseline_failures))
        cases += 1

        write_text(root / CLOSURE_REL, sample_closure_text().replace(EXPECTED_CLOSURE_PACKET_LINE + "\n", "", 1))
        failures = collect_failures(root)
        if f"{CLOSURE_REL.as_posix()}:current_reminder_packet_line:expected=1:actual=0" not in failures:
            raise AssertionError(("missing_closure_packet_line", failures))
        cases += 1

        write_sample_root(root)
        missing_closure_item = sample_closure_text().replace("- `scripts/zigux/check-phase1-bench.py`\n", "", 1)
        write_text(root / CLOSURE_REL, missing_closure_item)
        failures = collect_failures(root)
        if f"{CLOSURE_REL.as_posix()}:current_reminder_packet_items_drift" not in failures:
            raise AssertionError(("missing_closure_item", failures))
        cases += 1

        write_sample_root(root)
        stale_scripts = sample_scripts_text().replace(
            "`scripts/zigux/check-phase1-bench.py`",
            "`scripts/zigux/check-phase1-bench-current-packet.py`",
            1,
        )
        write_text(root / SCRIPTS_README_REL, stale_scripts)
        failures = collect_failures(root)
        if not any(failure.startswith(f"{SCRIPTS_README_REL.as_posix()}:marker:expected=1:actual=0") for failure in failures):
            raise AssertionError(("stale_scripts_marker", failures))
        cases += 1

        write_sample_root(root)
        reordered_tests = sample_tests_text().replace(
            "- `Documentation/zigux/phase1-closure.md`\n- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`\n",
            "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`\n- `Documentation/zigux/phase1-closure.md`\n",
            1,
        )
        write_text(root / TESTS_README_REL, reordered_tests)
        failures = collect_failures(root)
        if f"{TESTS_README_REL.as_posix()}:current_direct_readback_packet_items_drift" not in failures:
            raise AssertionError(("reordered_tests_items", failures))
        cases += 1

        write_sample_root(root)
        write_text(root / TESTS_README_REL, sample_tests_text().replace(EXPECTED_TESTS_ROUTE_LINES[0] + "\n", "", 1))
        failures = collect_failures(root)
        if f"{TESTS_README_REL.as_posix()}:route_marker:expected=1:actual=0" not in failures:
            raise AssertionError(("missing_tests_route_marker", failures))
        cases += 1

        write_sample_root(root)
        (root / TESTS_README_REL).unlink()
        failures = collect_failures(root)
        if f"missing_file:{TESTS_README_REL.as_posix()}" not in failures:
            raise AssertionError(("missing_tests_file", failures))
        cases += 1

    print("PHASE1_REMINDER_PACKET_MEMBERS_SELF_TEST=pass")
    print(f"PHASE1_REMINDER_PACKET_MEMBERS_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="Write a current-like minimal sample root for replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_REMINDER_PACKET_MEMBERS=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_REMINDER_PACKET_MEMBERS=pass")
    print(f"PHASE1_REMINDER_PACKET_MEMBERS_CLOSURE={CLOSURE_REL.as_posix()}")
    print(f"PHASE1_REMINDER_PACKET_MEMBERS_SCRIPTS={SCRIPTS_README_REL.as_posix()}")
    print(f"PHASE1_REMINDER_PACKET_MEMBERS_TESTS={TESTS_README_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
