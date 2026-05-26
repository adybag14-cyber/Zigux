#!/usr/bin/env python3
"""Guard the current directly readable shared Phase 2 packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

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
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
)

PHASE2_NOTES_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` is directly readable on current `master`",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit",
    "The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
)

REVIEW_CHECKLIST_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
)

EXPECTED_MANIFEST = {
    "phase": "Phase 2",
    "status": "active",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
    "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
    "repo_reality_gaps": [],
    "present_checks": (
        ("checkers", "scripts/zigux/check-zig-toolchain.py"),
        ("checkers", "scripts/zigux/check-phase2-toolchain-pinning.py"),
        ("checkers", "scripts/zigux/check-phase2-toolchain-pin-scope.py"),
        ("checkers", "scripts/zigux/check-phase2-required-make-routes.py"),
        ("checkers", "scripts/zigux/check-phase2-docs-shared-reminder.py"),
        ("checkers", "scripts/zigux/check-phase2-tool-manifest.py"),
        ("checkers", "scripts/zigux/check-phase2-artifact-tools-manifest.py"),
        ("checkers", "scripts/zigux/check-genksyms-bridge.py"),
        ("checkers", "scripts/zigux/check-phase2-fixdep-gate.py"),
        ("checkers", "scripts/zigux/check-fixdep-diff.py"),
        ("bootstrap_helpers", "scripts/zigux/install-zig.py"),
        ("cross_route_support", "scripts/zigux/check-phase2-cross.py"),
        ("cross_route_support", "zigux/tests/fixtures/phase2_cross_targets.json"),
        ("artifact_support", "scripts/zigux/artifact_diff.py"),
        ("artifact_support", "scripts/zigux/check-phase2-artifact-tools-manifest.py"),
        ("make_wrappers", "make -C zigux phase2-toolchain"),
        ("make_wrappers", "make -C zigux phase2-tools"),
        ("make_wrappers", "make -C zigux phase2-kconfig"),
        ("make_wrappers", "make -C zigux phase2-cross"),
        ("make_wrappers", "make -C zigux phase2-genksyms"),
        ("make_wrappers", "make -C zigux phase2-fixdep"),
        ("make_wrappers", "make -C zigux phase2-validate"),
    ),
}

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_LINES)
    + len(PHASE2_NOTES_MARKERS)
    + len(REVIEW_CHECKLIST_MARKERS)
    + len(SCRIPTS_README_MARKERS)
    + len(EXPECTED_MANIFEST["present_checks"])
    + 3
)


def resolve_path(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_missing_lines(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    lines = {line.strip() for line in text.splitlines()}
    return [(code, marker) for marker in markers if marker not in lines]


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    manifest = json.loads(read_text(resolve_path(root, TOOL_MANIFEST)))
    issues: list[tuple[str, str]] = []
    for field in ("phase", "status", "workflow", "scope", "repo_reality_gaps"):
        if manifest.get(field) != EXPECTED_MANIFEST[field]:
            issues.append(("MANIFEST_FIELD_MISMATCH", field))
    present = manifest.get("present_surfaces")
    if not isinstance(present, dict):
        return issues + [("MANIFEST_FIELD_MISMATCH", "present_surfaces")]
    for bucket, marker in EXPECTED_MANIFEST["present_checks"]:
        if marker not in present.get(bucket, []):
            issues.append(("MANIFEST_MISSING_SURFACE", f"{bucket}:{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_lines(read_text(resolve_path(root, WORKFLOW)), WORKFLOW_LINES, "MISSING_WORKFLOW_LINES"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, PHASE2_NOTES)), PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, REVIEW_CHECKLIST)), REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, SCRIPTS_README)), SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"))
    issues.extend(collect_manifest_issues(root))
    return issues


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    present_surfaces: dict[str, list[str]] = {}
    for bucket, marker in EXPECTED_MANIFEST["present_checks"]:
        present_surfaces.setdefault(bucket, []).append(marker)
    manifest = {
        "phase": EXPECTED_MANIFEST["phase"],
        "status": EXPECTED_MANIFEST["status"],
        "workflow": EXPECTED_MANIFEST["workflow"],
        "scope": EXPECTED_MANIFEST["scope"],
        "repo_reality_gaps": [],
        "present_surfaces": present_surfaces,
    }
    write_text(resolve_path(root, TOOL_MANIFEST), json.dumps(manifest, indent=2) + "\n")


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_CURRENT_PACKET=fail")
    for code, marker in issues:
        print(f"{code}:{marker}")
    return 1


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

        workflow_path = resolve_path(root, WORKFLOW)
        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            write_text(workflow_path, remove_once(read_text(workflow_path), marker))
            assert ("MISSING_WORKFLOW_LINES", marker) in collect_issues(root)
            checks_run += 1

        for rel, markers, code in (
            (PHASE2_NOTES, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKERS"),
            (REVIEW_CHECKLIST, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"),
            (SCRIPTS_README, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"),
        ):
            for marker in markers:
                build_sample_root(root)
                path = resolve_path(root, rel)
                write_text(path, read_text(path).replace(marker, "", 1))
                assert (code, marker) in collect_issues(root)
                checks_run += 1

        for bucket, marker in EXPECTED_MANIFEST["present_checks"]:
            build_sample_root(root)
            manifest_path = resolve_path(root, TOOL_MANIFEST)
            manifest = json.loads(read_text(manifest_path))
            manifest["present_surfaces"][bucket].remove(marker)
            write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
            assert ("MANIFEST_MISSING_SURFACE", f"{bucket}:{marker}") in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        manifest_path = resolve_path(root, TOOL_MANIFEST)
        manifest = json.loads(read_text(manifest_path))
        manifest["scope"] = "wrong"
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("MANIFEST_FIELD_MISMATCH", "scope") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["repo_reality_gaps"] = ["scripts/zigux/install-zig.py"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("MANIFEST_FIELD_MISMATCH", "repo_reality_gaps") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        assert collect_issues(root) == []
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
    print("PHASE2_CURRENT_PACKET_REQUIRED_FILE_COUNT=5")
    print(f"PHASE2_CURRENT_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_CURRENT_PACKET_NOTES_MARKER_COUNT={len(PHASE2_NOTES_MARKERS)}")
    print(f"PHASE2_CURRENT_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_CURRENT_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_CURRENT_PACKET_MANIFEST_SURFACE_COUNT={len(EXPECTED_MANIFEST['present_checks'])}")
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
