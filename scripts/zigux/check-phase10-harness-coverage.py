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
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test",
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "python3 scripts/zigux/check-phase10-harness-coverage.py --self-test",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
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
    "`drivers/virtio/virtio_input.zig`",
    "`drivers/virtio/virtio_input_verify.zig`",
    "`drivers/virtio/virtio_mmio.zig`",
    "`drivers/virtio/virtio_mmio_verify.zig`",
    "`make -C zigux phase10-validate`",
    "current `master` does not materialize `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, or `Documentation/zigux/phase10-virtio-mmio-slice.md`, so the scripts-root reminder should keep those five slice-note companions framed as repo-reality gaps rather than shipped shared review surfaces.",
]

DOC_README_MARKERS = [
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-core-survey.md`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
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
    "`make -C zigux phase10-validate`",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
    "the remaining missing slice-note paths `Documentation/zigux/phase10-virtio-core-slice.md` and `Documentation/zigux/phase10-virtio-mmio-slice.md` remain repo-reality gaps rather than shipped docs-root evidence on current `master`, and the directly re-readable `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md` stay part of the current shared review packet.",
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
    "`scripts/zigux/README.md` still presents",
    "repo-reality gaps",
]

REVIEW_CHECKLIST_MARKERS = [
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`drivers/virtio/virtio.zig`",
    "`drivers/virtio/virtio_driver_id.zig`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
    "`Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md` framed as repo-reality gaps rather than shipped current-`master` evidence",
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


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    checks = [
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
    text_files = {
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
                "- repo-reality gaps stay explicit through `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md`",
                "- `scripts/zigux/README.md` still presents those missing slice-note paths as live evidence, so the next same-lane repair stays in the scripts-root summary",
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
        "zigux/tests/phase10_closure_manifest.json": json.dumps(
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
        )
        + "\n",
        "zigux/tests/README.md": "\n".join(TESTS_README_MARKERS) + "\n",
    }
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
                "the remaining missing slice-note paths `Documentation/zigux/phase10-virtio-core-slice.md` and `Documentation/zigux/phase10-virtio-mmio-slice.md` remain repo-reality gaps rather than shipped docs-root evidence on current `master`, and the directly re-readable `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md` stay part of the current shared review packet.",
                "the scripts root now treats every Phase 10 slice note as shipped docs-root evidence.",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "doc_readme_slice_gap_phrase",
            root,
            "doc_readme:the remaining missing slice-note paths `Documentation/zigux/phase10-virtio-core-slice.md` and `Documentation/zigux/phase10-virtio-mmio-slice.md` remain repo-reality gaps rather than shipped docs-root evidence on current `master`, and the directly re-readable `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md` stay part of the current shared review packet.",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        scripts_readme_path = root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "current `master` does not materialize `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, or `Documentation/zigux/phase10-virtio-mmio-slice.md`, so the scripts-root reminder should keep those five slice-note companions framed as repo-reality gaps rather than shipped shared review surfaces.",
                "the scripts-root reminder now treats every Phase 10 slice note as shipped current-master evidence.",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_slice_gap_phrase",
            root,
            "scripts_readme:current `master` does not materialize `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, or `Documentation/zigux/phase10-virtio-mmio-slice.md`, so the scripts-root reminder should keep those five slice-note companions framed as repo-reality gaps rather than shipped shared review surfaces.",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        review_checklist_path = root / "Documentation/zigux/review-checklist.md"
        original_review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            original_review_checklist.replace(
                "framed as repo-reality gaps rather than shipped current-`master` evidence",
                "framed as shared reminder evidence on current `master`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_checklist_repo_reality_gap_phrase",
            root,
            "review_checklist:`Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md` framed as repo-reality gaps rather than shipped current-`master` evidence",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_checks"] = [
            "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test",
            "python3 scripts/zigux/check-phase10-harness-coverage.py --self-test",
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_exact_checks_direct_core",
            root,
            "manifest:exact_checks:python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        )
        expect_missing_marker(
            "manifest_exact_checks_harness",
            root,
            "manifest:exact_checks:python3 scripts/zigux/check-phase10-harness-coverage.py",
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

        checker_path = root / "scripts/zigux/check-phase10-tests-readme-core-surfaces.py"
        checker_path.unlink()
        expect_missing_file(
            "checker_file",
            root,
            "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        )

    print("PHASE10_HARNESS_COVERAGE_SELF_TEST=pass")
    print("PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT=8")
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
    f"{len(CLOSURE_NOTE_MARKERS) + len(COMPANION_MARKERS) + len(LANE_NOTE_MARKERS) + len(INPUT_SURVEY_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(DOC_README_MARKERS) + len(SCRIPTS_README_MARKERS) + len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(BUILD_MARKERS) + len(MANIFEST_TEXT_MARKERS) + len(EXACT_CHECK_MARKERS) + len(TESTS_README_MARKERS)}"
)
