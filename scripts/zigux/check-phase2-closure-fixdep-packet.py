#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
FIXDEP_CASES_REL = Path("zigux/tests/fixtures/fixdep/cases.json")
FIXDEP_GATE_REL = Path("scripts/zigux/check-phase2-fixdep-gate.py")
FIXDEP_DIFF_REL = Path("scripts/zigux/check-fixdep-diff.py")
FIXDEP_ZIG_REL = Path("scripts/zigux/fixdep.zig")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    CLOSURE_REL,
    MANIFEST_REL,
    FIXDEP_CASES_REL,
    FIXDEP_GATE_REL,
    FIXDEP_DIFF_REL,
    FIXDEP_ZIG_REL,
    MAKEFILE_REL,
)

CLOSURE_REQUIRED_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
    "`zig test scripts/zigux/fixdep.zig`",
)

FIXDEP_SUPPORT_REQUIRED = (
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
)

MAKE_WRAPPER_REQUIRED = "make -C zigux phase2-fixdep"

FIXDEP_CASE_NAMES = (
    "sample",
    "sample_multi_target",
    "sample_escaped_space",
    "sample_escaped_colon",
    "sample_concatenated",
    "sample_dependency_continuation",
    "sample_comment_continuation",
    "sample_double_backslash_comment",
    "sample_comment_only",
    "sample_comment_only_stdout_full",
    "sample_missing_dep",
    "sample_missing_dep_stdout_full",
    "sample_output_write",
)

FIXDEP_GATE_REQUIRED_MARKERS = (
    'FIXDEP_DIFF_REL = Path("scripts/zigux/check-fixdep-diff.py")',
    'FIXDEP_CASES_REL = Path("zigux/tests/fixtures/fixdep/cases.json")',
    'print("PHASE2_FIXDEP_GATE=pass")',
)

FIXDEP_DIFF_REQUIRED_MARKERS = (
    'ZIG_FIXDEP = ROOT / "scripts" / "zigux" / "fixdep.zig"',
    'CASES_PATH = FIXTURE_DIR / "cases.json"',
    "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)",
    'print("FIXDEP_DIFF=pass")',
    'print("FIXDEP_DETERMINISM=pass")',
)

FIXDEP_ZIG_REQUIRED_MARKERS = (
    "const FixdepError = error{",
    "fn isIgnoredFile(path: []const u8) bool {",
    'test "config parsing trims _MODULE and deduplicates symbols" {',
)

MAKEFILE_REQUIRED_MARKERS = (
    ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

EXPECTED_SELF_TEST_CASE_COUNT = 6


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    write_text(path, json.dumps(data, indent=2) + "\n")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).is_file():
            issues.append(f"missing_file:{rel.as_posix()}")
    if issues:
        return issues

    closure_text = read_text(resolve(root, CLOSURE_REL))
    for marker in CLOSURE_REQUIRED_MARKERS:
        if marker not in closure_text:
            issues.append(f"missing_closure_marker:{marker}")

    manifest = json.loads(read_text(resolve(root, MANIFEST_REL)))
    if manifest.get("phase") != "Phase 2":
        issues.append(f"unexpected_manifest_phase:{manifest.get('phase')!r}")

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append("missing_manifest_present_surfaces")
        return issues

    fixdep_support = present_surfaces.get("fixdep_support")
    if not isinstance(fixdep_support, list):
        issues.append("missing_manifest_fixdep_support")
    else:
        for entry in FIXDEP_SUPPORT_REQUIRED:
            if entry not in fixdep_support:
                issues.append(f"missing_manifest_fixdep_support_entry:{entry}")

    make_wrappers = present_surfaces.get("make_wrappers")
    if not isinstance(make_wrappers, list):
        issues.append("missing_manifest_make_wrappers")
    elif MAKE_WRAPPER_REQUIRED not in make_wrappers:
        issues.append(f"missing_manifest_make_wrapper:{MAKE_WRAPPER_REQUIRED}")

    cases = json.loads(read_text(resolve(root, FIXDEP_CASES_REL)))
    if not isinstance(cases, list):
        issues.append("invalid_fixdep_cases_type")
    else:
        case_names = [case.get("name") for case in cases if isinstance(case, dict)]
        if case_names != list(FIXDEP_CASE_NAMES):
            issues.append(f"unexpected_fixdep_case_order:{case_names!r}")

    gate_text = read_text(resolve(root, FIXDEP_GATE_REL))
    for marker in FIXDEP_GATE_REQUIRED_MARKERS:
        if marker not in gate_text:
            issues.append(f"missing_fixdep_gate_marker:{marker}")

    diff_text = read_text(resolve(root, FIXDEP_DIFF_REL))
    for marker in FIXDEP_DIFF_REQUIRED_MARKERS:
        if marker not in diff_text:
            issues.append(f"missing_fixdep_diff_marker:{marker}")

    fixdep_zig_text = read_text(resolve(root, FIXDEP_ZIG_REL))
    for marker in FIXDEP_ZIG_REQUIRED_MARKERS:
        if marker not in fixdep_zig_text:
            issues.append(f"missing_fixdep_zig_marker:{marker}")

    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    for marker in MAKEFILE_REQUIRED_MARKERS:
        if marker not in makefile_text:
            issues.append(f"missing_makefile_marker:{marker}")

    return issues


