#!/usr/bin/env python3
"""Guard the current Phase 1 bootstrap packet across reminder surfaces and workflow order."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_SEQUENCING_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
PHASE1_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    DOCS_ROOT_REL,
    PHASE1_CLOSURE_REL,
    LANE_SEQUENCING_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    PHASE1_MANIFEST_REL,
    MAKEFILE_REL,
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py"),
    Path("scripts/zigux/check-phase1-find-bit-review-packet.py"),
    Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py"),
    Path("scripts/zigux/check-phase1-rbtree-review-packet.py"),
    Path("scripts/zigux/check-phase1-route-summary-counts.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
)

WORKFLOW_PACKET_STEPS = (
    (
        "Check current Phase 2 closure packet",
        "python3 scripts/zigux/validate-phase2-closure.py",
    ),
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
        "Self-test current Phase 1 bitmap direct-anchor checker",
        "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    ),
    (
        "Check current Phase 1 bitmap direct-anchor packet",
        "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    ),
    (
        "Self-test current Phase 1 rbtree review checker",
        "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 rbtree review packet",
        "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
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
        "Run current Phase 3 export/UAPI C header smoke",
        "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    ),
    (
        "Run current Phase 3 export/UAPI layout replay",
        "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    ),
    (
        "Run current Phase 3 export shim replay",
        "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    ),
    (
        "Run current Phase 3 policy starter-packet replay",
        "make -C zigux phase3-policy-starter-packet-test",
    ),
    (
        "Run current Phase 3 policy unsafe replay",
        "zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    ),
    (
        "Run current Phase 3 policy unsafe make route",
        "make -C zigux phase3-policy-unsafe-test",
    ),
    (
        "Run current Phase 3 policy dump replay",
        "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    ),
    (
        "Run current Phase 3 policy dump make wrapper",
        "make -C zigux phase3-policy-dump",
    ),
    (
        "Self-test current Phase 3 low-level wrapper survey validator",
        "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    ),
    (
        "Check current Phase 3 low-level wrapper survey packet",
        "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    ),
    (
        "Run current Phase 3 low-level wrapper replay",
        "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    (
        "Run current Phase 3 low-level wrapper make route",
        "make -C zigux phase3-low-level-wrappers",
    ),
    (
        "Run current Phase 3 focused low-level wrapper make route",
        "make -C zigux phase3-low-level-wrappers-test",
    ),
    (
        "Run current Phase 3 shared tests-root packet",
        "zig build phase3-test --build-file zigux/tests/build.zig",
    ),
    (
        "Run current Phase 3 ABI dump replay",
        "zig build phase3-dump --build-file zigux/tests/build.zig",
    ),
    (
        "Run current Phase 1 shared tests-root smoke",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    (
        "Self-test current Phase 4 repo-reality warning checker",
        "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
    ),
    (
        "Check current Phase 4 repo-reality warning packet",
        "python3 scripts/zigux/check-phase4-repo-reality-warning.py",
    ),
)

REQUIRED_MARKERS = {
    DOCS_ROOT_REL: (
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
        "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
        "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    ),
    PHASE1_CLOSURE_REL: (
        "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
        "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
        "- `PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
        "- `PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
        "- `PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
    ),
    LANE_SEQUENCING_REL: (
        "- `PHASE1_LANE_RULE_SUMMARY=Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
    ),
    REVIEW_CHECKLIST_REL: (
        "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, keep `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `zigux/Makefile` explicit as the adjacent Phase 1 route-summary evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?`",
    ),
    SCRIPTS_README_REL: (
        "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
        "- `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig` restore a focused fixture-backed helper replay anchor on current `master` without widening back into the older validator-first or bench-route stack",
    ),
    TESTS_README_REL: (
        "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
}

REQUIRED_BUILD_MARKERS = (
    "const phase1_step = b.step(",
    '"phase1-host-tools-smoke",',
    '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests",',
    "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
)

REQUIRED_PHASE1_SMOKE_MARKERS = (
    'test "phase1 host-tools smoke imports the live helper modules" {',
    'test "phase1 host-tools smoke exercises live helper behavior" {',
    'test "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned" {',
)

REQUIRED_MANIFEST_MARKERS = (
    '"phase": "Phase 1"',
    '"status": "closed"',
    '"helper_count": 13',
    '"rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master."',
)

REQUIRED_MAKEFILE_MARKERS = (
    ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2 phase3-validate phase3",
    "phase1-route-summary:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py",
    "phase3-validate:",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase10-validate:",
    "phase12-validate:",
    "phase14-validate:",
)

FORBIDDEN_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase1-bench.py",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    ".PHONY: phase1-validate",
    ".PHONY: phase1-test",
    ".PHONY: phase1-bench",
    "\nphase1-validate:",
    "\nphase1-test:",
    "\nphase1-bench:",
    "\nphase1:",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def count_line(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line == needle)


def require_marker_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_line_once(text: str, label: str, line: str) -> list[str]:
    count = count_line(text, line)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_line_absent(text: str, label: str, line: str) -> list[str]:
    count = count_line(text, line)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def workflow_block(step_name: str, run_command: str) -> str:
    return f"      - name: {step_name}\n        run: {run_command}"


def workflow_step_names(text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix):] for line in text.splitlines() if line.startswith(prefix)]


def find_adjacent_chain(names: list[str], chain: tuple[str, ...]) -> bool:
    width = len(chain)
    for index in range(len(names) - width + 1):
        if tuple(names[index:index + width]) == chain:
            return True
    return False


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_marker_once(text, f"{relative_path.as_posix()}:{marker}", marker))

    build_text = read_text(root, TESTS_BUILD_REL)
    for marker in REQUIRED_BUILD_MARKERS:
        failures.extend(require_line_once(build_text, f"{TESTS_BUILD_REL.as_posix()}:{marker}", marker))

    smoke_text = read_text(root, PHASE1_SMOKE_REL)
    for marker in REQUIRED_PHASE1_SMOKE_MARKERS:
        failures.extend(require_line_once(smoke_text, f"{PHASE1_SMOKE_REL.as_posix()}:{marker}", marker))

    manifest_text = read_text(root, PHASE1_MANIFEST_REL)
    for marker in REQUIRED_MANIFEST_MARKERS:
        failures.extend(require_marker_once(manifest_text, f"{PHASE1_MANIFEST_REL.as_posix()}:{marker}", marker))

    makefile_text = read_text(root, MAKEFILE_REL)
    for marker in REQUIRED_MAKEFILE_MARKERS:
        failures.extend(require_line_once(makefile_text, f"{MAKEFILE_REL.as_posix()}:{marker}", marker))
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        count = makefile_text.count(marker)
        if count:
            failures.append(f"{MAKEFILE_REL.as_posix()}:{marker}:expected=0:actual={count}")

    workflow_text = read_text(root, WORKFLOW_REL)
    for step_name, run_command in WORKFLOW_PACKET_STEPS:
        name_line = f"      - name: {step_name}"
        run_line = f"        run: {run_command}"
        failures.extend(require_line_once(workflow_text, f"workflow_step:{step_name}", name_line))
        failures.extend(require_line_once(workflow_text, f"workflow_run:{run_command}", run_line))
        pair_count = workflow_text.count(workflow_block(step_name, run_command))
        if pair_count != 1:
            failures.append(f"workflow_pair:{step_name}:expected=1:actual={pair_count}")
    for line in FORBIDDEN_WORKFLOW_LINES:
        failures.extend(require_line_absent(workflow_text, f"{WORKFLOW_REL.as_posix()}:{line}", f"        {line}"))
    if failures:
        return failures

    chain = tuple(step_name for step_name, _ in WORKFLOW_PACKET_STEPS)
    if not find_adjacent_chain(workflow_step_names(workflow_text), chain):
        failures.append("workflow:phase1_bootstrap_packet:expected=adjacent_chain:actual=split_or_reordered")
    return failures


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, "placeholder\n")

    for relative_path, markers in REQUIRED_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")

    write_text(root, TESTS_BUILD_REL, "\n".join(REQUIRED_BUILD_MARKERS) + "\n")
    write_text(root, PHASE1_SMOKE_REL, "\n".join(REQUIRED_PHASE1_SMOKE_MARKERS) + "\n")
    write_text(root, PHASE1_MANIFEST_REL, "\n".join(REQUIRED_MANIFEST_MARKERS) + "\n")
    write_text(root, MAKEFILE_REL, "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n")
    write_text(
        root,
        WORKFLOW_REL,
        "\n".join(workflow_block(step_name, run_command) for step_name, run_command in WORKFLOW_PACKET_STEPS) + "\n",
    )


def run_self_test() -> int:
    cases = (
        ("success", None),
        ("missing_file", ("unlink", DOCS_ROOT_REL)),
        ("missing_marker", ("remove", PHASE1_CLOSURE_REL, REQUIRED_MARKERS[PHASE1_CLOSURE_REL][0])),
        ("duplicate_marker", ("duplicate", PHASE1_CLOSURE_REL, REQUIRED_MARKERS[PHASE1_CLOSURE_REL][1])),
        ("missing_build_marker", ("remove_line", TESTS_BUILD_REL, REQUIRED_BUILD_MARKERS[0])),
        ("missing_smoke_marker", ("remove_line", PHASE1_SMOKE_REL, REQUIRED_PHASE1_SMOKE_MARKERS[0])),
        ("forbidden_makefile", ("append", MAKEFILE_REL, "phase1-validate:\n")),
        ("forbidden_workflow", ("append", WORKFLOW_REL, "        run: python3 scripts/zigux/check-phase1-bench.py\n")),
        ("workflow_reordered", ("swap_steps",)),
    )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bootstrap-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "unlink":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    relative_path, marker = mutation[1], mutation[2]
                    text = read_text(root, relative_path)
                    write_text(root, relative_path, text.replace(marker + "\n", "", 1))
                elif kind == "remove_line":
                    relative_path, line = mutation[1], mutation[2]
                    text = read_text(root, relative_path)
                    write_text(root, relative_path, text.replace(line + "\n", "", 1))
                elif kind == "duplicate":
                    relative_path, marker = mutation[1], mutation[2]
                    text = read_text(root, relative_path)
                    write_text(root, relative_path, text.replace(marker, marker + "\n" + marker, 1))
                elif kind == "append":
                    relative_path, extra = mutation[1], mutation[2]
                    write_text(root, relative_path, read_text(root, relative_path) + extra)
                elif kind == "swap_steps":
                    text = read_text(root, WORKFLOW_REL)
                    first = workflow_block(*WORKFLOW_PACKET_STEPS[0])
                    second = workflow_block(*WORKFLOW_PACKET_STEPS[1])
                    swapped = text.replace(first + "\n" + second, second + "\n" + first, 1)
                    write_text(root, WORKFLOW_REL, swapped)
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST_CASE_FAILED={name}")
                return 1

    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", help="write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        build_sample_repo(destination)
        print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SAMPLE_ROOT={destination}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT=pass")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_REQUIRED_WORKFLOW_STEP_COUNT={len(WORKFLOW_PACKET_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
