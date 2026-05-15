#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

FILES = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "zigux/tests/README.md",
]

MMIO_PACKET_FILES = [
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
]

REQUIRED_FILES = [*FILES, *MMIO_PACKET_FILES]

MAKE_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py --self-test",
    "scripts/zigux/check-phase10-harness-coverage.py",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 10 harness coverage checker",
    "python3 scripts/zigux/check-phase10-harness-coverage.py --self-test",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
]

BUILD_MARKERS = [
    "phase10-virtio-core-reset-queue-tests",
    "phase10-virtio-driver-id-tests",
    "phase10-virtio-input-status-drain-tests",
    "phase10-virtio-input-queue-callback-preflight-tests",
    "phase10-virtio-mmio-verify-tests",
]

MANIFEST_TEXT_MARKERS = [
    '"phase": "Phase 10"',
    '"tranche": "virtio-lab-bundle"',
    '"test_count":',
    '"scripts/zigux/check-phase10-harness-coverage.py"',
    '"scripts/zigux/check-phase10-tests-readme-core-surfaces.py"',
    '"zigux/tests/phase10_build.zig"',
]

EXACT_CHECK_MARKERS = [
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test",
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
]

EXPECTED_READY_TRANSPORT_FOLLOWUPS = {
    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
}

EXPECTED_LAB_VALIDATION_EVIDENCE = [
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
]

EXPECTED_FOCUSED_HARNESS_REPLAYS = {
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig": [
        "phase10 core compound-ack replay"
    ],
    "zigux/tests/phase10_virtio_core_reset_queue.zig": [
        "phase10 core reset-queue replay"
    ],
    "zigux/tests/phase10_virtio_driver_id.zig": [
        "phase10 driver-id review path replay"
    ],
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig": [
        "phase10 ring drained-reset reuse replay"
    ],
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig": [
        "phase10 input queue-callback-preflight replay"
    ],
    "zigux/tests/phase10_virtio_input_status_drain.zig": [
        "phase10 input status-drain replay"
    ],
    "zigux/tests/phase10_virtio_input_probe_preflight.zig": [
        "phase10 input probe-preflight replay"
    ],
    "zigux/tests/phase10_virtio_input_registration_preflight.zig": [
        "phase10 input registration-preflight replay"
    ],
    "zigux/tests/phase10_virtio_input_teardown_observation.zig": [
        "phase10 input teardown-observation replay"
    ],
}

EXPECTED_TEST_LIST_MARKERS = list(EXPECTED_FOCUSED_HARNESS_REPLAYS.keys())

EXPECTED_TEST_COUNT = 17

SCRIPTS_README_MARKERS = [
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`Documentation/zigux/phase10-virtio-core-slice.md`",
    "`Documentation/zigux/phase10-virtio-ring-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
]

TESTS_ROOT_COMPANION_MARKERS = [
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`Documentation/zigux/phase10-virtio-core-slice.md`",
    "`Documentation/zigux/phase10-virtio-ring-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
]

