#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
]

PHASE4_GATE_EXPECTATIONS = {
    "runtime_atomic64_diff.zig": {
        "owner": "ABI and Runtime Team",
        "rollback_owner": "ABI and Runtime Team",
        "fallback_path": "keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses",
        "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
        "matrix_purpose": "bounded atomic64 exchange, cmpxchg, add_unless, and selftest-family replay",
    },
    "bitmap_diff.zig": {
        "owner": "Shared Subsystems Pod",
        "rollback_owner": "Shared Subsystems Pod",
        "fallback_path": "keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses",
        "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        "matrix_purpose": "bounded broad bitmap rollback-readiness replay",
    },
}

REQUIRED_MAKE_MARKERS = [
    "PHONY += phase4-validate phase4-test phase4",
    "phase4-validate:",
    "scripts/zigux/validate-phase4.py",
    "phase4-test:",
    "zigux/tests/phase4_build.zig",
]
REQUIRED_WORKFLOW_MARKERS = [
    "python3 scripts/zigux/validate-phase4.py",
    "python3 scripts/zigux/validate-phase4.py --self-test",
    "zig build test --build-file zigux/tests/phase4_build.zig",
]
REQUIRED_DOC_MARKERS = [
    "Current Phase 4 use",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-validation-matrix.md",
]
REQUIRED_TESTS_README_MARKERS = [
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
]
REQUIRED_SCRIPT_README_MARKERS = [
    "validate-phase4.py",
    "Phase 4 flow",
    "phase4_build.zig",
    "phase4-validation-matrix.md",
]
REQUIRED_DOC_README_MARKERS = [
    "Phase 4 notes",
    "validate-phase4.py",
    "phase4-validation-matrix.md",
]
REQUIRED_PHASE4_MATRIX_MARKERS = [
    "runtime_atomic64_diff.zig",
    "bitmap_diff.zig",
    "rollback owner",
    "lab and CI matrix",
    "perf threshold status",
    "zig build test --build-file zigux/tests/phase4_build.zig",
]
REQUIRED_PHASE4_BUILD_MARKERS = [
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "bitmap_diff.zig",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-bitmap-diff-tests",
]


def _missing_files(root: Path) -> list[str]:
    missing = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def check_gate_matrix_alignment(phase4_matrix: str, gate_name: str, expectation: dict[str, str]) -> list[str]:
    gate_heading = f"### `zigux/tests/{gate_name}`"
    gate_heading_index = phase4_matrix.find(gate_heading)
    if gate_heading_index == -1:
        return [f"phase4_matrix:missing_gate_heading:{gate_name}"]

    next_heading_index = phase4_matrix.find("\n### `zigux/tests/", gate_heading_index + len(gate_heading))
    matrix_heading_index = phase4_matrix.find("\n## Lab And CI Matrix", gate_heading_index + len(gate_heading))
    gate_block_end = matrix_heading_index if matrix_heading_index != -1 else len(phase4_matrix)
    if next_heading_index != -1 and next_heading_index < gate_block_end:
        gate_block_end = next_heading_index
    gate_block = phase4_matrix[gate_heading_index:gate_block_end]

    row_prefix = f"| `zigux/tests/{gate_name}` |"
    row = next((line for line in phase4_matrix.splitlines() if line.startswith(row_prefix)), "")

    missing = []
    if f"- owner: `{expectation['owner']}`" not in gate_block:
        missing.append(f"phase4_matrix:owner:{gate_name}:{expectation['owner']}")
    if f"- rollback owner: `{expectation['rollback_owner']}`" not in gate_block:
        missing.append(f"phase4_matrix:rollback_owner:{gate_name}:{expectation['rollback_owner']}")
    if f"- fallback path: {expectation['fallback_path']}" not in gate_block:
        missing.append(f"phase4_matrix:fallback_path:{gate_name}:{expectation['fallback_path']}")
    if expectation["threshold_posture"] not in row:
        missing.append(f"phase4_matrix:threshold_posture:{gate_name}:{expectation['threshold_posture']}")
    if expectation["matrix_purpose"] not in row:
        missing.append(f"phase4_matrix:matrix_purpose:{gate_name}:{expectation['matrix_purpose']}")
    if expectation["owner"] not in row:
        missing.append(f"phase4_matrix:matrix_owner:{gate_name}:{expectation['owner']}")
    if expectation["rollback_owner"] not in row:
        missing.append(f"phase4_matrix:matrix_rollback_owner:{gate_name}:{expectation['rollback_owner']}")
    return missing


