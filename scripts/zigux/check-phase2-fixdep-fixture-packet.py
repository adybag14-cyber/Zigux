#!/usr/bin/env python3
"""Guard the current Phase 2 fixdep fixture packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
TOOL_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
FIXDEP_GATE_REL = Path("scripts/zigux/check-phase2-fixdep-gate.py")
FIXDEP_DIFF_REL = Path("scripts/zigux/check-fixdep-diff.py")
FIXDEP_ZIG_REL = Path("scripts/zigux/fixdep.zig")
FIXDEP_CASES_REL = Path("zigux/tests/fixtures/fixdep/cases.json")

REQUIRED_FILES = (
    BOOTSTRAP_NOTES_REL,
    PHASE2_CLOSURE_REL,
    TOOL_MANIFEST_REL,
    FIXDEP_GATE_REL,
    FIXDEP_DIFF_REL,
    FIXDEP_ZIG_REL,
    FIXDEP_CASES_REL,
)

BOOTSTRAP_REQUIRED_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

PHASE2_CLOSURE_REQUIRED_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

MANIFEST_FIXDEP_SUPPORT_REQUIRED = (
    "scripts/basic/fixdep.c",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation.d",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation.d",
    "zigux/tests/fixtures/fixdep/sample_double_backslash_comment.d",
    "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt",
    "zigux/tests/fixtures/fixdep/shared:config.h",
)

MANIFEST_NOTES_REQUIRED = (
    "full fixdep C-versus-Zig parity fixture packet",
)

FIXDEP_GATE_REQUIRED_MARKERS = (
    '"sample_comment_continuation"',
    '"sample_dependency_continuation"',
    '"sample_double_backslash_comment"',
    '"sample_comment_only_stdout_full"',
    '"sample_missing_dep_stdout_full"',
    '"sample_output_write"',
)

FIXDEP_DIFF_REQUIRED_MARKERS = (
    '"sample_comment_continuation"',
    '"sample_dependency_continuation"',
    '"sample_double_backslash_comment"',
    '"sample_comment_only_stdout_full"',
    '"sample_missing_dep_stdout_full"',
    '"sample_output_write"',
    r'"sample_output_write_expected.stderr.txt"',
    r'"shared:config.h"',
)

REQUIRED_CASE_ORDER = (
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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_missing_items(items: list[object], required: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    actual = {item for item in items if isinstance(item, str)}
    return [(code, marker) for marker in required if marker not in actual]


def load_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {path}: {exc.msg}") from exc


def collect_manifest_issues(path: Path) -> list[tuple[str, str]]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        return [("INVALID_MANIFEST_PAYLOAD", type(payload).__name__)]

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return [("INVALID_MANIFEST_PRESENT_SURFACES", type(present_surfaces).__name__)]

    fixdep_support = present_surfaces.get("fixdep_support")
    if not isinstance(fixdep_support, list):
        return [("INVALID_MANIFEST_FIXDEP_SUPPORT", type(fixdep_support).__name__)]

    notes = payload.get("notes")
    if not isinstance(notes, list):
        return [("INVALID_MANIFEST_NOTES", type(notes).__name__)]

    issues = collect_missing_items(
        fixdep_support,
        MANIFEST_FIXDEP_SUPPORT_REQUIRED,
        "MISSING_MANIFEST_FIXDEP_SUPPORT",
    )
    note_text = "\n".join(note for note in notes if isinstance(note, str))
    issues.extend(
        collect_missing_markers(note_text, MANIFEST_NOTES_REQUIRED, "MISSING_MANIFEST_NOTES_MARKER")
    )
    return issues


def collect_case_issues(path: Path) -> list[tuple[str, str]]:
    payload = load_json(path)
    if not isinstance(payload, list):
        return [("INVALID_FIXDEP_CASES_PAYLOAD", type(payload).__name__)]

    names: list[str] = []
    issues: list[tuple[str, str]] = []
    seen: set[str] = set()
    duplicates: set[str] = set()

    for index, case in enumerate(payload):
        if not isinstance(case, dict):
            issues.append(("INVALID_FIXDEP_CASE_ENTRY", f"index={index}:type={type(case).__name__}"))
            continue
        name = case.get("name")
        if not isinstance(name, str) or not name:
            issues.append(("INVALID_FIXDEP_CASE_NAME", f"index={index}:name={name!r}"))
            continue
        names.append(name)
        if name in seen:
            duplicates.add(name)
        seen.add(name)

    for name in sorted(duplicates):
        issues.append(("DUPLICATE_FIXDEP_CASE", name))

    for name in REQUIRED_CASE_ORDER:
        if name not in seen:
            issues.append(("MISSING_FIXDEP_CASE", name))

    if names != list(REQUIRED_CASE_ORDER):
        issues.append(
            (
                "FIXDEP_CASE_ORDER_MISMATCH",
                f"actual={names!r}:expected={list(REQUIRED_CASE_ORDER)!r}",
            )
        )
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    bootstrap_text = read_text(resolve(root, BOOTSTRAP_NOTES_REL))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE_REL))
    fixdep_gate_text = read_text(resolve(root, FIXDEP_GATE_REL))
    fixdep_diff_text = read_text(resolve(root, FIXDEP_DIFF_REL))

    issues.extend(
        collect_missing_markers(
            bootstrap_text, BOOTSTRAP_REQUIRED_MARKERS, "MISSING_BOOTSTRAP_MARKER"
        )
    )
    issues.extend(
        collect_missing_markers(
            closure_text, PHASE2_CLOSURE_REQUIRED_MARKERS, "MISSING_PHASE2_CLOSURE_MARKER"
        )
    )
    issues.extend(
        collect_missing_markers(
            fixdep_gate_text, FIXDEP_GATE_REQUIRED_MARKERS, "MISSING_FIXDEP_GATE_MARKER"
        )
    )
    issues.extend(
        collect_missing_markers(
            fixdep_diff_text, FIXDEP_DIFF_REQUIRED_MARKERS, "MISSING_FIXDEP_DIFF_MARKER"
        )
    )
    issues.extend(collect_manifest_issues(resolve(root, TOOL_MANIFEST_REL)))
    issues.extend(collect_case_issues(resolve(root, FIXDEP_CASES_REL)))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_FIXDEP_FIXTURE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve(root, BOOTSTRAP_NOTES_REL),
        "\n".join(
            (
                "# Phase 2 Toolchain Bootstrap Notes",
                *BOOTSTRAP_REQUIRED_MARKERS,
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, PHASE2_CLOSURE_REL),
        "\n".join(
            (
                "# Phase 2 Closure",
                *PHASE2_CLOSURE_REQUIRED_MARKERS,
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, FIXDEP_GATE_REL),
        "\n".join(FIXDEP_GATE_REQUIRED_MARKERS) + "\n",
    )
    write_text(
        resolve(root, FIXDEP_DIFF_REL),
        "\n".join(FIXDEP_DIFF_REQUIRED_MARKERS) + "\n",
    )
    write_text(resolve(root, FIXDEP_ZIG_REL), "present\n")
    write_text(
        resolve(root, TOOL_MANIFEST_REL),
        json.dumps(
            {
                "present_surfaces": {
                    "fixdep_support": list(MANIFEST_FIXDEP_SUPPORT_REQUIRED),
                },
                "notes": list(MANIFEST_NOTES_REQUIRED),
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve(root, FIXDEP_CASES_REL),
        json.dumps([{"name": name} for name in REQUIRED_CASE_ORDER], indent=2) + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_fixdep_fixture_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in BOOTSTRAP_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, BOOTSTRAP_NOTES_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_BOOTSTRAP_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in PHASE2_CLOSURE_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, PHASE2_CLOSURE_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_PHASE2_CLOSURE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in FIXDEP_GATE_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_GATE_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_FIXDEP_GATE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in FIXDEP_DIFF_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_DIFF_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_FIXDEP_DIFF_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in MANIFEST_FIXDEP_SUPPORT_REQUIRED:
            build_self_test_root(root)
            path = resolve(root, TOOL_MANIFEST_REL)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["present_surfaces"]["fixdep_support"].remove(marker)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_FIXDEP_SUPPORT", marker) in collect_issues(root)
            checks_run += 1

        for marker in MANIFEST_NOTES_REQUIRED:
            build_self_test_root(root)
            path = resolve(root, TOOL_MANIFEST_REL)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["notes"] = []
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_NOTES_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for name in REQUIRED_CASE_ORDER:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_CASES_REL)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload = [entry for entry in payload if entry.get("name") != name]
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_FIXDEP_CASE", name) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload[0]["name"] = "unexpected_fixdep_case"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_FIXDEP_CASE", REQUIRED_CASE_ORDER[0]) in issues
        assert any(code == "FIXDEP_CASE_ORDER_MISMATCH" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload[1]["name"] = payload[0]["name"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("DUPLICATE_FIXDEP_CASE", REQUIRED_CASE_ORDER[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload[0] = "broken"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXDEP_CASE_ENTRY", "index=0:type=str") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload[0]["name"] = ""
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXDEP_CASE_NAME", "index=0:name=''") in collect_issues(root)
        checks_run += 1

        for rel in REQUIRED_FILES:
            build_self_test_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in collect_issues(root)
            checks_run += 1

    print("PHASE2_FIXDEP_FIXTURE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_FIXTURE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 2 fixdep fixture packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a passing sample root for focused replay validation",
    )
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_FIXDEP_FIXTURE_PACKET=pass")
    print(f"PHASE2_FIXDEP_FIXTURE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE2_FIXDEP_FIXTURE_PACKET_MANIFEST_SUPPORT_COUNT="
        f"{len(MANIFEST_FIXDEP_SUPPORT_REQUIRED)}"
    )
    print(
        "PHASE2_FIXDEP_FIXTURE_PACKET_REQUIRED_CASE_COUNT="
        f"{len(REQUIRED_CASE_ORDER)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
