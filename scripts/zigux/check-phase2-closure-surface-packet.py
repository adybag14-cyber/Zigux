#!/usr/bin/env python3
"""Guard the current closure-side Phase 2 surface packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

SURFACE_PATHS = (
    ROOT / "third_party" / "README.md",
    ROOT / "scripts" / "zigux" / "check-lane05-local-first-archive-workflow.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-archive-readme.py",
    ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py",
    ROOT / "scripts" / "zigux" / "check-fixdep-diff.py",
    ROOT / "scripts" / "zigux" / "fixdep.zig",
    ROOT / "scripts" / "zigux" / "genksyms_version_before_invalid_long_option_test.zig",
    ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py",
    ROOT / "scripts" / "zigux" / "genksyms.zig",
    ROOT / "scripts" / "zigux" / "validate-phase2.py",
    ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_comment_only_expected.stderr.txt",
)

CLOSURE_MARKERS = (
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
)

REVIEW_MARKERS = (
    "`third_party/README.md`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
)

TESTS_MARKERS = (
    "`third_party/README.md`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
)

EXPECTED_MANIFEST_LOCATIONS = {
    ("present_surfaces", "checkers"): [
        "scripts/zigux/check-lane05-local-first-archive-workflow.py",
        "scripts/zigux/check-lane05-local-archive-readme.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/check-genksyms-bridge.py",
    ],
    ("present_surfaces", "bridge_helpers"): [
        "scripts/zigux/genksyms.zig",
        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    ],
    ("present_surfaces", "fixdep_support"): [
        "scripts/basic/fixdep.c",
        "scripts/zigux/fixdep.zig",
        "zigux/tests/fixtures/fixdep/cases.json",
        "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt",
    ],
    ("present_surfaces", "fixture_roster"): [
        "zigux/tests/fixtures/genksyms_bridge/manifest.json",
        "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt",
    ],
}

MANIFEST_NOTE_MARKERS = (
    "invalid-long-option version-side-effect proof",
    "process-output fixture set",
    "full fixdep C-versus-Zig parity fixture packet",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(CLOSURE_MARKERS)
    + len(REVIEW_MARKERS)
    + len(TESTS_MARKERS)
    + sum(len(values) for values in EXPECTED_MANIFEST_LOCATIONS.values())
    + len(MANIFEST_NOTE_MARKERS)
    + len(SURFACE_PATHS)
    + 4
)


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_manifest_issues(payload: object) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return [("INVALID_MANIFEST_PAYLOAD", type(payload).__name__)]

    issues: list[tuple[str, str]] = []
    notes = payload.get("notes")
    if not isinstance(notes, list):
        issues.append(("INVALID_MANIFEST_NOTES", type(notes).__name__))
    else:
        joined_notes = "\n".join(note for note in notes if isinstance(note, str))
        issues.extend(collect_missing_markers(joined_notes, MANIFEST_NOTE_MARKERS, "MISSING_MANIFEST_NOTE_MARKERS"))

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return issues + [("INVALID_PRESENT_SURFACES", type(present_surfaces).__name__)]

    for (group_key, list_key), expected_values in EXPECTED_MANIFEST_LOCATIONS.items():
        if group_key != "present_surfaces":
            continue
        actual_values = present_surfaces.get(list_key)
        if not isinstance(actual_values, list):
            issues.append(("INVALID_MANIFEST_SURFACE_LIST", list_key))
            continue
        for expected_value in expected_values:
            if expected_value not in actual_values:
                issues.append(("MISSING_MANIFEST_SURFACE_VALUE", f"{list_key}:{expected_value}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    review_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_text = read_text(resolve_path(root, TESTS_README))
    issues.extend(collect_missing_markers(closure_text, CLOSURE_MARKERS, "MISSING_CLOSURE_MARKERS"))
    issues.extend(collect_missing_markers(review_text, REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"))
    issues.extend(collect_missing_markers(tests_text, TESTS_MARKERS, "MISSING_TESTS_MARKERS"))

    manifest_path = resolve_path(root, TOOL_MANIFEST)
    try:
        manifest_payload = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_MANIFEST_JSON", exc.msg))
    else:
        issues.extend(collect_manifest_issues(manifest_payload))

    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_SURFACE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    closure_lines = ["# Phase 2 Closure", *CLOSURE_MARKERS]
    review_lines = ["# Zigux Review Checklist", *REVIEW_MARKERS]
    tests_lines = ["# zigux/tests", *TESTS_MARKERS]
    manifest_payload = {
        "present_surfaces": {
            "checkers": EXPECTED_MANIFEST_LOCATIONS[("present_surfaces", "checkers")],
            "bridge_helpers": EXPECTED_MANIFEST_LOCATIONS[("present_surfaces", "bridge_helpers")],
            "fixdep_support": EXPECTED_MANIFEST_LOCATIONS[("present_surfaces", "fixdep_support")],
            "fixture_roster": EXPECTED_MANIFEST_LOCATIONS[("present_surfaces", "fixture_roster")],
        },
        "notes": [
            "Keep the standalone invalid-long-option version-side-effect proof explicit.",
            "Keep the manifest-backed process-output fixture set explicit.",
            "Keep the full fixdep C-versus-Zig parity fixture packet explicit.",
        ],
    }

    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(closure_lines) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(review_lines) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(tests_lines) + "\n")
    write_text(resolve_path(root, TOOL_MANIFEST), json.dumps(manifest_payload, indent=2) + "\n")

    for path in SURFACE_PATHS:
        if path in (PHASE2_CLOSURE, REVIEW_CHECKLIST, TESTS_README, TOOL_MANIFEST):
            continue
        write_text(resolve_path(root, path), "present\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_surface_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_CLOSURE_MARKERS", marker) in issues
            checks_run += 1

        for marker in REVIEW_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_REVIEW_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_MARKERS", marker) in issues
            checks_run += 1

        for (group_key, list_key), expected_values in EXPECTED_MANIFEST_LOCATIONS.items():
            for expected_value in expected_values:
                build_self_test_root(root)
                payload = json.loads(resolve_path(root, TOOL_MANIFEST).read_text(encoding="utf-8"))
                payload[group_key][list_key].remove(expected_value)
                resolve_path(root, TOOL_MANIFEST).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
                issues = collect_issues(root)
                assert ("MISSING_MANIFEST_SURFACE_VALUE", f"{list_key}:{expected_value}") in issues
                checks_run += 1

        for marker in MANIFEST_NOTE_MARKERS:
            build_self_test_root(root)
            payload = json.loads(resolve_path(root, TOOL_MANIFEST).read_text(encoding="utf-8"))
            payload["notes"][0] = payload["notes"][0].replace(marker, "")
            payload["notes"][1] = payload["notes"][1].replace(marker, "")
            payload["notes"][2] = payload["notes"][2].replace(marker, "")
            resolve_path(root, TOOL_MANIFEST).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MANIFEST_NOTE_MARKERS", marker) in issues
            checks_run += 1

        for path in SURFACE_PATHS:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()) in issues
            checks_run += 1

        build_self_test_root(root)
        resolve_path(root, TOOL_MANIFEST).write_text("{\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "INVALID_MANIFEST_JSON" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, TOOL_MANIFEST).write_text("[]\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_PAYLOAD", "list") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(resolve_path(root, TOOL_MANIFEST).read_text(encoding="utf-8"))
        payload["present_surfaces"] = []
        resolve_path(root, TOOL_MANIFEST).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_PRESENT_SURFACES", "list") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(resolve_path(root, TOOL_MANIFEST).read_text(encoding="utf-8"))
        payload["notes"] = []
        resolve_path(root, TOOL_MANIFEST).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_NOTE_MARKERS", MANIFEST_NOTE_MARKERS[0]) in issues
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CLOSURE_SURFACE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_SURFACE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current closure-side Phase 2 surface packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE2_CLOSURE_SURFACE_PACKET=pass")
    print(f"PHASE2_CLOSURE_SURFACE_PACKET_CLOSURE_MARKER_COUNT={len(CLOSURE_MARKERS)}")
    print(f"PHASE2_CLOSURE_SURFACE_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_MARKERS)}")
    print(f"PHASE2_CLOSURE_SURFACE_PACKET_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    print(
        "PHASE2_CLOSURE_SURFACE_PACKET_MANIFEST_VALUE_COUNT="
        f"{sum(len(values) for values in EXPECTED_MANIFEST_LOCATIONS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
