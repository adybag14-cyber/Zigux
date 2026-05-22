#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

REQUIRED_FILES = (
    BOOTSTRAP_NOTES,
    WORKFLOW,
    SCRIPTS_README,
    TESTS_README,
    REVIEW_CHECKLIST,
    TOOL_MANIFEST,
)

BOOTSTRAP_NOTE_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-phase2-required-make-routes.py --self-test`",
    "`python3 scripts/zigux/check-phase2-required-make-routes.py`",
    "`python3 scripts/zigux/check-phase2-tool-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase2-tool-manifest.py`",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`python3 scripts/zigux/check-genksyms-bridge.py --self-test`",
    "`python3 scripts/zigux/check-genksyms-bridge.py`",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py`",
    "`python3 scripts/zigux/check-fixdep-diff.py --self-test`",
    "`python3 scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "make-wrapper-backed `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, and `phase2-validate` route replays",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
)

BOOTSTRAP_NOTE_FORBIDDEN_MARKERS = (
    "make-wrapper-backed toolchain plus direct-cross route replays",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
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
    "run: zig test scripts/zigux/fixdep.zig",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
)

COMPANION_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/install-zig.py`",
)

EXPECTED_MANIFEST = {
    "phase": "Phase 2",
    "status": "active",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
    "required_checkers": [
        "scripts/zigux/check-zig-toolchain.py",
        "scripts/zigux/check-phase2-toolchain-pinning.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "scripts/zigux/check-phase2-required-make-routes.py",
        "scripts/zigux/check-phase2-docs-shared-reminder.py",
        "scripts/zigux/check-phase2-tool-manifest.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
    ],
    "required_make_wrappers": [
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ],
    "required_notes": [
        "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option version-side-effect proof, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
    ],
}


