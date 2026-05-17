#!/usr/bin/env python3
"""Validate the current-master-safe Phase 1 closure anchor."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

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

REQUIRED_NOTE_MARKERS = [
    "`PHASE1_STATUS=parked`",
    "`PHASE1_CLOSURE_RESTORE_STATE=partial`",
    "`PHASE1_HELPER_COUNT=13`",
    "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`PHASE1_SHARED_REMINDER_SYNC_STATE=pending`",
    "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c,zigux/Makefile`",
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
]

REQUIRED_README_MARKERS = [
    "restored closure anchor and narrow closure validator",
    "`python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/validate-phase1-closure.py --self-test`",
    "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/validate-phase1-closure.py`",
    "`Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/README.md`, and `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it",
]

FORBIDDEN_README_MARKERS = [
    "`Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`",
    "`scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`",
]

REQUIRED_BUILD_MARKERS = [
    'const phase1_step = b.step(',
    '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests"',
    '"phase1_host_tools_smoke.zig"',
]

REQUIRED_SMOKE_MARKERS = [
    '@hasDecl(argv_split, "argvSplit")',
    '@hasDecl(cmdline, "memparse")',
    '@hasDecl(find_bit, "findFirstBit")',
    '@hasDecl(bitmap, "setRange")',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_once(text: str, marker: str, label: str, failures: list[str]) -> None:
    count = text.count(marker)
    if count != 1:
        failures.append(f"{label}:expected=1:actual={count}")


def collect_failures(root: Path) -> list[str]:
    note_path = root / "Documentation/zigux/phase1-closure.md"
    readme_path = root / "scripts/zigux/README.md"
    manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    build_path = root / "zigux/tests/build.zig"
    smoke_path = root / "zigux/tests/phase1_host_tools_smoke.zig"

    failures: list[str] = []
    for path in (note_path, readme_path, manifest_path, build_path, smoke_path):
        if not path.exists():
            failures.append(f"missing_file:{path.relative_to(root).as_posix()}")
    if failures:
        return failures

    note_text = read_text(note_path)
    readme_text = read_text(readme_path)
    build_text = read_text(build_path)
    smoke_text = read_text(smoke_path)
    manifest = json.loads(read_text(manifest_path))

    for marker in REQUIRED_NOTE_MARKERS:
        require_once(note_text, marker, "phase1_closure_note", failures)
    for marker in REQUIRED_README_MARKERS:
        require_once(readme_text, marker, "scripts_readme", failures)
    for marker in FORBIDDEN_README_MARKERS:
        if marker in readme_text:
            failures.append(f"scripts_readme:forbidden={marker}")
    for marker in REQUIRED_BUILD_MARKERS:
        require_once(build_text, marker, "build_zig", failures)
    for marker in REQUIRED_SMOKE_MARKERS:
        require_once(smoke_text, marker, "phase1_host_tools_smoke", failures)

    if manifest.get("phase") != "Phase 1":
        failures.append("manifest:phase")
    if manifest.get("status") != "closed":
        failures.append("manifest:status")
    if manifest.get("helper_count") != 13:
        failures.append("manifest:helper_count")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        failures.append("manifest:helpers")

    return failures


def make_fixture_tree(root: Path) -> None:
    write_text(
        root / "Documentation/zigux/phase1-closure.md",
        """# Phase 1 Closure

This note restores a direct Lane 15 closure anchor in a current-master-safe form.

## Status

- `PHASE1_STATUS=parked`
- `PHASE1_CLOSURE_RESTORE_STATE=partial`
- `PHASE1_HELPER_COUNT=13`
- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`

The committed helper manifest remains the authority for the closed thirteen-helper tranche, while the older wider replay stack still needs a separate same-lane rebuild.

## Current Reminder Packet

The currently reviewable Phase 1 packet is:

- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
- `scripts/zigux/check-phase1-string-review-packet.py`
- `scripts/zigux/check-phase1-direct-owner-markers.py`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_host_tools_smoke.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`

- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,zigux/tests/fixtures/phase1_helper_manifest.json`
- `PHASE1_SHARED_REMINDER_SYNC_STATE=pending`

## Current Repo-Reality Gaps

Current `master` still does not directly materialize the broader validator-first and replay-side closure companions:

- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/check-phase1-parity.py`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`
- `zigux/Makefile`

- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c,zigux/Makefile`

Restoring this note does not claim those broader replay routes are back. It restores a directly readable closure anchor and records the exact gap that still separates the closed helper tranche from the older wider closure stack.

## Closure Validation

The current Lane 15 validation step stays narrow on purpose:

