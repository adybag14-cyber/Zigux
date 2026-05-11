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
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
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
]

EXACT_CHECK_MARKERS = [
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test",
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
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
        ("make", "zigux/Makefile", MAKE_MARKERS),
        ("workflow", ".github/workflows/zigux-bootstrap.yml", WORKFLOW_MARKERS),
        ("build", "zigux/tests/phase10_build.zig", BUILD_MARKERS),
        ("manifest", "zigux/tests/phase10_closure_manifest.json", MANIFEST_TEXT_MARKERS),
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
                    "scripts/zigux/check-phase10-harness-coverage.py",
                    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
                ]:
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

    return [], missing


def write_fixture(root: Path) -> None:
    text_files = {
        "scripts/zigux/check-phase10-harness-coverage.py": "fixture\n",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py": "fixture\n",
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

        manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            "zigux/tests/phase10_build.zig",
            "scripts/zigux/check-phase10-harness-coverage.py",
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_checker_evidence",
            root,
            "manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence:scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
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

        checker_path = root / "scripts/zigux/check-phase10-tests-readme-core-surfaces.py"
        checker_path.unlink()
        expect_missing_file(
            "checker_file",
            root,
            "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        )

    print("PHASE10_HARNESS_COVERAGE_SELF_TEST=pass")
    print("PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT=5")
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
    f"{len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(BUILD_MARKERS) + len(MANIFEST_TEXT_MARKERS) + len(EXACT_CHECK_MARKERS)}"
)
