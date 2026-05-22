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
BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
VALIDATE_CLOSURE_REL = Path("scripts/zigux/validate-phase1-closure.py")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
HOST_TOOLS_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
CHECKER_REL = Path("scripts/zigux/check-phase1-current-reminder-packet.py")

REMINDER_PACKET_FILES = (
    CLOSURE_REL,
    SEQUENCING_REL,
    DOCS_README_REL,
    REVIEW_REL,
    SCRIPTS_README_REL,
    STRING_REVIEW_REL,
    DIRECT_OWNER_REL,
    BENCH_REL,
    SHARED_REMINDER_REL,
    VALIDATE_CLOSURE_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    HOST_TOOLS_SMOKE_REL,
    WORKFLOW_REL,
    MANIFEST_REL,
)

REQUIRED_FILES = REMINDER_PACKET_FILES + (CHECKER_REL,)

EXACT_LINE_MARKERS = {
    CLOSURE_REL: (
        "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    REVIEW_REL: (
        "  * if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    SCRIPTS_README_REL: (
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
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
        "- `scripts/zigux/check-phase1-bench.py`",
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `scripts/zigux/validate-phase1-closure.py`",
        "- `zigux/tests/build.zig`",
        "- `zigux/tests/phase1_host_tools_smoke.zig`",
        "- `.github/workflows/zigux-bootstrap.yml`",
        "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
        "- `zigux/tests/README.md`",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
        "- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
    ),
}

EXPECTED_TEXT_SNIPPETS = {
    CLOSURE_REL: (
        "- current authority: the committed helper manifest, this closure note, the narrow closure validator, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche, while the route-summary checker stays an adjacent workflow and Makefile guard.",
    ),
}


def load_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def write_text(root: Path, relative: Path, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
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
            failures.extend(require_once(text, f"{relative.as_posix()}:{marker}", marker))

    for relative, snippets in EXPECTED_TEXT_SNIPPETS.items():
        text = load_text(root, relative)
        for snippet in snippets:
            failures.extend(
                require_contains(text, f"{relative.as_posix()}:{snippet}", snippet)
            )

    return failures


def sample_text(relative: Path) -> str:
    lines = list(EXACT_LINE_MARKERS.get(relative, ()))
    extra = list(EXPECTED_TEXT_SNIPPETS.get(relative, ()))
    return "\n".join(lines + extra) + ("\n" if lines or extra else "")


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
        root = Path(tmpdir)

        write_sample_root(root)
        if collect_failures(root):
            print("self-test:baseline_failed")
            return 1
        case_count += 1

        sample_root = root / "sample-root"
        write_sample_root(sample_root)
        if collect_failures(sample_root):
            print("self-test:written_sample_failed")
            return 1
        case_count += 1

        broken_root = root / "missing_checker"
        write_sample_root(broken_root)
        (broken_root / CHECKER_REL).unlink()
        failures = collect_failures(broken_root)
        if f"missing_file:{CHECKER_REL.as_posix()}" not in failures:
            print("self-test:missing_checker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_closure_packet_line"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            CLOSURE_REL,
            remove_line(load_text(broken_root, CLOSURE_REL), EXACT_LINE_MARKERS[CLOSURE_REL][0]),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{CLOSURE_REL.as_posix()}:{EXACT_LINE_MARKERS[CLOSURE_REL][0]}") for item in failures):
            print("self-test:missing_closure_packet_line_not_detected")
            return 1
        case_count += 1

        broken_root = root / "duplicate_review_line"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            REVIEW_REL,
            duplicate_line(load_text(broken_root, REVIEW_REL), EXACT_LINE_MARKERS[REVIEW_REL][0]),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{REVIEW_REL.as_posix()}:{EXACT_LINE_MARKERS[REVIEW_REL][0]}") for item in failures):
            print("self-test:duplicate_review_line_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_tests_item"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            TESTS_README_REL,
            remove_line(load_text(broken_root, TESTS_README_REL), EXACT_LINE_MARKERS[TESTS_README_REL][7]),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{TESTS_README_REL.as_posix()}:{EXACT_LINE_MARKERS[TESTS_README_REL][7]}") for item in failures):
            print("self-test:missing_tests_item_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_scripts_line"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            SCRIPTS_README_REL,
            remove_line(load_text(broken_root, SCRIPTS_README_REL), EXACT_LINE_MARKERS[SCRIPTS_README_REL][0]),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{SCRIPTS_README_REL.as_posix()}:{EXACT_LINE_MARKERS[SCRIPTS_README_REL][0]}") for item in failures):
            print("self-test:missing_scripts_line_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_authority_snippet"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            CLOSURE_REL,
            remove_snippet(
                load_text(broken_root, CLOSURE_REL),
                EXPECTED_TEXT_SNIPPETS[CLOSURE_REL][0],
            ),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{CLOSURE_REL.as_posix()}:{EXPECTED_TEXT_SNIPPETS[CLOSURE_REL][0]}") for item in failures):
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
    args = parser.parse_args()

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
        "PHASE1_CURRENT_REMINDER_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_LINE_MARKERS.values()) + sum(len(snippets) for snippets in EXPECTED_TEXT_SNIPPETS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
