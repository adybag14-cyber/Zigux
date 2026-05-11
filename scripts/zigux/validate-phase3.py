#!/usr/bin/env python3
"""Validate the landed Phase 3 ABI validator packet that is currently shipped."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import tempfile


ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDINGS_PATH = Path("zigux/bindings/abi.zig")
HEADER_DEFINE_RE = re.compile(r"^\s*#define\s+([A-Z0-9_]+)\b")
HEADER_STRUCT_RE = re.compile(r"^\s*struct\s+([A-Za-z_][A-Za-z0-9_]*)\b")
ZIG_CONST_RE = re.compile(r"^\s*pub const\s+([A-Za-z_][A-Za-z0-9_]*)\s*:")
ZIG_EXTERN_STRUCT_RE = re.compile(
    r"^\s*pub const\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*extern struct\b"
)

REPO_FILES = (
    Path("Documentation/zigux/phase3-abi-slice.md"),
    Path("Documentation/zigux/phase3-boundary-lane-sequencing.md"),
    Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"),
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("Documentation/zigux/phase3-linux-zigux-header-governance.md"),
    Path("Documentation/zigux/phase3-abi-header-family-survey.md"),
    Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("include/linux/zigux.h"),
    ABI_HEADER_PATH,
    ABI_BINDINGS_PATH,
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/unsafe/narrow.zig"),
    Path("zigux/tests/phase3_abi.zig"),
    Path("zigux/tests/phase3_abi_dump.zig"),
    Path("zigux/tests/fixtures/phase3_abi_manifest.json"),
    Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"),
    Path("zigux/tests/fixtures/phase3_abi/expected.json"),
    Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"),
    Path("scripts/zigux/check-phase3-selftest-surface.py"),
    Path("scripts/zigux/check-phase3-abi-dump-gate.py"),
    Path("scripts/zigux/check-phase3-catalog-selftest.py"),
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
    Path("scripts/zigux/validate-phase3-abi-bindings-syntax.py"),
    Path("scripts/zigux/survey-phase3-abi-constant-parity.py"),
    Path("scripts/zigux/phase3_catalog.py"),
    Path("scripts/zigux/phase3_check_lib.py"),
    Path("scripts/zigux/generate-phase3-check-wrappers.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/README.md"),
    Path("zigux/Makefile"),
)

MAKE_MARKERS = (
    "phase3-validate:",
    "$(PYTHON) scripts/zigux/validate-phase3.py",
    "$(PYTHON) scripts/zigux/validate-phase3.py --self-test",
    "$(PYTHON) scripts/zigux/validate-phase3-validator-support-surface.py",
    "$(PYTHON) scripts/zigux/validate-phase3-validator-support-surface.py --self-test",
    "$(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "$(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py",
    "$(PYTHON) scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "$(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "$(PYTHON) scripts/zigux/check-phase3-policy-byte-guards.py",
    "$(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "$(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py",
    "$(PYTHON) scripts/zigux/check-phase3-selftest-surface.py",
    "$(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "$(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py",
    "$(PYTHON) scripts/zigux/check-phase3-catalog-selftest.py --self-test",
    "$(PYTHON) scripts/zigux/phase3_catalog.py --self-test",
    "$(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "$(PYTHON) scripts/zigux/phase3_check_lib.py --self-test",
    "$(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check",
    "$(PYTHON) scripts/zigux/run-phase3-checks.py --self-test",
    "$(PYTHON) scripts/zigux/validate_phase3_selftest.py",
)

README_MARKERS = (
    "validate-phase3.py",
    "validate_phase3_selftest.py",
    "check-phase3-selftest-surface.py",
    "check-phase3-readme-tooling-inventory.py",
    "check-phase3-abi-dump-gate.py",
    "check-phase3-catalog-selftest.py",
    "validate-phase3-policy-unsafe-survey.py",
    "check-phase3-policy-byte-guards.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "validate-phase3-export-uapi-survey.py",
    "validate-phase3-abi-header-family-survey.py",
    "validate-phase3-validator-support-surface.py",
    "validate-phase3-abi-bindings-syntax.py",
    "survey-phase3-abi-constant-parity.py",
    "phase3_catalog.py",
    "phase3_check_lib.py",
    "generate-phase3-check-wrappers.py",
    "run-phase3-checks.py",
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "make -C zigux phase3-validate",
    "make -C zigux phase3-selftest",
    "make -C zigux phase3",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _record_duplicate(
    seen: dict[str, int], issues: list[str], label: str, name: str, lineno: int
) -> None:
    previous = seen.get(name)
    if previous is None:
        seen[name] = lineno
        return
    issues.append(
        f"duplicate {label}: {name} (first line {previous}, duplicate line {lineno})"
    )


def _validate_duplicate_declarations(text: str, matchers: tuple[tuple[str, re.Pattern[str]], ...]) -> list[str]:
    issues: list[str] = []
    for label, pattern in matchers:
        seen: dict[str, int] = {}
        for lineno, line in enumerate(text.splitlines(), start=1):
            match = pattern.match(line)
            if match is None:
                continue
            _record_duplicate(seen, issues, label, match.group(1), lineno)
    return issues


def validate_abi_surface_sanity(repo_root: Path) -> list[str]:
    issues: list[str] = []

    header_path = repo_root / ABI_HEADER_PATH
    if header_path.is_file():
        issues.extend(
            _validate_duplicate_declarations(
                _read(header_path),
                (
                    ("ABI header #define", HEADER_DEFINE_RE),
                    ("ABI header struct", HEADER_STRUCT_RE),
                ),
            )
        )

    bindings_path = repo_root / ABI_BINDINGS_PATH
    if bindings_path.is_file():
        issues.extend(
            _validate_duplicate_declarations(
                _read(bindings_path),
                (
                    ("ABI binding const", ZIG_CONST_RE),
                    ("ABI binding extern struct", ZIG_EXTERN_STRUCT_RE),
                ),
            )
        )

    return issues


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REPO_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    makefile_path = repo_root / "zigux/Makefile"
    if makefile_path.is_file():
        makefile_text = _read(makefile_path)
        for marker in MAKE_MARKERS:
            if marker not in makefile_text:
                issues.append(f"missing make marker: {marker}")

    readme_path = repo_root / "scripts/zigux/README.md"
    if readme_path.is_file():
        readme_text = _read(readme_path)
        for marker in README_MARKERS:
            if marker not in readme_text:
                issues.append(f"missing scripts README marker: {marker}")

    issues.extend(validate_abi_surface_sanity(repo_root))
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _populate_repo(root: Path) -> None:
    for rel_path in REPO_FILES:
        _write(root / rel_path, "# stub\n")

    _write(
        root / ABI_HEADER_PATH,
        "#define ZIGUX_ABI_VERSION 1\n"
        "#define ZIGUX_ABI_MINOR 2\n"
        "struct zigux_layout {\n"
        "    int value;\n"
        "};\n",
    )
    _write(
        root / ABI_BINDINGS_PATH,
        "pub const ZIGUX_ABI_VERSION: u32 = 1;\n"
        "pub const ZiguxLayout = extern struct {\n"
        "    value: i32,\n"
        "};\n",
    )
    _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
    _write(root / "scripts/zigux/README.md", "\n".join(README_MARKERS) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validate_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        missing_rel = REPO_FILES[0]
        (root / missing_rel).unlink()
        issues = validate_repo(root)
        expected_missing = f"missing repo file: {missing_rel.as_posix()}"
        if expected_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing repo file was not reported")
            return 1
        case_count += 1

        phase3_abi_rel = Path("zigux/tests/phase3_abi.zig")
        _write(root / missing_rel, "# restored\n")
        (root / phase3_abi_rel).unlink()
        issues = validate_repo(root)
        expected_phase3_abi_missing = f"missing repo file: {phase3_abi_rel.as_posix()}"
        if expected_phase3_abi_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing phase3_abi replay was not reported")
            return 1
        case_count += 1

        manifest_rel = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
        _write(root / phase3_abi_rel, "# restored\n")
        (root / manifest_rel).unlink()
        issues = validate_repo(root)
        expected_manifest_missing = f"missing repo file: {manifest_rel.as_posix()}"
        if expected_manifest_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing phase3 ABI manifest was not reported")
            return 1
        case_count += 1

        next_step_rel = Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")
        _write(root / manifest_rel, "# restored\n")
        (root / next_step_rel).unlink()
        issues = validate_repo(root)
        expected_next_step_missing = f"missing repo file: {next_step_rel.as_posix()}"
        if expected_next_step_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing next-step note was not reported")
            return 1
        case_count += 1

        validator_support_rel = Path("Documentation/zigux/phase3-validator-support-surface.md")
        _write(root / next_step_rel, "# restored\n")
        (root / validator_support_rel).unlink()
        issues = validate_repo(root)
        expected_validator_support_missing = (
            f"missing repo file: {validator_support_rel.as_posix()}"
        )
        if expected_validator_support_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing validator-support note was not reported")
            return 1
        case_count += 1

        support_validator_rel = Path(
            "scripts/zigux/validate-phase3-validator-support-surface.py"
        )
        _write(root / validator_support_rel, "# restored\n")
        (root / support_validator_rel).unlink()
        issues = validate_repo(root)
        expected_support_validator_missing = (
            f"missing repo file: {support_validator_rel.as_posix()}"
        )
        if expected_support_validator_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing validator-support checker was not reported")
            return 1
        case_count += 1

        _write(root / support_validator_rel, "# restored\n")
        _write(root / "zigux/Makefile", "phase3-validate:\n")
        issues = validate_repo(root)
        expected_marker = f"missing make marker: {MAKE_MARKERS[1]}"
        if expected_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing make marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "zigux/Makefile",
            _read(root / "zigux/Makefile").replace(
                "$(PYTHON) scripts/zigux/validate-phase3-validator-support-surface.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_validator_marker = (
            "missing make marker: $(PYTHON) "
            "scripts/zigux/validate-phase3-validator-support-surface.py --self-test"
        )
        if expected_validator_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing validator-support make marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "scripts/zigux/README.md",
            _read(root / "scripts/zigux/README.md").replace(
                "validate-phase3-validator-support-surface.py\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_support_readme_marker = (
            "missing scripts README marker: validate-phase3-validator-support-surface.py"
        )
        if expected_support_readme_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing validator-support README marker was not reported")
            return 1
        case_count += 1

        _write(root / "scripts/zigux/README.md", "\n".join(README_MARKERS) + "\n")
        _write(
            root / "scripts/zigux/README.md",
            _read(root / "scripts/zigux/README.md").replace(
                "Documentation/zigux/phase3-validator-support-surface.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_support_note_readme_marker = (
            "missing scripts README marker: Documentation/zigux/phase3-validator-support-surface.md"
        )
        if expected_support_note_readme_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing validator-support note README marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "zigux/Makefile",
            _read(root / "zigux/Makefile").replace(
                "$(PYTHON) scripts/zigux/check-phase3-catalog-selftest.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_catalog_marker = (
            "missing make marker: $(PYTHON) "
            "scripts/zigux/check-phase3-catalog-selftest.py --self-test"
        )
        if expected_catalog_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing catalog self-test make marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(root / "scripts/zigux/README.md", "validate-phase3.py\n")
        issues = validate_repo(root)
        expected_readme_marker = (
            "missing scripts README marker: validate-phase3-policy-unsafe-survey.py"
        )
        if expected_readme_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing README marker was not reported")
            return 1
        case_count += 1

        _write(root / "scripts/zigux/README.md", "\n".join(README_MARKERS) + "\n")
        _write(
            root / ABI_HEADER_PATH,
            _read(root / ABI_HEADER_PATH) + "#define ZIGUX_ABI_VERSION 3\n",
        )
        issues = validate_repo(root)
        expected_duplicate_define = (
            "duplicate ABI header #define: ZIGUX_ABI_VERSION "
            "(first line 1, duplicate line 6)"
        )
        if expected_duplicate_define not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected duplicate header define was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        _write(
            root / ABI_BINDINGS_PATH,
            _read(root / ABI_BINDINGS_PATH)
            + "pub const ZIGUX_ABI_VERSION: u32 = 2;\n",
        )
        issues = validate_repo(root)
        expected_duplicate_const = (
            "duplicate ABI binding const: ZIGUX_ABI_VERSION "
            "(first line 1, duplicate line 5)"
        )
        if expected_duplicate_const not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected duplicate binding const was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        _write(
            root / ABI_BINDINGS_PATH,
            _read(root / ABI_BINDINGS_PATH)
            + "pub const ZiguxLayout = extern struct {\n"
            + "    value: i32,\n"
            + "};\n",
        )
        issues = validate_repo(root)
        expected_duplicate_extern_struct = (
            "duplicate ABI binding extern struct: ZiguxLayout "
            "(first line 2, duplicate line 5)"
        )
        if expected_duplicate_extern_struct not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected duplicate extern struct was not reported")
            return 1
        case_count += 1

    print("PHASE3_VALIDATE_SELF_TEST=pass")
    print(f"PHASE3_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shipped Phase 3 ABI boundary survey and support-script packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains scripts/zigux/ and zigux/Makefile",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_VALIDATE=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / 'scripts/zigux/README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