- `python3 scripts/zigux/validate-phase1-closure.py`
- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`

The validator checks this note against the committed helper manifest and the already-landed shared tests-root smoke anchor without pretending the older parity, bench, build, or make routes have returned.

- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`
- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`

## Next Step

The next same-lane follow-up is to realign the shared docs-root, scripts-root, and tests-root reminder surfaces around this restored closure anchor before widening back into replay-side helper or bench claims.

- `PHASE1_NEXT_SAFE_STEP=sync Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, scripts/zigux/README.md, and zigux/tests/README.md to this restored closure anchor before widening into zigux/tests/phase1_helpers.zig or bench claims`
""",
    )
    write_text(
        root / "scripts/zigux/README.md",
        """# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 1

- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards together with the restored closure anchor and narrow closure validator instead of rebuilding the broader installer-backed closure packet from older missing routes
- `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/validate-phase1-closure.py --self-test` replay the shipped bounded Phase 1 reminder checks
- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner marker, and closure-anchor packet explicit from the scripts root
- `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/README.md`, and `zigux/tests/fixtures/phase1_helper_manifest.json` remain the current reminder-surface companions for that packet
- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence
- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here
- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts
""",
    )
    write_text(
        root / "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": 13,
                "helpers": EXPECTED_HELPERS,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / "zigux/tests/build.zig",
        """const phase1_step = b.step(
    "phase1-host-tools-smoke",
    "Run the shared Phase 1 host-tools smoke anchor from zigux/tests",
);
const smoke_file = "phase1_host_tools_smoke.zig";
""",
    )
    write_text(
        root / "zigux/tests/phase1_host_tools_smoke.zig",
        """const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const find_bit = @import("find_bit");
const bitmap = @import("bitmap");

test "phase1 host-tools smoke imports the live helper modules" {
    try std.testing.expect(@hasDecl(argv_split, "argvSplit"));
    try std.testing.expect(@hasDecl(cmdline, "memparse"));
    try std.testing.expect(@hasDecl(find_bit, "findFirstBit"));
    try std.testing.expect(@hasDecl(bitmap, "setRange"));
}
""",
    )


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    cases = [
        ("baseline", None, True),
        (
            "missing_note_marker",
            lambda root: write_text(
                root / "Documentation/zigux/phase1-closure.md",
                replace_once(
                    read_text(root / "Documentation/zigux/phase1-closure.md"),
                    "`PHASE1_SHARED_REMINDER_SYNC_STATE=pending`",
                    "`PHASE1_SHARED_REMINDER_SYNC_STATE=drifted`",
                ),
            ),
            False,
        ),
        (
            "scripts_readme_missing_marker",
            lambda root: write_text(
                root / "scripts/zigux/README.md",
                replace_once(
                    read_text(root / "scripts/zigux/README.md"),
                    "restored closure anchor and narrow closure validator",
                    "owner-map and string-review guards",
                ),
            ),
            False,
        ),
        (
            "build_missing_marker",
            lambda root: write_text(
                root / "zigux/tests/build.zig",
                replace_once(
                    read_text(root / "zigux/tests/build.zig"),
                    '"phase1_host_tools_smoke.zig"',
                    '"phase1_host_tools_smoke_missing.zig"',
                ),
            ),
            False,
        ),
        (
            "smoke_missing_marker",
            lambda root: write_text(
                root / "zigux/tests/phase1_host_tools_smoke.zig",
                replace_once(
                    read_text(root / "zigux/tests/phase1_host_tools_smoke.zig"),
                    '@hasDecl(bitmap, "setRange")',
                    '@hasDecl(bitmap, "setBits")',
                ),
            ),
            False,
        ),
        (
            "manifest_bad_phase",
            lambda root: write_text(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                json.dumps(
                    {
                        **json.loads(
                            read_text(root / "zigux/tests/fixtures/phase1_helper_manifest.json")
                        ),
                        "phase": "Phase X",
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "manifest_bad_status",
            lambda root: write_text(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                json.dumps(
                    {
                        **json.loads(
                            read_text(root / "zigux/tests/fixtures/phase1_helper_manifest.json")
                        ),
                        "status": "parked",
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "manifest_bad_helper_count",
            lambda root: write_text(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                json.dumps(
                    {
                        **json.loads(
                            read_text(root / "zigux/tests/fixtures/phase1_helper_manifest.json")
                        ),
                        "helper_count": 12,
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "manifest_bad_helpers",
            lambda root: write_text(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                json.dumps(
                    {
                        **json.loads(
                            read_text(root / "zigux/tests/fixtures/phase1_helper_manifest.json")
                        ),
                        "helpers": EXPECTED_HELPERS[:-1],
                    },
                    indent=2,
                )
                + "\n",
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
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in validator self-tests",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve() if args.root else DEFAULT_ROOT.resolve()
    failures = collect_failures(root)
    if failures:
        for item in failures:
            print(item)
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print("PHASE1_CLOSURE_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
