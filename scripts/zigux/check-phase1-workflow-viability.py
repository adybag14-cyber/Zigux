#!/usr/bin/env python3
"""Guard the current Lane 17 Phase 1 workflow-viability packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[3] if len(HERE.parents) > 3 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
SMOKE_TEST_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
MAKEFILE_REL = Path("zigux/Makefile")
ROUTE_SUMMARY_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
FIND_BIT_BENCH_ANCHOR_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
DIRECT_ANCHOR_MANIFEST_GATE_REL = Path(
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py"
)
STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
FIND_BIT_REVIEW_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")

REQUIRED_FILES = (
    WORKFLOW_REL,
    CLOSURE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    LANE_NOTE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    SMOKE_TEST_REL,
    MANIFEST_REL,
    MAKEFILE_REL,
    ROUTE_SUMMARY_REL,
    BENCH_REL,
    FIND_BIT_BENCH_ANCHOR_REL,
    SHARED_REMINDER_REL,
    CLOSURE_VALIDATOR_REL,
    DIRECT_OWNER_REL,
    DIRECT_ANCHOR_MANIFEST_GATE_REL,
    STRING_REVIEW_REL,
    FIND_BIT_REVIEW_REL,
)

REQUIRED_MARKERS = {
    CLOSURE_REL: (
        "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
        "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
        "- `PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
        "- `PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    ),
    DOCS_ROOT_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
        "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    ),
    REVIEW_CHECKLIST_REL: (
        "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    LANE_NOTE_REL: (
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
        "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
        "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`",
        "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
        "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
    ),
    SCRIPTS_README_REL: (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    ),
    TESTS_README_REL: (
        "  * current direct-readback Phase 1 reminder packet:",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
    TESTS_BUILD_REL: (
        '.name = "phase1-host-tools-smoke",',
        'const phase1_step = b.step(',
        '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests",',
    ),
    SMOKE_TEST_REL: (
        'test "phase1 host-tools smoke imports the live helper modules" {',
        'test "phase1 host-tools smoke exercises live helper behavior" {',
        'test "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned" {',
    ),
    MANIFEST_REL: (
        '"direct_anchor_followup_helpers": [',
        '"tools/lib/bitmap.zig",',
        '"tools/lib/find_bit.zig",',
        '"tools/lib/rbtree.zig",',
        '"tools/lib/string.zig"',
        '"rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master."',
    ),
    MAKEFILE_REL: (
        "phase1-route-summary:",
        "phase2-toolchain:",
        "phase2-tools:",
        "phase2-kconfig:",
        "phase2-cross:",
        "phase2-genksyms:",
        "phase3-validate:",
        "phase14-validate:",
    ),
    ROUTE_SUMMARY_REL: (
        'print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")',
    ),
    BENCH_REL: (
        "FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {",
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
    ),
    FIND_BIT_BENCH_ANCHOR_REL: (
        'print("PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass")',
        'print("PHASE1_FIND_BIT_BENCH_ANCHORS=pass")',
        "REQUIRED_TEST_MARKERS = {",
        "REQUIRED_SOURCE_EXACT_MARKERS = {",
    ),
    SHARED_REMINDER_REL: (
        '"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""',
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
    ),
    CLOSURE_VALIDATOR_REL: (
        'print("PHASE1_CLOSURE_SELF_TEST=pass")',
        'print("PHASE1_CLOSURE_VALIDATION=pass")',
    ),
    DIRECT_OWNER_REL: (
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
        'print("phase1-direct-owner-markers:ok")',
    ),
    DIRECT_ANCHOR_MANIFEST_GATE_REL: (
        'print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")',
        'print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass")',
        'print("PHASE1_RBTREE_DIRECT_ANCHOR_CHECKER=pass")',
    ),
    STRING_REVIEW_REL: (
        "EXPECTED_STRING_SOURCE_SYMBOLS = [",
        'print("PHASE1_STRING_REVIEW_PACKET_SELF_TEST=pass")',
        'print("phase1-string-review-packet:ok")',
    ),
    FIND_BIT_REVIEW_REL: (
        'print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass")',
        'print("PHASE1_FIND_BIT_REVIEW_PACKET=pass")',
        "EXPECTED_FIXTURE_VALUES = {",
    ),
}

REQUIRED_WORKFLOW_STEPS = (
    (
        "Self-test current Phase 1 direct-owner checker",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    ),
    (
        "Check current Phase 1 direct-owner markers",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    ),
    (
        "Self-test current Phase 1 direct-anchor manifest gate",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    ),
    (
        "Check current Phase 1 direct-anchor manifest gate",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    ),
    (
        "Self-test current Phase 1 string review checker",
        "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 string review packet",
        "python3 scripts/zigux/check-phase1-string-review-packet.py",
    ),
    (
        "Self-test current Phase 1 find-bit review checker",
        "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 find-bit review packet",
        "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    ),
    (
        "Self-test current Phase 1 route summary checker",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    ),
    (
        "Check current Phase 1 route summary packet",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ),
    (
        "Self-test current Phase 1 bench checker",
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    (
        "Self-test current Phase 1 find-bit bench anchor checker",
        "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    ),
    (
        "Check current Phase 1 find-bit bench anchor packet",
        "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    ),
    (
        "Self-test current Phase 1 shared reminder checker",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    ),
    (
        "Check current Phase 1 shared reminder packet",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    ),
    (
        "Self-test current Phase 1 closure validator",
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    ),
    (
        "Check current Phase 1 closure packet",
        "python3 scripts/zigux/validate-phase1-closure.py",
    ),
    (
        "Self-test current Phase 3 interop packet",
        "python3 scripts/zigux/validate_phase3_selftest.py",
    ),
    (
        "Check current Phase 3 interop packet",
        "python3 scripts/zigux/run-phase3-checks.py",
    ),
    (
        "Run current Phase 1 shared tests-root smoke",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
)

REQUIRED_WORKFLOW_CHAIN = tuple(step for step, _ in REQUIRED_WORKFLOW_STEPS[:-1])

FORBIDDEN_WORKFLOW_COMMANDS = (
    "python3 scripts/zigux/check-phase1-bench.py",
    "python3 scripts/zigux/validate-phase1.py --self-test",
    "python3 scripts/zigux/validate-phase1.py",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
    "make -C zigux phase1",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_text_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_line_once(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current.strip() == line.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def workflow_step_names(workflow_text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in workflow_text.splitlines() if line.startswith(prefix)]


def require_workflow_step(workflow_text: str, step_name: str, run_command: str) -> list[str]:
    failures: list[str] = []
    failures.extend(
        require_line_once(
            workflow_text,
            f"workflow_step:{step_name}",
            f"- name: {step_name}",
        )
    )
    pair = f"      - name: {step_name}\n        run: {run_command}"
    count = workflow_text.count(pair)
    if count != 1:
        failures.append(f"workflow_run:{step_name}:expected=1:actual={count}")
    return failures


def require_workflow_chain(workflow_text: str, step_names: tuple[str, ...]) -> list[str]:
    names = workflow_step_names(workflow_text)
    width = len(step_names)
    for index in range(len(names) - width + 1):
        if tuple(names[index : index + width]) == step_names:
            return []
    return [f"workflow_chain:missing:{'->'.join(step_names)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = read_text(root, WORKFLOW_REL)
    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for idx, marker in enumerate(markers):
            failures.extend(
                require_text_once(
                    text,
                    f"{relative_path.as_posix()}:marker_{idx}",
                    marker,
                )
            )

    for step_name, run_command in REQUIRED_WORKFLOW_STEPS:
        failures.extend(require_workflow_step(workflow_text, step_name, run_command))
    failures.extend(require_workflow_chain(workflow_text, REQUIRED_WORKFLOW_CHAIN))

    workflow_lines = [line.strip() for line in workflow_text.splitlines()]
    for command in FORBIDDEN_WORKFLOW_COMMANDS:
        count = sum(1 for line in workflow_lines if line == f"run: {command}")
        if count:
            failures.append(f"workflow_forbidden:{command}:actual={count}")

    makefile_text = read_text(root, MAKEFILE_REL)
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        count = makefile_text.count(marker)
        if count:
            failures.append(f"makefile_forbidden:{marker}:actual={count}")

    return failures


def write_file(root: Path, relative_path: Path, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == WORKFLOW_REL:
            continue
        write_file(
            root,
            relative_path,
            "\n".join(REQUIRED_MARKERS.get(relative_path, ())) + "\n",
        )

    workflow_lines = [
        "name: zigux-bootstrap",
        "",
        "jobs:",
        "  bootstrap:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "",
    ]
    for step_name, run_command in REQUIRED_WORKFLOW_STEPS:
        workflow_lines.append(f"      - name: {step_name}")
        workflow_lines.append(f"        run: {run_command}")
        workflow_lines.append("")
    write_file(root, WORKFLOW_REL, "\n".join(workflow_lines))


def mutate_remove_text(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1).replace(marker, "", 1), encoding="utf-8")


def mutate_duplicate_text(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, str, Path | None, str | None]] = [("success", "none", None, None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", "missing_file", relative_path, None))
    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path.as_posix()}", "remove", relative_path, marker))
            cases.append((f"duplicate_marker:{relative_path.as_posix()}", "duplicate", relative_path, marker))
    for step_name, run_command in REQUIRED_WORKFLOW_STEPS:
        block = f"      - name: {step_name}\n        run: {run_command}\n"
        cases.append((f"missing_step:{step_name}", "remove", WORKFLOW_REL, block))
        cases.append((f"duplicate_step:{step_name}", "duplicate", WORKFLOW_REL, block))
    cases.append(
        (
            "forbidden_workflow_bench_run",
            "append",
            WORKFLOW_REL,
            "      - name: Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py\n",
        )
    )
    cases.append(
        (
            "forbidden_makefile_phase1_validate",
            "append",
            MAKEFILE_REL,
            "phase1-validate:\n",
        )
    )
    cases.append(
        (
            "out_of_order_chain",
            "replace",
            WORKFLOW_REL,
            (
                "      - name: Check current Phase 1 closure packet\n        run: python3 scripts/zigux/validate-phase1-closure.py\n\n"
                "      - name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py\n"
            ),
        )
    )

    for name, operation, relative_path, payload in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if operation == "missing_file" and relative_path is not None:
                (root / relative_path).unlink()
            elif operation == "remove" and relative_path is not None and payload is not None:
                mutate_remove_text(root, relative_path, payload)
            elif operation == "duplicate" and relative_path is not None and payload is not None:
                mutate_duplicate_text(root, relative_path, payload)
            elif operation == "append" and relative_path is not None and payload is not None:
                path = root / relative_path
                path.write_text(path.read_text(encoding="utf-8") + payload, encoding="utf-8")
            elif operation == "replace" and relative_path is not None and payload is not None:
                path = root / relative_path
                text = path.read_text(encoding="utf-8")
                old = (
                    "      - name: Self-test current Phase 1 closure validator\n"
                    "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n\n"
                    "      - name: Check current Phase 1 closure packet\n"
                    "        run: python3 scripts/zigux/validate-phase1-closure.py\n\n"
                    "      - name: Self-test current Phase 3 interop packet\n"
                    "        run: python3 scripts/zigux/validate_phase3_selftest.py\n"
                )
                text = text.replace(old, payload, 1)
                path.write_text(text, encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("phase1-workflow-viability-self-test:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"phase1-workflow-viability-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample root to the given path and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        build_sample_repo(destination)
        print(f"PHASE1_WORKFLOW_VIABILITY_SAMPLE_ROOT={destination}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_WORKFLOW_VIABILITY=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_VIABILITY=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_WORKFLOW_VIABILITY_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
