#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parent

REQUIRED_FILES = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase9_build.zig",
]

REQUIRED_MAKE_MARKERS = [
    "PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4",
    "phase4-validate:",
    "scripts/zigux/validate-phase4.py --self-test",
    "scripts/zigux/validate-phase4.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "phase4-bitmap-diff-survey:",
    "zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-live-helper-replay:",
]

REQUIRED_WORKFLOW_MARKERS = [
    "python3 scripts/zigux/validate-phase4.py --self-test",
    "python3 scripts/zigux/validate-phase4.py",
    "zig build test --build-file zigux/tests/phase4_build.zig",
]

REQUIRED_ARTIFACT_DOC_MARKERS = [
    "Current Phase 4 use",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-validation-matrix.md",
]

REQUIRED_DOC_README_MARKERS = [
    "Phase 4 notes",
    "validate-phase4.py",
    "phase4-gate-evidence.md",
    "phase4-validation-matrix.md",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "intentionally unapproved perf-threshold posture",
]

REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 4 flow",
    "validate-phase4.py",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "phase4-gate-evidence.md",
    "phase4-validation-matrix.md",
    "phase4_build.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
    "make -C zigux phase4-bitmap-live-helper-replay",
    "intentionally unapproved perf-threshold posture",
]

REQUIRED_TESTS_README_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 4 validation packet",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zig build test --build-file zigux/tests/phase4_build.zig",
    "intentionally unapproved perf-threshold posture",
]

REQUIRED_PHASE4_MATRIX_MARKERS = [
    "phase4_runtime_atomic64_diff_manifest.json",
    "phase4_runtime_atomic64_diff_survey.zig",
    "bitmap_diff.zig",
    "phase4_bitmap_diff_manifest.json",
    "phase4_bitmap_diff_survey.zig",
    "phase4_bitmap_live_helper_replay.zig",
    "rollback owner",
    "Lab And CI Matrix",
    "threshold posture",
    "zig build test --build-file zigux/tests/phase4_build.zig",
    "Remaining Roadmap Gaps",
]

REQUIRED_PHASE4_BUILD_MARKERS = [
    'root_source_file = b.path("atomic64_diff.zig")',
    'root_source_file = b.path("phase4_runtime_atomic64_diff_survey.zig")',
    'root_source_file = b.path("bitmap_diff.zig")',
    'root_source_file = b.path("phase4_bitmap_diff_survey.zig")',
    'root_source_file = b.path("phase4_bitmap_live_helper_replay.zig")',
    'name = "phase4-runtime-atomic64-diff-tests"',
    'name = "phase4-runtime-atomic64-diff-survey-tests"',
    'name = "phase4-bitmap-diff-tests"',
    'name = "phase4-bitmap-diff-survey-tests"',
    'name = "phase4-bitmap-live-helper-replay-tests"',
]

FORBIDDEN_SCRIPT_README_MARKERS = [
    "phase4-perf-baseline-survey",
]

PHASE4_RUNTIME_ATOMIC64_PIN_TARGETS = {
    "phase4_build_blob_sha": "zigux/tests/phase4_build.zig",
    "phase4_validator_blob_sha": "scripts/zigux/validate-phase4.py",
    "phase4_validation_matrix_blob_sha": "Documentation/zigux/phase4-validation-matrix.md",
    "phase4_review_checklist_blob_sha": "Documentation/zigux/review-checklist.md",
    "phase9_build_blob_sha": "zigux/tests/phase9_build.zig",
}

PHASE4_BITMAP_PIN_TARGETS = {
    "live_gate_blob_sha": "zigux/tests/bitmap_diff.zig",
    "helper_replay_blob_sha": "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "gate_evidence_blob_sha": "Documentation/zigux/phase4-gate-evidence.md",
    "phase4_build_blob_sha": "zigux/tests/phase4_build.zig",
}


def _missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]


def _git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def _line_value(lines: list[str], prefix: str) -> str | None:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    return None


