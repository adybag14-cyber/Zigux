#!/usr/bin/env python3
"""Fail closed when the Phase 2 closure matrix stops covering live manifest surfaces."""

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
VALIDATOR_REL = Path("scripts/zigux/validate-phase2-closure.py")
MATRIX_REL = Path("scripts/zigux/check-phase2-closure-matrix.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")


def load_module(root: Path, rel: Path, name: str):
    path = root / rel
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as exc:
        raise SystemExit(f"unable to load module: {path}") from exc
    return module


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def require_str_tuple(module_name: str, attr_name: str, value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
        raise SystemExit(f"{module_name}.{attr_name} must stay tuple[str, ...]")
    return value


def require_path_tuple(module_name: str, attr_name: str, value: object) -> tuple[Path, ...]:
    if not isinstance(value, tuple) or not all(isinstance(item, Path) for item in value):
        raise SystemExit(f"{module_name}.{attr_name} must stay tuple[Path, ...]")
    return value


def build_validator_expectations(validator, matrix) -> dict[str, tuple[str, ...]]:
    raw = getattr(matrix, "VALIDATOR_MANIFEST_SURFACE_EXPECTATION_ATTRS", None)
    if not isinstance(raw, tuple):
        raise SystemExit("matrix.VALIDATOR_MANIFEST_SURFACE_EXPECTATION_ATTRS must stay a tuple")

    expectations: dict[str, tuple[str, ...]] = {}
    for pair in raw:
        if (
            not isinstance(pair, tuple)
            or len(pair) != 2
            or not isinstance(pair[0], str)
            or not isinstance(pair[1], str)
        ):
            raise SystemExit(
                "matrix.VALIDATOR_MANIFEST_SURFACE_EXPECTATION_ATTRS must stay tuple[tuple[str, str], ...]"
            )
        key, attr = pair
        expectations[key] = require_str_tuple("validator", attr, getattr(validator, attr, None))
    return expectations


def build_direct_expectations(matrix) -> dict[str, tuple[str, ...]]:
    raw = getattr(matrix, "DIRECT_MANIFEST_SURFACE_EXPECTATIONS", None)
    if not isinstance(raw, dict):
        raise SystemExit("matrix.DIRECT_MANIFEST_SURFACE_EXPECTATIONS must stay dict[str, tuple[str, ...]]")

    expectations: dict[str, tuple[str, ...]] = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            raise SystemExit("matrix.DIRECT_MANIFEST_SURFACE_EXPECTATIONS keys must stay strings")
        expectations[key] = require_str_tuple("matrix", f"DIRECT_MANIFEST_SURFACE_EXPECTATIONS[{key!r}]", value)
    return expectations


def build_surface_map(root: Path) -> dict[str, list[str]]:
    payload = load_json(root / MANIFEST_REL)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid manifest root shape: {root / MANIFEST_REL}")

    surfaces = payload.get("present_surfaces")
    if not isinstance(surfaces, dict):
        raise SystemExit(f"invalid manifest present_surfaces shape: {root / MANIFEST_REL}")

    normalized: dict[str, list[str]] = {}
    for key, value in surfaces.items():
        if not isinstance(key, str):
            raise SystemExit(f"invalid manifest surface key type: {root / MANIFEST_REL}")
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise SystemExit(f"invalid manifest surface list shape for {key}: {root / MANIFEST_REL}")
        normalized[key] = list(value)
    return normalized


def collect_issues(root: Path) -> list[tuple[str, str]]:
    validator = load_module(root, VALIDATOR_REL, "zigux_validate_phase2_closure")
    matrix = load_module(root, MATRIX_REL, "zigux_check_phase2_closure_matrix")
    validator_expectations = build_validator_expectations(validator, matrix)
    direct_expectations = build_direct_expectations(matrix)
    surfaces = build_surface_map(root)

    issues: list[tuple[str, str]] = []
    covered_keys = set(validator_expectations) | set(direct_expectations)

    for key in sorted(surfaces):
        if key not in covered_keys:
            issues.append(("UNCOVERED_MANIFEST_SURFACE_KEY", key))

    for key in sorted(covered_keys):
        actual = surfaces.get(key)
        if actual is None:
            issues.append(("MISSING_MANIFEST_SURFACE_KEY", key))
            continue

        validator_items = validator_expectations.get(key, ())
        direct_items = direct_expectations.get(key, ())
        covered_items = set(validator_items) | set(direct_items)
        actual_items = set(actual)

        for item in sorted(covered_items - actual_items):
            issues.append(("MISSING_MATRIX_COVERED_ITEM", f"{key}:{item}"))
        for item in sorted(actual_items - covered_items):
            issues.append(("UNCOVERED_MANIFEST_ITEM", f"{key}:{item}"))

    validator_required = {
        path.as_posix()
        for path in require_path_tuple("validator", "REQUIRED_FILES", getattr(validator, "REQUIRED_FILES", None))
    }
    extra_required = {
        path.as_posix()
        for path in require_path_tuple("matrix", "EXTRA_REQUIRED_FILES", getattr(matrix, "EXTRA_REQUIRED_FILES", None))
    }
    manifest_items = {item for values in surfaces.values() for item in values if "/" in item and not item.startswith("make -C ")}

    for item in sorted(extra_required & validator_required):
        issues.append(("REDUNDANT_EXTRA_REQUIRED_FILE", item))
    for item in sorted(extra_required - manifest_items):
        issues.append(("EXTRA_REQUIRED_FILE_NOT_IN_MANIFEST", item))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_MATRIX_COVERAGE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def build_self_test_root(root: Path) -> None:
    validator_source = """\
from pathlib import Path

EXPECTED_MANIFEST_REVIEW_SURFACES = ("review.md",)
EXPECTED_MANIFEST_CLOSURE_NOTES = ("closure-note.md",)
EXPECTED_MANIFEST_VALIDATORS = ("scripts/zigux/validate-phase2.py",)
EXPECTED_MANIFEST_CHECKERS = ("check-base.py",)
EXPECTED_MANIFEST_BRIDGE_HELPERS = ("bridge-a.zig",)
EXPECTED_MANIFEST_FIXTURE_ROSTER = ("fixture-a.json",)
REQUIRED_FILES = (
    Path("Documentation/zigux/phase2-closure.md"),
    Path("scripts/zigux/validate-phase2-closure.py"),
    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),
)
"""
    matrix_source = """\
from pathlib import Path

VALIDATOR_MANIFEST_SURFACE_EXPECTATION_ATTRS = (
    ("review_surfaces", "EXPECTED_MANIFEST_REVIEW_SURFACES"),
    ("closure_notes", "EXPECTED_MANIFEST_CLOSURE_NOTES"),
    ("validators", "EXPECTED_MANIFEST_VALIDATORS"),
    ("checkers", "EXPECTED_MANIFEST_CHECKERS"),
    ("bridge_helpers", "EXPECTED_MANIFEST_BRIDGE_HELPERS"),
    ("fixture_roster", "EXPECTED_MANIFEST_FIXTURE_ROSTER"),
)
DIRECT_MANIFEST_SURFACE_EXPECTATIONS = {
    "bootstrap_helpers": (
        "scripts/zigux/install-zig.py",
        "scripts/zigux/stage-pinned-zig-archive.py",
    ),
    "checkers": (
        "scripts/zigux/check-extra.py",
    ),
    "policy": (
        "policy-a.json",
    ),
}
EXTRA_REQUIRED_FILES = (
    Path("scripts/zigux/stage-pinned-zig-archive.py"),
    Path("scripts/zigux/check-extra.py"),
)
"""
    manifest = {
        "present_surfaces": {
            "review_surfaces": ["review.md"],
            "closure_notes": ["closure-note.md"],
            "validators": ["scripts/zigux/validate-phase2.py"],
            "checkers": ["check-base.py", "scripts/zigux/check-extra.py"],
            "bridge_helpers": ["bridge-a.zig"],
            "fixture_roster": ["fixture-a.json"],
            "policy": ["policy-a.json"],
            "bootstrap_helpers": [
                "scripts/zigux/install-zig.py",
                "scripts/zigux/stage-pinned-zig-archive.py",
            ],
        }
    }

    write_text(root / VALIDATOR_REL, validator_source)
    write_text(root / MATRIX_REL, matrix_source)
    write_json(root / MANIFEST_REL, manifest)
    write_text(root / "scripts/zigux/stage-pinned-zig-archive.py", "present\n")
    write_text(root / "scripts/zigux/check-extra.py", "present\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_matrix_coverage_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        manifest_path = root / MANIFEST_REL
        validator_path = root / VALIDATOR_REL
        matrix_path = root / MATRIX_REL

        payload = load_json(manifest_path)
        payload["present_surfaces"]["unexpected_bucket"] = ["unexpected.txt"]
        write_json(manifest_path, payload)
        assert ("UNCOVERED_MANIFEST_SURFACE_KEY", "unexpected_bucket") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        del payload["present_surfaces"]["closure_notes"]
        write_json(manifest_path, payload)
        assert ("MISSING_MANIFEST_SURFACE_KEY", "closure_notes") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        del payload["present_surfaces"]["validators"]
        write_json(manifest_path, payload)
        assert ("MISSING_MANIFEST_SURFACE_KEY", "validators") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        payload["present_surfaces"]["bootstrap_helpers"].append("scripts/zigux/new-helper.py")
        write_json(manifest_path, payload)
        assert ("UNCOVERED_MANIFEST_ITEM", "bootstrap_helpers:scripts/zigux/new-helper.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        payload["present_surfaces"]["closure_notes"].remove("closure-note.md")
        write_json(manifest_path, payload)
        assert ("MISSING_MATRIX_COVERED_ITEM", "closure_notes:closure-note.md") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        payload["present_surfaces"]["validators"].remove("scripts/zigux/validate-phase2.py")
        write_json(manifest_path, payload)
        assert ("MISSING_MATRIX_COVERED_ITEM", "validators:scripts/zigux/validate-phase2.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        payload["present_surfaces"]["checkers"].remove("scripts/zigux/check-extra.py")
        write_json(manifest_path, payload)
        assert ("MISSING_MATRIX_COVERED_ITEM", "checkers:scripts/zigux/check-extra.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        payload["present_surfaces"]["bootstrap_helpers"].remove("scripts/zigux/stage-pinned-zig-archive.py")
        write_json(manifest_path, payload)
        assert (
            "MISSING_MATRIX_COVERED_ITEM",
            "bootstrap_helpers:scripts/zigux/stage-pinned-zig-archive.py",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        payload["present_surfaces"]["policy"].remove("policy-a.json")
        write_json(manifest_path, payload)
        assert ("MISSING_MATRIX_COVERED_ITEM", "policy:policy-a.json") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_json(manifest_path, [])
        assert_system_exit_contains(
            lambda: collect_issues(root),
            f"invalid manifest root shape: {manifest_path}",
        )
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        payload["present_surfaces"] = []
        write_json(manifest_path, payload)
        assert_system_exit_contains(
            lambda: collect_issues(root),
            f"invalid manifest present_surfaces shape: {manifest_path}",
        )
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        payload["present_surfaces"]["policy"] = "drifted"
        write_json(manifest_path, payload)
        assert_system_exit_contains(
            lambda: collect_issues(root),
            f"invalid manifest surface list shape for policy: {manifest_path}",
        )
        checks_run += 1

        build_self_test_root(root)
        payload = load_json(manifest_path)
        payload["present_surfaces"]["policy"].append(7)
        write_json(manifest_path, payload)
        assert_system_exit_contains(
            lambda: collect_issues(root),
            f"invalid manifest surface list shape for policy: {manifest_path}",
        )
        checks_run += 1

        build_self_test_root(root)
        manifest_path.write_text("{\n", encoding="utf-8")
        assert_system_exit_contains(
            lambda: collect_issues(root),
            f"invalid json in required file: {manifest_path}:",
        )
        checks_run += 1

        build_self_test_root(root)
        validator_text = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            validator_text.replace(
                'EXPECTED_MANIFEST_FIXTURE_ROSTER = ("fixture-a.json",)\n',
                'EXPECTED_MANIFEST_FIXTURE_ROSTER = ["fixture-a.json"]\n',
                1,
            ),
            encoding="utf-8",
        )
        assert_system_exit_contains(
            lambda: collect_issues(root),
            "validator.EXPECTED_MANIFEST_FIXTURE_ROSTER must stay tuple[str, ...]",
        )
        checks_run += 1

        build_self_test_root(root)
        validator_text = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            validator_text.replace(
                'EXPECTED_MANIFEST_FIXTURE_ROSTER = ("fixture-a.json",)\n',
                'EXPECTED_MANIFEST_FIXTURE_ROSTER = ("fixture-a.json", 7)\n',
                1,
            ),
            encoding="utf-8",
        )
        assert_system_exit_contains(
            lambda: collect_issues(root),
            "validator.EXPECTED_MANIFEST_FIXTURE_ROSTER must stay tuple[str, ...]",
        )
        checks_run += 1

        build_self_test_root(root)
        validator_text = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            validator_text.replace(
                'REQUIRED_FILES = (\n'
                '    Path("Documentation/zigux/phase2-closure.md"),\n'
                '    Path("scripts/zigux/validate-phase2-closure.py"),\n'
                '    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),\n'
                ')\n',
                'REQUIRED_FILES = ["Documentation/zigux/phase2-closure.md"]\n',
                1,
            ),
            encoding="utf-8",
        )
        assert_system_exit_contains(
            lambda: collect_issues(root),
            "validator.REQUIRED_FILES must stay tuple[Path, ...]",
        )
        checks_run += 1

        build_self_test_root(root)
        matrix_text = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            matrix_text.replace(
                "VALIDATOR_MANIFEST_SURFACE_EXPECTATION_ATTRS = (\n"
                '    ("review_surfaces", "EXPECTED_MANIFEST_REVIEW_SURFACES"),\n'
                '    ("closure_notes", "EXPECTED_MANIFEST_CLOSURE_NOTES"),\n'
                '    ("validators", "EXPECTED_MANIFEST_VALIDATORS"),\n'
                '    ("checkers", "EXPECTED_MANIFEST_CHECKERS"),\n'
                '    ("bridge_helpers", "EXPECTED_MANIFEST_BRIDGE_HELPERS"),\n'
                '    ("fixture_roster", "EXPECTED_MANIFEST_FIXTURE_ROSTER"),\n'
                ")\n",
                'VALIDATOR_MANIFEST_SURFACE_EXPECTATION_ATTRS = "drifted"\n',
                1,
            ),
            encoding="utf-8",
        )
        assert_system_exit_contains(
            lambda: collect_issues(root),
            "matrix.VALIDATOR_MANIFEST_SURFACE_EXPECTATION_ATTRS must stay a tuple",
        )
        checks_run += 1

        build_self_test_root(root)
        matrix_text = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            matrix_text.replace(
                '    ("fixture_roster", "EXPECTED_MANIFEST_FIXTURE_ROSTER"),\n',
                '    "fixture_roster",\n',
                1,
            ),
            encoding="utf-8",
        )
        assert_system_exit_contains(
            lambda: collect_issues(root),
            "matrix.VALIDATOR_MANIFEST_SURFACE_EXPECTATION_ATTRS must stay tuple[tuple[str, str], ...]",
        )
        checks_run += 1

        build_self_test_root(root)
        matrix_text = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            matrix_text.replace(
                "DIRECT_MANIFEST_SURFACE_EXPECTATIONS = {\n"
                '    "bootstrap_helpers": (\n'
                '        "scripts/zigux/install-zig.py",\n'
                '        "scripts/zigux/stage-pinned-zig-archive.py",\n'
                "    ),\n"
                '    "checkers": (\n'
                '        "scripts/zigux/check-extra.py",\n'
                "    ),\n"
                '    "policy": (\n'
                '        "policy-a.json",\n'
                "    ),\n"
                "}\n",
                'DIRECT_MANIFEST_SURFACE_EXPECTATIONS = "drifted"\n',
                1,
            ),
            encoding="utf-8",
        )
        assert_system_exit_contains(
            lambda: collect_issues(root),
            "matrix.DIRECT_MANIFEST_SURFACE_EXPECTATIONS must stay dict[str, tuple[str, ...]]",
        )
        checks_run += 1

        build_self_test_root(root)
        matrix_text = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            matrix_text.replace(
                '    "policy": (\n'
                '        "policy-a.json",\n'
                "    ),\n",
                "    7: (\n"
                '        "policy-a.json",\n'
                "    ),\n",
                1,
            ),
            encoding="utf-8",
        )
        assert_system_exit_contains(
            lambda: collect_issues(root),
            "matrix.DIRECT_MANIFEST_SURFACE_EXPECTATIONS keys must stay strings",
        )
        checks_run += 1

        build_self_test_root(root)
        matrix_text = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            matrix_text.replace(
                '    "policy": (\n'
                '        "policy-a.json",\n'
                "    ),\n",
                '    "policy": [\n'
                '        "policy-a.json",\n'
                "    ],\n",
                1,
            ),
            encoding="utf-8",
        )
        assert_system_exit_contains(
            lambda: collect_issues(root),
            "matrix.DIRECT_MANIFEST_SURFACE_EXPECTATIONS['policy'] must stay tuple[str, ...]",
        )
        checks_run += 1

        build_self_test_root(root)
        matrix_text = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            matrix_text.replace(
                '    "policy": (\n'
                '        "policy-a.json",\n'
                "    ),\n",
                '    "policy": (\n'
                '        "policy-a.json",\n'
                "        7,\n"
                "    ),\n",
                1,
            ),
            encoding="utf-8",
        )
        assert_system_exit_contains(
            lambda: collect_issues(root),
            "matrix.DIRECT_MANIFEST_SURFACE_EXPECTATIONS['policy'] must stay tuple[str, ...]",
        )
        checks_run += 1

        build_self_test_root(root)
        matrix_text = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            matrix_text.replace(
                '    Path("scripts/zigux/check-extra.py"),\n',
                '    "scripts/zigux/check-extra.py",\n',
                1,
            ),
            encoding="utf-8",
        )
        assert_system_exit_contains(
            lambda: collect_issues(root),
            "matrix.EXTRA_REQUIRED_FILES must stay tuple[Path, ...]",
        )
        checks_run += 1

        build_self_test_root(root)
        matrix_text = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            matrix_text.replace(
                '    Path("scripts/zigux/check-extra.py"),\n',
                '    Path("scripts/zigux/check-extra.py"),\n    Path("scripts/zigux/not-in-manifest.py"),\n',
                1,
            ),
            encoding="utf-8",
        )
        assert ("EXTRA_REQUIRED_FILE_NOT_IN_MANIFEST", "scripts/zigux/not-in-manifest.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        matrix_text = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            matrix_text.replace(
                '    Path("scripts/zigux/check-extra.py"),\n',
                '    Path("scripts/zigux/check-extra.py"),\n    Path("scripts/zigux/validate-phase2-closure.py"),\n',
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "REDUNDANT_EXTRA_REQUIRED_FILE",
            "scripts/zigux/validate-phase2-closure.py",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / VALIDATOR_REL).unlink()
        assert_system_exit_contains(
            lambda: collect_issues(root),
            f"unable to load module: {root / VALIDATOR_REL}",
        )
        checks_run += 1

        build_self_test_root(root)
        (root / MATRIX_REL).unlink()
        assert_system_exit_contains(
            lambda: collect_issues(root),
            f"unable to load module: {root / MATRIX_REL}",
        )
        checks_run += 1

    print("PHASE2_CLOSURE_MATRIX_COVERAGE_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_MATRIX_COVERAGE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def assert_system_exit_contains(action, expected_substring: str) -> None:
    try:
        action()
    except SystemExit as exc:
        if expected_substring not in str(exc):
            raise AssertionError(
                f"expected SystemExit containing {expected_substring!r}; saw {exc!r}"
            ) from exc
        return
    raise AssertionError(f"expected SystemExit containing {expected_substring!r}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the current Phase 2 tool manifest outgrows the closure-matrix coverage set."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_MATRIX_COVERAGE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
