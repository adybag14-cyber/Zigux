#!/usr/bin/env python3
"""Fail closed when the shared Phase 2 validator leaves manifest surfaces implicit."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

VALIDATOR_REL = Path("scripts/zigux/validate-phase2.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

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


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def require_manifest_list(issues: list[tuple[str, str]], manifest: dict[str, object], key: str) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)


def ensure_validator_surface_coverage(issues: list[tuple[str, str]], validator_text: str, surface_key: str) -> None:
    constant_name = EXPECTED_CONSTANT_NAMES[surface_key]
    required_snippets = (
        constant_name,
        f'require_manifest_list(issues, manifest, "{surface_key}")',
        f'expect_subset(issues, "{surface_key}"',
    )
    for snippet in required_snippets:
        if snippet not in validator_text:
            issues.append(("MISSING_VALIDATOR_MARKER", f"{surface_key}:{snippet}"))
    for anchor in EXPECTED_SURFACE_ANCHORS[surface_key]:
        if anchor not in validator_text:
            issues.append(("MISSING_VALIDATOR_MARKER", f"{surface_key}:{anchor}"))


def ensure_manifest_surface_anchors(
    issues: list[tuple[str, str]], manifest: dict[str, object], surface_key: str
) -> None:
    values = require_manifest_list(issues, manifest, surface_key)
    if values is None:
        return
    for anchor in EXPECTED_SURFACE_ANCHORS[surface_key]:
        if anchor not in values:
            issues.append(("MISSING_MANIFEST_SURFACE", f"{surface_key}:{anchor}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in (VALIDATOR_REL, MANIFEST_REL):
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    validator_text = read_text(resolve(root, VALIDATOR_REL))
    manifest = read_json(resolve(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    for surface_key in EXPECTED_SURFACE_ANCHORS:
        ensure_validator_surface_coverage(issues, validator_text, surface_key)
        ensure_manifest_surface_anchors(issues, manifest, surface_key)

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_VALIDATOR_MANIFEST_SURFACE_COVERAGE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    validator_text = """\
EXPECTED_MANIFEST_ARTIFACT_SUPPORT = (
    \"scripts/zigux/artifact_diff.py\",
    \"scripts/zigux/check-phase2-artifact-tools-manifest.py\",
    \"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\",
)
EXPECTED_MANIFEST_CROSS_ROUTE_SUPPORT = (
    \"scripts/zigux/check-phase2-cross.py\",
    \"zigux/tests/fixtures/phase2_cross_targets.json\",
)
EXPECTED_MANIFEST_FIXDEP_SUPPORT = (
    \"scripts/zigux/check-phase2-fixdep-gate.py\",
    \"scripts/zigux/check-fixdep-diff.py\",
    \"scripts/zigux/fixdep.zig\",
    \"zigux/tests/fixtures/fixdep/cases.json\",
)
EXPECTED_MANIFEST_MAKE_WRAPPERS = (
    \"zigux/Makefile\",
    \"make -C zigux phase2-toolchain\",
    \"make -C zigux phase2-tools\",
    \"make -C zigux phase2-kconfig\",
    \"make -C zigux phase2-cross\",
    \"make -C zigux phase2-genksyms\",
    \"make -C zigux phase2-fixdep\",
    \"make -C zigux phase2-validate\",
    \"make -C zigux phase2\",
)
EXPECTED_MANIFEST_POLICY = (
    \"scripts/zigux/zig-toolchain-policy.json\",
)
expect_subset(issues, \"artifact_support\", require_manifest_list(issues, manifest, \"artifact_support\"), EXPECTED_MANIFEST_ARTIFACT_SUPPORT)
expect_subset(issues, \"cross_route_support\", require_manifest_list(issues, manifest, \"cross_route_support\"), EXPECTED_MANIFEST_CROSS_ROUTE_SUPPORT)
expect_subset(issues, \"fixdep_support\", require_manifest_list(issues, manifest, \"fixdep_support\"), EXPECTED_MANIFEST_FIXDEP_SUPPORT)
expect_subset(issues, \"make_wrappers\", require_manifest_list(issues, manifest, \"make_wrappers\"), EXPECTED_MANIFEST_MAKE_WRAPPERS)
expect_subset(issues, \"policy\", require_manifest_list(issues, manifest, \"policy\"), EXPECTED_MANIFEST_POLICY)
"""
    manifest = {
        "phase": "Phase 2",
        "present_surfaces": {key: list(values) for key, values in EXPECTED_SURFACE_ANCHORS.items()},
    }
    write_text(resolve(root, VALIDATOR_REL), validator_text)
    write_text(resolve(root, MANIFEST_REL), json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    expected_case_count = 1 + len(EXPECTED_SURFACE_ANCHORS) + len(EXPECTED_SURFACE_ANCHORS) + 3 + 2
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validator_manifest_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for surface_key in EXPECTED_SURFACE_ANCHORS:
            build_sample_root(root)
            validator_path = resolve(root, VALIDATOR_REL)
            validator_text = read_text(validator_path)
            snippet = f'expect_subset(issues, "{surface_key}"'
            validator_path.write_text(
                validator_text.replace(snippet, 'expect_subset(issues, "drifted"', 1),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_VALIDATOR_MARKER", f"{surface_key}:{snippet}") in issues, issues
            checks += 1

        for surface_key, anchors in EXPECTED_SURFACE_ANCHORS.items():
            build_sample_root(root)
            manifest_path = resolve(root, MANIFEST_REL)
            manifest = json.loads(read_text(manifest_path))
            manifest["present_surfaces"][surface_key].remove(anchors[0])
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MANIFEST_SURFACE", f"{surface_key}:{anchors[0]}") in issues, issues
            checks += 1

        build_sample_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        manifest_path.write_text("[]\n", encoding="utf-8")
        assert ("INVALID_MANIFEST_SHAPE", "root") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        manifest = json.loads(read_text(manifest_path))
        manifest["present_surfaces"] = []
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_MANIFEST_SHAPE", "present_surfaces") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        manifest = json.loads(read_text(manifest_path))
        manifest["present_surfaces"]["policy"] = [123]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_MANIFEST_SHAPE", "policy") in collect_issues(root)
        checks += 1

        for rel in (VALIDATOR_REL, MANIFEST_REL):
            build_sample_root(root)
            resolve(root, rel).unlink()
            issues = collect_issues(root)
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in issues, issues
            checks += 1

    assert checks == expected_case_count
    print("PHASE2_VALIDATOR_MANIFEST_SURFACE_COVERAGE_SELF_TEST=pass")
    print(f"PHASE2_VALIDATOR_MANIFEST_SURFACE_COVERAGE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that scripts/zigux/validate-phase2.py explicitly covers the extra present_surfaces groups already shipped in the Phase 2 tool manifest."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a focused sample root for local replay")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_VALIDATOR_MANIFEST_SURFACE_COVERAGE_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_VALIDATOR_MANIFEST_SURFACE_COVERAGE=pass")
    print(f"PHASE2_VALIDATOR_MANIFEST_SURFACE_COVERAGE_SURFACE_COUNT={len(EXPECTED_SURFACE_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
