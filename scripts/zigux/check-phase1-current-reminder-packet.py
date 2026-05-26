#!/usr/bin/env python3
"""Guard the current Phase 1 direct-readback reminder packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
SEQUENCING_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
REVIEW_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
DIRECT_ANCHOR_GATE_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")
BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
VALIDATE_CLOSURE_REL = Path("scripts/zigux/validate-phase1-closure.py")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
HOST_TOOLS_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
CHECKER_REL = Path("scripts/zigux/check-phase1-current-reminder-packet.py")

REQUIRED_FILES = (
    CLOSURE_REL,
    SEQUENCING_REL,
    DOCS_README_REL,
    REVIEW_REL,
    SCRIPTS_README_REL,
    STRING_REVIEW_REL,
    DIRECT_OWNER_REL,
    DIRECT_ANCHOR_GATE_REL,
    BENCH_REL,
    SHARED_REMINDER_REL,
    VALIDATE_CLOSURE_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    HOST_TOOLS_SMOKE_REL,
    WORKFLOW_REL,
    MANIFEST_REL,
    CHECKER_REL,
)

EXACT_LINE_MARKERS = {
    CLOSURE_REL: (
        "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    SEQUENCING_REL: (
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
    ),
    REVIEW_REL: (
        "  * if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, keep `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `zigux/Makefile` explicit as the adjacent Phase 1 route-summary evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?`",
    ),
    SCRIPTS_README_REL: (
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, and `zigux/tests/phase1_host_tools_smoke.zig` remain the current reminder-surface companions for that packet",
    ),
    TESTS_README_REL: (
        "  * current direct-readback Phase 1 reminder packet:",
        "- `Documentation/zigux/phase1-closure.md`",
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "- `Documentation/zigux/README.md`",
        "- `Documentation/zigux/review-checklist.md`",
        "- `scripts/zigux/README.md`",
        "- `scripts/zigux/check-phase1-string-review-packet.py`",
        "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
        "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
        "- `scripts/zigux/check-phase1-bench.py`",
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `scripts/zigux/validate-phase1-closure.py`",
        "- `zigux/tests/build.zig`",
        "- `zigux/tests/phase1_host_tools_smoke.zig`",
        "- `.github/workflows/zigux-bootstrap.yml`",
        "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
        "- `zigux/tests/README.md`",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}

EXPECTED_SNIPPETS = {
    CLOSURE_REL: (
        "- current authority: the committed helper manifest, this closure note, the narrow closure validator, the direct-anchor manifest gate, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche, while the route-summary checker stays an adjacent workflow and Makefile guard.",
    ),
    DOCS_README_REL: (
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `scripts/zigux/check-phase1-bench.py`",
        "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
    ),
}


def load_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def write_text(root: Path, relative: Path, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def exact_line_count(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker.strip())


def require_line_once(text: str, label: str, marker: str) -> list[str]:
    count = exact_line_count(text, marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_contains(text: str, label: str, snippet: str) -> list[str]:
    return [] if snippet in text else [f"{label}:missing"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            failures.append(f"missing_file:{relative.as_posix()}")
        elif not path.is_file():
            failures.append(f"non_file_path:{relative.as_posix()}")
    if failures:
        return failures

    for relative, markers in EXACT_LINE_MARKERS.items():
        text = load_text(root, relative)
        for marker in markers:
            failures.extend(
                require_line_once(text, f"{relative.as_posix()}:{marker}", marker)
            )

    for relative, snippets in EXPECTED_SNIPPETS.items():
        text = load_text(root, relative)
        for snippet in snippets:
            failures.extend(
                require_contains(text, f"{relative.as_posix()}:{snippet}", snippet)
            )

    return failures


def sample_text(relative: Path) -> str:
    lines = list(EXACT_LINE_MARKERS.get(relative, ()))
    snippets = list(EXPECTED_SNIPPETS.get(relative, ()))
    body = lines + snippets
    return "\n".join(body) + ("\n" if body else "")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    for relative in REQUIRED_FILES:
        write_text(root, relative, sample_text(relative))


def remove_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            return "\n".join(lines) + ("\n" if lines else "")
    raise AssertionError(f"missing sample marker: {marker}")


def duplicate_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"missing sample marker: {marker}")


def remove_snippet(text: str, snippet: str) -> str:
    if snippet not in text:
        raise AssertionError(f"missing sample snippet: {snippet}")
    return text.replace(snippet, "", 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-current-reminder-packet-") as tmpdir:
        base = Path(tmpdir)

        write_sample_root(base)
        if collect_failures(base):
            print("self-test:baseline_failed")
            return 1
        case_count += 1

        sample_root = base / "written-sample"
        write_sample_root(sample_root)
        if collect_failures(sample_root):
            print("self-test:written_sample_failed")
            return 1
        case_count += 1

        broken = base / "missing_checker"
        write_sample_root(broken)
        (broken / CHECKER_REL).unlink()
        if f"missing_file:{CHECKER_REL.as_posix()}" not in collect_failures(broken):
            print("self-test:missing_checker_not_detected")
            return 1
        case_count += 1

        broken = base / "missing_closure_packet"
        write_sample_root(broken)
        write_text(
            broken,
            CLOSURE_REL,
            remove_line(load_text(broken, CLOSURE_REL), EXACT_LINE_MARKERS[CLOSURE_REL][0]),
        )
        if not any(item.startswith(f"{CLOSURE_REL.as_posix()}:{EXACT_LINE_MARKERS[CLOSURE_REL][0]}") for item in collect_failures(broken)):
            print("self-test:missing_closure_packet_not_detected")
            return 1
        case_count += 1

        broken = base / "duplicate_tests_packet_item"
        write_sample_root(broken)
        write_text(
            broken,
            TESTS_README_REL,
            duplicate_line(
                load_text(broken, TESTS_README_REL),
                EXACT_LINE_MARKERS[TESTS_README_REL][8],
            ),
        )
        if not any(item.startswith(f"{TESTS_README_REL.as_posix()}:{EXACT_LINE_MARKERS[TESTS_README_REL][8]}") for item in collect_failures(broken)):
            print("self-test:duplicate_tests_packet_item_not_detected")
            return 1
        case_count += 1

        broken = base / "missing_workflow_line"
        write_sample_root(broken)
        write_text(
            broken,
            WORKFLOW_REL,
            remove_line(load_text(broken, WORKFLOW_REL), EXACT_LINE_MARKERS[WORKFLOW_REL][6]),
        )
        if not any(item.startswith(f"{WORKFLOW_REL.as_posix()}:{EXACT_LINE_MARKERS[WORKFLOW_REL][6]}") for item in collect_failures(broken)):
            print("self-test:missing_workflow_line_not_detected")
            return 1
        case_count += 1

        broken = base / "missing_scripts_line"
        write_sample_root(broken)
        write_text(
            broken,
            SCRIPTS_README_REL,
            remove_line(
                load_text(broken, SCRIPTS_README_REL),
                EXACT_LINE_MARKERS[SCRIPTS_README_REL][0],
            ),
        )
        if not any(item.startswith(f"{SCRIPTS_README_REL.as_posix()}:{EXACT_LINE_MARKERS[SCRIPTS_README_REL][0]}") for item in collect_failures(broken)):
            print("self-test:missing_scripts_line_not_detected")
            return 1
        case_count += 1

        broken = base / "missing_authority_snippet"
        write_sample_root(broken)
        write_text(
            broken,
            CLOSURE_REL,
            remove_snippet(load_text(broken, CLOSURE_REL), EXPECTED_SNIPPETS[CLOSURE_REL][0]),
        )
        if not any(item.startswith(f"{CLOSURE_REL.as_posix()}:{EXPECTED_SNIPPETS[CLOSURE_REL][0]}") for item in collect_failures(broken)):
            print("self-test:missing_authority_snippet_not_detected")
            return 1
        case_count += 1

    print("PHASE1_CURRENT_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CURRENT_REMINDER_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE1_CURRENT_REMINDER_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root.resolve())
    if failures:
        print("PHASE1_CURRENT_REMINDER_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CURRENT_REMINDER_PACKET=pass")
    print(f"PHASE1_CURRENT_REMINDER_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CURRENT_REMINDER_PACKET_REQUIRED_LINE_COUNT="
        f"{sum(len(markers) for markers in EXACT_LINE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
