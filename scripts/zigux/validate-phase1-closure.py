#!/usr/bin/env python3
"""Validate the current Phase 1 closure note against the live reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    MANIFEST_REL,
)

EXPECTED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_MARKERS = {
    "status": "`PHASE1_STATUS=parked`",
    "restore_state": "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "helper_count": "`PHASE1_HELPER_COUNT=13`",
    "reminder_packet": (
        "`PHASE1_CURRENT_REMINDER_PACKET="
        "Documentation/zigux/phase1-closure.md,"
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md,"
        "Documentation/zigux/README.md,"
        "Documentation/zigux/review-checklist.md,"
        "scripts/zigux/README.md,"
        "scripts/zigux/check-phase1-string-review-packet.py,"
        "scripts/zigux/check-phase1-direct-owner-markers.py,"
        "scripts/zigux/validate-phase1-closure.py,"
        "zigux/tests/README.md,"
        "zigux/tests/build.zig,"
        "zigux/tests/phase1_host_tools_smoke.zig,"
        "zigux/tests/fixtures/phase1_helper_manifest.json`"
    ),
    "gap_packet": (
        "`PHASE1_CURRENT_GAP_PACKET="
        "scripts/zigux/validate-phase1.py,"
        "scripts/zigux/check-phase1-parity.py,"
        "zigux/tests/phase1_helpers.zig,"
        "zigux/tests/phase1_bench.zig,"
        "zigux/tests/fixtures/phase1_bench_expectations.json,"
        "zigux/tests/fixtures/phase1_helpers_c_harness.c,"
        "zigux/Makefile`"
    ),
    "closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "next_step": (
        "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface against the restored closure note "
        "and closure validator`"
    ),
}

FORBIDDEN_MARKERS = (
    "`PHASE1_CLOSURE_RESTORE_STATE=docs_only`",
    "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=add scripts/zigux/validate-phase1-closure.py on current master and then sync one shared reminder surface against this restored closure note`",
    "scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-parity.py",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    if actual != expected:
        return [f"{label}:expected={expected!r}:actual={actual!r}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for label, marker in EXPECTED_MARKERS.items():
        failures.extend(
            require_exact_occurrence(closure_text, f"phase1_closure:{label}", marker)
        )

    for marker in FORBIDDEN_MARKERS:
        if marker in closure_text:
            failures.append(f"phase1_closure:forbidden={marker}")

    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    failures.extend(
        require_exact_value(f"{MANIFEST_REL.as_posix()}:phase", manifest.get("phase"), "Phase 1")
    )
    failures.extend(
        require_exact_value(f"{MANIFEST_REL.as_posix()}:status", manifest.get("status"), "closed")
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:helper_count",
            manifest.get("helper_count"),
            len(EXPECTED_HELPERS),
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:helpers",
            manifest.get("helpers"),
            EXPECTED_HELPERS,
        )
    )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")

    write_text(
        root / PHASE1_CLOSURE_REL,
        "\n".join(
            [
                "# Phase 1 Closure",
                "",
                EXPECTED_MARKERS["status"],
                EXPECTED_MARKERS["restore_state"],
                EXPECTED_MARKERS["helper_count"],
                EXPECTED_MARKERS["reminder_packet"],
                EXPECTED_MARKERS["gap_packet"],
                EXPECTED_MARKERS["closure_validator"],
                EXPECTED_MARKERS["shared_tests_route"],
                EXPECTED_MARKERS["validator_state"],
                EXPECTED_MARKERS["next_step"],
                "",
            ]
        ),
    )
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": EXPECTED_HELPERS,
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    cases = [
        ("baseline", None, True),
        (
            "missing_restore_state",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(
                    load_text(root, PHASE1_CLOSURE_REL),
                    EXPECTED_MARKERS["restore_state"],
                    "`PHASE1_CLOSURE_RESTORE_STATE=docs_only`",
                ),
            ),
            False,
        ),
        (
            "missing_validator_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(
                    load_text(root, PHASE1_CLOSURE_REL),
                    EXPECTED_MARKERS["closure_validator"],
                    "`PHASE1_CLOSURE_VALIDATOR=missing`",
                ),
            ),
            False,
        ),
        (
            "missing_file",
            lambda root: (root / PHASE1_SMOKE_REL).unlink(),
            False,
        ),
        (
            "bad_helper_count",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": 12,
                        "helpers": EXPECTED_HELPERS,
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "bad_helper_list",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": len(EXPECTED_HELPERS),
                        "helpers": EXPECTED_HELPERS[:-1],
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "forbidden_old_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL) + "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`\n",
            ),
            False,
        ),
    ]

    for name, mutate, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-selftest-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            ok = not failures
            if ok != expect_ok:
                print(f"phase1-closure-self-test:{name}:unexpected={failures}")
                return 1

    print("PHASE1_CLOSURE_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run validator self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print("PHASE1_CLOSURE_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
