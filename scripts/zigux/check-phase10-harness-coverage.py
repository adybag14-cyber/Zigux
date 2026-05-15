#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

FILES = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/README.md",
]

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
    '"zigux/tests/phase10_virtio_ring_reset_reuse.zig"',
]

EXACT_CHECK_MARKERS = [
    "python3 scripts/zigux/validate-phase10.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "make -C zigux phase10-validate",
    "python3 scripts/zigux/check-phase10-core-packet.py",
    "python3 scripts/zigux/check-phase10-ring-packet.py",
    "python3 scripts/zigux/check-phase10-input-packet.py",
    "python3 scripts/zigux/check-phase10-mmio-packet.py",
    "python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py",
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test",
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "python3 scripts/zigux/check-phase10-harness-coverage.py --self-test",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

SCRIPTS_README_MARKERS = [
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`scripts/zigux/validate-phase10.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`drivers/virtio/virtio_ring.zig`",
    "`drivers/virtio/virtio_ring_verify.zig`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "`zigux/tests/phase10_virtio_ring_manifest.json`",
    "`drivers/virtio/virtio_input.zig`",
    "`drivers/virtio/virtio_input_verify.zig`",
    "`zigux/tests/phase10_virtio_input_probe_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_registration_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_observation.zig`",
    "`zigux/tests/phase10_virtio_input_status_drain.zig`",
    "`zigux/tests/phase10_virtio_input_manifest.json`",
    "`drivers/virtio/virtio_mmio.zig`",
    "`drivers/virtio/virtio_mmio_verify.zig`",
    "`zigux/tests/phase10_virtio_mmio.zig`",
    "`zigux/tests/phase10_virtio_mmio_manifest.json`",
    "`Documentation/zigux/phase10-virtio-core-slice.md`",
    "`Documentation/zigux/phase10-virtio-ring-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
    "`make -C zigux phase10-validate`",
    "`make -C zigux phase10-test`",
]

DOC_README_MARKERS = [
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-core-survey.md`",
    "`Documentation/zigux/phase10-virtio-ring-survey.md`",
    "`Documentation/zigux/phase10-virtio-input-survey.md`",
    "`Documentation/zigux/phase10-virtio-mmio-survey.md`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`scripts/zigux/check-phase10-mmio-packet.py`",
    "`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
    "`scripts/zigux/validate-phase10.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`drivers/virtio/virtio.zig`",
    "`drivers/virtio/virtio_driver_id.zig`",
    "`drivers/virtio/virtio_verify.zig`",
    "`zigux/tests/phase10_virtio_core.zig`",
    "`zigux/tests/phase10_virtio_core_reset_queue.zig`",
    "`zigux/tests/phase10_virtio_driver_id.zig`",
    "`drivers/virtio/virtio_ring.zig`",
    "`drivers/virtio/virtio_ring_verify.zig`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "`zigux/tests/phase10_virtio_ring_manifest.json`",
    "`drivers/virtio/virtio_input_probe_preflight.zig`",
    "`drivers/virtio/virtio_mmio.zig`",
    "`drivers/virtio/virtio_mmio_verify.zig`",
    "`zigux/tests/phase10_virtio_mmio.zig`",
    "`zigux/tests/phase10_virtio_mmio_manifest.json`",
    "`Documentation/zigux/phase10-virtio-core-slice.md`",
    "`Documentation/zigux/phase10-virtio-ring-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
    "`make -C zigux phase10-validate`",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
]

TESTS_README_MARKERS = [
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`drivers/virtio/virtio.zig`",
    "`drivers/virtio/virtio_driver_id.zig`",
    "`drivers/virtio/virtio_ring.zig`",
    "`drivers/virtio/virtio_ring_verify.zig`",
    "`zigux/tests/phase10_virtio_ring_manifest.json`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
]

REVIEW_CHECKLIST_MARKERS = [
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-virtio-core-slice.md`",
    "`Documentation/zigux/phase10-virtio-ring-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
    "`scripts/zigux/check-phase10-core-packet.py`",
    "`scripts/zigux/check-phase10-ring-packet.py`",
    "`scripts/zigux/check-phase10-input-packet.py`",
    "`scripts/zigux/check-phase10-mmio-packet.py`",
    "`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`scripts/zigux/validate-phase10.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`drivers/virtio/virtio_ring.zig`",
    "`drivers/virtio/virtio_ring_verify.zig`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "`drivers/virtio/virtio_input.zig`",
    "`drivers/virtio/virtio_input_verify.zig`",
    "`drivers/virtio/virtio_mmio.zig`",
    "`drivers/virtio/virtio_mmio_verify.zig`",
    "`zigux/tests/phase10_virtio_mmio.zig`",
    "`zigux/tests/phase10_virtio_mmio_manifest.json`",
    "`make -C zigux phase10-validate`",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
]

CLOSURE_NOTE_MARKERS = [
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`zigux/Makefile` `phase10-test` route",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "ring drained-reset reuse replay",
    "`Documentation/zigux/phase10-virtio-core-slice.md`",
    "`Documentation/zigux/phase10-virtio-ring-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
    "`Documentation/zigux/README.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` should all treat the core, ring, input, input-module, and MMIO slice notes as restored current-`master` evidence",
    "This closure note should no longer treat `Documentation/zigux/phase10-virtio-mmio-slice.md` as a remaining repo-reality gap.",
]

COMPANION_MARKERS = [
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "ring drained-reset reuse replay",
    "`drivers/virtio/virtio_input_probe_preflight.zig`",
]

LANE_NOTE_MARKERS = [
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "`make -C zigux phase10-validate`",
    "`drivers/virtio/virtio_input_probe_preflight.zig`",
]

INPUT_SURVEY_MARKERS = [
    "`drivers/virtio/virtio_input_probe_preflight.zig`",
]

CHECKS = [
    ("closure_note", "Documentation/zigux/phase10-closure-evidence.md", CLOSURE_NOTE_MARKERS),
    (
        "companion",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
        COMPANION_MARKERS,
    ),
    ("lane_note", "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", LANE_NOTE_MARKERS),
    ("input_survey", "Documentation/zigux/phase10-virtio-input-survey.md", INPUT_SURVEY_MARKERS),
    ("review_checklist", "Documentation/zigux/review-checklist.md", REVIEW_CHECKLIST_MARKERS),
    ("doc_readme", "Documentation/zigux/README.md", DOC_README_MARKERS),
    ("scripts_readme", "scripts/zigux/README.md", SCRIPTS_README_MARKERS),
    ("make", "zigux/Makefile", MAKE_MARKERS),
    ("workflow", ".github/workflows/zigux-bootstrap.yml", WORKFLOW_MARKERS),
    ("build", "zigux/tests/phase10_build.zig", BUILD_MARKERS),
    ("manifest", "zigux/tests/phase10_closure_manifest.json", MANIFEST_TEXT_MARKERS),
    ("tests_readme", "zigux/tests/README.md", TESTS_README_MARKERS),
]

FIXTURE_CONTENT = {
    "Documentation/zigux/phase10-closure-evidence.md": "\n".join(
        [
            "# Phase 10 Closure Evidence",
            "",
            "- a dedicated shared harness-coverage checker, `scripts/zigux/check-phase10-harness-coverage.py`, keeps the packet honest",
            "- a focused tests-root direct-core checker, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, keeps the direct-core reminder explicit",
            "- a manifest-backed closure packet, `zigux/tests/phase10_closure_manifest.json`, still records the intended packet",
            "- the broader shared reminder packet keeps the exact `zigux/tests/phase10_virtio_ring_reset_reuse.zig` replay explicit on current `master`",
            "- the ring drained-reset reuse replay stays visible beside the shared closure packet",
            "- the live `zigux/Makefile` `phase10-test` route reruns the shared packet",
            "- `make -C zigux phase10-test` and `make -C zigux phase10` remain the local replay wrappers",
            "- direct rereads still keep `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md` explicit in the closure packet",
            "- `Documentation/zigux/README.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` should all treat the core, ring, input, input-module, and MMIO slice notes as restored current-`master` evidence instead of leaving the MMIO slice note framed as a missing companion.",
            "- This closure note should no longer treat `Documentation/zigux/phase10-virtio-mmio-slice.md` as a remaining repo-reality gap.",
            "",
        ]
    ),
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": "\n".join(COMPANION_MARKERS)
    + "\n",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "\n".join(LANE_NOTE_MARKERS) + "\n",
    "Documentation/zigux/phase10-virtio-input-survey.md": "\n".join(INPUT_SURVEY_MARKERS) + "\n",
    "Documentation/zigux/review-checklist.md": "# Zigux Review Checklist\n\n"
    + "\n".join(REVIEW_CHECKLIST_MARKERS)
    + "\n",
    "Documentation/zigux/README.md": "\n".join(DOC_README_MARKERS) + "\n",
    "scripts/zigux/check-phase10-harness-coverage.py": "fixture\n",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py": "fixture\n",
    "scripts/zigux/README.md": "\n".join(SCRIPTS_README_MARKERS) + "\n",
    "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
    ".github/workflows/zigux-bootstrap.yml": "\n".join(WORKFLOW_MARKERS) + "\n",
    "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
    "zigux/tests/README.md": "\n".join(TESTS_README_MARKERS) + "\n",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def manifest_fixture_text() -> str:
    return json.dumps(
        {
            "phase": "Phase 10",
            "tranche": "virtio-lab-bundle",
            "test_count": 16,
            "roadmap_parity_scoreboard": {
                "lab_only_driver_validation": {
                    "evidence": [
                        "zigux/tests/phase10_build.zig",
                        "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                        "scripts/zigux/check-phase10-harness-coverage.py",
                        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
                    ]
                }
            },
            "exact_checks": EXACT_CHECK_MARKERS,
        },
        indent=2,
    ) + "\n"


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    for label, rel_path, markers in CHECKS:
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
                for path in [
                    "zigux/tests/phase10_build.zig",
                    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                    "scripts/zigux/check-phase10-harness-coverage.py",
                    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
                ]:
                    if path not in evidence:
                        missing.append(
                            "manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence:" + path
                        )

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        missing.append("manifest:exact_checks")
    else:
        for marker in EXACT_CHECK_MARKERS:
            if marker not in exact_checks:
                missing.append(f"manifest:exact_checks:{marker}")

    return [], missing


def write_fixture(root: Path) -> None:
    text_files = dict(FIXTURE_CONTENT)
    text_files["zigux/tests/phase10_closure_manifest.json"] = manifest_fixture_text()
    for rel_path, content in text_files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"phase10-harness-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}")
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
        raise SystemExit(f"phase10-harness-self-test:{label}:expected_missing_file:{rel_path}:actual:{actual}")


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

        review_checklist_path = root / "Documentation/zigux/review-checklist.md"
        original_review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            original_review_checklist.replace(
                "`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
                "`scripts/zigux/check-phase10-mmio-freeze-boundary-missing.py`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_checklist_mmio_freeze_checker",
            root,
            "review_checklist:`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        review_checklist_path.write_text(
            original_review_checklist.replace(
                "`Documentation/zigux/phase10-closure-evidence.md`",
                "`Documentation/zigux/phase10-closure-evidence-missing.md`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_checklist_closure_evidence_marker",
            root,
            "review_checklist:`Documentation/zigux/phase10-closure-evidence.md`",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        review_checklist_path.write_text(
            original_review_checklist.replace(
                "`Documentation/zigux/phase10-virtio-core-slice.md`",
                "`Documentation/zigux/phase10-virtio-core-slice-missing.md`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_checklist_core_slice_marker",
            root,
            "review_checklist:`Documentation/zigux/phase10-virtio-core-slice.md`",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        review_checklist_path.write_text(
            original_review_checklist.replace(
                "`make -C zigux phase10-validate`",
                "`make -C zigux phase10-validate-missing`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_checklist_phase10_validate_route",
            root,
            "review_checklist:`make -C zigux phase10-validate`",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        review_checklist_path.write_text(
            original_review_checklist.replace(
                "`drivers/virtio/virtio_input.zig`",
                "`drivers/virtio/virtio_input_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_checklist_input_driver_surface",
            root,
            "review_checklist:`drivers/virtio/virtio_input.zig`",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        review_checklist_path.write_text(
            original_review_checklist.replace(
                "`drivers/virtio/virtio_input_verify.zig`",
                "`drivers/virtio/virtio_input_verify_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_checklist_input_verify_surface",
            root,
            "review_checklist:`drivers/virtio/virtio_input_verify.zig`",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        doc_readme_path = root / "Documentation/zigux/README.md"
        original_doc_readme = doc_readme_path.read_text(encoding="utf-8")
        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`scripts/zigux/check-phase10-harness-coverage.py`",
                "`scripts/zigux/check-phase10-harness-coverage-removed.py`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "doc_readme_harness_checker",
            root,
            "doc_readme:`scripts/zigux/check-phase10-harness-coverage.py`",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`Documentation/zigux/phase10-virtio-core-slice.md`",
                "`Documentation/zigux/phase10-virtio-core-slice-missing.md`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "doc_readme_core_slice_marker",
            root,
            "doc_readme:`Documentation/zigux/phase10-virtio-core-slice.md`",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
                "`Documentation/zigux/phase10-virtio-mmio-slice-missing.md`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "doc_readme_mmio_slice_marker",
            root,
            "doc_readme:`Documentation/zigux/phase10-virtio-mmio-slice.md`",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`Documentation/zigux/phase10-virtio-mmio-survey.md`",
                "`Documentation/zigux/phase10-virtio-mmio-survey-missing.md`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "doc_readme_mmio_survey_note",
            root,
            "doc_readme:`Documentation/zigux/phase10-virtio-mmio-survey.md`",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`scripts/zigux/check-phase10-mmio-packet.py`",
                "`scripts/zigux/check-phase10-mmio-packet-missing.py`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "doc_readme_mmio_packet_checker",
            root,
            "doc_readme:`scripts/zigux/check-phase10-mmio-packet.py`",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`drivers/virtio/virtio_mmio_verify.zig`",
                "`drivers/virtio/virtio_mmio_verify_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "doc_readme_mmio_verify_surface",
            root,
            "doc_readme:`drivers/virtio/virtio_mmio_verify.zig`",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`drivers/virtio/virtio_ring_verify.zig`",
                "`drivers/virtio/virtio_ring_verify_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "doc_readme_ring_verify_surface",
            root,
            "doc_readme:`drivers/virtio/virtio_ring_verify.zig`",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
                "`zigux/tests/phase10_virtio_ring_reset_reuse_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "doc_readme_ring_reset_reuse_surface",
            root,
            "doc_readme:`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        scripts_readme_path = root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace("`make -C zigux phase10-test`", "`make -C zigux phase10-shared-test`", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_phase10_test_route",
            root,
            "scripts_readme:`make -C zigux phase10-test`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
                "`zigux/tests/phase10_virtio_input_queue_callback_preflight_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_input_queue_callback_preflight",
            root,
            "scripts_readme:`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "`zigux/tests/phase10_virtio_input_status_drain.zig`",
                "`zigux/tests/phase10_virtio_input_status_drain_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_input_status_drain",
            root,
            "scripts_readme:`zigux/tests/phase10_virtio_input_status_drain.zig`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "`zigux/tests/phase10_virtio_input_manifest.json`",
                "`zigux/tests/phase10_virtio_input_manifest_missing.json`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_input_manifest",
            root,
            "scripts_readme:`zigux/tests/phase10_virtio_input_manifest.json`",
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
            "scripts_readme_ring_slice_marker",
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
            "scripts_readme_input_module_slice_marker",
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
            "scripts_readme_mmio_slice_marker",
            root,
            "scripts_readme:`Documentation/zigux/phase10-virtio-mmio-slice.md`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "`drivers/virtio/virtio_ring_verify.zig`",
                "`drivers/virtio/virtio_ring_verify_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_ring_verify_surface",
            root,
            "scripts_readme:`drivers/virtio/virtio_ring_verify.zig`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
                "`zigux/tests/phase10_virtio_ring_reset_reuse_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_ring_reset_reuse_surface",
            root,
            "scripts_readme:`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        build_path = root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace(
                "phase10-virtio-input-status-drain-tests",
                "phase10-virtio-input-status-drain-tests-missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_input_status_drain_route",
            root,
            "build:phase10-virtio-input-status-drain-tests",
        )
        build_path.write_text(original_build, encoding="utf-8")

        manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_checks"] = [
            "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test",
            "python3 scripts/zigux/check-phase10-harness-coverage.py --self-test",
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_exact_checks_validate_phase10",
            root,
            "manifest:exact_checks:python3 scripts/zigux/validate-phase10.py",
        )
        expect_missing_marker(
            "manifest_exact_checks_phase10_route",
            root,
            "manifest:exact_checks:make -C zigux phase10",
        )
        write_fixture(root)

        tests_readme_path = root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "`zigux/tests/phase10_virtio_ring_manifest.json`",
                "`zigux/tests/phase10_virtio_ring_manifest_missing.json`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_ring_manifest",
            root,
            "tests_readme:`zigux/tests/phase10_virtio_ring_manifest.json`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "`drivers/virtio/virtio_ring_verify.zig`",
                "`drivers/virtio/virtio_ring_verify_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_ring_verify_surface",
            root,
            "tests_readme:`drivers/virtio/virtio_ring_verify.zig`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
                "`zigux/tests/phase10_virtio_ring_reset_reuse_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_ring_reset_reuse_surface",
            root,
            "tests_readme:`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        checker_path = root / "scripts/zigux/check-phase10-tests-readme-core-surfaces.py"
        checker_path.unlink()
        expect_missing_file("checker_file", root, "scripts/zigux/check-phase10-tests-readme-core-surfaces.py")

    print("PHASE10_HARNESS_COVERAGE_SELF_TEST=pass")
    print("PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT=30")
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
print(f"PHASE10_HARNESS_REQUIRED_FILE_COUNT={len(FILES)}")
print(
    "PHASE10_HARNESS_REQUIRED_MARKER_COUNT="
    f"{sum(len(markers) for _, _, markers in CHECKS) + len(EXACT_CHECK_MARKERS)}"
)
