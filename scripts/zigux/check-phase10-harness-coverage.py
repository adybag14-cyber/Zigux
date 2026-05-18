#!/usr/bin/env python3
"""Fail closed when the shared Phase 10 harness-coverage packet drifts."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 2
    else Path(__file__).resolve().parent
)

FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_build.zig",
    "scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "scripts/zigux/README.md",
]

DOCS_ROOT_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/tests/phase10_closure_manifest.json",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_mmio.zig",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

REVIEW_CHECKLIST_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/tests/phase10_closure_manifest.json",
    "Documentation/zigux/phase10-closure-evidence.md",
    "make -C zigux phase10-validate",
]

COMPANION_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "Documentation/zigux/phase10-virtio-ring-slice.md",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_build.zig",
]

LANE_SEQUENCING_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "ring lane `P10-L10` owns the queue-local wrapper packet",
    "Use the directly re-readable ring, input, and MMIO anchors before widening shared wording",
    "`zigux/tests/phase10_virtio_mmio.zig` is back as a directly re-readable helper-local replay anchor",
    "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/Makefile` still materialize here",
]

LANE_SEQUENCING_FORBIDDEN_MARKERS = [
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, and `zigux/tests/phase10_virtio_mmio_survey.zig` should stay framed as last-known packet members until a fresh direct reread proves they materialize again on current `master`",
    "`Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, and `zigux/tests/phase10_virtio_mmio_survey.zig`",
]

MODULE_SLICE_MARKERS = [
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "queued status completions reclaimable in memory",
    "registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice",
]

BUILD_MARKERS = [
    "phase10_virtio_input_survey_module",
    "virtio_input_verify_module",
    "virtio_mmio_module",
    "phase10_virtio_mmio_survey_module",
    "virtio_ring_module",
    "virtio_ring_verify_module",
    "phase10_virtio_ring_prepare_kick_idempotent_module",
    "phase10_virtio_ring_broken_queue_queue_discipline_module",
    "phase10_virtio_ring_delayed_callback_budget_module",
    '"phase10-virtio-input-queue-callback-preflight-tests"',
    '"phase10-virtio-input-registration-preflight-tests"',
    '"phase10-virtio-input-status-drain-tests"',
    '"phase10-virtio-input-teardown-observation-tests"',
    '"phase10-virtio-input-survey-tests"',
    '"phase10-virtio-input-verify-tests"',
    '"phase10-virtio-ring-verify-tests"',
    '"phase10-virtio-ring-prepare-kick-idempotent-tests"',
    '"phase10-virtio-ring-reset-reuse-tests"',
    '"phase10-virtio-ring-broken-queue-queue-discipline-tests"',
    '"phase10-virtio-ring-delayed-callback-budget-tests"',
    '"phase10-virtio-mmio-tests"',
    '"phase10-virtio-mmio-survey-tests"',
    "Run the live Phase 10 virtio input, ring, and MMIO lab validation tests",
]

REGISTRATION_HELPER_MARKERS = [
    "pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;",
    "pub const RegistrationBlocker = virtio_input.RegistrationBlocker;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {",
    "pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
]

VERIFY_MARKERS = [
    'test "phase10 virtio input verify keeps wrapper-facing queue preflight ordering explicit" {',
    'test "phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims" {',
]

SHARED_FREEZE_BOUNDARY_MARKERS = [
    'CHECK_COMMAND = "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py"',
    '"kernel/workqueue.c"',
    '"kernel/trace/ring_buffer.c"',
    '"kernel/sched/core.c"',
    '"net/core/skbuff.c"',
]

CLOSURE_EVIDENCE_MARKERS = [
    "`PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`",
    "shared packet direct-readback inventory is mixed on current `master`, and the directly re-readable set is narrower than the full shared reminder packet:",
    "directly re-readable shared reminder surfaces now include `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`",
    "directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/Makefile`",
    "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json` and `zigux/tests/phase10_virtio_input_manifest.json`",
    "current contents reads still do not materialize `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_core_manifest.json`, `Documentation/zigux/phase10-virtio-core-survey.md`",
    "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `drivers/virtio/virtio_ring.zig`, while `zigux/tests/phase10_virtio_ring_survey.zig` still remains a direct-readback gap in this lane.",
    "The shared bootstrap-route guard now stays explicit through `scripts/zigux/check-phase10-bootstrap-route.py` so the closure packet fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`.",
    "`zigux/Makefile` itself now rematerializes on current `master`, and its live body exposes the dedicated shared Phase 10 validate/test route stack, so keep the returned file and that returned build-gate posture explicit here rather than framing it as a repo-reality gap.",
    "`virtqueue_wrappers=starter_landed`",
    "`mmio_wrappers=starter_landed`",
    "`lab_only_driver_validation=starter_landed`",
]

SCRIPTS_README_MARKERS = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "shared closure-packet vocabulary and public-tree-backed companions rather than as absent current-`master` scripts-root evidence",
]

SCRIPTS_README_FORBIDDEN_MARKERS = [
    "still return missing for `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def check_absent_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            missing.append(f"{label}:forbidden:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []

    docs_root = read_text(root, "Documentation/zigux/README.md")
    review_checklist = read_text(root, "Documentation/zigux/review-checklist.md")
    companion = read_text(root, "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
    closure_evidence = read_text(root, "Documentation/zigux/phase10-closure-evidence.md")
    lane_sequencing = read_text(root, "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md")
    module_slice = read_text(root, "Documentation/zigux/phase10-virtio-input-module-slice.md")
    build = read_text(root, "zigux/tests/phase10_build.zig")
    registration_helper = read_text(root, "drivers/virtio/virtio_input_registration_preflight.zig")
    verify = read_text(root, "drivers/virtio/virtio_input_verify.zig")
    shared_freeze_boundary = read_text(root, "scripts/zigux/check-phase10-shared-freeze-boundary.py")
    scripts_readme = read_text(root, "scripts/zigux/README.md")

    check_markers(missing_markers, "docs_root", docs_root, DOCS_ROOT_MARKERS)
    check_markers(missing_markers, "review_checklist", review_checklist, REVIEW_CHECKLIST_MARKERS)
    check_markers(missing_markers, "tests_root_companion", companion, COMPANION_MARKERS)
    check_markers(missing_markers, "phase10_closure_evidence", closure_evidence, CLOSURE_EVIDENCE_MARKERS)
    check_markers(missing_markers, "phase10_lane_sequencing", lane_sequencing, LANE_SEQUENCING_MARKERS)
    check_absent_markers(missing_markers, "phase10_lane_sequencing", lane_sequencing, LANE_SEQUENCING_FORBIDDEN_MARKERS)
    check_markers(missing_markers, "phase10_input_module_slice", module_slice, MODULE_SLICE_MARKERS)
    check_markers(missing_markers, "phase10_build", build, BUILD_MARKERS)
    check_markers(missing_markers, "virtio_input_registration_preflight", registration_helper, REGISTRATION_HELPER_MARKERS)
    check_markers(missing_markers, "virtio_input_verify", verify, VERIFY_MARKERS)
    check_markers(missing_markers, "phase10_shared_freeze_boundary", shared_freeze_boundary, SHARED_FREEZE_BOUNDARY_MARKERS)
    check_markers(missing_markers, "scripts_readme", scripts_readme, SCRIPTS_README_MARKERS)
    check_absent_markers(missing_markers, "scripts_readme", scripts_readme, SCRIPTS_README_FORBIDDEN_MARKERS)

    return [], missing_markers


def write_fixture(root: Path) -> None:
    fixture_contents = {
        "Documentation/zigux/README.md": "\n".join(DOCS_ROOT_MARKERS) + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": "\n".join(COMPANION_MARKERS) + "\n",
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_EVIDENCE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "\n".join(LANE_SEQUENCING_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-module-slice.md": "\n".join(MODULE_SLICE_MARKERS) + "\n",
        "drivers/virtio/virtio_input_registration_preflight.zig": "\n".join(REGISTRATION_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input_verify.zig": "\n".join(VERIFY_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input_survey.zig": "phase10 survey gate placeholder\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "scripts/zigux/check-phase10-shared-freeze-boundary.py": "\n".join(SHARED_FREEZE_BOUNDARY_MARKERS) + "\n",
        "scripts/zigux/README.md": "\n".join(SCRIPTS_README_MARKERS) + "\n",
    }

    for rel_path, content in fixture_contents.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def expect_missing_marker(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"phase10-harness-coverage-self-test:unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-harness-coverage-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def expect_missing_file(root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"phase10-harness-coverage-self-test:unexpected_missing_markers:{','.join(missing_markers)}")
    if expected not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"phase10-harness-coverage-self-test:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_harness_coverage_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-harness-coverage-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        expect_missing_marker(root, "Documentation/zigux/phase10-closure-evidence.md", "`virtqueue_wrappers=starter_landed`", "`virtqueue_wrappers=repo_reality_gap`", "phase10_closure_evidence:`virtqueue_wrappers=starter_landed`")
        expect_missing_marker(root, "Documentation/zigux/phase10-closure-evidence.md", "directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/Makefile`", "directly re-readable helper, verify, and build anchors now include `drivers/virtio/virtio_input.zig`", "phase10_closure_evidence:directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/Makefile`")
        expect_missing_marker(root, "Documentation/zigux/phase10-closure-evidence.md", "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json` and `zigux/tests/phase10_virtio_input_manifest.json`", "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json`", "phase10_closure_evidence:directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json` and `zigux/tests/phase10_virtio_input_manifest.json`")
        expect_missing_marker(root, "Documentation/zigux/phase10-closure-evidence.md", "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `drivers/virtio/virtio_ring.zig`, while `zigux/tests/phase10_virtio_ring_survey.zig` still remains a direct-readback gap in this lane.", "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md` only.", "phase10_closure_evidence:The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `drivers/virtio/virtio_ring.zig`, while `zigux/tests/phase10_virtio_ring_survey.zig` still remains a direct-readback gap in this lane.")
        expect_missing_marker(root, "Documentation/zigux/phase10-closure-evidence.md", "The shared bootstrap-route guard now stays explicit through `scripts/zigux/check-phase10-bootstrap-route.py` so the closure packet fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`.", "The shared bootstrap-route guard remains optional.", "phase10_closure_evidence:The shared bootstrap-route guard now stays explicit through `scripts/zigux/check-phase10-bootstrap-route.py` so the closure packet fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`.")
        expect_missing_marker(root, "Documentation/zigux/phase10-closure-evidence.md", "`zigux/Makefile` itself now rematerializes on current `master`, and its live body exposes the dedicated shared Phase 10 validate/test route stack, so keep the returned file and that returned build-gate posture explicit here rather than framing it as a repo-reality gap.", "`zigux/Makefile` still exposes only the Phase 2 toolchain and kbuild routes.", "phase10_closure_evidence:`zigux/Makefile` itself now rematerializes on current `master`, and its live body exposes the dedicated shared Phase 10 validate/test route stack, so keep the returned file and that returned build-gate posture explicit here rather than framing it as a repo-reality gap.")
        expect_missing_marker(root, "Documentation/zigux/review-checklist.md", "Documentation/zigux/phase10-closure-evidence.md", "Documentation/zigux/phase10-closure-evidence-missing.md", "review_checklist:Documentation/zigux/phase10-closure-evidence.md")
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", "Run the live Phase 10 virtio input, ring, and MMIO lab validation tests", "Run the live Phase 10 virtio input and MMIO lab validation tests", "phase10_build:Run the live Phase 10 virtio input, ring, and MMIO lab validation tests")
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-input-queue-callback-preflight-tests"', '"phase10-virtio-input-queue-callback-drift-tests"', 'phase10_build:"phase10-virtio-input-queue-callback-preflight-tests"')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-input-registration-preflight-tests"', '"phase10-virtio-input-registration-drift-tests"', 'phase10_build:"phase10-virtio-input-registration-preflight-tests"')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-input-status-drain-tests"', '"phase10-virtio-input-status-drift-tests"', 'phase10_build:"phase10-virtio-input-status-drain-tests"')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-input-teardown-observation-tests"', '"phase10-virtio-input-teardown-drift-tests"', 'phase10_build:"phase10-virtio-input-teardown-observation-tests"')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-input-survey-tests"', '"phase10-virtio-input-survey-drift-tests"', 'phase10_build:"phase10-virtio-input-survey-tests"')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-input-verify-tests"', '"phase10-virtio-input-verify-drift-tests"', 'phase10_build:"phase10-virtio-input-verify-tests"')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-ring-verify-tests"', '"phase10-virtio-ring-drift-tests"', 'phase10_build:"phase10-virtio-ring-verify-tests"')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-ring-prepare-kick-idempotent-tests"', '"phase10-virtio-ring-prepare-kick-drift-tests"', 'phase10_build:"phase10-virtio-ring-prepare-kick-idempotent-tests"')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-ring-reset-reuse-tests"', '"phase10-virtio-ring-reset-reuse-drift-tests"', 'phase10_build:"phase10-virtio-ring-reset-reuse-tests"')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", "phase10_virtio_ring_delayed_callback_budget_module", "phase10_virtio_ring_delayed_callback_budget_drift_module", "phase10_build:phase10_virtio_ring_delayed_callback_budget_module")
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-ring-delayed-callback-budget-tests"', '"phase10-virtio-ring-delayed-callback-budget-drift-tests"', 'phase10_build:"phase10-virtio-ring-delayed-callback-budget-tests"')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", "phase10_virtio_mmio_survey_module", "phase10_virtio_mmio_survey_drift_module", "phase10_build:phase10_virtio_mmio_survey_module")
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", '"phase10-virtio-mmio-survey-tests"', '"phase10-virtio-mmio-survey-drift-tests"', 'phase10_build:"phase10-virtio-mmio-survey-tests"')
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-input-module-slice.md", "zigux/tests/phase10_virtio_input_survey.zig", "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig", "phase10_input_module_slice:zigux/tests/phase10_virtio_input_survey.zig")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-input-module-slice.md", "queued status completions reclaimable in memory", "queued status completions drain directly to the transport", "phase10_input_module_slice:queued status completions reclaimable in memory")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", "`zigux/tests/phase10_virtio_mmio.zig` is back as a directly re-readable helper-local replay anchor", "`zigux/tests/phase10_virtio_mmio.zig` remains a gap", "phase10_lane_sequencing:`zigux/tests/phase10_virtio_mmio.zig` is back as a directly re-readable helper-local replay anchor")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/Makefile` still materialize here", "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md` and `zigux/tests/phase10_virtio_mmio.zig` still materialize here", "phase10_lane_sequencing:`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/Makefile` still materialize here")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", "Use the directly re-readable ring, input, and MMIO anchors before widening shared wording", "Use the directly re-readable ring, input, and MMIO anchors before widening shared wording\n`Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, and `zigux/tests/phase10_virtio_mmio_survey.zig` should stay framed as last-known packet members until a fresh direct reread proves they materialize again on current `master`", "phase10_lane_sequencing:forbidden:`Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, and `zigux/tests/phase10_virtio_mmio_survey.zig` should stay framed as last-known packet members until a fresh direct reread proves they materialize again on current `master`")
        expect_missing_marker(root, "scripts/zigux/README.md", "shared closure-packet vocabulary and public-tree-backed companions rather than as absent current-`master` scripts-root evidence", "absent scripts-root evidence", "scripts_readme:shared closure-packet vocabulary and public-tree-backed companions rather than as absent current-`master` scripts-root evidence")
        expect_missing_marker(root, "scripts/zigux/README.md", "scripts/zigux/check-phase10-harness-coverage.py", "scripts/zigux/check-phase10-harness-coverage-missing.py", "scripts_readme:scripts/zigux/check-phase10-harness-coverage.py")
        expect_missing_marker(root, "drivers/virtio/virtio_input_registration_preflight.zig", "pub const RegistrationBlocker = virtio_input.RegistrationBlocker;", "pub const RegistrationGate = virtio_input.RegistrationBlocker;", "virtio_input_registration_preflight:pub const RegistrationBlocker = virtio_input.RegistrationBlocker;")
        expect_missing_marker(root, "drivers/virtio/virtio_input_verify.zig", 'test "phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims" {', 'test "phase10 virtio input verify drift" {', 'virtio_input_verify:test "phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims" {')
        expect_missing_marker(root, "scripts/zigux/check-phase10-shared-freeze-boundary.py", '"kernel/trace/ring_buffer.c"', '"kernel/trace/ring_buffer.zig"', 'phase10_shared_freeze_boundary:"kernel/trace/ring_buffer.c"')

        (root / "Documentation/zigux/phase10-closure-evidence.md").unlink()
        expect_missing_file(root, "Documentation/zigux/phase10-closure-evidence.md")
        write_fixture(root)

        print("PHASE10_HARNESS_COVERAGE_SELF_TEST=pass")
        print("PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT=28")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 10 harness-coverage reminder packet.")
    parser.add_argument("--self-test", action="store_true", help="run the checker's built-in synthetic drift tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_HARNESS_COVERAGE=fail")
        print("MISSING_PHASE10_HARNESS_COVERAGE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_HARNESS_COVERAGE_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_HARNESS_COVERAGE=fail")
        print("MISSING_PHASE10_HARNESS_COVERAGE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_HARNESS_COVERAGE_MARKERS_END")
        return 1

    print("PHASE10_HARNESS_COVERAGE=pass")
    print(f"PHASE10_HARNESS_COVERAGE_REQUIRED_FILE_COUNT={len(FILES)}")
    print("PHASE10_HARNESS_COVERAGE_REQUIRED_MARKER_COUNT=" f"{len(DOCS_ROOT_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(COMPANION_MARKERS) + len(LANE_SEQUENCING_MARKERS) + len(CLOSURE_EVIDENCE_MARKERS) + len(MODULE_SLICE_MARKERS) + len(BUILD_MARKERS) + len(REGISTRATION_HELPER_MARKERS) + len(VERIFY_MARKERS) + len(SHARED_FREEZE_BOUNDARY_MARKERS) + len(SCRIPTS_README_MARKERS)}")
    print("PHASE10_HARNESS_COVERAGE_FORBIDDEN_MARKER_COUNT=" f"{len(LANE_SEQUENCING_FORBIDDEN_MARKERS) + len(SCRIPTS_README_FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