def resolve_path(root: Path, path: Path) -> Path:
    return root / path.relative_to(ROOT)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_missing_exact_lines(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    lines = {line.strip() for line in text.splitlines()}
    return [(code, marker) for marker in markers if marker not in lines]


def collect_missing_paths(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path in REQUIRED_FILES:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_FILE", str(path.relative_to(ROOT))))
    return issues


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    manifest = read_json(resolve_path(root, TOOL_MANIFEST))
    issues: list[tuple[str, str]] = []
    if manifest.get("phase") != EXPECTED_MANIFEST["phase"]:
        issues.append(("MANIFEST_PHASE", str(manifest.get("phase"))))
    if manifest.get("status") != EXPECTED_MANIFEST["status"]:
        issues.append(("MANIFEST_STATUS", str(manifest.get("status"))))
    if manifest.get("workflow") != EXPECTED_MANIFEST["workflow"]:
        issues.append(("MANIFEST_WORKFLOW", str(manifest.get("workflow"))))

    present_surfaces = manifest.get("present_surfaces", {})
    checkers = present_surfaces.get("checkers", [])
    make_wrappers = present_surfaces.get("make_wrappers", [])
    notes = manifest.get("notes", [])

    for entry in EXPECTED_MANIFEST["required_checkers"]:
        if entry not in checkers:
            issues.append(("MISSING_MANIFEST_CHECKER", entry))
    for entry in EXPECTED_MANIFEST["required_make_wrappers"]:
        if entry not in make_wrappers:
            issues.append(("MISSING_MANIFEST_WRAPPER", entry))
    for entry in EXPECTED_MANIFEST["required_notes"]:
        if entry not in notes:
            issues.append(("MISSING_MANIFEST_NOTE", entry))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues = collect_missing_paths(root)
    if issues:
        return issues

    bootstrap_notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    scripts_text = read_text(resolve_path(root, SCRIPTS_README))
    tests_text = read_text(resolve_path(root, TESTS_README))
    review_text = read_text(resolve_path(root, REVIEW_CHECKLIST))

    issues.extend(collect_missing_markers(bootstrap_notes_text, BOOTSTRAP_NOTE_MARKERS, "MISSING_BOOTSTRAP_NOTE_MARKER"))
    issues.extend(collect_forbidden_markers(bootstrap_notes_text, BOOTSTRAP_NOTE_FORBIDDEN_MARKERS, "FORBIDDEN_BOOTSTRAP_NOTE_MARKER"))
    issues.extend(collect_missing_exact_lines(workflow_text, WORKFLOW_MARKERS, "MISSING_WORKFLOW_MARKER"))
    issues.extend(collect_missing_markers(scripts_text, COMPANION_MARKERS, "MISSING_SCRIPTS_MARKER"))
    issues.extend(collect_missing_markers(tests_text, COMPANION_MARKERS, "MISSING_TESTS_MARKER"))
    issues.extend(collect_missing_markers(review_text, COMPANION_MARKERS, "MISSING_REVIEW_MARKER"))
    issues.extend(collect_manifest_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_BOOTSTRAP_NOTES_PACKET=fail")
    grouped: dict[str, list[str]] = {}
    for code, marker in issues:
        grouped.setdefault(code, []).append(marker)
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, content: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(BOOTSTRAP_NOTE_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(COMPANION_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(COMPANION_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(COMPANION_MARKERS) + "\n")
    write_json(
        resolve_path(root, TOOL_MANIFEST),
        {
            "phase": EXPECTED_MANIFEST["phase"],
            "status": EXPECTED_MANIFEST["status"],
            "workflow": EXPECTED_MANIFEST["workflow"],
            "present_surfaces": {
                "checkers": EXPECTED_MANIFEST["required_checkers"],
                "make_wrappers": EXPECTED_MANIFEST["required_make_wrappers"],
            },
            "notes": EXPECTED_MANIFEST["required_notes"],
        },
    )


def remove_marker(text: str, marker: str) -> str:
    exact_line = marker + "\n"
    if exact_line in text:
        return text.replace(exact_line, "", 1)
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(BOOTSTRAP_NOTE_MARKERS)
        + len(BOOTSTRAP_NOTE_FORBIDDEN_MARKERS)
        + len(WORKFLOW_MARKERS)
        + 3 * len(COMPANION_MARKERS)
        + len(EXPECTED_MANIFEST["required_checkers"])
        + len(EXPECTED_MANIFEST["required_make_wrappers"])
        + len(EXPECTED_MANIFEST["required_notes"])
        + len(REQUIRED_FILES)
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_note_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in BOOTSTRAP_NOTE_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert (("MISSING_BOOTSTRAP_NOTE_MARKER", marker)) in issues
            checks_run += 1

        for marker in BOOTSTRAP_NOTE_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert (("FORBIDDEN_BOOTSTRAP_NOTE_MARKER", marker)) in issues
            checks_run += 1

        for marker in WORKFLOW_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert (("MISSING_WORKFLOW_MARKER", marker)) in issues
            checks_run += 1

        for path in (SCRIPTS_README, TESTS_README, REVIEW_CHECKLIST):
            for marker in COMPANION_MARKERS:
                build_sample_root(root)
                target = resolve_path(root, path)
                target.write_text(remove_marker(target.read_text(encoding="utf-8"), marker), encoding="utf-8")
                issues = collect_issues(root)
                code = {
                    SCRIPTS_README: "MISSING_SCRIPTS_MARKER",
                    TESTS_README: "MISSING_TESTS_MARKER",
                    REVIEW_CHECKLIST: "MISSING_REVIEW_MARKER",
                }[path]
                assert ((code, marker)) in issues
                checks_run += 1

        for entry in EXPECTED_MANIFEST["required_checkers"]:
            build_sample_root(root)
            path = resolve_path(root, TOOL_MANIFEST)
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["present_surfaces"]["checkers"].remove(entry)
            write_json(path, manifest)
            issues = collect_issues(root)
            assert (("MISSING_MANIFEST_CHECKER", entry)) in issues
            checks_run += 1

        for entry in EXPECTED_MANIFEST["required_make_wrappers"]:
            build_sample_root(root)
            path = resolve_path(root, TOOL_MANIFEST)
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["present_surfaces"]["make_wrappers"].remove(entry)
            write_json(path, manifest)
            issues = collect_issues(root)
            assert (("MISSING_MANIFEST_WRAPPER", entry)) in issues
            checks_run += 1

        for entry in EXPECTED_MANIFEST["required_notes"]:
            build_sample_root(root)
            path = resolve_path(root, TOOL_MANIFEST)
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["notes"].remove(entry)
            write_json(path, manifest)
            issues = collect_issues(root)
            assert (("MISSING_MANIFEST_NOTE", entry)) in issues
            checks_run += 1

        for path in REQUIRED_FILES:
            build_sample_root(root)
            resolve_path(root, path).unlink()
            issues = collect_issues(root)
            assert (("MISSING_REQUIRED_FILE", str(path.relative_to(ROOT)))) in issues
            checks_run += 1

    assert checks_run == expected_case_count, (checks_run, expected_case_count)
    print("PHASE2_BOOTSTRAP_NOTES_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_NOTES_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(root: Path) -> int:
    build_sample_root(root)
    print(f"PHASE2_BOOTSTRAP_NOTES_PACKET_SAMPLE_ROOT={root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 2 bootstrap note packet aligned with the workflow, companion reminders, and tool manifest."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a synthetic passing root for local validation")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_NOTES_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_NOTES_PACKET_NOTE_MARKER_COUNT={len(BOOTSTRAP_NOTE_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_NOTES_PACKET_FORBIDDEN_MARKER_COUNT={len(BOOTSTRAP_NOTE_FORBIDDEN_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_NOTES_PACKET_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_NOTES_PACKET_COMPANION_MARKER_COUNT={len(COMPANION_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_NOTES_PACKET_MANIFEST_CHECKER_COUNT={len(EXPECTED_MANIFEST['required_checkers'])}")
    print(f"PHASE2_BOOTSTRAP_NOTES_PACKET_MANIFEST_WRAPPER_COUNT={len(EXPECTED_MANIFEST['required_make_wrappers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
