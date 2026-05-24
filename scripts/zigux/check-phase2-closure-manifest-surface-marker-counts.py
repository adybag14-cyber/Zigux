#!/usr/bin/env python3
"""Fail closed when the closure manifest-surface coverage checker drifts."""

from __future__ import annotations

import argparse
import ast
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

COVERAGE_CHECKER_REL = Path("scripts/zigux/check-phase2-closure-manifest-surface-coverage.py")

EXPECTED_SURFACE_ANCHORS = {
    "artifact_support": (
        "scripts/zigux/artifact_diff.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    ),
    "cross_route_support": (
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    ),
    "fixdep_support": (
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/fixdep.zig",
        "zigux/tests/fixtures/fixdep/cases.json",
    ),
    "make_wrappers": (
        "zigux/Makefile",
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ),
    "policy": ("scripts/zigux/zig-toolchain-policy.json",),
}

EXPECTED_CONSTANT_NAMES = {
    "artifact_support": "EXPECTED_MANIFEST_ARTIFACT_SUPPORT",
    "cross_route_support": "EXPECTED_MANIFEST_CROSS_ROUTE_SUPPORT",
    "fixdep_support": "EXPECTED_MANIFEST_FIXDEP_SUPPORT",
    "make_wrappers": "EXPECTED_MANIFEST_MAKE_WRAPPERS",
    "policy": "EXPECTED_MANIFEST_POLICY",
}


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_dict_assignment(module: ast.Module, name: str) -> tuple[dict[str, object] | None, list[str]]:
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name:
                if not isinstance(node.value, ast.Dict):
                    return None, []
                duplicates: list[str] = []
                for key in node.value.keys:
                    if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                        continue
                    if key.value in duplicates:
                        continue
                    if sum(
                        1
                        for candidate in node.value.keys
                        if isinstance(candidate, ast.Constant) and candidate.value == key.value
                    ) > 1:
                        duplicates.append(key.value)
                value = ast.literal_eval(node.value)
                if not isinstance(value, dict):
                    return None, duplicates
                return value, duplicates
    return None, []


def require_exact_count(issues: list[tuple[str, str]], text: str, marker: str, count: int) -> None:
    actual = text.count(marker)
    if actual == count:
        return
    code = "MISSING_MARKER" if actual < count else "DUPLICATE_MARKER"
    issues.append((code, f"{marker}:expected={count}:actual={actual}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    checker_path = resolve(root, COVERAGE_CHECKER_REL)
    if not checker_path.exists():
        return [("MISSING_REQUIRED_FILE", COVERAGE_CHECKER_REL.as_posix())]

    checker_text = read_text(checker_path)
    try:
        module = ast.parse(checker_text, filename=str(checker_path))
    except SyntaxError as exc:
        return [("INVALID_PYTHON", f"{checker_path}:{exc.lineno}:{exc.msg}")]

    anchors_value, anchor_duplicates = parse_dict_assignment(module, "EXPECTED_SURFACE_ANCHORS")
    constants_value, constant_duplicates = parse_dict_assignment(module, "EXPECTED_CONSTANT_NAMES")

    for key in anchor_duplicates:
        issues.append(("DUPLICATE_SURFACE_KEY", f"EXPECTED_SURFACE_ANCHORS:{key}"))
    for key in constant_duplicates:
        issues.append(("DUPLICATE_SURFACE_KEY", f"EXPECTED_CONSTANT_NAMES:{key}"))

    if anchors_value is None:
        issues.append(("MISSING_ASSIGNMENT", "EXPECTED_SURFACE_ANCHORS"))
    elif anchors_value != EXPECTED_SURFACE_ANCHORS:
        issues.append(("SURFACE_ANCHOR_MISMATCH", "EXPECTED_SURFACE_ANCHORS"))

    if constants_value is None:
        issues.append(("MISSING_ASSIGNMENT", "EXPECTED_CONSTANT_NAMES"))
    elif constants_value != EXPECTED_CONSTANT_NAMES:
        issues.append(("SURFACE_CONSTANT_MISMATCH", "EXPECTED_CONSTANT_NAMES"))

    require_exact_count(
        issues,
        checker_text,
        "for surface_key in EXPECTED_SURFACE_ANCHORS:",
        1,
    )
    require_exact_count(
        issues,
        checker_text,
        "for surface_key, anchors in EXPECTED_SURFACE_ANCHORS.items():",
        1,
    )

    for surface_key, anchors in EXPECTED_SURFACE_ANCHORS.items():
        require_exact_count(
            issues,
            checker_text,
            f'require_manifest_list(issues, manifest, "{surface_key}")',
            1,
        )
        require_exact_count(
            issues,
            checker_text,
            f'expect_subset(issues, "{surface_key}"',
            1,
        )
        require_exact_count(
            issues,
            checker_text,
            f'ensure_validator_surface_coverage(issues, validator_text, "{surface_key}")',
            0,
        )
        require_exact_count(
            issues,
            checker_text,
            EXPECTED_CONSTANT_NAMES[surface_key],
            3,
        )
        for anchor in anchors:
            require_exact_count(issues, checker_text, f'"{anchor}"', 2)

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_MANIFEST_SURFACE_MARKER_COUNTS=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    content = """#!/usr/bin/env python3
EXPECTED_SURFACE_ANCHORS = {
    "artifact_support": (
        "scripts/zigux/artifact_diff.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    ),
    "cross_route_support": (
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    ),
    "fixdep_support": (
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/fixdep.zig",
        "zigux/tests/fixtures/fixdep/cases.json",
    ),
    "make_wrappers": (
        "zigux/Makefile",
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ),
    "policy": ("scripts/zigux/zig-toolchain-policy.json",),
}

EXPECTED_CONSTANT_NAMES = {
    "artifact_support": "EXPECTED_MANIFEST_ARTIFACT_SUPPORT",
    "cross_route_support": "EXPECTED_MANIFEST_CROSS_ROUTE_SUPPORT",
    "fixdep_support": "EXPECTED_MANIFEST_FIXDEP_SUPPORT",
    "make_wrappers": "EXPECTED_MANIFEST_MAKE_WRAPPERS",
    "policy": "EXPECTED_MANIFEST_POLICY",
}

EXPECTED_MANIFEST_ARTIFACT_SUPPORT = (
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
)
EXPECTED_MANIFEST_CROSS_ROUTE_SUPPORT = (
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)
EXPECTED_MANIFEST_FIXDEP_SUPPORT = (
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
)
EXPECTED_MANIFEST_MAKE_WRAPPERS = (
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)
EXPECTED_MANIFEST_POLICY = ("scripts/zigux/zig-toolchain-policy.json",)

def collect_issues(root):
    return []

for surface_key in EXPECTED_SURFACE_ANCHORS:
    pass
for surface_key, anchors in EXPECTED_SURFACE_ANCHORS.items():
    pass

expect_subset(issues, "artifact_support", require_manifest_list(issues, manifest, "artifact_support"), EXPECTED_MANIFEST_ARTIFACT_SUPPORT)
expect_subset(issues, "cross_route_support", require_manifest_list(issues, manifest, "cross_route_support"), EXPECTED_MANIFEST_CROSS_ROUTE_SUPPORT)
expect_subset(issues, "fixdep_support", require_manifest_list(issues, manifest, "fixdep_support"), EXPECTED_MANIFEST_FIXDEP_SUPPORT)
expect_subset(issues, "make_wrappers", require_manifest_list(issues, manifest, "make_wrappers"), EXPECTED_MANIFEST_MAKE_WRAPPERS)
expect_subset(issues, "policy", require_manifest_list(issues, manifest, "policy"), EXPECTED_MANIFEST_POLICY)
"""
    write_text(resolve(root, COVERAGE_CHECKER_REL), content)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_manifest_surface_marker_counts_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        checker_path = resolve(root, COVERAGE_CHECKER_REL)
        checker_path.write_text(
            read_text(checker_path).replace('"policy": ("scripts/zigux/zig-toolchain-policy.json",),', "", 1),
            encoding="utf-8",
        )
        assert ("SURFACE_ANCHOR_MISMATCH", "EXPECTED_SURFACE_ANCHORS") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        checker_path = resolve(root, COVERAGE_CHECKER_REL)
        checker_path.write_text(
            read_text(checker_path).replace(
                '"artifact_support": "EXPECTED_MANIFEST_ARTIFACT_SUPPORT",',
                '"artifact_support": "EXPECTED_MANIFEST_ARTIFACT_SUPPORT",\n    "artifact_support": "DRIFTED",',
                1,
            ),
            encoding="utf-8",
        )
        assert ("DUPLICATE_SURFACE_KEY", "EXPECTED_CONSTANT_NAMES:artifact_support") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        checker_path = resolve(root, COVERAGE_CHECKER_REL)
        checker_path.write_text(
            read_text(checker_path).replace(
                'expect_subset(issues, "fixdep_support"',
                'expect_subset(issues, "drifted_support"',
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_MARKER",
            'expect_subset(issues, "fixdep_support":expected=1:actual=0',
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        checker_path = resolve(root, COVERAGE_CHECKER_REL)
        checker_path.write_text(
            read_text(checker_path).replace(
                '"scripts/zigux/check-phase2-cross.py"',
                '"scripts/zigux/check-phase2-cross.py"\n    "scripts/zigux/check-phase2-cross.py"',
                1,
            ),
            encoding="utf-8",
        )
        assert any(code == "DUPLICATE_MARKER" and "scripts/zigux/check-phase2-cross.py" in value for code, value in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        resolve(root, COVERAGE_CHECKER_REL).unlink()
        assert ("MISSING_REQUIRED_FILE", COVERAGE_CHECKER_REL.as_posix()) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_MANIFEST_SURFACE_MARKER_COUNTS_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_MANIFEST_SURFACE_MARKER_COUNTS_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the closure manifest-surface coverage checker for duplicate or missing surface markers."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a focused sample root for local replay")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_CLOSURE_MANIFEST_SURFACE_MARKER_COUNTS_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_MANIFEST_SURFACE_MARKER_COUNTS=pass")
    print(f"PHASE2_CLOSURE_MANIFEST_SURFACE_MARKER_COUNTS_SURFACE_COUNT={len(EXPECTED_SURFACE_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
