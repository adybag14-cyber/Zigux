#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

REVIEW_CHECKLIST_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`make -C zigux phase2-genksyms`",
)

REVIEW_CHECKLIST_EXACT_COUNT_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`make -C zigux phase2-genksyms`",
)

TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
)

MANIFEST_MARKERS = (
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/genksyms.zig",
    "make -C zigux phase2-genksyms",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def collect_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        items: set[str] = set()
        for entry in value:
            items.update(collect_strings(entry))
        return items
    if isinstance(value, dict):
        items: set[str] = set()
        for entry in value.values():
            items.update(collect_strings(entry))
        return items
    return set()


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_missing_manifest_strings(strings: set[str]) -> list[tuple[str, str]]:
    return [("MISSING_MANIFEST_MARKERS", marker) for marker in MANIFEST_MARKERS if marker not in strings]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    review_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_text = read_text(resolve_path(root, TESTS_README))
    manifest = read_json(resolve_path(root, PHASE2_TOOL_MANIFEST))
    manifest_strings = collect_strings(manifest)

    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_markers(review_text, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(
        collect_exact_count_markers(
            review_text,
            REVIEW_CHECKLIST_EXACT_COUNT_MARKERS,
            "EXACT_COUNT_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(collect_missing_markers(tests_text, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))
    issues.extend(collect_missing_manifest_strings(manifest_strings))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(
        resolve_path(root, PHASE2_TOOL_MANIFEST),
        json.dumps(
            {
                "phase": "Phase 2",
                "present_surfaces": {
                    "checkers": ["scripts/zigux/check-genksyms-bridge.py"],
                    "bridge_helpers": ["scripts/zigux/genksyms.zig"],
                    "make_wrappers": ["make -C zigux phase2-genksyms"],
                    "fixture_roster": [
                        "zigux/tests/fixtures/genksyms_bridge/cases.json",
                        "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
                    ],
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(REVIEW_CHECKLIST_MARKERS) + 1 + len(TESTS_README_MARKERS) + len(MANIFEST_MARKERS) + 3
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_checklist_genksyms_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REVIEW_CHECKLIST_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_REVIEW_CHECKLIST_MARKERS", marker) in issues
            checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, REVIEW_CHECKLIST)
        path.write_text(path.read_text(encoding="utf-8") + REVIEW_CHECKLIST_EXACT_COUNT_MARKERS[0] + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("EXACT_COUNT_REVIEW_CHECKLIST_MARKERS", f"2::{REVIEW_CHECKLIST_EXACT_COUNT_MARKERS[0]}") in issues
        checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in MANIFEST_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, PHASE2_TOOL_MANIFEST)
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["present_surfaces"]["fixture_roster"] = [v for v in manifest["present_surfaces"]["fixture_roster"] if v != marker]
            if marker == "scripts/zigux/check-genksyms-bridge.py":
                manifest["present_surfaces"]["checkers"] = []
            elif marker == "scripts/zigux/genksyms.zig":
                manifest["present_surfaces"]["bridge_helpers"] = []
            elif marker == "make -C zigux phase2-genksyms":
                manifest["present_surfaces"]["make_wrappers"] = []
            path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MANIFEST_MARKERS", marker) in issues
            checks_run += 1

        for rel_path in (REVIEW_CHECKLIST, TESTS_README, PHASE2_TOOL_MANIFEST):
            build_sample_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the review-checklist-side Phase 2 genksyms packet drifts below the shipped tests-root and manifest roster."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET=pass")
    print(
        "PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET_MARKER_COUNT="
        f"{len(REVIEW_CHECKLIST_MARKERS) + len(TESTS_README_MARKERS) + len(MANIFEST_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