def build_sample_root(root: Path) -> None:
    write_text(root / CLOSURE_REL, "\n".join(CLOSURE_REQUIRED_MARKERS) + "\n")
    write_json(
        root / MANIFEST_REL,
        {
            "phase": "Phase 2",
            "present_surfaces": {
                "fixdep_support": list(FIXDEP_SUPPORT_REQUIRED),
                "make_wrappers": [MAKE_WRAPPER_REQUIRED],
            },
        },
    )
    write_json(
        root / FIXDEP_CASES_REL,
        [
            {
                "name": name,
                "depfile": f"{name}.d",
                "target": f"{name}.o",
                "cmdline": f"clang -c {name}.c -o {name}.o",
                "expected": f"{name}.txt",
                "expected_exit_code": 0,
            }
            for name in FIXDEP_CASE_NAMES
        ],
    )
    write_text(root / FIXDEP_GATE_REL, "\n".join(FIXDEP_GATE_REQUIRED_MARKERS) + "\n")
    write_text(root / FIXDEP_DIFF_REL, "\n".join(FIXDEP_DIFF_REQUIRED_MARKERS) + "\n")
    write_text(root / FIXDEP_ZIG_REL, "\n".join(FIXDEP_ZIG_REQUIRED_MARKERS) + "\n")
    write_text(root / MAKEFILE_REL, "\n".join(MAKEFILE_REQUIRED_MARKERS) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_closure_fixdep_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        case_count += 1

        build_sample_root(root)
        write_text(root / CLOSURE_REL, "`scripts/zigux/check-phase2-fixdep-gate.py`\n")
        issues = collect_issues(root)
        assert any(issue.startswith("missing_closure_marker:") for issue in issues)
        case_count += 1

        build_sample_root(root)
        manifest = json.loads(read_text(root / MANIFEST_REL))
        manifest["present_surfaces"]["fixdep_support"] = manifest["present_surfaces"]["fixdep_support"][:-1]
        write_json(root / MANIFEST_REL, manifest)
        issues = collect_issues(root)
        assert f"missing_manifest_fixdep_support_entry:{FIXDEP_SUPPORT_REQUIRED[-1]}" in issues
        case_count += 1

        build_sample_root(root)
        cases = json.loads(read_text(root / FIXDEP_CASES_REL))
        write_json(root / FIXDEP_CASES_REL, cases[:-1])
        issues = collect_issues(root)
        assert any(issue.startswith("unexpected_fixdep_case_order:") for issue in issues)
        case_count += 1

        build_sample_root(root)
        write_text(root / MAKEFILE_REL, "phase2-fixdep:\n")
        issues = collect_issues(root)
        assert any(issue.startswith("missing_makefile_marker:") for issue in issues)
        case_count += 1

        build_sample_root(root)
        (root / FIXDEP_DIFF_REL).unlink()
        issues = collect_issues(root)
        assert f"missing_file:{FIXDEP_DIFF_REL.as_posix()}" in issues
        case_count += 1

    assert case_count == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CLOSURE_FIXDEP_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_FIXDEP_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 closure-side fixdep packet stays aligned with the live reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing repository-shaped root for focused replay coverage",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_CLOSURE_FIXDEP_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_CLOSURE_FIXDEP_PACKET=pass")
    print(f"PHASE2_CLOSURE_FIXDEP_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_CLOSURE_FIXDEP_PACKET_CLOSURE_MARKER_COUNT={len(CLOSURE_REQUIRED_MARKERS)}")
    print(f"PHASE2_CLOSURE_FIXDEP_PACKET_CASE_COUNT={len(FIXDEP_CASE_NAMES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
