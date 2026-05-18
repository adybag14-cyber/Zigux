#!/usr/bin/env python3
"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
)

MARKERS = {
    "Documentation/zigux/README.md": (
        "keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
        "`Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit",
        "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded current reminder checks",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    "Documentation/zigux/review-checklist.md": (
        "`Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` keep the shipped current-`master` Phase 1 reminder packet explicit",
        "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded live reminder checks",
    ),
    "scripts/zigux/README.md": (
        "`Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/validate-phase1-closure.py` remain the current reminder-surface companions for that packet",
        "current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it",
    ),
    "scripts/zigux/check-phase1-bench.py": (
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        "def run_self_test() -> None:",
    ),
    "scripts/zigux/validate-phase1-closure.py": (
        "PHASE1_CLOSURE_VALIDATION=pass",
        "PHASE1_CLOSURE_SELF_TEST=pass",
    ),
    "zigux/tests/README.md": (
        "current direct-readback Phase 1 reminder packet: `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py`",
        "the restored `Documentation/zigux/phase1-closure.md` note and `scripts/zigux/validate-phase1-closure.py` now keep the current-master-safe closure packet explicit from the tests root, while `scripts/zigux/check-phase1-bench.py` remains the shipped bench-side checker for the remaining shared reminder wording",
    ),
    "zigux/tests/build.zig": (
        'root_source_file = b.path("phase1_host_tools_smoke.zig"),',
        '.name = "phase1-host-tools-smoke",',
    ),
    "zigux/tests/phase1_host_tools_smoke.zig": (
        'const argv_split = @import("argv_split");',
        'try std.testing.expect(@hasDecl(bitmap, "setRange"));',
    ),
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    ),
}

