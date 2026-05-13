#!/usr/bin/env python3
"""Validate the landed Phase 3 ABI validator packet that is currently shipped."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile


ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDINGS_PATH = Path("zigux/bindings/abi.zig")
ABI_MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
ATOMIC_HELPER_PATH = Path("zigux/helpers/atomic.zig")
BARRIER_HELPER_PATH = Path("zigux/helpers/barrier.zig")
MMIO_HELPER_PATH = Path("zigux/helpers/mmio.zig")
LOW_LEVEL_TEST_PATH = Path("zigux/tests/phase3_low_level_wrappers.zig")
LOW_LEVEL_BUILD_PATH = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
TEST_BUILD_PATH = Path("zigux/tests/build.zig")
HEADER_DEFINE_RE = re.compile(r"^\s*#define\s+([A-Z0-9_]+)\b")
HEADER_STRUCT_RE = re.compile(r"^\s*struct\s+([A-Za-z_][A-Za-z0-9_]*)\b")
ZIG_CONST_RE = re.compile(r"^\s*pub const\s+([A-Za-z_][A-Za-z0-9_]*)\s*:")
ZIG_EXTERN_STRUCT_RE = re.compile(
    r"^\s*pub const\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*extern struct\b"
)

REQUIRED_MANIFEST_FILES = (
    Path("zigux/uapi/dev_t.zig"),
)

REPO_FILES = (
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("Documentation/zigux/phase3-abi-slice.md"),
    Path("Documentation/zigux/phase3-boundary-lane-sequencing.md"),
    Path("Documentation/zigux/phase3-kernel-export-shim-governance.md"),
    Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"),
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    Path("Documentation/zigux/phase3-linux-zigux-header-governance.md"),
    Path("Documentation/zigux/phase3-abi-header-family-survey.md"),
    Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("include/linux/zigux.h"),
    ABI_HEADER_PATH,
    ABI_BINDINGS_PATH,
    Path("zigux/helpers/layout_assert.zig"),
    Path("zigux/helpers/panic_policy.zig"),
    Path("zigux/helpers/allocator_policy.zig"),
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/uapi/dev_t.zig"),
    Path("zigux/unsafe/narrow.zig"),
    ATOMIC_HELPER_PATH,
    BARRIER_HELPER_PATH,
    MMIO_HELPER_PATH,
    LOW_LEVEL_BUILD_PATH,
    LOW_LEVEL_TEST_PATH,
    TEST_BUILD_PATH,
    Path("zigux/tests/README.md"),
    Path("zigux/tests/phase3_abi.zig"),
    Path("zigux/tests/phase3_abi_dump.zig"),
    ABI_MANIFEST_PATH,
    Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"),
    Path("zigux/tests/fixtures/phase3_abi/expected.json"),
    Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"),
    Path("scripts/zigux/check-phase3-selftest-surface.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/check-phase3-abi-dump-gate.py"),
    Path("scripts/zigux/check-phase3-catalog-selftest.py"),
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"),
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
    Path("scripts/zigux/README.md"),
    Path("zigux/Makefile"),
    Path(".github/workflows/zigux-bootstrap.yml"),
)

MAKE_MARKERS = (
    "phase3-validate:",
    "$(PYTHON) scripts/zigux/validate-phase3.py",
    "$(PYTHON) scripts/zigux/validate-phase3.py --self-test",
    "$(PYTHON) scripts/zigux/validate-phase3-validator-support-surface.py",
    "$(PYTHON) scripts/zigux/validate-phase3-validator-support-surface.py --self-test",
    "$(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "$(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test",
    "$(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py",
    "$(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py --self-test",
    "$(PYTHON) scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "$(PYTHON) scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test",
    "$(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "$(PYTHON) scripts/zigux/check-phase3-policy-byte-guards.py",
    "$(PYTHON) scripts/zigux/check-phase3-policy-byte-guards.py --self-test",
    "$(PYTHON) scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "$(PYTHON) scripts/zigux/check-phase3-policy-unsafe-focused-replay.py --self-test",
    "$(PYTHON) scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "$(PYTHON) scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py --self-test",
    "$(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "$(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "$(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py",
    "$(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "$(PYTHON) scripts/zigux/check-phase3-selftest-surface.py",
    "$(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "$(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py",
    "$(PYTHON) scripts/zigux/check-phase3-catalog-selftest.py --self-test",
    "$(PYTHON) scripts/zigux/phase3_catalog.py --self-test",
    "$(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "$(PYTHON) scripts/zigux/phase3_check_lib.py --self-test",
    "$(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test",
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
    "check-phase3-policy-unsafe-focused-replay.py",
    "check-phase3-policy-unsafe-mmio-consumer.py",
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
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "zigux/uapi/dev_t.zig",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "make -C zigux phase3-validate",
    "make -C zigux phase3-selftest",
    "make -C zigux phase3",
)

LOW_LEVEL_WRAPPER_SOURCE_MARKERS = {
    LOW_LEVEL_TEST_PATH: (
        "atomic.load(u32, &value, .seq_cst)",
        "atomic.store(u32, &value, 8, .seq_cst)",
        "atomic.exchange(u32, &value, 13, .seq_cst)",
        "atomic.fetchAdd(u32, &value, 4, .seq_cst)",
        "atomic.compareExchange(u32, &value, 13, 21, .seq_cst, .seq_cst)",
        "barrier.acquire();",
        "barrier.release();",
        "barrier.full();",
        "mmio.range(base, 24, 4)",
        "mmio.read16(base, 2)",
        "mmio.read32(base, @sizeOf(u32))",
        "mmio.write16(base, 2, 0xbeef)",
        "mmio.write32(base, @sizeOf(u32), 0xfeedbeef)",
        "mmio.rangeInteropPolicy(base, 16, 4, mmio_policy)",
        "mmio.read32InteropPolicy(base, 4, mmio_policy)",
        "mmio.write32InteropPolicy(base, 4, 0xfeed_beef, mmio_policy)",
        "abi.InteropPolicy{",
        "@intFromEnum(abi.UnsafeScope.volatile_mmio)",
    ),
}


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


def _validate_duplicate_declarations(
    text: str, matchers: tuple[tuple[str, re.Pattern[str]], ...]
) -> list[str]:
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


def validate_manifest(repo_root: Path) -> list[str]:
    manifest_path = repo_root / ABI_MANIFEST_PATH
    if not manifest_path.is_file():
        return []

    issues: list[str] = []
    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"invalid phase3 ABI manifest JSON: {exc.msg}"]

    files = manifest.get("files")
    if not isinstance(files, list):
        return ["invalid phase3 ABI manifest files list"]

    file_count = manifest.get("file_count")
    if isinstance(file_count, int) and file_count != len(files):
        issues.append(
            f"phase3 ABI manifest file_count drift: expected {len(files)}, found {file_count}"
        )

    file_entries: set[str] = set()
    for entry in files:
        if not isinstance(entry, str):
            issues.append(f"invalid phase3 ABI manifest file entry: {entry!r}")
            continue
        file_entries.add(entry)
        if not (repo_root / entry).is_file():
            issues.append(f"missing manifest-tracked repo file: {entry}")

    for rel_path in REQUIRED_MANIFEST_FILES:
        if rel_path.as_posix() not in file_entries:
            issues.append(f"missing phase3 ABI manifest entry: {rel_path.as_posix()}")

    return issues


def validate_source_markers(
    repo_root: Path, required_markers: dict[Path, tuple[str, ...]]
) -> list[str]:
    issues: list[str] = []
    for rel_path, markers in required_markers.items():
        source_path = repo_root / rel_path
        if not source_path.is_file():
            continue
        source_text = _read(source_path)
        for marker in markers:
            if marker not in source_text:
                issues.append(f"missing source marker: {rel_path.as_posix()} :: {marker}")
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

    issues.extend(validate_manifest(repo_root))
    issues.extend(validate_source_markers(repo_root, LOW_LEVEL_WRAPPER_SOURCE_MARKERS))
    issues.extend(validate_abi_surface_sanity(repo_root))
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _manifest_payload(files: list[str], file_count: int | None = None) -> str:
    payload = {
        "phase": "Phase 3",
        "status": "active",
        "slice": "abi-substrate-skeleton",
        "file_count": len(files) if file_count is None else file_count,
        "files": files,
    }
    return json.dumps(payload, indent=2) + "\n"


def _low_level_wrapper_stub() -> str:
    return """const abi = @import(\"abi_bindings\");
test \"phase3 low-level wrappers stub markers\" {
    _ = atomic.load(u32, &value, .seq_cst);
    atomic.store(u32, &value, 8, .seq_cst);
    _ = atomic.exchange(u32, &value, 13, .seq_cst);
    _ = atomic.fetchAdd(u32, &value, 4, .seq_cst);
    _ = atomic.compareExchange(u32, &value, 13, 21, .seq_cst, .seq_cst);
    barrier.acquire();
    barrier.release();
    barrier.full();
    _ = mmio.range(base, 24, 4);
    _ = mmio.read16(base, 2);
    _ = mmio.read32(base, @sizeOf(u32));
    mmio.write16(base, 2, 0xbeef);
    mmio.write32(base, @sizeOf(u32), 0xfeedbeef);
    const mmio_policy = abi.InteropPolicy{
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
    };
    _ = mmio.rangeInteropPolicy(base, 16, 4, mmio_policy);
    _ = mmio.read32InteropPolicy(base, 4, mmio_policy);
    try mmio.write32InteropPolicy(base, 4, 0xfeed_beef, mmio_policy);
}
"""


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
    _write(
        root / ABI_MANIFEST_PATH,
        _manifest_payload([rel_path.as_posix() for rel_path in REQUIRED_MANIFEST_FILES]),
    )
    _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
    _write(root / "scripts/zigux/README.md", "\n".join(README_MARKERS) + "\n")
    _write(root / LOW_LEVEL_TEST_PATH, _low_level_wrapper_stub())
    _write(root / "include/zigux/dev_t.h", "#define ZIGUX_DEV_T_BITS 32\n")
    _write(root / "zigux/bindings/dev_t.zig", "pub const dev_t = u32;\n")
    _write(root / "zigux/bindings/notifier_abi.zig", "pub const notifier_call = i32;\n")
    _write(root / "zigux/helpers/layout_assert.zig", "pub fn layoutAssert() void {}\n")
    _write(root / "zigux/helpers/panic_policy.zig", "pub fn panicPolicy() void {}\n")
    _write(root / "zigux/helpers/allocator_policy.zig", "pub fn allocatorPolicy() void {}\n")
    _write(
        root / ABI_MANIFEST_PATH,
        _manifest_payload(
            [rel_path.as_posix() for rel_path in REQUIRED_MANIFEST_FILES]
            + [
                "include/zigux/dev_t.h",
                "zigux/bindings/dev_t.zig",
                "zigux/bindings/notifier_abi.zig",
                "zigux/helpers/layout_assert.zig",
                "zigux/helpers/panic_policy.zig",
                "zigux/helpers/allocator_policy.zig",
            ]
        ),
    )


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

        review_checklist_rel = Path("Documentation/zigux/review-checklist.md")
        _write(root / missing_rel, "# restored\n")
        (root / review_checklist_rel).unlink()
        issues = validate_repo(root)
        expected_review_checklist_missing = (
            f"missing repo file: {review_checklist_rel.as_posix()}"
        )
        if expected_review_checklist_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing review checklist was not reported")
            return 1
        case_count += 1

        tests_readme_rel = Path("zigux/tests/README.md")
        _write(root / review_checklist_rel, "# restored\n")
        (root / tests_readme_rel).unlink()
        issues = validate_repo(root)
        expected_tests_readme_missing = f"missing repo file: {tests_readme_rel.as_posix()}"
        if expected_tests_readme_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing tests README was not reported")
            return 1
        case_count += 1

        selftest_driver_rel = Path("scripts/zigux/validate_phase3_selftest.py")
        _write(root / tests_readme_rel, "# restored\n")
        (root / selftest_driver_rel).unlink()
        issues = validate_repo(root)
        expected_selftest_driver_missing = (
            f"missing repo file: {selftest_driver_rel.as_posix()}"
        )
        if expected_selftest_driver_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing phase3 selftest driver was not reported")
            return 1
        case_count += 1

        workflow_rel = Path(".github/workflows/zigux-bootstrap.yml")
        _write(root / selftest_driver_rel, "# restored\n")
        (root / workflow_rel).unlink()
        issues = validate_repo(root)
        expected_workflow_missing = f"missing repo file: {workflow_rel.as_posix()}"
        if expected_workflow_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing workflow was not reported")
            return 1
        case_count += 1

        phase3_abi_rel = Path("zigux/tests/phase3_abi.zig")
        _write(root / workflow_rel, "# restored\n")
        (root / phase3_abi_rel).unlink()
        issues = validate_repo(root)
        expected_phase3_abi_missing = f"missing repo file: {phase3_abi_rel.as_posix()}"
        if expected_phase3_abi_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing phase3_abi replay was not reported")
            return 1
        case_count += 1

        layout_assert_rel = Path("zigux/helpers/layout_assert.zig")
        _write(root / phase3_abi_rel, "# restored\n")
        (root / layout_assert_rel).unlink()
        issues = validate_repo(root)
        expected_layout_assert_missing = (
            f"missing repo file: {layout_assert_rel.as_posix()}"
        )
        if expected_layout_assert_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing layout-assert helper was not reported")
            return 1
        case_count += 1

        _write(root / layout_assert_rel, "pub fn layoutAssert() void {}\n")
        (root / LOW_LEVEL_TEST_PATH).unlink()
        issues = validate_repo(root)
        expected_low_level_test_missing = f"missing repo file: {LOW_LEVEL_TEST_PATH.as_posix()}"
        if expected_low_level_test_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing low-level replay was not reported")
            return 1
        case_count += 1

        _write(root / LOW_LEVEL_TEST_PATH, "# restored\n")
        issues = validate_repo(root)
        expected_low_level_marker_missing = (
            "missing source marker: "
            f"{LOW_LEVEL_TEST_PATH.as_posix()} :: atomic.load(u32, &value, .seq_cst)"
        )
        if expected_low_level_marker_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing low-level wrapper marker was not reported")
            return 1
        case_count += 1

        low_level_build_rel = LOW_LEVEL_BUILD_PATH
        _write(root / LOW_LEVEL_TEST_PATH, _low_level_wrapper_stub())
        (root / low_level_build_rel).unlink()
        issues = validate_repo(root)
        expected_low_level_build_missing = (
            f"missing repo file: {low_level_build_rel.as_posix()}"
        )
        if expected_low_level_build_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing low-level wrapper build anchor was not reported")
            return 1
        case_count += 1

        low_level_note_rel = Path(
            "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"
        )
        _write(root / low_level_build_rel, "# restored\n")
        (root / low_level_note_rel).unlink()
        issues = validate_repo(root)
        expected_low_level_note_missing = (
            f"missing repo file: {low_level_note_rel.as_posix()}"
        )
        if expected_low_level_note_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing low-level wrapper note was not reported")
            return 1
        case_count += 1

        _write(root / low_level_note_rel, "# restored\n")
        (root / MMIO_HELPER_PATH).unlink()
        issues = validate_repo(root)
        expected_mmio_missing = f"missing repo file: {MMIO_HELPER_PATH.as_posix()}"
        if expected_mmio_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing mmio helper was not reported")
            return 1
        case_count += 1

        _write(root / MMIO_HELPER_PATH, "# restored\n")
        panic_policy_rel = Path("zigux/helpers/panic_policy.zig")
        allocator_policy_rel = Path("zigux/helpers/allocator_policy.zig")
        _write(root / allocator_policy_rel, "pub fn allocatorPolicy() void {}\n")
        (root / panic_policy_rel).unlink()
        issues = validate_repo(root)
        expected_panic_policy_missing = (
            f"missing repo file: {panic_policy_rel.as_posix()}"
        )
        if expected_panic_policy_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing panic-policy helper was not reported")
            return 1
        case_count += 1

        manifest_rel = ABI_MANIFEST_PATH
        _write(root / panic_policy_rel, "pub fn panicPolicy() void {}\n")
        _write(root / ABI_MANIFEST_PATH, _manifest_payload([]))
        issues = validate_repo(root)
        expected_manifest_entry_missing = "missing phase3 ABI manifest entry: zigux/uapi/dev_t.zig"
        if expected_manifest_entry_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing phase3 ABI manifest entry was not reported")
            return 1
        case_count += 1

        _write(
            root / ABI_MANIFEST_PATH,
            _manifest_payload([rel_path.as_posix() for rel_path in REQUIRED_MANIFEST_FILES], file_count=2),
        )
        issues = validate_repo(root)
        expected_manifest_count_drift = "phase3 ABI manifest file_count drift: expected 1, found 2"
        if expected_manifest_count_drift not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected phase3 ABI manifest file_count drift was not reported")
            return 1
        case_count += 1

        _write(
            root / ABI_MANIFEST_PATH,
            _manifest_payload(
                [rel_path.as_posix() for rel_path in REQUIRED_MANIFEST_FILES]
                + ["zigux/helpers/panic_policy.zig"]
            ),
        )
        (root / "zigux/helpers/panic_policy.zig").unlink()
        issues = validate_repo(root)
        expected_manifest_tracked_helper_missing = (
            "missing manifest-tracked repo file: zigux/helpers/panic_policy.zig"
        )
        if expected_manifest_tracked_helper_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing manifest-tracked panic policy helper was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/helpers/panic_policy.zig", "pub fn panicPolicy() void {}\n")
        _write(
            root / ABI_MANIFEST_PATH,
            _manifest_payload(
                [rel_path.as_posix() for rel_path in REQUIRED_MANIFEST_FILES]
                + ["include/zigux/dev_t.h"]
            ),
        )
        (root / "include/zigux/dev_t.h").unlink()
        issues = validate_repo(root)
        expected_manifest_tracked_header_missing = (
            "missing manifest-tracked repo file: include/zigux/dev_t.h"
        )
        if expected_manifest_tracked_header_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing manifest-tracked dev_t header was not reported")
            return 1
        case_count += 1

        _write(root / "include/zigux/dev_t.h", "#define ZIGUX_DEV_T_BITS 32\n")
        _write(root / ABI_MANIFEST_PATH, _manifest_payload([rel_path.as_posix() for rel_path in REQUIRED_MANIFEST_FILES]))
        (root / manifest_rel).unlink()
        issues = validate_repo(root)
        expected_manifest_missing = f"missing repo file: {manifest_rel.as_posix()}"
        if expected_manifest_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing phase3 ABI manifest was not reported")
            return 1
        case_count += 1

        next_step_rel = Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")
        _write(root / manifest_rel, _manifest_payload([rel_path.as_posix() for rel_path in REQUIRED_MANIFEST_FILES]))
        (root / next_step_rel).unlink()
        issues = validate_repo(root)
        expected_next_step_missing = f"missing repo file: {next_step_rel.as_posix()}"
        if expected_next_step_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing next-step note was not reported")
            return 1
        case_count += 1

        kernel_export_governance_rel = Path(
            "Documentation/zigux/phase3-kernel-export-shim-governance.md"
        )
        _write(root / next_step_rel, "# restored\n")
        (root / kernel_export_governance_rel).unlink()
        issues = validate_repo(root)
        expected_kernel_export_governance_missing = (
            f"missing repo file: {kernel_export_governance_rel.as_posix()}"
        )
        if expected_kernel_export_governance_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing kernel export-shim governance note was not reported")
            return 1
        case_count += 1

        validator_support_rel = Path("Documentation/zigux/phase3-validator-support-surface.md")
        _write(root / kernel_export_governance_rel, "# restored\n")
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
            root / "zigux/Makefile",
            _read(root / "zigux/Makefile").replace(
                "$(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_export_uapi_selftest_marker = (
            "missing make marker: $(PYTHON) "
            "scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"
        )
        if expected_export_uapi_selftest_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing export-uapi self-test make marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "zigux/Makefile",
            _read(root / "zigux/Makefile").replace(
                "$(PYTHON) scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_header_family_selftest_marker = (
            "missing make marker: $(PYTHON) "
            "scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test"
        )
        if expected_header_family_selftest_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing header-family self-test make marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "zigux/Makefile",
            _read(root / "zigux/Makefile").replace(
                "$(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_bindings_syntax_selftest_marker = (
            "missing make marker: $(PYTHON) "
            "scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test"
        )
        if expected_bindings_syntax_selftest_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing bindings-syntax self-test make marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "zigux/Makefile",
            _read(root / "zigux/Makefile").replace(
                "$(PYTHON) scripts/zigux/check-phase3-policy-byte-guards.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_policy_guard_selftest_marker = (
            "missing make marker: $(PYTHON) "
            "scripts/zigux/check-phase3-policy-byte-guards.py --self-test"
        )
        if expected_policy_guard_selftest_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing policy-byte guard self-test make marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "zigux/Makefile",
            _read(root / "zigux/Makefile").replace(
                "$(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_constant_parity_selftest_marker = (
            "missing make marker: $(PYTHON) "
            "scripts/zigux/survey-phase3-abi-constant-parity.py --self-test"
        )
        if expected_constant_parity_selftest_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing constant-parity self-test make marker was not reported")
            return 1
        case_count += 1

        low_level_survey_rel = Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")
        _write(root / support_validator_rel, "# restored\n")
        (root / low_level_survey_rel).unlink()
        issues = validate_repo(root)
        expected_low_level_survey_missing = (
            f"missing repo file: {low_level_survey_rel.as_posix()}"
        )
        if expected_low_level_survey_missing not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing low-level wrapper survey checker was not reported")
            return 1
        case_count += 1

        _write(root / low_level_survey_rel, "# restored\n")
        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "zigux/Makefile",
            _read(root / "zigux/Makefile").replace(
                "$(PYTHON) scripts/zigux/check-phase3-policy-unsafe-focused-replay.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_focused_replay_selftest_marker = (
            "missing make marker: $(PYTHON) "
            "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py --self-test"
        )
        if expected_focused_replay_selftest_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing focused policy replay self-test make marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "zigux/Makefile",
            _read(root / "zigux/Makefile").replace(
                "$(PYTHON) scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_mmio_consumer_selftest_marker = (
            "missing make marker: $(PYTHON) "
            "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py --self-test"
        )
        if expected_mmio_consumer_selftest_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected typed-policy mmio consumer self-test make marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "zigux/Makefile",
            _read(root / "zigux/Makefile").replace(
                "$(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_wrapper_selftest_marker = (
            "missing make marker: $(PYTHON) "
            "scripts/zigux/generate-phase3-check-wrappers.py --self-test"
        )
        if expected_wrapper_selftest_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing generated-wrapper self-test make marker was not reported")
            return 1
        case_count += 1

        _write(root / "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / "scripts/zigux/README.md",
            _read(root / "scripts/zigux/README.md").replace(
                "validate-phase3-low-level-wrapper-survey.py\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_support_readme_marker = (
            "missing scripts README marker: validate-phase3-low-level-wrapper-survey.py"
        )
        if expected_support_readme_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing low-level-wrapper README marker was not reported")
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

        _write(root / "scripts/zigux/README.md", "\n".join(README_MARKERS) + "\n")
        _write(
            root / "scripts/zigux/README.md",
            _read(root / "scripts/zigux/README.md").replace(
                "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_low_level_note_readme_marker = (
            "missing scripts README marker: Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"
        )
        if expected_low_level_note_readme_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing low-level-wrapper note README marker was not reported")
            return 1
        case_count += 1

        _write(root / "scripts/zigux/README.md", "\n".join(README_MARKERS) + "\n")
        _write(
            root / "scripts/zigux/README.md",
            _read(root / "scripts/zigux/README.md").replace(
                "check-phase3-policy-unsafe-focused-replay.py\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_focused_replay_readme_marker = (
            "missing scripts README marker: check-phase3-policy-unsafe-focused-replay.py"
        )
        if expected_focused_replay_readme_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing focused policy replay README marker was not reported")
            return 1
        case_count += 1

        _write(root / "scripts/zigux/README.md", "\n".join(README_MARKERS) + "\n")
        _write(
            root / "scripts/zigux/README.md",
            _read(root / "scripts/zigux/README.md").replace(
                "check-phase3-policy-unsafe-mmio-consumer.py\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_mmio_consumer_readme_marker = (
            "missing scripts README marker: check-phase3-policy-unsafe-mmio-consumer.py"
        )
        if expected_mmio_consumer_readme_marker not in issues:
            print("PHASE3_VALIDATE_SELF_TEST=fail")
            print("expected missing mmio consumer README marker was not reported")
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
