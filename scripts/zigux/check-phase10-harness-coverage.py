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
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_mmio_manifest.json",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
        "blocked risky-transport posture",
    ],
    "Documentation/zigux/phase10-closure-evidence.md": [
        "`PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`",
        "directly re-readable shared reminder surfaces now include `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`",
        "directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/Makefile`",
        "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, and `zigux/tests/phase10_virtio_mmio_manifest.json`",
        "`zigux/Makefile` itself now rematerializes on current `master`, and its live body exposes the dedicated shared Phase 10 validate/test route stack, so keep the returned file and that returned build-gate posture explicit here rather than framing it as a repo-reality gap.",
        "The shared bootstrap-route guard now stays explicit through `scripts/zigux/check-phase10-bootstrap-route.py` so the closure packet fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`.",
        "`lab_only_driver_validation=starter_landed`",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "drivers/virtio/virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "current `master` still does not materialize `scripts/zigux/validate-phase10.py` or `scripts/zigux/validate-phase10-closure.py` through the direct readback available in this lane, while `zigux/Makefile` now rematerializes and its live body exposes `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10`, so keep those still-missing dedicated validator-script names framed as last-known packet members or repo-reality gaps while treating the returned Makefile-backed route stack as the shared build gate",
        "`zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig` are back as directly re-readable helper-local manifest and replay anchors",
        "Keep the returned `zigux/Makefile` body together with `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit as the shared build gate rather than restating them as gaps.",
        "Treat the shared `zigux/tests/phase10_build.zig` route as already-landed validation evidence",
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
        'test "phase10 virtio input verify keeps wrapper-facing queue preflight ordering explicit" {',
        'test "phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims" {',
        'test "phase10 virtio input verify keeps teardown wrapper parity explicit across reset" {',
    ],
    "zigux/tests/phase10_build.zig": [
        '"phase10-virtio-core-tests"',
        '"phase10-virtio-input-queue-callback-preflight-tests"',
        '"phase10-virtio-input-teardown-observation-tests"',
        '"phase10-virtio-input-verify-tests"',
        '"phase10-virtio-ring-verify-tests"',
        '"phase10-virtio-mmio-verify-tests"',
        '"phase10-virtio-mmio-survey-tests"',
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
        'VALIDATE_STEP = "Validate Phase 10 checker-backed review packet"',
        'VALIDATE_CMD = "make -C zigux phase10-validate"',
        'TEST_STEP = "Run Phase 10 helper tests"',
        'TEST_CMD = "make -C zigux phase10-test"',
    ],
    "scripts/zigux/check-phase10-shared-freeze-boundary.py": [
        'CHECK_COMMAND = "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py"',
        '"kernel/workqueue.c"',
        '"kernel/trace/ring_buffer.c"',
        '"kernel/sched/core.c"',
        '"net/core/skbuff.c"',
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
                "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, and `zigux/tests/phase10_virtio_mmio_manifest.json`",
                "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json` and `zigux/tests/phase10_virtio_input_manifest.json`",
                "Documentation/zigux/phase10-closure-evidence.md:forbidden:directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json` and `zigux/tests/phase10_virtio_input_manifest.json`",
            ),
            (
                "Documentation/zigux/phase10-closure-evidence.md",
                "`zigux/Makefile` itself now rematerializes on current `master`, and its live body exposes the dedicated shared Phase 10 validate/test route stack, so keep the returned file and that returned build-gate posture explicit here rather than framing it as a repo-reality gap.",
                "`zigux/Makefile` still exposes only the earlier toolchain routes.",
                "Documentation/zigux/phase10-closure-evidence.md:`zigux/Makefile` itself now rematerializes on current `master`, and its live body exposes the dedicated shared Phase 10 validate/test route stack, so keep the returned file and that returned build-gate posture explicit here rather than framing it as a repo-reality gap.",
            ),
            (
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
                "drivers/virtio/virtio_input_queue_callback_preflight.zig",
                "drivers/virtio/virtio_input_queue_callback_preflight_missing.zig",
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md:drivers/virtio/virtio_input_queue_callback_preflight.zig",
            ),
            (
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
                "Keep the returned `zigux/Makefile` body together with `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit as the shared build gate rather than restating them as gaps.",
                "Keep the shared build gate implicit.",
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md:Keep the returned `zigux/Makefile` body together with `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit as the shared build gate rather than restating them as gaps.",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                "drivers/virtio/virtio_input_queue_callback_preflight.zig",
                "drivers/virtio/virtio_input_queue_callback_preflight_missing.zig",
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:drivers/virtio/virtio_input_queue_callback_preflight.zig",
            ),
            (
                "Documentation/zigux/phase10-virtio-input-module-slice.md",
                "queued status completions reclaimable in memory",
                "queued status completions drain directly to the transport",
                "Documentation/zigux/phase10-virtio-input-module-slice.md:queued status completions reclaimable in memory",
            ),
            (
                "drivers/virtio/virtio_input_verify.zig",
                'test "phase10 virtio input verify keeps teardown wrapper parity explicit across reset" {',
                'test "phase10 virtio input verify drift" {',
                'drivers/virtio/virtio_input_verify.zig:test "phase10 virtio input verify keeps teardown wrapper parity explicit across reset" {',
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
                'TEST_CMD = "make -C zigux phase10-test"',
                'TEST_CMD = "make -C zigux phase10-test-missing"',
                'scripts/zigux/check-phase10-bootstrap-route.py:TEST_CMD = "make -C zigux phase10-test"',
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

    print("PHASE10_HARNESS_COVERAGE_SELF_TEST=pass")
    print("PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT=12")
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
