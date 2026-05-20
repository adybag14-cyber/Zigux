#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 toolchain/action-path packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

PHASE2_NOTES_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, or returned fixdep packet on current `master`.",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` is directly readable on current `master`",
    "`scripts/zigux/install-zig.py` is directly readable on current `master`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test`",
    "`python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test`",
    "`python3 scripts/zigux/check-phase2-tool-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test`",
    "`python3 scripts/zigux/check-genksyms-bridge.py --self-test`",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "`python3 scripts/zigux/check-fixdep-diff.py --self-test`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit",
    "`make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet",
)

PHASE2_NOTES_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
    "historical packet members until same-lane work rematerializes them on `master`",
)

REVIEW_CHECKLIST_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-genksyms`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current rematerialized Phase 2 closure-side, closure-validator, validation, installer, direct cross-route",
)

REVIEW_CHECKLIST_FORBIDDEN_MARKERS = (
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay framed as historical packet members",
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
)

TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, genksyms bridge, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, kconfig bridge checker, and genksyms bridge set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "Keep the current direct-readback Phase 2 kconfig and genksyms bridge packet:",
)

SCRIPTS_README_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
)

TESTS_README_FORBIDDEN_MARKERS = ()

EXPECTED_MANIFEST = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "current directly readable scripts-root toolchain, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
    "checkers": [
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
    ],
    "make_wrappers": [
        "make -C zigux phase2-tools",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
    ],
    "artifact_support": [
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    ],
    "cross_route_support": [
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    ],
    "fixdep_support": [
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/fixdep.zig",
        "zigux/tests/fixtures/fixdep/cases.json",
    ],
    "repo_reality_gaps": [],
}

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_LINES)
    + len(PHASE2_NOTES_MARKERS)
    + len(PHASE2_NOTES_FORBIDDEN_MARKERS)
    + len(REVIEW_CHECKLIST_MARKERS)
    + len(REVIEW_CHECKLIST_FORBIDDEN_MARKERS)
    + len(SCRIPTS_README_MARKERS)
    + len(SCRIPTS_README_FORBIDDEN_MARKERS)
    + len(TESTS_README_MARKERS)
    + len(TESTS_README_FORBIDDEN_MARKERS)
    + 4
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_missing_lines(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    lines = {line.strip() for line in text.splitlines()}
    return [(code, marker) for marker in markers if marker not in lines]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    manifest = json.loads(read_text(resolve_path(root, TOOL_MANIFEST)))
    issues: list[tuple[str, str]] = []
    if manifest.get("phase") != EXPECTED_MANIFEST["phase"]:
        issues.append(("MANIFEST_FIELD_MISMATCH", "phase"))
    if manifest.get("status") != EXPECTED_MANIFEST["status"]:
        issues.append(("MANIFEST_FIELD_MISMATCH", "status"))
    if manifest.get("scope") != EXPECTED_MANIFEST["scope"]:
        issues.append(("MANIFEST_FIELD_MISMATCH", "scope"))
    if manifest.get("workflow") != EXPECTED_MANIFEST["workflow"]:
        issues.append(("MANIFEST_FIELD_MISMATCH", "workflow"))
    present = manifest.get("present_surfaces", {})
    for value in EXPECTED_MANIFEST["checkers"]:
        if value not in present.get("checkers", []):
            issues.append(("MANIFEST_MISSING_CHECKERS", value))
    for value in EXPECTED_MANIFEST["make_wrappers"]:
        if value not in present.get("make_wrappers", []):
            issues.append(("MANIFEST_MISSING_MAKE_WRAPPERS", value))
    for value in EXPECTED_MANIFEST["artifact_support"]:
        if value not in present.get("artifact_support", []):
            issues.append(("MANIFEST_MISSING_ARTIFACT_SUPPORT", value))
    for value in EXPECTED_MANIFEST["cross_route_support"]:
        if value not in present.get("cross_route_support", []):
            issues.append(("MANIFEST_MISSING_CROSS_ROUTE_SUPPORT", value))
    for value in EXPECTED_MANIFEST["fixdep_support"]:
        if value not in present.get("fixdep_support", []):
            issues.append(("MANIFEST_MISSING_FIXDEP_SUPPORT", value))
    if manifest.get("repo_reality_gaps") != EXPECTED_MANIFEST["repo_reality_gaps"]:
        issues.append(("MANIFEST_FIELD_MISMATCH", "repo_reality_gaps"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    issues.extend(collect_missing_lines(workflow_text, WORKFLOW_LINES, "MISSING_WORKFLOW_LINES"))
    issues.extend(collect_missing_markers(notes_text, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKERS"))
    issues.extend(collect_forbidden_markers(notes_text, PHASE2_NOTES_FORBIDDEN_MARKERS, "FORBIDDEN_PHASE2_NOTES_MARKERS"))
    issues.extend(collect_missing_markers(checklist_text, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(collect_forbidden_markers(checklist_text, REVIEW_CHECKLIST_FORBIDDEN_MARKERS, "FORBIDDEN_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(collect_missing_markers(scripts_readme_text, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"))
    issues.extend(collect_forbidden_markers(scripts_readme_text, SCRIPTS_README_FORBIDDEN_MARKERS, "FORBIDDEN_SCRIPTS_README_MARKERS"))
    issues.extend(collect_missing_markers(tests_readme_text, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))
    issues.extend(collect_forbidden_markers(tests_readme_text, TESTS_README_FORBIDDEN_MARKERS, "FORBIDDEN_TESTS_README_MARKERS"))
    issues.extend(collect_manifest_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CURRENT_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    manifest = {
        "phase": EXPECTED_MANIFEST["phase"],
        "status": EXPECTED_MANIFEST["status"],
        "scope": EXPECTED_MANIFEST["scope"],
        "workflow": EXPECTED_MANIFEST["workflow"],
        "present_surfaces": {
            "checkers": list(EXPECTED_MANIFEST["checkers"]),
            "make_wrappers": list(EXPECTED_MANIFEST["make_wrappers"]),
            "artifact_support": list(EXPECTED_MANIFEST["artifact_support"]),
            "cross_route_support": list(EXPECTED_MANIFEST["cross_route_support"]),
            "fixdep_support": list(EXPECTED_MANIFEST["fixdep_support"]),
        },
        "repo_reality_gaps": [],
    }
    write_text(resolve_path(root, TOOL_MANIFEST), json.dumps(manifest, indent=2) + "\n")


def remove_once(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_current_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            write_text(path, remove_once(read_text(path), marker))
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_LINES", marker) in issues
            checks_run += 1

        for marker in PHASE2_NOTES_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            write_text(path, remove_once(read_text(path), marker))
            issues = collect_issues(root)
            assert ("MISSING_PHASE2_NOTES_MARKERS", marker) in issues
            checks_run += 1

        for marker in PHASE2_NOTES_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            write_text(path, read_text(path) + marker + "\n")
            issues = collect_issues(root)
            assert ("FORBIDDEN_PHASE2_NOTES_MARKERS", marker) in issues
            checks_run += 1

        for marker in REVIEW_CHECKLIST_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            write_text(path, remove_once(read_text(path), marker))
            issues = collect_issues(root)
            assert ("MISSING_REVIEW_CHECKLIST_MARKERS", marker) in issues
            checks_run += 1

        for marker in REVIEW_CHECKLIST_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            write_text(path, read_text(path) + marker + "\n")
            issues = collect_issues(root)
            assert ("FORBIDDEN_REVIEW_CHECKLIST_MARKERS", marker) in issues
            checks_run += 1

        for marker in SCRIPTS_README_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, SCRIPTS_README)
            write_text(path, remove_once(read_text(path), marker))
            issues = collect_issues(root)
            assert ("MISSING_SCRIPTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in SCRIPTS_README_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, SCRIPTS_README)
            write_text(path, read_text(path) + marker + "\n")
            issues = collect_issues(root)
            assert ("FORBIDDEN_SCRIPTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TESTS_README)
            write_text(path, remove_once(read_text(path), marker))
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_README_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TESTS_README)
            write_text(path, read_text(path) + marker + "\n")
            issues = collect_issues(root)
            assert ("FORBIDDEN_TESTS_README_MARKERS", marker) in issues
            checks_run += 1

        build_sample_root(root)
        manifest_path = resolve_path(root, TOOL_MANIFEST)
        manifest = json.loads(read_text(manifest_path))
        manifest["present_surfaces"]["fixdep_support"].remove("scripts/zigux/check-fixdep-diff.py")
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MANIFEST_MISSING_FIXDEP_SUPPORT", "scripts/zigux/check-fixdep-diff.py") in issues
        checks_run += 1

        build_sample_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["repo_reality_gaps"] = ["scripts/zigux/install-zig.py"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MANIFEST_FIELD_MISMATCH", "repo_reality_gaps") in issues
        checks_run += 1

        build_sample_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["workflow"] = "scripts/zigux/README.md"
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MANIFEST_FIELD_MISMATCH", "workflow") in issues
        checks_run += 1

        build_sample_root(root)
        issues = collect_issues(root)
        assert issues == []
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT, (checks_run, EXPECTED_SELF_TEST_CASE_COUNT)
    print("PHASE2_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CURRENT_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def run_packet_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)
    print("PHASE2_CURRENT_PACKET=pass")
    print("PHASE2_CURRENT_PACKET_REQUIRED_FILE_COUNT=6")
    print(f"PHASE2_CURRENT_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_CURRENT_PACKET_NOTES_MARKER_COUNT={len(PHASE2_NOTES_MARKERS)}")
    print(f"PHASE2_CURRENT_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_CURRENT_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_CURRENT_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print("PHASE2_CURRENT_PACKET_MANIFEST_GAP_COUNT=0")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repo root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in self-test suite.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal current-packet sample tree.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0
    return run_packet_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