TESTS_README_MARKERS = [
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`drivers/virtio/virtio.zig`",
    "`drivers/virtio/virtio_driver_id.zig`",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    checks = [
        ("scripts_readme", "scripts/zigux/README.md", SCRIPTS_README_MARKERS),
        (
            "tests_root_companion",
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            TESTS_ROOT_COMPANION_MARKERS,
        ),
        ("make", "zigux/Makefile", MAKE_MARKERS),
        ("workflow", ".github/workflows/zigux-bootstrap.yml", WORKFLOW_MARKERS),
        ("build", "zigux/tests/phase10_build.zig", BUILD_MARKERS),
        ("manifest", "zigux/tests/phase10_closure_manifest.json", MANIFEST_TEXT_MARKERS),
        ("tests_readme", "zigux/tests/README.md", TESTS_README_MARKERS),
    ]
    for label, rel_path, markers in checks:
        check_markers(missing, label, read_text(root, rel_path), markers)

    manifest = json.loads(read_text(root, "zigux/tests/phase10_closure_manifest.json"))
    scoreboard = manifest.get("roadmap_parity_scoreboard")
    if not isinstance(scoreboard, dict):
        missing.append("manifest:roadmap_parity_scoreboard")
    else:
        lab_validation = scoreboard.get("lab_only_driver_validation")
        if not isinstance(lab_validation, dict):
            missing.append("manifest:roadmap_parity_scoreboard:lab_only_driver_validation")
        else:
            evidence = lab_validation.get("evidence")
            if not isinstance(evidence, list):
                missing.append("manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence")
            else:
                for path in EXPECTED_LAB_VALIDATION_EVIDENCE:
                    if path not in evidence:
                        missing.append(
                            "manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence:"
                            + path
                        )

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        missing.append("manifest:exact_checks")
    else:
        for marker in EXACT_CHECK_MARKERS:
            if marker not in exact_checks:
                missing.append(f"manifest:exact_checks:{marker}")

    tests = manifest.get("tests")
    if not isinstance(tests, list):
        missing.append("manifest:tests")
    else:
        for marker in EXPECTED_TEST_LIST_MARKERS:
            if marker not in tests:
                missing.append(f"manifest:tests:{marker}")

    actual_test_count = manifest.get("test_count")
    if actual_test_count != EXPECTED_TEST_COUNT:
        missing.append(f"manifest:test_count={actual_test_count!r}")
    elif isinstance(tests, list) and len(tests) != EXPECTED_TEST_COUNT:
        missing.append(f"manifest:tests:length={len(tests)!r}")

    focused_harness_replays = manifest.get("focused_harness_replays")
    if not isinstance(focused_harness_replays, dict):
        missing.append("manifest:focused_harness_replays")
    else:
        for path, expected in EXPECTED_FOCUSED_HARNESS_REPLAYS.items():
            actual = focused_harness_replays.get(path)
            if actual != expected:
                missing.append(
                    "manifest:focused_harness_replays:" + path + "=" + repr(actual)
                )

    ready_transport_followups = manifest.get("ready_transport_followups")
    if not isinstance(ready_transport_followups, dict):
        missing.append("manifest:ready_transport_followups")
    else:
        for path, gap_id in EXPECTED_READY_TRANSPORT_FOLLOWUPS.items():
            actual = ready_transport_followups.get(path)
            if actual != gap_id:
                missing.append(
                    "manifest:ready_transport_followups:" + path + "=" + repr(actual)
                )
        for path in sorted(set(ready_transport_followups) - set(EXPECTED_READY_TRANSPORT_FOLLOWUPS)):
            missing.append(
                "manifest:ready_transport_followups:extra:"
                + path
                + "="
                + repr(ready_transport_followups[path])
            )

    blocked_transport_gaps = manifest.get("blocked_transport_gaps")
    if not isinstance(blocked_transport_gaps, dict):
        missing.append("manifest:blocked_transport_gaps")
    else:
        for path, gap_id in EXPECTED_READY_TRANSPORT_FOLLOWUPS.items():
            actual = blocked_transport_gaps.get(path)
            if actual != gap_id:
                missing.append(
                    "manifest:blocked_transport_gaps:" + path + "=" + repr(actual)
                )

    return [], missing


def write_fixture(root: Path) -> None:
    text_files = {
        "Documentation/zigux/phase10-virtio-mmio-slice.md": "fixture\n",
        "Documentation/zigux/phase10-virtio-mmio-survey.md": "fixture\n",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": "\n".join(
            TESTS_ROOT_COMPANION_MARKERS
        )
        + "\n",
        "scripts/zigux/check-phase10-harness-coverage.py": "fixture\n",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py": "fixture\n",
        "scripts/zigux/check-phase10-mmio-packet.py": "fixture\n",
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py": "fixture\n",
        "scripts/zigux/README.md": "\n".join(SCRIPTS_README_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(WORKFLOW_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/tests/phase10_closure_manifest.json": json.dumps(
            {
                "phase": "Phase 10",
                "tranche": "virtio-lab-bundle",
                "test_count": EXPECTED_TEST_COUNT,
                "roadmap_parity_scoreboard": {
                    "lab_only_driver_validation": {
                        "evidence": EXPECTED_LAB_VALIDATION_EVIDENCE
                    }
                },
                "exact_checks": EXACT_CHECK_MARKERS,
                "ready_transport_followups": EXPECTED_READY_TRANSPORT_FOLLOWUPS,
                "focused_harness_replays": EXPECTED_FOCUSED_HARNESS_REPLAYS,
                "tests": [
                    "zigux/tests/phase10_virtio_core.zig",
                    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
                    "zigux/tests/phase10_virtio_core_reset_queue.zig",
                    "zigux/tests/phase10_virtio_core_survey.zig",
                    "zigux/tests/phase10_virtio_driver_id.zig",
                    "zigux/tests/phase10_virtio_ring.zig",
                    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                    "zigux/tests/phase10_virtio_ring_survey.zig",
                    "zigux/tests/phase10_virtio_input.zig",
                    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
                    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
                    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
                    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
                    "zigux/tests/phase10_virtio_input_status_drain.zig",
                    "zigux/tests/phase10_virtio_input_survey.zig",
                    "zigux/tests/phase10_virtio_mmio.zig",
                    "zigux/tests/phase10_virtio_mmio_survey.zig",
                ],
                "blocked_transport_gaps": {
                    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
                    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
                },
            },
            indent=2,
        )
        + "\n",
        "zigux/tests/phase10_virtio_mmio.zig": "fixture\n",
        "zigux/tests/phase10_virtio_mmio_manifest.json": "fixture\n",
        "zigux/tests/phase10_virtio_mmio_survey.zig": "fixture\n",
        "zigux/tests/README.md": "\n".join(TESTS_README_MARKERS) + "\n",
        "drivers/virtio/virtio_mmio.zig": "fixture\n",
        "drivers/virtio/virtio_mmio_verify.zig": "fixture\n",
    }
    for rel_path, content in text_files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase10-harness-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase10-harness-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def expect_missing_file(label: str, root: Path, rel_path: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(
            f"phase10-harness-self-test:{label}:unexpected_missing_markers:{','.join(missing_markers)}"
        )
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(
            f"phase10-harness-self-test:{label}:expected_missing_file:{rel_path}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_harness_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-harness-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        mmio_verify_path = root / "drivers/virtio/virtio_mmio_verify.zig"
        mmio_verify_path.unlink()
        expect_missing_file(
            "mmio_verify_surface",
            root,
            "drivers/virtio/virtio_mmio_verify.zig",
        )
        write_fixture(root)

        build_path = root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace("phase10-virtio-driver-id-tests", "phase10-driver-id-drift", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_driver_id_marker",
            root,
            "build:phase10-virtio-driver-id-tests",
        )
        build_path.write_text(original_build, encoding="utf-8")

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "Self-test Phase 10 harness coverage checker",
                "Phase 10 harness drift",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_selftest_step",
            root,
            "workflow:Self-test Phase 10 harness coverage checker",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        scripts_readme_path = root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
                "`scripts/zigux/check-phase10-tests-readme-core-surfaces-removed.py`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_core_checker",
            root,
            "scripts_readme:`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "`Documentation/zigux/phase10-virtio-ring-slice.md`",
                "`Documentation/zigux/phase10-virtio-ring-slice-missing.md`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_ring_slice",
            root,
            "scripts_readme:`Documentation/zigux/phase10-virtio-ring-slice.md`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
                "`Documentation/zigux/phase10-virtio-input-module-slice-missing.md`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_input_module_slice",
            root,
            "scripts_readme:`Documentation/zigux/phase10-virtio-input-module-slice.md`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
                "`Documentation/zigux/phase10-virtio-mmio-slice-missing.md`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_mmio_slice",
            root,
            "scripts_readme:`Documentation/zigux/phase10-virtio-mmio-slice.md`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        tests_root_companion_path = (
            root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        )
        original_tests_root_companion = tests_root_companion_path.read_text(encoding="utf-8")
        tests_root_companion_path.write_text(
            original_tests_root_companion.replace(
                "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
                "`Documentation/zigux/phase10-virtio-input-module-slice-missing.md`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_root_companion_input_module_slice",
            root,
            "tests_root_companion:`Documentation/zigux/phase10-virtio-input-module-slice.md`",
        )
        tests_root_companion_path.write_text(original_tests_root_companion, encoding="utf-8")

        tests_root_companion_path.write_text(
            original_tests_root_companion.replace(
                "`scripts/zigux/check-phase10-harness-coverage.py`",
                "`scripts/zigux/check-phase10-harness-coverage-missing.py`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_root_companion_harness_checker",
            root,
            "tests_root_companion:`scripts/zigux/check-phase10-harness-coverage.py`",
        )
        tests_root_companion_path.write_text(original_tests_root_companion, encoding="utf-8")

        manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            "zigux/tests/phase10_build.zig",
            "scripts/zigux/check-phase10-harness-coverage.py",
            "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_checker_evidence",
            root,
            "manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence:zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_checks"] = [
            "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_exact_checks",
            root,
            "manifest:exact_checks:python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["focused_harness_replays"] = {}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_compound_ack_replay",
            root,
            "manifest:focused_harness_replays:zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig=None",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["focused_harness_replays"]["zigux/tests/phase10_virtio_ring_reset_reuse.zig"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_ring_reset_reuse_replay",
            root,
            "manifest:focused_harness_replays:zigux/tests/phase10_virtio_ring_reset_reuse.zig=None",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tests"] = [
            path
            for path in manifest["tests"]
            if path != "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_tests_core_compound_ack",
            root,
            "manifest:tests:zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tests"] = [
            path
            for path in manifest["tests"]
            if path != "zigux/tests/phase10_virtio_input_status_drain.zig"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_tests_input_status_drain",
            root,
            "manifest:tests:zigux/tests/phase10_virtio_input_status_drain.zig",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["test_count"] = 16
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_test_count",
            root,
            "manifest:test_count=16",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["ready_transport_followups"][
            "zigux/tests/phase10_virtio_input_manifest.json"
        ] = "phase10-virtio-input-registration-lifecycle-drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_ready_transport_followup_input",
            root,
            "manifest:ready_transport_followups:zigux/tests/phase10_virtio_input_manifest.json='phase10-virtio-input-registration-lifecycle-drift'",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["ready_transport_followups"][
            "zigux/tests/phase10_virtio_ring_manifest.json"
        ] = "phase10-ring-lab-driver-bridge"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_ready_transport_followup_extra",
            root,
            "manifest:ready_transport_followups:extra:zigux/tests/phase10_virtio_ring_manifest.json='phase10-ring-lab-driver-bridge'",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["blocked_transport_gaps"][
            "zigux/tests/phase10_virtio_mmio_manifest.json"
        ] = "phase10-mmio-lifecycle-and-irq-paths-drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_blocked_transport_gap_mmio",
            root,
            "manifest:blocked_transport_gaps:zigux/tests/phase10_virtio_mmio_manifest.json='phase10-mmio-lifecycle-and-irq-paths-drift'",
        )
        write_fixture(root)

        tests_readme_path = root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "`drivers/virtio/virtio_driver_id.zig`",
                "`drivers/virtio/virtio_driver_id_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_direct_core_surface",
            root,
            "tests_readme:`drivers/virtio/virtio_driver_id.zig`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        checker_path = root / "scripts/zigux/check-phase10-tests-readme-core-surfaces.py"
        checker_path.unlink()
        expect_missing_file(
            "checker_file",
            root,
            "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        )

    print("PHASE10_HARNESS_COVERAGE_SELF_TEST=pass")
    print("PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT=29")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE10_HARNESS_COVERAGE=fail")
    print("MISSING_PHASE10_HARNESS_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE10_HARNESS_FILES_END")
    sys.exit(1)
if missing_markers:
    print("PHASE10_HARNESS_COVERAGE=fail")
    print("MISSING_PHASE10_HARNESS_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE10_HARNESS_MARKERS_END")
    sys.exit(1)

print("PHASE10_HARNESS_COVERAGE=pass")
print(f"PHASE10_HARNESS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(
    "PHASE10_HARNESS_REQUIRED_MARKER_COUNT="
    f"{len(SCRIPTS_README_MARKERS) + len(TESTS_ROOT_COMPANION_MARKERS) + len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(BUILD_MARKERS) + len(MANIFEST_TEXT_MARKERS) + len(EXACT_CHECK_MARKERS) + len(TESTS_README_MARKERS)}"
)