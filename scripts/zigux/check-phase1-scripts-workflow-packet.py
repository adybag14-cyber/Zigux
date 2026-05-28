#!/usr/bin/env python3
"""Guard the current Phase 1 scripts-plus-workflow closure packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

SCRIPTS_README_REL = Path("scripts/zigux/README.md")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
SMOKE_TEST_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    SCRIPTS_README_REL,
    SHARED_REMINDER_CHECKER_REL,
    STRING_REVIEW_CHECKER_REL,
    DIRECT_OWNER_CHECKER_REL,
    BENCH_CHECKER_REL,
    CLOSURE_VALIDATOR_REL,
    CLOSURE_NOTE_REL,
    TESTS_BUILD_REL,
    SMOKE_TEST_REL,
    WORKFLOW_REL,
)

REQUIRED_MARKERS = {
    SCRIPTS_README_REL: (
        "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "- `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default",
    ),
    SHARED_REMINDER_CHECKER_REL: (
        '"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""',
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
    ),
    STRING_REVIEW_CHECKER_REL: (
        "EXPECTED_STRING_SOURCE_SYMBOLS = [",
        'print("phase1-string-review-packet:ok")',
    ),
    DIRECT_OWNER_CHECKER_REL: (
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
        'print("PHASE1_DIRECT_OWNER_MARKERS=pass")',
    ),
    BENCH_CHECKER_REL: (
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        "def run_self_test() -> None:",
    ),
    CLOSURE_VALIDATOR_REL: (
        "PHASE1_CLOSURE_VALIDATION=pass",
        "PHASE1_CLOSURE_SELF_TEST=pass",
    ),
    CLOSURE_NOTE_REL: (
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    TESTS_BUILD_REL: (
        'root_source_file = b.path("phase1_host_tools_smoke.zig"),',
        '.name = "phase1-host-tools-smoke",',
        'root_module.addImport("slab", slab_module);',
        'root_module.addImport("str_error_r", str_error_r_module);',
        'root_module.addImport("vsprintf", vsprintf_module);',
        'root_module.addImport("zalloc", zalloc_module);',
    ),
    SMOKE_TEST_REL: (
        'const slab = @import("slab");',
        'const str_error_r = @import("str_error_r");',
        'const vsprintf = @import("vsprintf");',
        'const zalloc = @import("zalloc");',
        'try std.testing.expect(@hasDecl(slab, "kmallocBytes"));',
        'try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));',
        'try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));',
        'try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));',
    ),
    WORKFLOW_REL: (
        "- name: Self-test current Phase 1 direct-owner checker",
        "- name: Check current Phase 1 direct-owner markers",
        "- name: Self-test current Phase 1 string review checker",
        "- name: Check current Phase 1 string review packet",
        "- name: Self-test current Phase 1 bench checker",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "- name: Self-test current Phase 1 shared reminder checker",
        "- name: Check current Phase 1 shared reminder packet",
        "- name: Self-test current Phase 1 closure validator",
        "- name: Check current Phase 1 closure packet",
        "- name: Run current Phase 1 shared tests-root smoke",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}

FORBIDDEN_MARKERS = {
    SCRIPTS_README_REL: (
        "`scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`",
    ),
    CLOSURE_NOTE_REL: (
        "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}:{marker}"]


def require_absent(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}:{marker}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_exact_occurrence(
                    text,
                    relative_path.as_posix(),
                    marker,
                )
            )

    for relative_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_absent(
                    text,
                    relative_path.as_posix(),
                    marker,
                )
            )

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, str | None, str]] = [("baseline", None, "ok")]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", relative_path.as_posix(), "remove_file"))
    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            token = f"{relative_path.as_posix()}::{marker}"
            cases.append((f"missing_marker:{relative_path.as_posix()}", token, "remove_marker"))
            cases.append((f"duplicate_marker:{relative_path.as_posix()}", token, "duplicate_marker"))
    for relative_path, markers in FORBIDDEN_MARKERS.items():
        for marker in markers:
            cases.append((f"forbidden_marker:{relative_path.as_posix()}", f"{relative_path.as_posix()}::{marker}", "insert_forbidden"))

    for name, payload, mode in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-scripts-workflow-packet-") as tmp_dir:
            root = Path(tmp_dir)
            build_sample_root(root)

            if mode == "remove_file" and payload is not None:
                (root / payload).unlink()
            elif mode in {"remove_marker", "duplicate_marker", "insert_forbidden"} and payload is not None:
                path_text, marker = payload.split("::", 1)
                target = root / path_text
                text = target.read_text(encoding="utf-8")
                if mode == "remove_marker":
                    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")
                elif mode == "duplicate_marker":
                    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")
                else:
                    target.write_text(text + marker + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-scripts-workflow-packet-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-scripts-workflow-packet-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_SCRIPTS_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SCRIPTS_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a sample root for checker replay and exit",
    )
    args = parser.parse_args()

    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_SCRIPTS_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_SCRIPTS_WORKFLOW_PACKET=pass")
    print(f"PHASE1_SCRIPTS_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_SCRIPTS_WORKFLOW_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE1_SCRIPTS_WORKFLOW_PACKET_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