FORBIDDEN_FRAGMENTS = (
    "`scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_stripped_line_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line.strip() == marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_forbidden_fragments(text: str, label: str) -> list[str]:
    issues: list[str] = []
    for fragment in FORBIDDEN_FRAGMENTS:
        count = text.count(fragment)
        if count != 0:
            issues.append(f"{label}:forbidden:{fragment}:actual={count}")
    return issues


def collect_missing_markers(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        if relative_path == ".github/workflows/zigux-bootstrap.yml":
            issues.extend(collect_stripped_line_markers(text, relative_path, markers))
        else:
            issues.extend(collect_exact_markers(text, relative_path, markers))
        issues.extend(collect_forbidden_fragments(text, relative_path))
    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        markers = MARKERS.get(relative_path, ())
        write_text(root, relative_path, "\n".join(markers) + ("\n" if markers else ""))


def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-shared-reminder-success-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_missing_markers(root)
        if issues:
            print("self-test:success:unexpected_failures")
            for item in issues:
                print(item)
            return 1

    cases = [
        ("missing_docs_root", lambda root: (root / "Documentation/zigux/README.md").unlink()),
        (
            "missing_docs_marker",
            lambda root: mutate_remove_marker(
                root,
                "Documentation/zigux/README.md",
                MARKERS["Documentation/zigux/README.md"][0],
            ),
        ),
        (
            "missing_docs_closure_companion_marker",
            lambda root: mutate_remove_marker(
                root,
                "Documentation/zigux/README.md",
                MARKERS["Documentation/zigux/README.md"][1],
            ),
        ),
        (
            "missing_docs_selftest_marker",
            lambda root: mutate_remove_marker(
                root,
                "Documentation/zigux/README.md",
                MARKERS["Documentation/zigux/README.md"][2],
            ),
        ),
        (
            "missing_closure_note",
            lambda root: (root / "Documentation/zigux/phase1-closure.md").unlink(),
        ),
        (
            "missing_closure_validator_file",
            lambda root: (root / "scripts/zigux/validate-phase1-closure.py").unlink(),
        ),
        (
            "missing_closure_marker",
            lambda root: mutate_remove_marker(
                root,
                "Documentation/zigux/phase1-closure.md",
                MARKERS["Documentation/zigux/phase1-closure.md"][0],
            ),
        ),
        (
            "missing_closure_shared_tests_route_marker",
            lambda root: mutate_remove_marker(
                root,
                "Documentation/zigux/phase1-closure.md",
                MARKERS["Documentation/zigux/phase1-closure.md"][1],
            ),
        ),
        (
            "missing_review_checklist_marker",
            lambda root: mutate_remove_marker(
                root,
                "Documentation/zigux/review-checklist.md",
                MARKERS["Documentation/zigux/review-checklist.md"][0],
            ),
        ),
        (
            "missing_review_checklist_selftest_marker",
            lambda root: mutate_remove_marker(
                root,
                "Documentation/zigux/review-checklist.md",
                MARKERS["Documentation/zigux/review-checklist.md"][1],
            ),
        ),
        (
            "missing_scripts_companion_marker",
            lambda root: mutate_remove_marker(
                root,
                "scripts/zigux/README.md",
                MARKERS["scripts/zigux/README.md"][0],
            ),
        ),
        (
            "missing_scripts_bench_marker",
            lambda root: mutate_remove_marker(
                root,
                "scripts/zigux/README.md",
                MARKERS["scripts/zigux/README.md"][1],
            ),
        ),
        (
            "duplicate_scripts_bench_marker",
            lambda root: mutate_duplicate_marker(
                root,
                "scripts/zigux/README.md",
                MARKERS["scripts/zigux/README.md"][1],
            ),
        ),
        (
            "missing_bench_checksum_anchor",
            lambda root: mutate_remove_marker(
                root,
                "scripts/zigux/check-phase1-bench.py",
                MARKERS["scripts/zigux/check-phase1-bench.py"][0],
            ),
        ),
        (
            "missing_bench_selftest_anchor",
            lambda root: mutate_remove_marker(
                root,
                "scripts/zigux/check-phase1-bench.py",
                MARKERS["scripts/zigux/check-phase1-bench.py"][1],
            ),
        ),
        (
            "missing_validator_marker",
            lambda root: mutate_remove_marker(
                root,
                "scripts/zigux/validate-phase1-closure.py",
                MARKERS["scripts/zigux/validate-phase1-closure.py"][0],
            ),
        ),
        (
            "missing_validator_selftest_marker",
            lambda root: mutate_remove_marker(
                root,
                "scripts/zigux/validate-phase1-closure.py",
                MARKERS["scripts/zigux/validate-phase1-closure.py"][1],
            ),
        ),
        (
            "missing_tests_build_root_marker",
            lambda root: mutate_remove_marker(
                root,
                "zigux/tests/build.zig",
                MARKERS["zigux/tests/build.zig"][0],
            ),
        ),
        (
            "missing_tests_build_route_marker",
            lambda root: mutate_remove_marker(
                root,
                "zigux/tests/build.zig",
                MARKERS["zigux/tests/build.zig"][1],
            ),
        ),
        (
            "missing_tests_smoke_import_marker",
            lambda root: mutate_remove_marker(
                root,
                "zigux/tests/phase1_host_tools_smoke.zig",
                MARKERS["zigux/tests/phase1_host_tools_smoke.zig"][0],
            ),
        ),
        (
            "missing_tests_smoke_anchor_marker",
            lambda root: mutate_remove_marker(
                root,
                "zigux/tests/phase1_host_tools_smoke.zig",
                MARKERS["zigux/tests/phase1_host_tools_smoke.zig"][1],
            ),
        ),
        (
            "missing_tests_direct_packet_marker",
            lambda root: mutate_remove_marker(
                root,
                "zigux/tests/README.md",
                MARKERS["zigux/tests/README.md"][0],
            ),
        ),
        (
            "missing_tests_closure_marker",
            lambda root: mutate_remove_marker(
                root,
                "zigux/tests/README.md",
                MARKERS["zigux/tests/README.md"][1],
            ),
        ),
        (
            "missing_workflow_bench_selftest",
            lambda root: mutate_remove_marker(
                root,
                ".github/workflows/zigux-bootstrap.yml",
                MARKERS[".github/workflows/zigux-bootstrap.yml"][0],
            ),
        ),
        (
            "missing_workflow_closure_validator",
            lambda root: mutate_remove_marker(
                root,
                ".github/workflows/zigux-bootstrap.yml",
                MARKERS[".github/workflows/zigux-bootstrap.yml"][1],
            ),
        ),
        (
            "duplicate_workflow_closure_validator",
            lambda root: mutate_duplicate_marker(
                root,
                ".github/workflows/zigux-bootstrap.yml",
                MARKERS[".github/workflows/zigux-bootstrap.yml"][1],
            ),
        ),
        (
            "missing_workflow_shared_reminder_selftest",
            lambda root: mutate_remove_marker(
                root,
                ".github/workflows/zigux-bootstrap.yml",
                MARKERS[".github/workflows/zigux-bootstrap.yml"][2],
            ),
        ),
        (
            "duplicate_workflow_shared_reminder_selftest",
            lambda root: mutate_duplicate_marker(
                root,
                ".github/workflows/zigux-bootstrap.yml",
                MARKERS[".github/workflows/zigux-bootstrap.yml"][2],
            ),
        ),
        (
            "duplicate_workflow_shared_reminder_live_check",
            lambda root: mutate_duplicate_marker(
                root,
                ".github/workflows/zigux-bootstrap.yml",
                MARKERS[".github/workflows/zigux-bootstrap.yml"][3],
            ),
        ),
        (
            "missing_workflow_shared_reminder_live_check",
            lambda root: mutate_remove_marker(
                root,
                ".github/workflows/zigux-bootstrap.yml",
                MARKERS[".github/workflows/zigux-bootstrap.yml"][3],
            ),
        ),
        (
            "forbidden_fragment",
            lambda root: write_text(
                root,
                "Documentation/zigux/README.md",
                read_text(root, "Documentation/zigux/README.md") + FORBIDDEN_FRAGMENTS[0] + "\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-shared-reminder-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            mutate(root)
            issues = collect_missing_markers(root)
            if not issues:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SHARED_REMINDER_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_missing_markers(repo_root(args.root))
    if issues:
        print("PHASE1_SHARED_REMINDER_PACKET=fail")
        for item in issues:
            print(item)
        return 1

    print("PHASE1_SHARED_REMINDER_PACKET=pass")
    print(f"PHASE1_SHARED_REMINDER_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_SHARED_REMINDER_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