def _run_python_script(root: Path, relative_path: str, *args: str) -> tuple[int, list[str]]:
    result = subprocess.run(
        [sys.executable, str(root / relative_path), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.splitlines()


def validate_root(root: Path) -> list[str]:
    problems: list[str] = []

    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/zigux-bootstrap.yml").read_text(encoding="utf-8")
    artifact_doc = (root / "Documentation/zigux/artifact-diff.md").read_text(encoding="utf-8")
    doc_readme = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    script_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation/zigux/review-checklist.md").read_text(encoding="utf-8")
    phase4_matrix = (root / "Documentation/zigux/phase4-validation-matrix.md").read_text(
        encoding="utf-8"
    )
    phase4_build = (root / "zigux/tests/phase4_build.zig").read_text(encoding="utf-8")

    for marker in REQUIRED_MAKE_MARKERS:
        if marker not in makefile:
            problems.append(f"make:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            problems.append(f"workflow:{marker}")
    for marker in REQUIRED_ARTIFACT_DOC_MARKERS:
        if marker not in artifact_doc:
            problems.append(f"artifact_doc:{marker}")
    for marker in REQUIRED_DOC_README_MARKERS:
        if marker not in doc_readme:
            problems.append(f"doc_readme:{marker}")
    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in script_readme:
            problems.append(f"script_readme:{marker}")
    for marker in FORBIDDEN_SCRIPT_README_MARKERS:
        if marker in script_readme:
            problems.append(f"script_readme:forbidden:{marker}")
    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            problems.append(f"tests_readme:{marker}")
    for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            problems.append(f"review_checklist:{marker}")
    for marker in REQUIRED_PHASE4_MATRIX_MARKERS:
        if marker not in phase4_matrix:
            problems.append(f"phase4_matrix:{marker}")
    for marker in REQUIRED_PHASE4_BUILD_MARKERS:
        if marker not in phase4_build:
            problems.append(f"phase4_build:{marker}")

    return problems


def run_artifact_diff_contract_check(root: Path) -> list[str]:
    code, lines = _run_python_script(root, "scripts/zigux/check-artifact-diff-contract.py")
    if code != 0:
        return [f"artifact_diff_contract:exit:{code}"]
    if "ARTIFACT_DIFF_CONTRACT=pass" not in lines:
        return ["artifact_diff_contract:missing_pass_marker"]
    return []


def run_artifact_diff_contract_self_test_check(root: Path) -> list[str]:
    code, lines = _run_python_script(root, "scripts/zigux/check-artifact-diff-contract.py", "--self-test")
    if code != 0:
        return [f"artifact_diff_contract_self_test:exit:{code}"]
    if "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass" not in lines:
        return ["artifact_diff_contract_self_test:missing_pass_marker"]
    return []


def run_phase4_gate_evidence_check(root: Path) -> list[str]:
    code, lines = _run_python_script(root, "scripts/zigux/check-phase4-gate-evidence.py")
    if code != 0:
        return [f"phase4_gate_evidence:exit:{code}"]
    if "PHASE4_GATE_EVIDENCE_CHECK=pass" not in lines:
        return ["phase4_gate_evidence:missing_pass_marker"]
    if _line_value(lines, "PHASE4_GATE_EVIDENCE_TARGET_COUNT=") != "16":
        return ["phase4_gate_evidence:unexpected_target_count"]
    return []


def run_phase4_gate_evidence_self_test_check(root: Path) -> list[str]:
    code, lines = _run_python_script(root, "scripts/zigux/check-phase4-gate-evidence.py", "--self-test")
    if code != 0:
        return [f"phase4_gate_evidence_self_test:exit:{code}"]
    if "PHASE4_GATE_EVIDENCE_SELF_TEST=pass" not in lines:
        return ["phase4_gate_evidence_self_test:missing_pass_marker"]
    return []


def run_phase4_runtime_atomic64_packet_check(root: Path) -> list[str]:
    manifest = json.loads(
        (root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json").read_text(encoding="utf-8")
    )
    survey = (root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig").read_text(
        encoding="utf-8"
    )
    problems: list[str] = []
    for field, relative_path in PHASE4_RUNTIME_ATOMIC64_PIN_TARGETS.items():
        expected = _git_blob_sha1((root / relative_path).read_bytes())
        actual = manifest.get(field)
        if actual != expected:
            problems.append(f"runtime_atomic64_manifest:{field}:{actual}:{expected}")
        if survey.count(expected) != 1:
            problems.append(f"runtime_atomic64_survey:{field}:{expected}:{survey.count(expected)}")
    return problems


def run_phase4_bitmap_packet_check(root: Path) -> list[str]:
    manifest = json.loads(
        (root / "zigux/tests/phase4_bitmap_diff_manifest.json").read_text(encoding="utf-8")
    )
    survey = (root / "zigux/tests/phase4_bitmap_diff_survey.zig").read_text(encoding="utf-8")
    problems: list[str] = []

    expected_strings = {
        "lane_key": "P4-L07",
        "phase": "Phase 4",
        "roadmap_target_path": "zigux/tests/bitmap_diff.zig",
        "owner": "Shared Subsystems Pod",
        "rollback_owner": "Shared Subsystems Pod",
        "shared_validator_path": "scripts/zigux/validate-phase4.py",
        "shared_matrix_path": "Documentation/zigux/phase4-validation-matrix.md",
        "shared_gate_evidence_path": "Documentation/zigux/phase4-gate-evidence.md",
        "gate_evidence_path": "Documentation/zigux/phase4-gate-evidence.md",
        "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    }
    for field, expected in expected_strings.items():
        if manifest.get(field) != expected:
            problems.append(f"bitmap_manifest:{field}:{manifest.get(field)}:{expected}")

    for field in [
        "roadmap_bitmap_diff_present",
        "phase4_build_present",
        "phase4_build_uses_bitmap_diff",
        "phase4_build_uses_bitmap_diff_survey",
    ]:
        if manifest.get(field) is not True:
            problems.append(f"bitmap_manifest:{field}:{manifest.get(field)}:true")

    for field, relative_path in PHASE4_BITMAP_PIN_TARGETS.items():
        expected = _git_blob_sha1((root / relative_path).read_bytes())
        actual = manifest.get(field)
        if actual != expected:
            problems.append(f"bitmap_manifest_sha:{field}:{actual}:{expected}")
        if survey.count(expected) != 1:
            problems.append(f"bitmap_survey_sha:{field}:{expected}:{survey.count(expected)}")

    survey_markers = [
        "phase 4 bitmap survey keeps the roadmap rollback gate and helper replay measurable",
        "phase 4 bitmap survey keeps the shared build route explicit",
        "phase 4 bitmap survey keeps bitmap gate-evidence coverage explicit",
        "phase 4 bitmap survey keeps owner and rollback owner governance explicit",
        "phase4_bitmap_diff_manifest.json",
        "phase4_bitmap_live_helper_replay.zig",
        "Shared Subsystems Pod",
        "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    ]
    for marker in survey_markers:
        if marker not in survey:
            problems.append(f"bitmap_survey_marker:{marker}")

    return problems


def _write(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_fixture_tree(root: Path) -> None:
    _write(root, "scripts/zigux/artifact_diff.py", "print('artifact diff fixture')\n")
    _write(
        root,
        "scripts/zigux/check-artifact-diff-contract.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "if '--self-test' in sys.argv:",
                "    print('ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass')",
                "else:",
                "    print('ARTIFACT_DIFF_CONTRACT=pass')",
            ]
        )
        + "\n",
    )
    _write(
        root,
        "scripts/zigux/check-phase4-gate-evidence.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "if '--self-test' in sys.argv:",
                "    print('PHASE4_GATE_EVIDENCE_SELF_TEST=pass')",
                "else:",
                "    print('PHASE4_GATE_EVIDENCE_CHECK=pass')",
                "    print('PHASE4_GATE_EVIDENCE_TARGET_COUNT=16')",
            ]
        )
        + "\n",
    )
    _write(root, "scripts/zigux/validate-phase4.py", "# fixture\n")
    _write(
        root,
        "Documentation/zigux/artifact-diff.md",
        "\n".join(
            [
                "Current Phase 4 use",
                "scripts/zigux/check-phase4-gate-evidence.py",
                "zigux/tests/atomic64_diff.zig",
                "zigux/tests/runtime_atomic64_diff.zig",
                "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
                "zigux/tests/bitmap_diff.zig",
                "zigux/tests/phase4_bitmap_diff_manifest.json",
                "zigux/tests/phase4_bitmap_diff_survey.zig",
                "zigux/tests/phase4_bitmap_live_helper_replay.zig",
                "zigux/tests/phase4_build.zig",
                "scripts/zigux/validate-phase4.py",
                "Documentation/zigux/phase4-validation-matrix.md",
                "",
            ]
        ),
    )
    _write(
        root,
        "Documentation/zigux/README.md",
        "\n".join(
            [
                "Phase 4 notes",
                "validate-phase4.py",
                "phase4-gate-evidence.md",
                "phase4-validation-matrix.md",
                "atomic64_diff.zig",
                "runtime_atomic64_diff.zig",
                "phase4_runtime_atomic64_diff_survey.zig",
                "zigux/tests/phase4_bitmap_live_helper_replay.zig",
                "intentionally unapproved perf-threshold posture",
                "",
            ]
        ),
    )
    _write(
        root,
        "scripts/zigux/README.md",
        "\n".join(
            [
                "Phase 4 flow",
                "validate-phase4.py",
                "atomic64_diff.zig",
                "runtime_atomic64_diff.zig",
                "phase4-gate-evidence.md",
                "phase4-validation-matrix.md",
                "phase4_build.zig",
                "phase4_runtime_atomic64_diff_survey.zig",
                "make -C zigux phase4-bitmap-live-helper-replay",
                "intentionally unapproved perf-threshold posture",
                "",
            ]
        ),
    )
    _write(
        root,
        "zigux/tests/README.md",
        "\n".join(
            [
                "zigux/tests/atomic64_diff.zig",
                "zigux/tests/runtime_atomic64_diff.zig",
                "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
                "zigux/tests/bitmap_diff.zig",
                "zigux/tests/phase4_bitmap_live_helper_replay.zig",
                "zigux/tests/phase4_build.zig",
                "scripts/zigux/validate-phase4.py",
                "",
            ]
        ),
    )
    _write(
        root,
        "Documentation/zigux/review-checklist.md",
        "\n".join(
            [
                "if the change touches the shared Phase 4 validation packet",
                "Documentation/zigux/phase4-validation-matrix.md",
                "Documentation/zigux/phase4-gate-evidence.md",
                "scripts/zigux/check-phase4-gate-evidence.py",
                "scripts/zigux/validate-phase4.py",
                "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
                "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
                "zigux/tests/phase4_bitmap_live_helper_replay.zig",
                "zig build test --build-file zigux/tests/phase4_build.zig",
                "intentionally unapproved perf-threshold posture",
                "",
            ]
        ),
    )
    _write(
        root,
        "Documentation/zigux/phase4-validation-matrix.md",
        "\n".join(
            [
                "phase4_runtime_atomic64_diff_manifest.json",
                "phase4_runtime_atomic64_diff_survey.zig",
                "bitmap_diff.zig",
                "phase4_bitmap_diff_manifest.json",
                "phase4_bitmap_diff_survey.zig",
                "phase4_bitmap_live_helper_replay.zig",
                "rollback owner",
                "Lab And CI Matrix",
                "threshold posture",
                "zig build test --build-file zigux/tests/phase4_build.zig",
                "Remaining Roadmap Gaps",
                "",
            ]
        ),
    )
    _write(
        root,
        "zigux/Makefile",
        "\n".join(REQUIRED_MAKE_MARKERS) + "\n",
    )
    _write(root, ".github/workflows/zigux-bootstrap.yml", "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n")
    _write(root, "zigux/tests/atomic64_diff.zig", "// atomic64 diff\n")
    _write(root, "zigux/tests/runtime_atomic64_diff.zig", "// runtime atomic64 diff\n")
    _write(root, "zigux/tests/bitmap_diff.zig", "// bitmap diff\n")
    _write(root, "zigux/tests/phase4_bitmap_live_helper_replay.zig", "// helper replay\n")
    _write(
        root,
        "Documentation/zigux/phase4-gate-evidence.md",
        "phase4 gate evidence fixture\n",
    )
    _write(
        root,
        "zigux/tests/phase4_build.zig",
        "\n".join(REQUIRED_PHASE4_BUILD_MARKERS) + "\n",
    )
    _write(root, "zigux/tests/phase9_build.zig", "// phase9 build\n")

    runtime_manifest = {
        field: _git_blob_sha1((root / path).read_bytes())
        for field, path in PHASE4_RUNTIME_ATOMIC64_PIN_TARGETS.items()
    }
    _write(
        root,
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        json.dumps(runtime_manifest, indent=2) + "\n",
    )
    _write(
        root,
        "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
        "\n".join(runtime_manifest.values()) + "\n",
    )

    bitmap_manifest = {
        "lane_key": "P4-L07",
        "phase": "Phase 4",
        "roadmap_target_path": "zigux/tests/bitmap_diff.zig",
        "roadmap_bitmap_diff_present": True,
        "live_gate_path": "zigux/tests/bitmap_diff.zig",
        "helper_replay_path": "zigux/tests/phase4_bitmap_live_helper_replay.zig",
        "owner": "Shared Subsystems Pod",
        "rollback_owner": "Shared Subsystems Pod",
        "shared_validator_path": "scripts/zigux/validate-phase4.py",
        "shared_matrix_path": "Documentation/zigux/phase4-validation-matrix.md",
        "shared_gate_evidence_path": "Documentation/zigux/phase4-gate-evidence.md",
        "gate_evidence_path": "Documentation/zigux/phase4-gate-evidence.md",
        "phase4_build_present": True,
        "phase4_build_uses_bitmap_diff": True,
        "phase4_build_uses_bitmap_diff_survey": True,
        "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        "roadmap_gap_summary": "zigux/tests/bitmap_diff.zig shared Phase 4 gate-evidence note phase4_build.zig Shared Subsystems Pod owner plus rollback owner metadata",
        "reversible_delivery_evidence": "zigux/tests/bitmap_diff.zig zigux/tests/phase4_bitmap_live_helper_replay.zig Documentation/zigux/phase4-gate-evidence.md zigux/tests/phase4_bitmap_diff_manifest.json zigux/tests/phase4_bitmap_diff_survey.zig zigux/tests/phase4_build.zig measurable and reversible",
        "ready_next": "scripts/zigux/validate-phase4.py Documentation/zigux/phase4-validation-matrix.md Shared Subsystems Pod owner plus rollback owner metadata samples or perf-threshold approval",
    }
    for field, path in PHASE4_BITMAP_PIN_TARGETS.items():
        bitmap_manifest[field] = _git_blob_sha1((root / path).read_bytes())
    _write(
        root,
        "zigux/tests/phase4_bitmap_diff_manifest.json",
        json.dumps(bitmap_manifest, indent=2) + "\n",
    )
    _write(
        root,
        "zigux/tests/phase4_bitmap_diff_survey.zig",
        "\n".join(
            [
                "phase 4 bitmap survey keeps the roadmap rollback gate and helper replay measurable",
                "phase 4 bitmap survey keeps the shared build route explicit",
                "phase 4 bitmap survey keeps bitmap gate-evidence coverage explicit",
                "phase 4 bitmap survey keeps owner and rollback owner governance explicit",
                "phase4_bitmap_diff_manifest.json",
                "phase4_bitmap_live_helper_replay.zig",
                "Shared Subsystems Pod",
                "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
                bitmap_manifest["live_gate_blob_sha"],
                bitmap_manifest["helper_replay_blob_sha"],
                bitmap_manifest["gate_evidence_blob_sha"],
                bitmap_manifest["phase4_build_blob_sha"],
            ]
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_validator_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        assert _missing_files(root) == []
        assert validate_root(root) == []
        assert run_artifact_diff_contract_check(root) == []
        assert run_artifact_diff_contract_self_test_check(root) == []
        assert run_phase4_gate_evidence_check(root) == []
        assert run_phase4_gate_evidence_self_test_check(root) == []
        assert run_phase4_runtime_atomic64_packet_check(root) == []
        assert run_phase4_bitmap_packet_check(root) == []

        bad_root = Path(tmp_dir) / "bad"
        build_fixture_tree(bad_root)
        matrix = bad_root / "Documentation/zigux/phase4-validation-matrix.md"
        matrix.write_text(
            matrix.read_text(encoding="utf-8").replace("phase4_bitmap_diff_manifest.json\n", ""),
            encoding="utf-8",
        )
        assert validate_root(bad_root) == ["phase4_matrix:phase4_bitmap_diff_manifest.json"]

        bad_root2 = Path(tmp_dir) / "bad2"
        build_fixture_tree(bad_root2)
        manifest_path = bad_root2 / "zigux/tests/phase4_bitmap_diff_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["live_gate_blob_sha"] = "0" * 40
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        failures = run_phase4_bitmap_packet_check(bad_root2)
        assert failures and failures[0].startswith("bitmap_manifest_sha:live_gate_blob_sha:")

    print("PHASE4_VALIDATE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 4 rollback-readiness packet.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = _missing_files(ROOT)
    if missing:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE4_FILES_END")
        return 1

    problems = validate_root(ROOT)
    if problems:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_MARKERS_START")
        for item in problems:
            print(item)
        print("MISSING_PHASE4_MARKERS_END")
        return 1

    for label, failures in [
        ("ARTIFACT_DIFF_CONTRACT_CHECK", run_artifact_diff_contract_check(ROOT)),
        ("ARTIFACT_DIFF_CONTRACT_SELF_TEST_CHECK", run_artifact_diff_contract_self_test_check(ROOT)),
        ("PHASE4_GATE_EVIDENCE_CHECK", run_phase4_gate_evidence_check(ROOT)),
        ("PHASE4_GATE_EVIDENCE_SELF_TEST_CHECK", run_phase4_gate_evidence_self_test_check(ROOT)),
        ("PHASE4_RUNTIME_ATOMIC64_PACKET_CHECK", run_phase4_runtime_atomic64_packet_check(ROOT)),
        ("PHASE4_BITMAP_PACKET_CHECK", run_phase4_bitmap_packet_check(ROOT)),
    ]:
        if failures:
            print("PHASE4_VALIDATION=fail")
            print(f"{label}_START")
            for item in failures:
                print(item)
            print(f"{label}_END")
            return 1

    print("PHASE4_VALIDATION=pass")
    print(f"PHASE4_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    marker_count = sum(
        len(group)
        for group in [
            REQUIRED_MAKE_MARKERS,
            REQUIRED_WORKFLOW_MARKERS,
            REQUIRED_ARTIFACT_DOC_MARKERS,
            REQUIRED_DOC_README_MARKERS,
            REQUIRED_SCRIPT_README_MARKERS,
            REQUIRED_TESTS_README_MARKERS,
            REQUIRED_REVIEW_CHECKLIST_MARKERS,
            REQUIRED_PHASE4_MATRIX_MARKERS,
            REQUIRED_PHASE4_BUILD_MARKERS,
        ]
    )
    print(f"PHASE4_REQUIRED_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
