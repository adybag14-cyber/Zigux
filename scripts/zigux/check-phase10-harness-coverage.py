#!/usr/bin/env python3
"""Validate the shared Phase 10 harness-coverage packet against current repo reality."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
import sys


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_MARKERS = {
    "Documentation/zigux/review-checklist.md": [
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "zigux/Makefile",
        "zigux/tests/phase10_build.zig",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "drivers/virtio/virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "drivers/virtio/virtio_input_teardown_observation.zig",
        "drivers/virtio/virtio_input_verify.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
        "drivers/virtio/virtio_ring_verify.zig",
        "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
        "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
        "zigux/tests/phase10_virtio_mmio_manifest.json",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
        "blocked risky-transport posture",
        "returned shared closure packet anchors: `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `Documentation/zigux/phase10-virtio-core-survey.md`, and `zigux/tests/phase10_closure_manifest.json`",
        "Keep `zigux/tests/phase10_virtio_ring_survey.zig` explicit as the returned dedicated ring survey gate beside `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `zigux/tests/phase10_build.zig` instead of framing that survey replay as a last-known packet member.",
    ],
    "Documentation/zigux/phase10-closure-evidence.md": [
        "`PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`",
        "directly re-readable shared reminder surfaces now include `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`",
        "directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, and `zigux/Makefile`",
        "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, and `zigux/tests/phase10_virtio_mmio_manifest.json`",
        "current contents reads still do not materialize `zigux/tests/phase10_virtio_core_manifest.json`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, and `zigux/tests/phase10_virtio_core_survey.zig` through the direct readback available in this lane, while the returned `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, and `zigux/Makefile` now rematerialize the dedicated shared Phase 10 validate/test route surface on current `master`",
        "`scripts/zigux/validate-phase10.py` and `zigux/Makefile` themselves now rematerialize on current `master`, and their live bodies expose the dedicated shared Phase 10 validate/test route stack, so keep those returned files and that returned build-gate posture explicit here rather than framing them as repo-reality gaps.",
        "The shared bootstrap-route guard now stays explicit through `scripts/zigux/check-phase10-bootstrap-route.py` so the closure packet fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`.",
        "Treat `scripts/zigux/README.md` as a neighboring shared reminder surface until a fresh same-lane reread rematerializes a dedicated Phase 10 scripts-root packet on current `master`.",
        "`lab_only_driver_validation=starter_landed`",
        "- evidence: `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `zigux/tests/phase10_build.zig`, `zigux/Makefile`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `the shared bootstrap-route guard in this closure note`, and `.github/workflows/zigux-bootstrap.yml`",
        "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, and `drivers/virtio/virtio_ring.zig`, while the broader `zigux/tests/phase10_virtio_ring.zig` replay still remains a direct-readback gap in this lane.",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "drivers/virtio/virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "current `master` now rematerializes `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/Makefile`; treat those returned validator and build-route surfaces as part of the shared closure gate while keeping only the still-missing core-side companions framed as last-known packet members or repo-reality gaps in this lane",
        "`scripts/zigux/README.md` remains a neighboring shared reminder surface until a dedicated Phase 10 scripts-root packet rematerializes on current `master`",
        "`zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig` are back as directly re-readable helper-local manifest and replay anchors",
        "Current `master` gives this lane a mixed but broader set of directly re-readable shared and packet-local anchors: `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/Makefile` still materialize here.",
        "Use the directly re-readable shared validator pair, closure manifest, and Makefile-backed route anchors together with the returned core-survey, ring, input, and MMIO packet anchors before widening shared wording back into direct claims about the still-missing core-side companions.",
        "Treat the shared `zigux/tests/phase10_build.zig` route as already-landed validation evidence",
        "Current `master` also rematerializes `zigux/tests/phase10_virtio_ring_survey.zig`, so keep that dedicated ring survey gate explicit with `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and the shared `zigux/tests/phase10_build.zig` route instead of framing the survey gate as a direct-readback gap.",
    ],
    "Documentation/zigux/phase10-virtio-input-module-slice.md": [
        "drivers/virtio/virtio_input_registration_preflight.zig",
        "drivers/virtio/virtio_input_status_drain.zig",
        "drivers/virtio/virtio_input_teardown_observation.zig",
        "drivers/virtio/virtio_input_verify.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_input_survey.zig",
        "queued status completions reclaimable in memory",
        "registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice",
    ],
    "drivers/virtio/virtio_input_registration_preflight.zig": [
        "pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;",
        "pub const RegistrationBlocker = virtio_input.RegistrationBlocker;",
        "pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {",
        "pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
    ],
    "drivers/virtio/virtio_input_verify.zig": [
        "test \"phase10 virtio input verify keeps wrapper-facing queue preflight ordering explicit\" {",
        "test \"phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims\" {",
        "test \"phase10 virtio input verify keeps teardown wrapper parity explicit across reset\" {",
    ],
    "drivers/virtio/virtio_ring_verify.zig": [
        "pub fn summarizeNotificationData(",
        "pub fn summarizeDelayedCallback(",
        "pub fn summarizeResetReadiness(",
        "test \"phase10 virtio ring verify keeps notification-data next-avail state reviewable across split packed and reset replay\" {",
        "test \"phase10 virtio ring verify keeps delayed callback wrapper thresholds explicit\" {",
        "test \"phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay\" {",
    ],
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig": [
        "test \"phase10 virtio ring repeated prepareKick stays idle until new descriptors are published\" {",
        "kick_summary = try ring.prepareKick(1);",
        "try std.testing.expect(!kick_summary.needs_kick);",
    ],
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig": [
        "test \"phase10 virtio ring reset reuse stays blocked until queue-local reset prerequisites clear and then replays from a clean queue state\" {",
        "const reset = try ring.resetQueue(2);",
        "const kick_after_reset = try ring.prepareKick(2);",
    ],
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig": [
        "test \"phase10 virtio ring broken-queue coverage kicks published work before used accounting and keeps notification history visible\" {",
        "try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));",
        "const cleared_summary = try ring.clearBroken(3);",
    ],
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig": [
        "test \"phase10 virtio ring delayed callback budget stays bounded to queue-local replay state\" {",
        "try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);",
        "try std.testing.expect(summary.should_poll);",
        "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
    ],
    "zigux/tests/phase10_build.zig": [
        "\"phase10-virtio-core-tests\"",
        "\"phase10-virtio-input-queue-callback-preflight-tests\"",
        "\"phase10-virtio-input-teardown-observation-tests\"",
        "\"phase10-virtio-input-survey-tests\"",
        "\"phase10-virtio-input-verify-tests\"",
        "\"phase10-virtio-ring-verify-tests\"",
        "\"phase10-virtio-ring-prepare-kick-idempotent-tests\"",
        "\"phase10-virtio-ring-reset-reuse-tests\"",
        "\"phase10-virtio-ring-broken-queue-queue-discipline-tests\"",
        "\"phase10-virtio-ring-delayed-callback-budget-tests\"",
        "\"phase10-virtio-ring-survey-tests\"",
        "\"phase10-virtio-mmio-verify-tests\"",
        "\"phase10-virtio-mmio-survey-tests\"",
        "Run the live Phase 10 virtio core, input, ring, and MMIO lab validation tests",
    ],
    "zigux/Makefile": [
        "phase10-validate:",
        "$(PYTHON) scripts/zigux/check-phase10-bootstrap-route.py",
        "$(PYTHON) scripts/zigux/check-phase10-shared-freeze-boundary.py",
        "$(PYTHON) scripts/zigux/check-phase10-harness-coverage.py",
        "$(PYTHON) scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "phase10-test:",
        "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
        "phase10: phase10-validate phase10-test",
    ],
    "scripts/zigux/check-phase10-bootstrap-route.py": [
        "VALIDATE_STEP = \"Validate Phase 10 checker-backed review packet\"",
        "VALIDATE_CMD = \"make -C zigux phase10-validate\"",
        "TEST_STEP = \"Run Phase 10 helper tests\"",
        "TEST_CMD = \"make -C zigux phase10-test\"",
    ],
    "scripts/zigux/check-phase10-shared-freeze-boundary.py": [
        "CHECK_COMMAND = \"python3 scripts/zigux/check-phase10-shared-freeze-boundary.py\"",
        "\"kernel/workqueue.c\"",
        "\"kernel/trace/ring_buffer.c\"",
        "\"kernel/sched/core.c\"",
        "\"net/core/skbuff.c\"",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Self-test current Phase 10 bootstrap route checker",
        "Check current Phase 10 bootstrap route",
        "Validate Phase 10 checker-backed review packet",
        "make -C zigux phase10-validate",
        "Run Phase 10 helper tests",
        "make -C zigux phase10-test",
    ],
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase10-closure-evidence.md": [
        "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json` and `zigux/tests/phase10_virtio_input_manifest.json`",
        "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `drivers/virtio/virtio_ring.zig`, while `zigux/tests/phase10_virtio_ring_survey.zig` still remains a direct-readback gap in this lane.",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "Authenticated contents reads still fail for `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, and the broader validator-first `scripts/zigux/validate-phase10.py` route through the direct readback available in this lane.",
        "current `master` still does not materialize `scripts/zigux/validate-phase10.py` through the direct readback available in this lane, but it now rematerializes `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/Makefile`; keep the still-missing broader validator-script name framed as a last-known packet member or repo-reality gap while treating the returned closure validator, closure manifest, and Makefile-backed `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` route stack as the shared closure and build gate",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "keep `zigux/tests/phase10_virtio_ring_survey.zig` framed as a last-known packet member until a fresh reread proves it rematerializes on current `master`.",
        "current `master` still does not materialize `scripts/zigux/validate-phase10.py`, `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, and `zigux/tests/phase10_virtio_ring.zig` through the direct readback available in this lane, so keep them framed as last-known packet members or repo-reality gaps rather than direct current-`master` evidence.",
    ],
    "zigux/tests/phase10_build.zig": [
        "Run the live Phase 10 virtio input, ring, and MMIO lab validation tests",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_MARKERS if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel_path}:{marker}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker in text:
                missing_markers.append(f"{rel_path}:forbidden:{marker}")

    return [], missing_markers


def write_fixture(root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(markers) + "\n", encoding="utf-8")


def expect_missing_marker(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    _, missing_markers = validate(root)
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-harness-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def expect_missing_file(root: Path, rel_path: str) -> None:
    path = root / rel_path
    path.unlink()
    missing_files, missing_markers = validate(root)
    if missing_markers:
        actual = ",".join(missing_markers)
        raise SystemExit(f"phase10-harness-self-test:unexpected_markers={actual}")
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"phase10-harness-self-test:expected={rel_path}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_harness_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-harness-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        cases = [
            (
                "Documentation/zigux/phase10-closure-evidence.md",
                "directly re-readable shared reminder surfaces now include `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`",
                "directly re-readable shared reminder surfaces now include `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`",
                "Documentation/zigux/phase10-closure-evidence.md:directly re-readable shared reminder surfaces now include `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`",
            ),
            (
                "Documentation/zigux/phase10-closure-evidence.md",
                "Treat `scripts/zigux/README.md` as a neighboring shared reminder surface until a fresh same-lane reread rematerializes a dedicated Phase 10 scripts-root packet on current `master`.",
                "Treat `scripts/zigux/README.md` as an active shared Phase 10 packet on current `master`.",
                "Documentation/zigux/phase10-closure-evidence.md:Treat `scripts/zigux/README.md` as a neighboring shared reminder surface until a fresh same-lane reread rematerializes a dedicated Phase 10 scripts-root packet on current `master`.",
            ),
            (
                "Documentation/zigux/phase10-closure-evidence.md",
                "directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, and `zigux/Makefile`",
                "directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/validate-phase10-closure.py`, and `zigux/Makefile`",
                "Documentation/zigux/phase10-closure-evidence.md:directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, and `zigux/Makefile`",
            ),
            (
                "Documentation/zigux/phase10-closure-evidence.md",
                "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, and `zigux/tests/phase10_virtio_mmio_manifest.json`",
                "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, and `zigux/tests/phase10_virtio_mmio_manifest.json`",
                "Documentation/zigux/phase10-closure-evidence.md:directly re-readable packet manifests in this lane now include `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, and `zigux/tests/phase10_virtio_mmio_manifest.json`",
            ),
            (
                "Documentation/zigux/phase10-closure-evidence.md",
                "`scripts/zigux/validate-phase10.py` and `zigux/Makefile` themselves now rematerialize on current `master`, and their live bodies expose the dedicated shared Phase 10 validate/test route stack, so keep those returned files and that returned build-gate posture explicit here rather than framing them as repo-reality gaps.",
                "`zigux/Makefile` still exposes only the earlier toolchain routes.",
                "Documentation/zigux/phase10-closure-evidence.md:`scripts/zigux/validate-phase10.py` and `zigux/Makefile` themselves now rematerialize on current `master`, and their live bodies expose the dedicated shared Phase 10 validate/test route stack, so keep those returned files and that returned build-gate posture explicit here rather than framing them as repo-reality gaps.",
            ),
            (
                "Documentation/zigux/phase10-closure-evidence.md",
                "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, and `drivers/virtio/virtio_ring.zig`, while the broader `zigux/tests/phase10_virtio_ring.zig` replay still remains a direct-readback gap in this lane.",
                "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `drivers/virtio/virtio_ring.zig`, while `zigux/tests/phase10_virtio_ring_survey.zig` still remains a direct-readback gap in this lane.",
                "Documentation/zigux/phase10-closure-evidence.md:forbidden:The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `drivers/virtio/virtio_ring.zig`, while `zigux/tests/phase10_virtio_ring_survey.zig` still remains a direct-readback gap in this lane.",
            ),
            (
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
                "drivers/virtio/virtio_input_queue_callback_preflight.zig",
                "drivers/virtio/virtio_input_queue_callback_preflight_missing.zig",
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md:drivers/virtio/virtio_input_queue_callback_preflight.zig",
            ),
            (
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
                "`scripts/zigux/README.md` remains a neighboring shared reminder surface until a dedicated Phase 10 scripts-root packet rematerializes on current `master`",
                "`scripts/zigux/README.md` now anchors the active shared Phase 10 packet on current `master`",
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md:`scripts/zigux/README.md` remains a neighboring shared reminder surface until a dedicated Phase 10 scripts-root packet rematerializes on current `master`",
            ),
            (
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
                "current `master` now rematerializes `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/Makefile`; treat those returned validator and build-route surfaces as part of the shared closure gate while keeping only the still-missing core-side companions framed as last-known packet members or repo-reality gaps in this lane",
                "current `master` now rematerializes `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/Makefile`; treat those returned validator and build-route surfaces as part of the shared closure gate while keeping only the still-missing core-side companions framed as last-known packet members or repo-reality gaps in this lane",
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md:current `master` now rematerializes `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/Makefile`; treat those returned validator and build-route surfaces as part of the shared closure gate while keeping only the still-missing core-side companions framed as last-known packet members or repo-reality gaps in this lane",
            ),
            (
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
                "Use the directly re-readable shared validator pair, closure manifest, and Makefile-backed route anchors together with the returned core-survey, ring, input, and MMIO packet anchors before widening shared wording back into direct claims about the still-missing core-side companions.",
                "Use the directly re-readable closure validator and closure manifest together with the returned core-survey, ring, input, and MMIO route anchors before widening shared wording back into direct claims about the still-missing core-side companions.",
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md:Use the directly re-readable shared validator pair, closure manifest, and Makefile-backed route anchors together with the returned core-survey, ring, input, and MMIO packet anchors before widening shared wording back into direct claims about the still-missing core-side companions.",
            ),
            (
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
                "Current `master` also rematerializes `zigux/tests/phase10_virtio_ring_survey.zig`, so keep that dedicated ring survey gate explicit with `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and the shared `zigux/tests/phase10_build.zig` route instead of framing the survey gate as a direct-readback gap.",
                "Authenticated contents reads still fail for `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, and the broader validator-first `scripts/zigux/validate-phase10.py` route through the direct readback available in this lane.",
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md:forbidden:Authenticated contents reads still fail for `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, and the broader validator-first `scripts/zigux/validate-phase10.py` route through the direct readback available in this lane.",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                "drivers/virtio/virtio_input_queue_callback_preflight.zig",
                "drivers/virtio/virtio_input_queue_callback_preflight_missing.zig",
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:drivers/virtio/virtio_input_queue_callback_preflight.zig",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                "drivers/virtio/virtio_input_verify.zig",
                "drivers/virtio/virtio_input_verify_missing.zig",
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:drivers/virtio/virtio_input_verify.zig",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                "drivers/virtio/virtio_ring_verify.zig",
                "drivers/virtio/virtio_ring_verify_missing.zig",
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:drivers/virtio/virtio_ring_verify.zig",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
                "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent_missing.zig",
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                "returned shared closure packet anchors: `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `Documentation/zigux/phase10-virtio-core-survey.md`, and `zigux/tests/phase10_closure_manifest.json`",
                "returned shared closure packet anchors: `scripts/zigux/validate-phase10-closure.py`, `Documentation/zigux/phase10-virtio-core-survey.md`, and `zigux/tests/phase10_closure_manifest.json`",
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:returned shared closure packet anchors: `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `Documentation/zigux/phase10-virtio-core-survey.md`, and `zigux/tests/phase10_closure_manifest.json`",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                "Keep `zigux/tests/phase10_virtio_ring_survey.zig` explicit as the returned dedicated ring survey gate beside `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `zigux/tests/phase10_build.zig` instead of framing that survey replay as a last-known packet member.",
                "keep `zigux/tests/phase10_virtio_ring_survey.zig` framed as a last-known packet member until a fresh reread proves it rematerializes on current `master`.",
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:forbidden:keep `zigux/tests/phase10_virtio_ring_survey.zig` framed as a last-known packet member until a fresh reread proves it rematerializes on current `master`.",
            ),
            (
                "Documentation/zigux/phase10-virtio-input-module-slice.md",
                "queued status completions reclaimable in memory",
                "queued status completions drain directly to the transport",
                "Documentation/zigux/phase10-virtio-input-module-slice.md:queued status completions reclaimable in memory",
            ),
            (
                "Documentation/zigux/review-checklist.md",
                "make -C zigux phase10-validate",
                "phase10 validate route missing",
                "Documentation/zigux/review-checklist.md:make -C zigux phase10-validate",
            ),
            (
                "drivers/virtio/virtio_input_registration_preflight.zig",
                "pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
                "pub fn blockerLabel(blocker: RegistrationBlocker) []const u8 {",
                "drivers/virtio/virtio_input_registration_preflight.zig:pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
            ),
            (
                "drivers/virtio/virtio_input_verify.zig",
                "test \"phase10 virtio input verify keeps teardown wrapper parity explicit across reset\" {",
                "test \"phase10 virtio input verify drift\" {",
                "drivers/virtio/virtio_input_verify.zig:test \"phase10 virtio input verify keeps teardown wrapper parity explicit across reset\" {",
            ),
            (
                "drivers/virtio/virtio_ring_verify.zig",
                "test \"phase10 virtio ring verify keeps delayed callback wrapper thresholds explicit\" {",
                "test \"phase10 virtio ring verify drift\" {",
                "drivers/virtio/virtio_ring_verify.zig:test \"phase10 virtio ring verify keeps delayed callback wrapper thresholds explicit\" {",
            ),
            (
                "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
                "test \"phase10 virtio ring repeated prepareKick stays idle until new descriptors are published\" {",
                "test \"phase10 virtio ring prepareKick drift\" {",
                "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig:test \"phase10 virtio ring repeated prepareKick stays idle until new descriptors are published\" {",
            ),
            (
                "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                "const reset = try ring.resetQueue(2);",
                "const reset = try ring.resetQueue(7);",
                "zigux/tests/phase10_virtio_ring_reset_reuse.zig:const reset = try ring.resetQueue(2);",
            ),
            (
                "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
                "const cleared_summary = try ring.clearBroken(3);",
                "const cleared_summary = try ring.clearBroken(7);",
                "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig:const cleared_summary = try ring.clearBroken(3);",
            ),
            (
                "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
                "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
                "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(5));",
                "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig:try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
            ),
            (
                "zigux/tests/phase10_build.zig",
                "\"phase10-virtio-input-survey-tests\"",
                "\"phase10-virtio-input-survey-tests-missing\"",
                "zigux/tests/phase10_build.zig:\"phase10-virtio-input-survey-tests\"",
            ),
            (
                "zigux/tests/phase10_build.zig",
                "\"phase10-virtio-input-verify-tests\"",
                "\"phase10-virtio-input-verify-tests-missing\"",
                "zigux/tests/phase10_build.zig:\"phase10-virtio-input-verify-tests\"",
            ),
            (
                "zigux/tests/phase10_build.zig",
                "\"phase10-virtio-ring-prepare-kick-idempotent-tests\"",
                "\"phase10-virtio-ring-prepare-kick-idempotent-tests-missing\"",
                "zigux/tests/phase10_build.zig:\"phase10-virtio-ring-prepare-kick-idempotent-tests\"",
            ),
            (
                "zigux/tests/phase10_build.zig",
                "\"phase10-virtio-ring-broken-queue-queue-discipline-tests\"",
                "\"phase10-virtio-ring-broken-queue-queue-discipline-tests-missing\"",
                "zigux/tests/phase10_build.zig:\"phase10-virtio-ring-broken-queue-queue-discipline-tests\"",
            ),
            (
                "zigux/tests/phase10_build.zig",
                "\"phase10-virtio-ring-survey-tests\"",
                "\"phase10-virtio-ring-survey-tests-missing\"",
                "zigux/tests/phase10_build.zig:\"phase10-virtio-ring-survey-tests\"",
            ),
            (
                "zigux/tests/phase10_build.zig",
                "Run the live Phase 10 virtio core, input, ring, and MMIO lab validation tests",
                "Run the live Phase 10 virtio input, ring, and MMIO lab validation tests",
                "zigux/tests/phase10_build.zig:forbidden:Run the live Phase 10 virtio input, ring, and MMIO lab validation tests",
            ),
            (
                "zigux/Makefile",
                "phase10: phase10-validate phase10-test",
                "phase10: phase10-validate",
                "zigux/Makefile:phase10: phase10-validate phase10-test",
            ),
            (
                "scripts/zigux/check-phase10-bootstrap-route.py",
                "TEST_CMD = \"make -C zigux phase10-test\"",
                "TEST_CMD = \"make -C zigux phase10-test-missing\"",
                "scripts/zigux/check-phase10-bootstrap-route.py:TEST_CMD = \"make -C zigux phase10-test\"",
            ),
            (
                "scripts/zigux/check-phase10-shared-freeze-boundary.py",
                "\"kernel/trace/ring_buffer.c\"",
                "\"kernel/trace/ring_buffer_drift.c\"",
                "scripts/zigux/check-phase10-shared-freeze-boundary.py:\"kernel/trace/ring_buffer.c\"",
            ),
            (
                ".github/workflows/zigux-bootstrap.yml",
                "Run Phase 10 helper tests",
                "Run Phase 10 helper drift",
                ".github/workflows/zigux-bootstrap.yml:Run Phase 10 helper tests",
            ),
        ]

        for rel_path, old, new, expected in cases:
            expect_missing_marker(root, rel_path, old, new, expected)

        expect_missing_file(root, "Documentation/zigux/phase10-closure-evidence.md")
        expect_missing_file(root, "drivers/virtio/virtio_ring_verify.zig")

    print("PHASE10_HARNESS_COVERAGE_SELF_TEST=pass")
    print("PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT=38")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 10 harness-coverage packet."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(args.repo_root)
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

    required_marker_count = sum(len(markers) for markers in REQUIRED_MARKERS.values())
    forbidden_marker_count = sum(len(markers) for markers in FORBIDDEN_MARKERS.values())
    print("PHASE10_HARNESS_COVERAGE=pass")
    print(f"PHASE10_HARNESS_COVERAGE_REQUIRED_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE10_HARNESS_COVERAGE_REQUIRED_MARKER_COUNT={required_marker_count}")
    print(f"PHASE10_HARNESS_COVERAGE_FORBIDDEN_MARKER_COUNT={forbidden_marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())