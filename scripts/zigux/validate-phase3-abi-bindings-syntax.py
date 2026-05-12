#!/usr/bin/env python3
"""Validate the shared Phase 3 ABI/bindings syntax review packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SLICE_NOTE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
NEXT_STEP_NOTE_PATH = Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")
README_PATH = Path("scripts/zigux/README.md")

REQUIRED_FILES = (
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("Documentation/zigux/phase3-abi-header-family-survey.md"),
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("include/linux/zigux.h"),
    Path("include/zigux/abi.h"),
    Path("include/zigux/dev_t.h"),
    Path("zigux/bindings/abi.zig"),
    Path("zigux/bindings/dev_t.zig"),
    Path("zigux/bindings/notifier_abi.zig"),
    Path("zigux/helpers/layout_assert.zig"),
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/unsafe/narrow.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/uapi/dev_t.zig"),
    Path("zigux/tests/phase3_abi_dump.zig"),
    Path("zigux/tests/phase3_low_level_wrappers.zig"),
    Path("zigux/tests/fixtures/phase3_abi_manifest.json"),
    Path("scripts/zigux/check-phase3-abi.py"),
    Path("scripts/zigux/check-phase3-abi-dump-gate.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/survey-phase3-abi-constant-parity.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
)

SLICE_NOTE_MARKERS = (
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/linux/zigux.h",
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "PHASE3_ABI_MANIFEST_FILE_COUNT=",
    "PHASE3_CURRENT_INTEROP_GAP=",
    "PHASE3_CURRENT_INTEROP_GAP_DETAIL=",
    "PHASE3_NEXT_SAFE_STEP=",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
)

NEXT_STEP_NOTE_MARKERS = (
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
)

README_MARKERS = (
    "validate-phase3-export-uapi-survey.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "validate-phase3-validator-support-surface.py",
    "validate-phase3-abi-bindings-syntax.py",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    if not (repo_root / SLICE_NOTE_PATH).is_file():
        issues.append(f"missing repo file: {SLICE_NOTE_PATH.as_posix()}")
    if not (repo_root / NEXT_STEP_NOTE_PATH).is_file():
        issues.append(f"missing repo file: {NEXT_STEP_NOTE_PATH.as_posix()}")
    if not (repo_root / README_PATH).is_file():
        issues.append(f"missing repo file: {README_PATH.as_posix()}")
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
    slice_note_path = repo_root / SLICE_NOTE_PATH
    if slice_note_path.is_file():
        slice_note_text = _read(slice_note_path)
        for marker in SLICE_NOTE_MARKERS:
            if marker not in slice_note_text:
                issues.append(f"missing slice marker: {marker}")
    next_step_note_path = repo_root / NEXT_STEP_NOTE_PATH
    if next_step_note_path.is_file():
        next_step_note_text = _read(next_step_note_path)
        for marker in NEXT_STEP_NOTE_MARKERS:
            if marker not in next_step_note_text:
                issues.append(f"missing next-step marker: {marker}")
    readme_path = repo_root / README_PATH
    if readme_path.is_file():
        readme_text = _read(readme_path)
        for marker in README_MARKERS:
            if marker not in readme_text:
                issues.append(f"missing scripts README marker: {marker}")
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path, "# stub\n")
    _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
    _write(root / NEXT_STEP_NOTE_PATH, "\n".join(NEXT_STEP_NOTE_MARKERS) + "\n")
    _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_bindings_syntax_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)
        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1
        missing_rel = REQUIRED_FILES[0]
        (root / missing_rel).unlink()
        issues = validate_repo(root)
        expected_missing = f"missing repo file: {missing_rel.as_posix()}"
        if expected_missing not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing repo file was not reported")
            return 1
        case_count += 1
        _write(root / missing_rel, "# restored\n")
        _write(root / SLICE_NOTE_PATH, _read(root / SLICE_NOTE_PATH).replace("zigux/uapi/version.zig\n", "", 1))
        issues = validate_repo(root)
        expected_slice_marker = "missing slice marker: zigux/uapi/version.zig"
        if expected_slice_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(
            root / SLICE_NOTE_PATH,
            _read(root / SLICE_NOTE_PATH).replace(
                "Documentation/zigux/phase3-export-uapi-boundary-survey.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_export_uapi_marker = (
            "missing slice marker: Documentation/zigux/phase3-export-uapi-boundary-survey.md"
        )
        if expected_export_uapi_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing export-uapi slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(root / SLICE_NOTE_PATH, _read(root / SLICE_NOTE_PATH).replace("zigux/uapi/dev_t.zig\n", "", 1))
        issues = validate_repo(root)
        expected_dev_t_marker = "missing slice marker: zigux/uapi/dev_t.zig"
        if expected_dev_t_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing dev_t slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(root / NEXT_STEP_NOTE_PATH, _read(root / NEXT_STEP_NOTE_PATH).replace("scripts/zigux/validate-phase3-abi-bindings-syntax.py\n", "", 1))
        issues = validate_repo(root)
        expected_next_step_marker = "missing next-step marker: scripts/zigux/validate-phase3-abi-bindings-syntax.py"
        if expected_next_step_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing next-step marker was not reported")
            return 1
        case_count += 1
        _write(root / NEXT_STEP_NOTE_PATH, "\n".join(NEXT_STEP_NOTE_MARKERS) + "\n")
        _write(root / SLICE_NOTE_PATH, _read(root / SLICE_NOTE_PATH).replace("PHASE3_CURRENT_INTEROP_GAP=\n", "", 1))
        issues = validate_repo(root)
        expected_gap_marker = "missing slice marker: PHASE3_CURRENT_INTEROP_GAP="
        if expected_gap_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing interop-gap marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(root / SLICE_NOTE_PATH, _read(root / SLICE_NOTE_PATH).replace("scripts/zigux/check-phase3-abi-dump-gate.py\n", "", 1))
        issues = validate_repo(root)
        expected_dump_gate_marker = "missing slice marker: scripts/zigux/check-phase3-abi-dump-gate.py"
        if expected_dump_gate_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing dump-gate marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(root / README_PATH, _read(root / README_PATH).replace("zigux/uapi/dev_t.zig\n", "", 1))
        issues = validate_repo(root)
        expected_readme_marker = "missing scripts README marker: zigux/uapi/dev_t.zig"
        if expected_readme_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing README dev_t marker was not reported")
            return 1
        case_count += 1
        _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")
        _write(root / SLICE_NOTE_PATH, _read(root / SLICE_NOTE_PATH).replace("Documentation/zigux/phase3-validator-support-surface.md\n", "", 1))
        issues = validate_repo(root)
        expected_validator_support_marker = "missing slice marker: Documentation/zigux/phase3-validator-support-surface.md"
        if expected_validator_support_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing validator-support slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(root / SLICE_NOTE_PATH, _read(root / SLICE_NOTE_PATH).replace("python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test\n", "", 1))
        issues = validate_repo(root)
        expected_low_level_selftest_marker = "missing slice marker: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"
        if expected_low_level_selftest_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing low-level self-test slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(root / README_PATH, _read(root / README_PATH).replace("Documentation/zigux/phase3-validator-support-surface.md\n", "", 1))
        issues = validate_repo(root)
        expected_validator_support_readme_marker = "missing scripts README marker: Documentation/zigux/phase3-validator-support-surface.md"
        if expected_validator_support_readme_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing validator-support README marker was not reported")
            return 1
        case_count += 1
        _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")
        _write(root / README_PATH, _read(root / README_PATH).replace("validate-phase3-low-level-wrapper-survey.py\n", "", 1))
        issues = validate_repo(root)
        expected_low_level_readme_marker = "missing scripts README marker: validate-phase3-low-level-wrapper-survey.py"
        if expected_low_level_readme_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing low-level README marker was not reported")
            return 1
        case_count += 1
    print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass")
    print(f"PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the shared Phase 3 ABI and bindings syntax review packet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root that contains the shared Phase 3 ABI packet")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_BINDINGS_SYNTAX=fail")
        for issue in issues:
            print(issue)
        return 1
    print(f"validated {args.repo_root / SLICE_NOTE_PATH}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
