#!/usr/bin/env python3
"""Validate the shipped Phase 2 validator packet stays aligned."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_FILES = (
    VALIDATE_REL,
    CLOSURE_VALIDATE_REL,
    MAKEFILE_REL,
    MANIFEST_REL,
)

VALIDATE_PATH_MARKERS = (
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
)

VALIDATE_WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/validate-phase2.py",
)

VALIDATE_MAKEFILE_MARKERS = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

CLOSURE_FILE_MARKERS = (
    'Path("scripts/zigux/validate-phase2.py")',
    'Path("scripts/zigux/validate-phase2-closure.py")',
    'Path("zigux/Makefile")',
    'Path("zigux/tests/fixtures/phase2_tool_manifest.json")',
)

CLOSURE_VALIDATOR_MARKERS = (
    '"scripts/zigux/validate-phase2.py"',
    '"scripts/zigux/validate-phase2-closure.py"',
)

MANIFEST_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

MANIFEST_MAKE_WRAPPERS = (
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)


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


def add_missing_markers(issues: list[tuple[str, str]], code: str, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append((code, marker))


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


def expect_markers_in_list(
    issues: list[tuple[str, str]],
    code: str,
    label: str,
    actual: list[str] | None,
    expected: tuple[str, ...],
) -> None:
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append((code, f"{label}:{marker}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    validate_text = read_text(resolve(root, VALIDATE_REL))
    closure_text = read_text(resolve(root, CLOSURE_VALIDATE_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    manifest = read_json(resolve(root, MANIFEST_REL))

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    add_missing_markers(issues, "MISSING_VALIDATE_PATH_MARKER", validate_text, VALIDATE_PATH_MARKERS)
    add_missing_markers(issues, "MISSING_VALIDATE_WORKFLOW_MARKER", validate_text, VALIDATE_WORKFLOW_MARKERS)
    add_missing_markers(issues, "MISSING_VALIDATE_MAKEFILE_MARKER", validate_text, VALIDATE_MAKEFILE_MARKERS)
    add_missing_markers(issues, "MISSING_CLOSURE_FILE_MARKER", closure_text, CLOSURE_FILE_MARKERS)
    add_missing_markers(issues, "MISSING_CLOSURE_VALIDATOR_MARKER", closure_text, CLOSURE_VALIDATOR_MARKERS)
    add_missing_markers(issues, "MISSING_MAKEFILE_MARKER", makefile_text, VALIDATE_MAKEFILE_MARKERS)

    expect_markers_in_list(
        issues,
        "MISSING_MANIFEST_SURFACE",
        "validators",
        require_manifest_list(issues, manifest, "validators"),
        MANIFEST_VALIDATORS,
    )
    expect_markers_in_list(
        issues,
        "MISSING_MANIFEST_SURFACE",
        "make_wrappers",
        require_manifest_list(issues, manifest, "make_wrappers"),
        MANIFEST_MAKE_WRAPPERS,
    )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_VALIDATE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        resolve(root, VALIDATE_REL),
        """#!/usr/bin/env python3
REQUIRED_PATHS = (
    \"scripts/zigux/validate-phase2-closure.py\",
    \"zigux/Makefile\",
    \"zigux/tests/fixtures/phase2_tool_manifest.json\",
)
REQUIRED_WORKFLOW_LINES = (
    \"run: python3 scripts/zigux/validate-phase2.py\",
)
REQUIRED_MAKEFILE_LINES = (
    \"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep\",
    \"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py\",
    \"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py\",
    \"phase2: phase2-validate\",
)
""",
    )
    write_text(
        resolve(root, CLOSURE_VALIDATE_REL),
        """#!/usr/bin/env python3
REQUIRED_FILES = (
    Path(\"scripts/zigux/validate-phase2.py\"),
    Path(\"scripts/zigux/validate-phase2-closure.py\"),
    Path(\"zigux/Makefile\"),
    Path(\"zigux/tests/fixtures/phase2_tool_manifest.json\"),
)
EXPECTED_MANIFEST_VALIDATORS = (
    \"scripts/zigux/validate-phase2.py\",
    \"scripts/zigux/validate-phase2-closure.py\",
)
""",
    )
    write_text(
        resolve(root, MAKEFILE_REL),
        """phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py
phase2: phase2-validate
""",
    )
    write_text(
        resolve(root, MANIFEST_REL),
        json.dumps(
            {
                "present_surfaces": {
                    "validators": list(MANIFEST_VALIDATORS),
                    "make_wrappers": list(MANIFEST_MAKE_WRAPPERS),
                }
            },
            indent=2,
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validate_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        validate_path = resolve(root, VALIDATE_REL)
        validate_path.write_text(
            replace_once(validate_path.read_text(encoding="utf-8"), '\"zigux/tests/fixtures/phase2_tool_manifest.json\"'),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATE_PATH_MARKER", "zigux/tests/fixtures/phase2_tool_manifest.json") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        validate_path = resolve(root, VALIDATE_REL)
        validate_path.write_text(
            replace_once(validate_path.read_text(encoding="utf-8"), '\"run: python3 scripts/zigux/validate-phase2.py\"'),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATE_WORKFLOW_MARKER", "run: python3 scripts/zigux/validate-phase2.py") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        makefile_path = resolve(root, MAKEFILE_REL)
        makefile_path.write_text(
            replace_once(makefile_path.read_text(encoding="utf-8"), "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py"),
            encoding="utf-8",
        )
        assert (
            "MISSING_MAKEFILE_MARKER",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        closure_path = resolve(root, CLOSURE_VALIDATE_REL)
        closure_path.write_text(
            replace_once(closure_path.read_text(encoding="utf-8"), 'Path(\"zigux/tests/fixtures/phase2_tool_manifest.json\")'),
            encoding="utf-8",
        )
        assert (
            "MISSING_CLOSURE_FILE_MARKER",
            'Path("zigux/tests/fixtures/phase2_tool_manifest.json")',
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["validators"].remove("scripts/zigux/validate-phase2-closure.py")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_MANIFEST_SURFACE",
            "validators:scripts/zigux/validate-phase2-closure.py",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["make_wrappers"].remove("make -C zigux phase2-validate")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_MANIFEST_SURFACE",
            "make_wrappers:make -C zigux phase2-validate",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        resolve(root, MANIFEST_REL).unlink()
        assert ("MISSING_REQUIRED_FILE", MANIFEST_REL.as_posix()) in collect_issues(root)
        checks_run += 1

    print("PHASE2_VALIDATE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_VALIDATE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 2 validator packet stays aligned.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_VALIDATE_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_VALIDATE_PACKET=pass")
    print(f"PHASE2_VALIDATE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_VALIDATE_PACKET_VALIDATOR_COUNT={len(MANIFEST_VALIDATORS)}")
    print(f"PHASE2_VALIDATE_PACKET_MAKE_WRAPPER_COUNT={len(MANIFEST_MAKE_WRAPPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