def validate_root(root: Path) -> list[str]:
    missing_markers: list[str] = []

    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/zigux-bootstrap.yml").read_text(encoding="utf-8")
    artifact_doc = (root / "Documentation/zigux/artifact-diff.md").read_text(encoding="utf-8")
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")
    script_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    doc_readme = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    phase4_matrix = (root / "Documentation/zigux/phase4-validation-matrix.md").read_text(encoding="utf-8")
    phase4_build = (root / "zigux/tests/phase4_build.zig").read_text(encoding="utf-8")

    for marker in REQUIRED_MAKE_MARKERS:
        if marker not in makefile:
            missing_markers.append(f"make:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            missing_markers.append(f"workflow:{marker}")
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in artifact_doc:
            missing_markers.append(f"doc:{marker}")
    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            missing_markers.append(f"tests_readme:{marker}")
    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in script_readme:
            missing_markers.append(f"script_readme:{marker}")
    for marker in REQUIRED_DOC_README_MARKERS:
        if marker not in doc_readme:
            missing_markers.append(f"doc_readme:{marker}")
    for marker in REQUIRED_PHASE4_MATRIX_MARKERS:
        if marker not in phase4_matrix:
            missing_markers.append(f"phase4_matrix:{marker}")
    for marker in REQUIRED_PHASE4_BUILD_MARKERS:
        if marker not in phase4_build:
            missing_markers.append(f"phase4_build:{marker}")

    for gate_name, expectation in PHASE4_GATE_EXPECTATIONS.items():
        missing_markers.extend(check_gate_matrix_alignment(phase4_matrix, gate_name, expectation))

    return missing_markers


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_validator_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)

        _write(
            root / "scripts/zigux/validate-phase4.py",
            "# placeholder\n",
        )
        _write(
            root / "Documentation/zigux/artifact-diff.md",
            "\n".join(
                [
                    "# Artifact Diff Policy",
                    "",
                    "Current Phase 4 use",
                    "- `zigux/tests/runtime_atomic64_diff.zig` remains in the packet.",
                    "- `zigux/tests/bitmap_diff.zig` remains in the packet.",
                    "- `zigux/tests/phase4_build.zig` remains in the packet.",
                    "- `scripts/zigux/validate-phase4.py` remains in the packet.",
                    "- `Documentation/zigux/phase4-validation-matrix.md` remains in the packet.",
                    "",
                ]
            )
            + "\n",
        )
        _write(
            root / "Documentation/zigux/phase4-validation-matrix.md",
            "\n".join(
                [
                    "# Phase 4 Validation Matrix",
                    "",
                    "rollback owner",
                    "lab and CI matrix",
                    "perf threshold status",
                    "zig build test --build-file zigux/tests/phase4_build.zig",
                    "",
                    "### `zigux/tests/runtime_atomic64_diff.zig`",
                    "",
                    "- owner: `ABI and Runtime Team`",
                    "- rollback owner: `ABI and Runtime Team`",
                    "- fallback path: keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses",
                    "",
                    "### `zigux/tests/bitmap_diff.zig`",
                    "",
                    "- owner: `Shared Subsystems Pod`",
                    "- rollback owner: `Shared Subsystems Pod`",
                    "- fallback path: keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses",
                    "",
                    "## Lab And CI Matrix",
                    "",
                    "| lane surface | purpose | owner | rollback owner | bootstrap CI replay | local lab replay | threshold posture |",
                    "| --- | --- | --- | --- | --- | --- | --- |",
                    "| `zigux/tests/runtime_atomic64_diff.zig` | bounded atomic64 exchange, cmpxchg, add_unless, and selftest-family replay | `ABI and Runtime Team` | `ABI and Runtime Team` | `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` | `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` | `threshold_pending_until_runtime_atomic64_scope_widens` |",
                    "| `zigux/tests/bitmap_diff.zig` | bounded broad bitmap rollback-readiness replay | `Shared Subsystems Pod` | `Shared Subsystems Pod` | `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` | `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` | `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` |",
                    "",
                ]
            ),
        )
        _write(
            root / "zigux/Makefile",
            "\n".join(
                [
                    "PHONY += phase4-validate phase4-test phase4",
                    "phase4-validate:",
                    "\tpython3 scripts/zigux/validate-phase4.py",
                    "phase4-test:",
                    "\tzig build test --build-file zigux/tests/phase4_build.zig",
                    "",
                ]
            ),
        )
        _write(
            root / ".github/workflows/zigux-bootstrap.yml",
            "\n".join(
                [
                    "jobs:",
                    "  bootstrap:",
                    "    steps:",
                    "      - name: Validate Phase 4 diff gates",
                    "        run: python3 scripts/zigux/validate-phase4.py",
                    "      - name: Self-test Phase 4 validator",
                    "        run: python3 scripts/zigux/validate-phase4.py --self-test",
                    "      - name: Run Phase 4 diff tests",
                    "        run: zig build test --build-file zigux/tests/phase4_build.zig",
                    "",
                ]
            ),
        )
        _write(root / "zigux/tests/atomic64_diff.zig", "// wrapper gate\n")
        _write(root / "zigux/tests/runtime_atomic64_diff.zig", "// runtime gate\n")
        _write(root / "zigux/tests/bitmap_diff.zig", "// bitmap gate\n")
        _write(
            root / "zigux/tests/phase4_build.zig",
            "\n".join(
                [
                    "atomic64_diff.zig",
                    "runtime_atomic64_diff.zig",
                    "bitmap_diff.zig",
                    "phase4-runtime-atomic64-diff-tests",
                    "phase4-bitmap-diff-tests",
                    "",
                ]
            ),
        )
        _write(
            root / "zigux/tests/README.md",
            "\n".join(
                [
                    "zigux/tests/runtime_atomic64_diff.zig",
                    "zigux/tests/bitmap_diff.zig",
                    "zigux/tests/phase4_build.zig",
                    "scripts/zigux/validate-phase4.py",
                    "",
                ]
            ),
        )
        _write(
            root / "scripts/zigux/README.md",
            "\n".join(
                [
                    "validate-phase4.py",
                    "Phase 4 flow",
                    "phase4_build.zig",
                    "phase4-validation-matrix.md",
                    "",
                ]
            ),
        )
        _write(
            root / "Documentation/zigux/README.md",
            "\n".join(
                [
                    "Phase 4 notes",
                    "validate-phase4.py",
                    "phase4-validation-matrix.md",
                    "",
                ]
            ),
        )

        assert _missing_files(root) == []
        assert validate_root(root) == []

        matrix_path = root / "Documentation/zigux/phase4-validation-matrix.md"
        original_matrix = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            original_matrix.replace("- rollback owner: `Shared Subsystems Pod`\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_root(root)
        assert "phase4_matrix:rollback_owner:bitmap_diff.zig:Shared Subsystems Pod" in issues
        matrix_path.write_text(original_matrix, encoding="utf-8", newline="\n")

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace("zig build test --build-file zigux/tests/phase4_build.zig", "zig build test --build-file zigux/tests/missing.zig"),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_root(root)
        assert "workflow:zig build test --build-file zigux/tests/phase4_build.zig" in issues
        workflow_path.write_text(original_workflow, encoding="utf-8", newline="\n")

        build_path = root / "zigux/tests/phase4_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace("phase4-bitmap-diff-tests\n", ""),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_root(root)
        assert "phase4_build:phase4-bitmap-diff-tests" in issues
        build_path.write_text(original_build, encoding="utf-8", newline="\n")

        matrix_path.write_text(
            original_matrix.replace(
                "bounded atomic64 exchange, cmpxchg, add_unless, and selftest-family replay",
                "bounded atomic64 exchange, cmpxchg, and selftest-family replay",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_root(root)
        assert (
            "phase4_matrix:matrix_purpose:runtime_atomic64_diff.zig:bounded atomic64 exchange, cmpxchg, add_unless, and selftest-family replay"
            in issues
        )

    print("PHASE4_VALIDATE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 4 rollback-readiness packet.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated Phase 4 validator coverage in a temporary workspace.",
    )
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

    missing_markers = validate_root(ROOT)
    if missing_markers:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE4_MARKERS_END")
        return 1

    print("PHASE4_VALIDATION=pass")
    print(f"PHASE4_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE4_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_MAKE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_DOC_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_SCRIPT_README_MARKERS) + len(REQUIRED_DOC_README_MARKERS) + len(REQUIRED_PHASE4_MATRIX_MARKERS) + len(REQUIRED_PHASE4_BUILD_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
