#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

REVIEW_CHECKLIST_MARKERS = (
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "`make -C zigux phase2-genksyms`",
    "current directly readable Phase 2 toolchain, installer, direct cross-route, kbuild, kconfig bridge, genksyms bridge, docs-shared-reminder, and required-make-route packet",
    "current rematerialized Phase 2 closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, toolchain self-check, genksyms bridge, and make-wrapper packet",
)

REVIEW_CHECKLIST_FORBIDDEN_MARKERS = (
    "current directly readable Phase 2 toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, and required-make-route packet",
    "current rematerialized Phase 2 closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, toolchain self-check, and make-wrapper packet",
    "`make -C zigux phase2-cross`, `make -C zigux phase2`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay explicit as the current rematerialized Phase 2 closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, toolchain self-check, and make-wrapper packet?",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
)

PHASE2_TOOL_MANIFEST_MARKERS = (
    "\"scripts/zigux/check-genksyms-bridge.py\"",
    "\"scripts/zigux/genksyms.zig\"",
    "\"make -C zigux phase2-genksyms\"",
    "\"zigux/tests/fixtures/genksyms_bridge/cases.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/help_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/minimal_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/long_options_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json\"",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    review_checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    manifest_text = read_text(resolve_path(root, PHASE2_TOOL_MANIFEST))
    issues.extend(
        collect_missing_markers(
            review_checklist_text,
            REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_forbidden_markers(
            review_checklist_text,
            REVIEW_CHECKLIST_FORBIDDEN_MARKERS,
            "FORBIDDEN_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_readme_text,
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            manifest_text,
            PHASE2_TOOL_MANIFEST_MARKERS,
            "MISSING_PHASE2_TOOL_MANIFEST_MARKERS",
        )
    )
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


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_TOOL_MANIFEST), "\n".join(PHASE2_TOOL_MANIFEST_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement)


def run_self_test() -> int:
    checks_run = (
        1
        + len(REVIEW_CHECKLIST_MARKERS)
        + len(REVIEW_CHECKLIST_FORBIDDEN_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(PHASE2_TOOL_MANIFEST_MARKERS)
        + 3
    )
    completed = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_checklist_genksyms_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        completed += 1

        for marker in REVIEW_CHECKLIST_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_REVIEW_CHECKLIST_MARKERS", marker) in issues
            completed += 1

        for marker in REVIEW_CHECKLIST_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_REVIEW_CHECKLIST_MARKERS", marker) in issues
            completed += 1

        for marker in TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues
            completed += 1

        for marker in PHASE2_TOOL_MANIFEST_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_TOOL_MANIFEST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_PHASE2_TOOL_MANIFEST_MARKERS", marker) in issues
            completed += 1

        for rel_path in (REVIEW_CHECKLIST, TESTS_README, PHASE2_TOOL_MANIFEST):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                completed += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert completed == checks_run
    print("PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET_SELF_TEST_CASE_COUNT={completed}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 review-checklist genksyms packet aligned to the shipped tests-root and manifest packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_GENKSYMS_PACKET_MANIFEST_MARKER_COUNT={len(PHASE2_TOOL_MANIFEST_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
