#!/usr/bin/env python3
"""Guard the live Phase 1 reminder packet against missing checker and marker drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_ROOT_REL = Path("scripts/zigux/README.md")
TESTS_ROOT_REL = Path("zigux/tests/README.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
SMOKE_ROUTE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
CHECKER_RELS = (
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-bitmap-review-packet.py"),
    Path("scripts/zigux/check-phase1-find-bit-clump.py"),
    Path("scripts/zigux/check-phase1-rbtree-review-packet.py"),
)

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    LANE_NOTE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_ROOT_REL,
    TESTS_ROOT_REL,
    MANIFEST_REL,
    TESTS_BUILD_REL,
    SMOKE_ROUTE_REL,
    *CHECKER_RELS,
)

PHASE1_CURRENT_REMINDER_PACKET = (
    "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,"
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,"
    "Documentation/zigux/review-checklist.md,scripts/zigux/README.md,"
    "scripts/zigux/check-phase1-string-review-packet.py,"
    "scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,"
    "scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,"
    "zigux/tests/phase1_host_tools_smoke.zig,zigux/tests/fixtures/phase1_helper_manifest.json`"
)

PHASE1_SHARED_TESTS_ROUTE = (
    "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`"
)

PHASE1_ACTIVE_PACKET = (
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,"
    "Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,"
    "zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,"
    "scripts/zigux/check-phase1-string-review-packet.py,"
    "scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py`"
)

SCRIPTS_LIVE_GUARDS = (
    "- `scripts/zigux/check-phase1-string-review-packet.py`, "
    "`scripts/zigux/check-phase1-direct-owner-markers.py`, "
    "`scripts/zigux/check-phase1-bench.py`, and "
    "`scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, "
    "direct-owner, bench, and closure-validator packet explicit from the scripts root"
)

SCRIPTS_SELF_TESTS = (
    "- `python3 scripts/zigux/validate-phase1-closure.py`, "
    "`python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, and "
    "`python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and "
    "`python3 scripts/zigux/check-phase1-bench.py --self-test` replay the shipped bounded Phase 1 reminder checks"
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    lane_text = load_text(root, LANE_NOTE_REL)
    scripts_text = load_text(root, SCRIPTS_ROOT_REL)

    failures.extend(
        require_exact_occurrence(
            closure_text,
            "phase1_closure:current_reminder_packet",
            PHASE1_CURRENT_REMINDER_PACKET,
        )
    )
    failures.extend(
        require_exact_occurrence(
            closure_text,
            "phase1_closure:shared_tests_route",
            PHASE1_SHARED_TESTS_ROUTE,
        )
    )
    failures.extend(
        require_exact_occurrence(
            lane_text,
            "phase1_lane_note:active_packet",
            PHASE1_ACTIVE_PACKET,
        )
    )
    failures.extend(
        require_exact_occurrence(
            scripts_text,
            "scripts_root:live_guards",
            SCRIPTS_LIVE_GUARDS,
        )
    )
    failures.extend(
        require_exact_occurrence(
            scripts_text,
            "scripts_root:self_tests",
            SCRIPTS_SELF_TESTS,
        )
    )

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, f"placeholder for {relative_path.as_posix()}\n")

    write_text(
        root,
        PHASE1_CLOSURE_REL,
        "# Phase 1 Closure\n\n"
        + PHASE1_CURRENT_REMINDER_PACKET
        + "\n"
        + PHASE1_SHARED_TESTS_ROUTE
        + "\n",
    )
    write_text(
        root,
        LANE_NOTE_REL,
        "# Phase 1 Host-Helper Lane Sequencing\n\n"
        + PHASE1_ACTIVE_PACKET
        + "\n",
    )
    write_text(
        root,
        SCRIPTS_ROOT_REL,
        "# scripts/zigux\n\n"
        + SCRIPTS_LIVE_GUARDS
        + "\n"
        + SCRIPTS_SELF_TESTS
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-reminder-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1

    cases = (
        ("missing_checker", CHECKER_RELS[-1], None, "missing_file"),
        ("missing_closure_marker", PHASE1_CLOSURE_REL, PHASE1_CURRENT_REMINDER_PACKET, "remove"),
        ("duplicate_closure_marker", PHASE1_CLOSURE_REL, PHASE1_CURRENT_REMINDER_PACKET, "duplicate"),
        ("missing_route_marker", PHASE1_CLOSURE_REL, PHASE1_SHARED_TESTS_ROUTE, "remove"),
        ("missing_lane_marker", LANE_NOTE_REL, PHASE1_ACTIVE_PACKET, "remove"),
        ("missing_scripts_live_guards", SCRIPTS_ROOT_REL, SCRIPTS_LIVE_GUARDS, "remove"),
        ("missing_scripts_self_tests", SCRIPTS_ROOT_REL, SCRIPTS_SELF_TESTS, "remove"),
    )

    for name, relative_path, marker, mode in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-reminder-packet-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            path = root / relative_path
            if mode == "missing_file":
                path.unlink()
            else:
                text = path.read_text(encoding="utf-8")
                if mode == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker, marker + "\n" + marker, 1)
                path.write_text(text, encoding="utf-8")

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE1_REMINDER_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-reminder-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
