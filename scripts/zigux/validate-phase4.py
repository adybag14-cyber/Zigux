#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
]

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
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-validation-matrix.md",
]
REQUIRED_TESTS_README_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
]
REQUIRED_SCRIPT_README_MARKERS = [
    "validate-phase4.py",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "Phase 4 flow",
    "phase4_build.zig",
    "phase4-validation-matrix.md",
]
REQUIRED_DOC_README_MARKERS = [
    "Phase 4 notes",
    "validate-phase4.py",
    "phase4-validation-matrix.md",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
]
REQUIRED_PHASE4_MATRIX_MARKERS = [
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "bitmap_diff.zig",
    "phase4_bitmap_live_helper_replay.zig",
    "rollback owner",
    "lab and CI matrix",
    "perf threshold status",
    "zig build test --build-file zigux/tests/phase4_build.zig",
]
REQUIRED_PHASE4_BUILD_MARKERS = [
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "bitmap_diff.zig",
    "phase4_bitmap_live_helper_replay.zig",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-bitmap-diff-tests",
    "phase4-bitmap-live-helper-replay-tests",
]
EXACT_ONCE_TESTS_README_MARKERS = [
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
]
EXACT_ONCE_SCRIPT_README_MARKERS = [
    "Phase 4 flow",
    "phase4_build.zig",
    "phase4-validation-matrix.md",
]
EXACT_ONCE_DOC_README_MARKERS = [
    "Phase 4 notes",
    "validate-phase4.py",
    "phase4-validation-matrix.md",
    "runtime_atomic64_diff.zig",
]


def _missing_files(root: Path) -> list[str]:
    missing = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def _count_marker(text: str, marker: str) -> int:
    return text.count(marker)


def _require_exact_once(text: str, marker: str, prefix: str, missing_markers: list[str]) -> None:
    count = _count_marker(text, marker)
    if count != 1:
        missing_markers.append(f"{prefix}:exact_once:{marker}:{count}")


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

    _require_exact_once(artifact_doc, "Current Phase 4 use", "doc", missing_markers)
    for marker in EXACT_ONCE_TESTS_README_MARKERS:
        _require_exact_once(tests_readme, marker, "tests_readme", missing_markers)
    for marker in EXACT_ONCE_SCRIPT_README_MARKERS:
        _require_exact_once(script_readme, marker, "script_readme", missing_markers)
    for marker in EXACT_ONCE_DOC_README_MARKERS:
        _require_exact_once(doc_readme, marker, "doc_readme", missing_markers)

    return missing_markers


def run_artifact_diff_contract_check(root: Path) -> list[str]:
    checker = root / "scripts/zigux/check-artifact-diff-contract.py"
    result = subprocess.run(
        [sys.executable, str(checker)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"artifact_diff_contract:exit:{result.returncode}"]
    if "ARTIFACT_DIFF_CONTRACT=pass" not in result.stdout:
        return ["artifact_diff_contract:missing_pass_marker"]
    return []


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_validator_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)

        _write(root / "scripts/zigux/artifact_diff.py", "# placeholder\n")
        _write(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            "#!/usr/bin/env python3\nprint('ARTIFACT_DIFF_CONTRACT=pass')\n",
        )
        _write(root / "scripts/zigux/validate-phase4.py", "# placeholder\n")
        _write(
            root / "Documentation/zigux/artifact-diff.md",
            "\n".join(
                [
                    "# Artifact Diff Policy",
                    "",
                    "Current Phase 4 use",
                    "- `scripts/zigux/artifact_diff.py` stays the shared host-side comparison helper.",
                    "- `zigux/tests/atomic64_diff.zig` remains in the packet as the roadmap-named wrapper.",
                    "- `zigux/tests/runtime_atomic64_diff.zig` remains in the packet as the shared replay body.",
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
                    "atomic64_diff.zig",
                    "runtime_atomic64_diff.zig",
                    "bitmap_diff.zig",
                    "phase4_bitmap_live_helper_replay.zig",
                    "rollback owner",
                    "lab and CI matrix",
                    "perf threshold status",
                    "zig build test --build-file zigux/tests/phase4_build.zig",
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
        _write(root / "zigux/tests/phase4_bitmap_live_helper_replay.zig", "// helper replay gate\n")
        _write(
            root / "zigux/tests/phase4_build.zig",
            "\n".join(
                [
                    "atomic64_diff.zig",
                    "runtime_atomic64_diff.zig",
                    "bitmap_diff.zig",
                    "phase4_bitmap_live_helper_replay.zig",
                    "phase4-runtime-atomic64-diff-tests",
                    "phase4-bitmap-diff-tests",
                    "phase4-bitmap-live-helper-replay-tests",
                    "",
                ]
            ),
        )
        _write(
            root / "zigux/tests/README.md",
            "\n".join(
                [
                    "zigux/tests/atomic64_diff.zig",
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
                    "atomic64_diff.zig",
                    "runtime_atomic64_diff.zig",
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
                    "atomic64_diff.zig",
                    "runtime_atomic64_diff.zig",
                    "",
                ]
            ),
        )

        assert _missing_files(root) == []
        assert validate_root(root) == []
        assert run_artifact_diff_contract_check(root) == []

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

    contract_failures = run_artifact_diff_contract_check(ROOT)
    if contract_failures:
        print("PHASE4_VALIDATION=fail")
        print("ARTIFACT_DIFF_CONTRACT_CHECK_START")
        for item in contract_failures:
            print(item)
        print("ARTIFACT_DIFF_CONTRACT_CHECK_END")
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
