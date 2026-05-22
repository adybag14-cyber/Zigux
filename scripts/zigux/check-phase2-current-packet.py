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
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-cross",
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
    "run: zig test scripts/zigux/genksyms.zig",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

PHASE2_NOTES_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` is directly readable on current `master`",
    "`scripts/zigux/install-zig.py` is directly readable on current `master` and keeps the pinned-channel archive download, SHA-256 verification, and install-root replay path explicit beside the reminder guards.",
    "`.github/workflows/zigux-bootstrap.yml` also derives `ZIGUX_ZIG_TARGET`, `ZIGUX_ZIG_FILENAME`, and `ZIGUX_ZIG_URL` from `scripts/zigux/zig-toolchain-policy.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
)

PHASE2_NOTES_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
    "historical packet members until same-lane work rematerializes them on `master`",
)

REVIEW_CHECKLIST_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

REVIEW_CHECKLIST_FORBIDDEN_MARKERS = (
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay framed as historical packet members rather than shipped current-`master` evidence",
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
)

SCRIPTS_README_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
)

TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "Keep the current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, genksyms bridge, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
    "Tests-root reviewer prompt:",
)

EXPECTED_MANIFEST_TOP_LEVEL = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
    "repo_reality_gaps": [],
}

EXPECTED_MANIFEST_SURFACES = {
    "checkers": (
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
    ),
    "archive_support": (
        "third_party/README.md",
        "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
    ),
    "artifact_support": (
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
        "make -C zigux phase2-tools",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
    ),
}

EXPECTED_MANIFEST_NOTES = (
    "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, the returned local-first archive workflow and archive README contract checkers, the shipped toolchain-pinning and pin-scope guards, the returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, kbuild routes checker, the live kconfig bridge checker and fixture roster, the dedicated genksyms selftest-alignment guard, the manifest-backed genksyms bridge checker plus its expanded expected and process-output fixture packet, the standalone invalid-long-option version-side-effect proof, the fixdep governance and parity checker pair, and the restored tranche-closure note.",
    "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose.",
    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
    "Keep the dedicated manifest guards and the dedicated genksyms selftest-alignment guard explicit through scripts/zigux/check-phase2-tool-manifest.py, scripts/zigux/check-phase2-artifact-tools-manifest.py, and scripts/zigux/check-phase2-genksyms-selftest-alignment.py so Phase 2 packet drift fails closed beside the other reminder checkers.",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_lines(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    lines = {line.strip() for line in text.splitlines()}
    return [(code, marker) for marker in markers if marker not in lines]


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    manifest = json.loads(read_text(resolve_path(root, TOOL_MANIFEST)))
    issues: list[tuple[str, str]] = []
    for key, expected in EXPECTED_MANIFEST_TOP_LEVEL.items():
        if manifest.get(key) != expected:
            issues.append(("MANIFEST_TOP_LEVEL_MISMATCH", key))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return issues + [("MANIFEST_PRESENT_SURFACES_MISSING", "present_surfaces")]

    for category, expected_values in EXPECTED_MANIFEST_SURFACES.items():
        values = present_surfaces.get(category)
        if not isinstance(values, list):
            issues.append(("MANIFEST_SURFACE_CATEGORY_MISSING", category))
            continue
        for value in expected_values:
            if value not in values:
                issues.append(("MANIFEST_SURFACE_VALUE_MISSING", f"{category}:{value}"))

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("MANIFEST_NOTES_MISSING", "notes"))
    else:
        for note in EXPECTED_MANIFEST_NOTES:
            if note not in notes:
                issues.append(("MANIFEST_NOTE_MISSING", note))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_lines(read_text(resolve_path(root, WORKFLOW)), WORKFLOW_LINES, "MISSING_WORKFLOW_LINES"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, PHASE2_NOTES)), PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKERS"))
    issues.extend(collect_forbidden_markers(read_text(resolve_path(root, PHASE2_NOTES)), PHASE2_NOTES_FORBIDDEN_MARKERS, "FORBIDDEN_PHASE2_NOTES_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, REVIEW_CHECKLIST)), REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(collect_forbidden_markers(read_text(resolve_path(root, REVIEW_CHECKLIST)), REVIEW_CHECKLIST_FORBIDDEN_MARKERS, "FORBIDDEN_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, SCRIPTS_README)), SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"))
    issues.extend(collect_forbidden_markers(read_text(resolve_path(root, SCRIPTS_README)), SCRIPTS_README_FORBIDDEN_MARKERS, "FORBIDDEN_SCRIPTS_README_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, TESTS_README)), TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))
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
        **EXPECTED_MANIFEST_TOP_LEVEL,
        "present_surfaces": {category: list(values) for category, values in EXPECTED_MANIFEST_SURFACES.items()},
        "notes": list(EXPECTED_MANIFEST_NOTES),
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
            assert ("MISSING_WORKFLOW_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in PHASE2_NOTES_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            write_text(path, remove_once(read_text(path), marker))
            assert ("MISSING_PHASE2_NOTES_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in PHASE2_NOTES_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            write_text(path, read_text(path) + marker + "\n")
            assert ("FORBIDDEN_PHASE2_NOTES_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in REVIEW_CHECKLIST_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            write_text(path, remove_once(read_text(path), marker))
            assert ("MISSING_REVIEW_CHECKLIST_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in REVIEW_CHECKLIST_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            write_text(path, read_text(path) + marker + "\n")
            assert ("FORBIDDEN_REVIEW_CHECKLIST_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in SCRIPTS_README_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, SCRIPTS_README)
            write_text(path, remove_once(read_text(path), marker))
            assert ("MISSING_SCRIPTS_README_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in SCRIPTS_README_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, SCRIPTS_README)
            write_text(path, read_text(path) + marker + "\n")
            assert ("FORBIDDEN_SCRIPTS_README_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TESTS_README)
            write_text(path, remove_once(read_text(path), marker))
            assert ("MISSING_TESTS_README_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        manifest_path = resolve_path(root, TOOL_MANIFEST)
        manifest = json.loads(read_text(manifest_path))
        manifest["present_surfaces"]["checkers"].remove("scripts/zigux/check-phase2-genksyms-selftest-alignment.py")
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert (
            "MANIFEST_SURFACE_VALUE_MISSING",
            "checkers:scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["workflow"] = "scripts/zigux/README.md"
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("MANIFEST_TOP_LEVEL_MISMATCH", "workflow") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["notes"] = manifest["notes"][:-1]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("MANIFEST_NOTE_MISSING", EXPECTED_MANIFEST_NOTES[-1]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

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
