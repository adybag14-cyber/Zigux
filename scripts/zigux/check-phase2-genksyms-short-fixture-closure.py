#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
PHASE2_TOOL_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
PHASE2_CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase2-closure.py")

SHORT_FIXTURE_REL = Path(
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json"
)
SHORT_FIXTURE_MARKER = f"`{SHORT_FIXTURE_REL.as_posix()}`"
VALIDATOR_PATH_LINE = f'SHORT_FIXTURE_REL = Path("{SHORT_FIXTURE_REL.as_posix()}")'
VALIDATOR_MARKER_LINE = f'SHORT_FIXTURE_MARKER = "{SHORT_FIXTURE_MARKER}"'


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    closure_text = read_text(resolve(root, PHASE2_CLOSURE_REL))
    if SHORT_FIXTURE_MARKER not in closure_text:
        issues.append(("MISSING_CLOSURE_MARKER", SHORT_FIXTURE_MARKER))

    manifest = read_json(resolve(root, PHASE2_TOOL_MANIFEST_REL))
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return issues

    fixture_roster = present_surfaces.get("fixture_roster")
    if not isinstance(fixture_roster, list) or not all(
        isinstance(entry, str) for entry in fixture_roster
    ):
        issues.append(("INVALID_MANIFEST_SHAPE", "fixture_roster"))
        return issues

    short_fixture_path = SHORT_FIXTURE_REL.as_posix()
    count = fixture_roster.count(short_fixture_path)
    if count == 0:
        issues.append(("MISSING_MANIFEST_FIXTURE", short_fixture_path))
    elif count != 1:
        issues.append(("DUPLICATE_MANIFEST_FIXTURE", f"{short_fixture_path}:count={count}"))

    validator_text = read_text(resolve(root, PHASE2_CLOSURE_VALIDATOR_REL))
    path_line_count = sum(
        1 for line in validator_text.splitlines() if line.strip() == VALIDATOR_PATH_LINE
    )
    marker_line_count = sum(
        1 for line in validator_text.splitlines() if line.strip() == VALIDATOR_MARKER_LINE
    )
    if path_line_count == 0:
        issues.append(("MISSING_VALIDATOR_PATH_REFERENCE", VALIDATOR_PATH_LINE))
    elif path_line_count != 1:
        issues.append(
            (
                "DUPLICATE_VALIDATOR_PATH_REFERENCE",
                f"{VALIDATOR_PATH_LINE}:count={path_line_count}",
            )
        )
    if marker_line_count == 0:
        issues.append(("MISSING_VALIDATOR_CLOSURE_MARKER", VALIDATOR_MARKER_LINE))
    elif marker_line_count != 1:
        issues.append(
            (
                "DUPLICATE_VALIDATOR_CLOSURE_MARKER",
                f"{VALIDATOR_MARKER_LINE}:count={marker_line_count}",
            )
        )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_GENKSYMS_SHORT_FIXTURE_CLOSURE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    short_fixture_path = SHORT_FIXTURE_REL.as_posix()
    write_text(resolve(root, PHASE2_CLOSURE_REL), f"- {SHORT_FIXTURE_MARKER}\n")
    write_text(
        resolve(root, PHASE2_TOOL_MANIFEST_REL),
        json.dumps(
            {"present_surfaces": {"fixture_roster": [short_fixture_path]}},
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve(root, PHASE2_CLOSURE_VALIDATOR_REL),
        "\n".join(
            (
                VALIDATOR_PATH_LINE,
                VALIDATOR_MARKER_LINE,
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_short_fixture_closure_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        write_text(resolve(root, PHASE2_CLOSURE_REL), "")
        assert ("MISSING_CLOSURE_MARKER", SHORT_FIXTURE_MARKER) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, PHASE2_TOOL_MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["fixture_roster"] = []
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_FIXTURE", SHORT_FIXTURE_REL.as_posix()) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        validator_path = resolve(root, PHASE2_CLOSURE_VALIDATOR_REL)
        validator_path.write_text("", encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR_PATH_REFERENCE", VALIDATOR_PATH_LINE) in issues
        assert ("MISSING_VALIDATOR_CLOSURE_MARKER", VALIDATOR_MARKER_LINE) in issues
        checks_run += 1

    print("PHASE2_GENKSYMS_SHORT_FIXTURE_CLOSURE_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_SHORT_FIXTURE_CLOSURE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 closure packet keeps the genksyms short-option fixture explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_SHORT_FIXTURE_CLOSURE=pass")
    print("PHASE2_GENKSYMS_SHORT_FIXTURE_PATH_COUNT=1")
    print("PHASE2_GENKSYMS_SHORT_FIXTURE_MARKER_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
