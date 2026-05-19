#!/usr/bin/env python3
"""Guard the current Phase 1 scripts-plus-workflow closure packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

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

MARKERS = {
    SCRIPTS_README_REL: (
        "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, and closure-validator packet explicit from the scripts root",
        "- `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default",
    ),
    SHARED_REMINDER_CHECKER_REL: (
        '"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""',
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
    ),
    STRING_REVIEW_CHECKER_REL: (
        "STRING_REVIEW_RULE_LINE = (",
        'print("phase1-string-review-packet:ok")',
    ),
    DIRECT_OWNER_CHECKER_REL: (
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
        'print("phase1-direct-owner-markers:ok")',
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
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}

FORBIDDEN_FRAGMENTS = {
    SCRIPTS_README_REL: (
        "`scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`",
    ),
    CLOSURE_NOTE_REL: (
        "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    ),
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_absent(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 0 else [f"{label}:forbidden:actual_count={count}:{needle}"]


def require_exact_line(text: str, label: str, needle: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == needle)
    return [] if count == 1 else [f"{label}:expected_line_once:actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            if relative_path == WORKFLOW_REL:
                failures.extend(require_exact_line(text, relative_path.as_posix(), marker))
            else:
                failures.extend(
                    require_exact_occurrence(text, relative_path.as_posix(), marker)
                )
        for forbidden in FORBIDDEN_FRAGMENTS.get(relative_path, ()):
            failures.extend(require_absent(text, relative_path.as_posix(), forbidden))

    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, "\n".join(MARKERS[relative_path]) + "\n")


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    if marker + "\n" in text:
        target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")
        return
    if marker in text:
        target.write_text(text.replace(marker, "", 1), encoding="utf-8")
        return
    raise AssertionError(f"missing marker in fixture: {marker}")


def add_forbidden(root: Path, relative_path: Path, forbidden: str) -> None:
    target = root / relative_path
    target.write_text(target.read_text(encoding="utf-8") + forbidden + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = [
        ("missing_scripts_readme", lambda root: (root / SCRIPTS_README_REL).unlink()),
        (
            "missing_scripts_flow_marker",
            lambda root: remove_marker(root, SCRIPTS_README_REL, MARKERS[SCRIPTS_README_REL][0]),
        ),
        (
            "missing_scripts_validation_marker",
            lambda root: remove_marker(root, SCRIPTS_README_REL, MARKERS[SCRIPTS_README_REL][1]),
        ),
        (
            "missing_shared_reminder_checker_file",
            lambda root: (root / SHARED_REMINDER_CHECKER_REL).unlink(),
        ),
        (
            "missing_shared_reminder_checker_marker",
            lambda root: remove_marker(
                root,
                SHARED_REMINDER_CHECKER_REL,
                MARKERS[SHARED_REMINDER_CHECKER_REL][1],
            ),
        ),
        (
            "missing_closure_validator_file",
            lambda root: (root / CLOSURE_VALIDATOR_REL).unlink(),
        ),
        (
            "missing_closure_note_shared_checker_bullet",
            lambda root: remove_marker(root, CLOSURE_NOTE_REL, MARKERS[CLOSURE_NOTE_REL][0]),
        ),
        (
            "missing_build_smoke_name",
            lambda root: remove_marker(root, TESTS_BUILD_REL, MARKERS[TESTS_BUILD_REL][1]),
        ),
        (
            "missing_smoke_vsprintf_decl",
            lambda root: remove_marker(root, SMOKE_TEST_REL, MARKERS[SMOKE_TEST_REL][6]),
        ),
        (
            "missing_workflow_shared_selftest",
            lambda root: remove_marker(root, WORKFLOW_REL, MARKERS[WORKFLOW_REL][1]),
        ),
        (
            "missing_workflow_smoke_route",
            lambda root: remove_marker(root, WORKFLOW_REL, MARKERS[WORKFLOW_REL][3]),
        ),
        (
            "forbidden_scripts_fragment",
            lambda root: add_forbidden(
                root,
                SCRIPTS_README_REL,
                FORBIDDEN_FRAGMENTS[SCRIPTS_README_REL][0],
            ),
        ),
        (
            "forbidden_closure_marker",
            lambda root: add_forbidden(
                root,
                CLOSURE_NOTE_REL,
                FORBIDDEN_FRAGMENTS[CLOSURE_NOTE_REL][0],
            ),
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="phase1-scripts-workflow-packet-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print(f"self-test:baseline:unexpected={failures}")
            return 1

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-scripts-workflow-packet-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            mutate(root)
            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_SCRIPTS_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SCRIPTS_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the checker self-test")
    args = parser.parse_args()

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
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
