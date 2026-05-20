#!/usr/bin/env python3
"""Validate the current Phase 1 closure note against the live reminder packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")
FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")
RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")
STRING_HELPER_REL = Path("tools/lib/string.zig")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    STRING_REVIEW_CHECKER_REL,
    DIRECT_OWNER_CHECKER_REL,
    BENCH_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    WORKFLOW_REL,
    MANIFEST_REL,
    BITMAP_HELPER_REL,
    FIND_BIT_HELPER_REL,
    RBTREE_HELPER_REL,
    STRING_HELPER_REL,
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

EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_MARKERS = {
    "status": "`PHASE1_STATUS=parked`",
    "restore_state": "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "helper_count": "`PHASE1_HELPER_COUNT=13`",
    "reminder_packet": (
        "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,"
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,"
        "Documentation/zigux/review-checklist.md,scripts/zigux/README.md,"
        "scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,"
        "scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,"
        "scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,"
        "zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,"
        "zigux/tests/fixtures/phase1_helper_manifest.json`"
    ),
    "gap_packet": (
        "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,"
        "zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,"
        "zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`"
    ),
    "closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "next_step": (
        "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker "
        "against the restored closure note, the closure validator, the shared tests-root smoke "
        "route, and the helper-specific next_safe_step_note entries in the committed manifest "
        "rather than widening back into the older validator-first or replay-side closure stack.`"
    ),
}

FORBIDDEN_MARKERS = {
    "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`",
}

DELEGATED_CHECKERS = (
    (STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet"),
    (DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers"),
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def run_checker(root: Path, script_rel: Path, label: str) -> list[str]:
    script_path = root / script_rel
    proc = subprocess.run(
        [sys.executable, str(script_path), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return []
    lines = []
    output = (proc.stdout + proc.stderr).splitlines()
    if not output:
        output = [f"{label}:checker_failed:returncode={proc.returncode}"]
    for line in output:
        lines.append(f"delegated:{label}:{line}")
    return lines


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for label, marker in EXPECTED_MARKERS.items():
        failures.extend(
            require_exact_occurrence(closure_text, f"{PHASE1_CLOSURE_REL.as_posix()}:{label}", marker)
        )
    for marker in FORBIDDEN_MARKERS:
        count = closure_text.count(marker)
        if count:
            failures.append(
                f"{PHASE1_CLOSURE_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}"
            )

    manifest = json.loads(load_text(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:phase", manifest.get("phase"), "Phase 1"))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:status", manifest.get("status"), "closed"))
    failures.extend(
        require_exact_value(f"{MANIFEST_REL.as_posix()}:helper_count", manifest.get("helper_count"), len(EXPECTED_HELPERS))
    )
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:helpers", manifest.get("helpers"), EXPECTED_HELPERS))

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        failures.append(f"{MANIFEST_REL.as_posix()}:lane_sequencing:expected=dict:actual={type(lane_sequencing).__name__}")
        return failures
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.shared_replay_parked_helpers",
            lane_sequencing.get("shared_replay_parked_helpers"),
            EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.direct_anchor_followup_helpers",
            lane_sequencing.get("direct_anchor_followup_helpers"),
            EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
        )
    )

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        failures.append(f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}")
        return failures
    for helper in ("tools/lib/bitmap.zig", "tools/lib/find_bit.zig", "tools/lib/rbtree.zig", "tools/lib/string.zig"):
        if not isinstance(review_anchors.get(helper), dict):
            failures.append(f"{MANIFEST_REL.as_posix()}:review_anchors.{helper}:expected=dict")

    for script_rel, label in DELEGATED_CHECKERS:
        failures.extend(run_checker(root, script_rel, label))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_checker_stub(path: Path, ok: bool = True) -> None:
    body = (
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "if '--root' in sys.argv:\n"
        "    pass\n"
        f"print({'\'stub:ok\'' if ok else '\'stub:failure\''})\n"
        f"raise SystemExit({0 if ok else 1})\n"
    )
    write_text(path, body)


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
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                },
                "review_anchors": {
                    "tools/lib/bitmap.zig": {},
                    "tools/lib/find_bit.zig": {},
                    "tools/lib/rbtree.zig": {},
                    "tools/lib/string.zig": {},
                },
            },
            indent=2,
        )
        + "\n",
    )

    make_checker_stub(root / STRING_REVIEW_CHECKER_REL)
    make_checker_stub(root / DIRECT_OWNER_CHECKER_REL)


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        (
            "missing_restore_state",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(load_text(root, PHASE1_CLOSURE_REL), EXPECTED_MARKERS["restore_state"], "`PHASE1_CLOSURE_RESTORE_STATE=docs_only`"),
            ),
        ),
        (
            "old_next_step_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(
                    load_text(root, PHASE1_CLOSURE_REL),
                    EXPECTED_MARKERS["next_step"],
                    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface against the restored closure note and closure validator`",
                ),
            ),
        ),
        (
            "bad_helper_count",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps({**json.loads(load_text(root, MANIFEST_REL)), "helper_count": 99}, indent=2) + "\n",
            ),
        ),
        (
            "missing_string_checker",
            lambda root: (root / STRING_REVIEW_CHECKER_REL).unlink(),
        ),
        (
            "failing_direct_owner_checker",
            lambda root: make_checker_stub(root / DIRECT_OWNER_CHECKER_REL, ok=False),
        ),
        (
            "forbidden_old_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL) + "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-selftest-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-self-test:{name}:expected_failure")
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

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print("PHASE1_CLOSURE_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
