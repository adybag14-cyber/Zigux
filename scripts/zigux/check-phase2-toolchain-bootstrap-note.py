#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
THIRD_PARTY_README = Path("third_party/README.md")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
MAKEFILE = Path("zigux/Makefile")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/artifact_diff.py`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

PHASE2_CLOSURE_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`",
)

THIRD_PARTY_README_MARKERS = (
    "file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "size: `58159088` bytes",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py --self-test",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "phase2-genksyms:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "phase2-fixdep:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-fixdep-gate.py --self-test",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test",
)

POLICY_REQUIRED_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

MANIFEST_PHASE = "Phase 2"
MANIFEST_STATUS = "active"
MANIFEST_SCOPE = (
    "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, "
    "kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet"
)
MANIFEST_WORKFLOW = ".github/workflows/zigux-bootstrap.yml"

MANIFEST_ARCHIVE_SUPPORT = (
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
)
MANIFEST_BOOTSTRAP_HELPERS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
)
MANIFEST_CHECKERS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
)
MANIFEST_MAKE_WRAPPERS = (
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)
MANIFEST_CLOSURE_NOTES = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
)
MANIFEST_REVIEW_SURFACES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)
MANIFEST_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)
MANIFEST_CROSS_ROUTE_SUPPORT = (
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)
MANIFEST_POLICY = ("scripts/zigux/zig-toolchain-policy.json",)


def read_text(root: Path, rel_path: Path) -> str:
    path = root / rel_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(root: Path, rel_path: Path) -> dict[str, object]:
    path = root / rel_path
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def require_string_list(
    issues: list[tuple[str, str]],
    present_surfaces: dict[str, object],
    key: str,
) -> list[str] | None:
    value = present_surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(entry, str) for entry in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return value


def require_manifest_members(
    issues: list[tuple[str, str]],
    values: list[str] | None,
    required: tuple[str, ...],
    code: str,
) -> None:
    if values is None:
        return
    for marker in required:
        if marker not in values:
            issues.append((code, marker))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    phase2_notes_text = read_text(root, PHASE2_NOTES)
    phase2_closure_text = read_text(root, PHASE2_CLOSURE)
    third_party_readme_text = read_text(root, THIRD_PARTY_README)
    makefile_text = read_text(root, MAKEFILE)
    manifest = read_json(root, PHASE2_TOOL_MANIFEST)
    policy = read_json(root, TOOLCHAIN_POLICY)

    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_markers(phase2_notes_text, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKER"))
    issues.extend(collect_missing_markers(phase2_closure_text, PHASE2_CLOSURE_MARKERS, "MISSING_PHASE2_CLOSURE_MARKER"))
    issues.extend(collect_missing_markers(third_party_readme_text, THIRD_PARTY_README_MARKERS, "MISSING_THIRD_PARTY_README_MARKER"))
    issues.extend(collect_missing_markers(makefile_text, MAKEFILE_MARKERS, "MISSING_MAKEFILE_MARKER"))

    if manifest.get("phase") != MANIFEST_PHASE:
        issues.append(("INVALID_MANIFEST_PHASE", str(manifest.get("phase"))))
    if manifest.get("status") != MANIFEST_STATUS:
        issues.append(("INVALID_MANIFEST_STATUS", str(manifest.get("status"))))
    if manifest.get("scope") != MANIFEST_SCOPE:
        issues.append(("INVALID_MANIFEST_SCOPE", str(manifest.get("scope"))))
    if manifest.get("workflow") != MANIFEST_WORKFLOW:
        issues.append(("INVALID_MANIFEST_WORKFLOW", str(manifest.get("workflow"))))
    if manifest.get("repo_reality_gaps") != []:
        issues.append(("INVALID_MANIFEST_REPO_REALITY_GAPS", json.dumps(manifest.get("repo_reality_gaps"))))

    if policy.get("phase") != "Phase 2":
        issues.append(("INVALID_POLICY_PHASE", str(policy.get("phase"))))
    if policy.get("channel") != "0.17.0-dev.87+9b177a7d2":
        issues.append(("INVALID_POLICY_CHANNEL", str(policy.get("channel"))))
    if policy.get("minimum_version") != "0.17.0-dev.87+9b177a7d2":
        issues.append(("INVALID_POLICY_MINIMUM_VERSION", str(policy.get("minimum_version"))))

    archive_sha = policy.get("archive_sha256")
    if not isinstance(archive_sha, dict) or archive_sha.get("x86_64-linux") != "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77":
        issues.append(("INVALID_POLICY_ARCHIVE_SHA", json.dumps(archive_sha, sort_keys=True)))

    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_UPGRADE_POLICY", str(type(upgrade_policy).__name__)))
    else:
        if upgrade_policy.get("channel_minimum_lockstep") is not True:
            issues.append(("INVALID_POLICY_LOCKSTEP", str(upgrade_policy.get("channel_minimum_lockstep"))))
        if upgrade_policy.get("archive_target_scope") != ["x86_64-linux"]:
            issues.append(("INVALID_POLICY_ARCHIVE_SCOPE", json.dumps(upgrade_policy.get("archive_target_scope"))))
        if upgrade_policy.get("required_make_routes") != list(POLICY_REQUIRED_ROUTES):
            issues.append(("INVALID_POLICY_REQUIRED_ROUTES", json.dumps(upgrade_policy.get("required_make_routes"))))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return issues

    archive_support = require_string_list(issues, present_surfaces, "archive_support")
    bootstrap_helpers = require_string_list(issues, present_surfaces, "bootstrap_helpers")
    checkers = require_string_list(issues, present_surfaces, "checkers")
    make_wrappers = require_string_list(issues, present_surfaces, "make_wrappers")
    closure_notes = require_string_list(issues, present_surfaces, "closure_notes")
    review_surfaces = require_string_list(issues, present_surfaces, "review_surfaces")
    validators = require_string_list(issues, present_surfaces, "validators")
    cross_route_support = require_string_list(issues, present_surfaces, "cross_route_support")
    policy_surfaces = require_string_list(issues, present_surfaces, "policy")

    require_manifest_members(issues, archive_support, MANIFEST_ARCHIVE_SUPPORT, "MISSING_MANIFEST_ARCHIVE_SUPPORT")
    require_manifest_members(issues, bootstrap_helpers, MANIFEST_BOOTSTRAP_HELPERS, "MISSING_MANIFEST_BOOTSTRAP_HELPER")
    require_manifest_members(issues, checkers, MANIFEST_CHECKERS, "MISSING_MANIFEST_CHECKER")
    require_manifest_members(issues, make_wrappers, MANIFEST_MAKE_WRAPPERS, "MISSING_MANIFEST_MAKE_WRAPPER")
    require_manifest_members(issues, closure_notes, MANIFEST_CLOSURE_NOTES, "MISSING_MANIFEST_CLOSURE_NOTE")
    require_manifest_members(issues, review_surfaces, MANIFEST_REVIEW_SURFACES, "MISSING_MANIFEST_REVIEW_SURFACE")
    require_manifest_members(issues, validators, MANIFEST_VALIDATORS, "MISSING_MANIFEST_VALIDATOR")
    require_manifest_members(issues, cross_route_support, MANIFEST_CROSS_ROUTE_SUPPORT, "MISSING_MANIFEST_CROSS_ROUTE_SUPPORT")
    require_manifest_members(issues, policy_surfaces, MANIFEST_POLICY, "MISSING_MANIFEST_POLICY_SURFACE")

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(root: Path, rel_path: Path, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(root: Path, rel_path: Path, payload: dict[str, object]) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(root, PHASE2_NOTES, "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(root, PHASE2_CLOSURE, "\n".join(PHASE2_CLOSURE_MARKERS) + "\n")
    write_text(root, THIRD_PARTY_README, "\n".join(THIRD_PARTY_README_MARKERS) + "\n")
    write_text(root, MAKEFILE, "\n".join(MAKEFILE_MARKERS) + "\n")
    write_json(
        root,
        PHASE2_TOOL_MANIFEST,
        {
            "phase": MANIFEST_PHASE,
            "status": MANIFEST_STATUS,
            "scope": MANIFEST_SCOPE,
            "workflow": MANIFEST_WORKFLOW,
            "repo_reality_gaps": [],
            "present_surfaces": {
                "archive_support": list(MANIFEST_ARCHIVE_SUPPORT),
                "bootstrap_helpers": list(MANIFEST_BOOTSTRAP_HELPERS),
                "checkers": list(MANIFEST_CHECKERS),
                "make_wrappers": list(MANIFEST_MAKE_WRAPPERS),
                "closure_notes": list(MANIFEST_CLOSURE_NOTES),
                "review_surfaces": list(MANIFEST_REVIEW_SURFACES),
                "validators": list(MANIFEST_VALIDATORS),
                "cross_route_support": list(MANIFEST_CROSS_ROUTE_SUPPORT),
                "policy": list(MANIFEST_POLICY),
            },
        },
    )
    write_json(
        root,
        TOOLCHAIN_POLICY,
        {
            "phase": "Phase 2",
            "channel": "0.17.0-dev.87+9b177a7d2",
            "minimum_version": "0.17.0-dev.87+9b177a7d2",
            "archive_sha256": {
                "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
            },
            "upgrade_policy": {
                "channel_minimum_lockstep": True,
                "archive_target_scope": ["x86_64-linux"],
                "required_make_routes": list(POLICY_REQUIRED_ROUTES),
            },
        },
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 9

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_bootstrap_note_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        note_path = root / PHASE2_NOTES
        note_path.write_text(replace_once(note_path.read_text(encoding="utf-8"), PHASE2_NOTES_MARKERS[0]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_PHASE2_NOTES_MARKER", PHASE2_NOTES_MARKERS[0]) in issues, issues
        build_sample_root(root)
        checks_run += 1

        closure_path = root / PHASE2_CLOSURE
        closure_path.write_text(replace_once(closure_path.read_text(encoding="utf-8"), PHASE2_CLOSURE_MARKERS[0]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_PHASE2_CLOSURE_MARKER", PHASE2_CLOSURE_MARKERS[0]) in issues, issues
        build_sample_root(root)
        checks_run += 1

        readme_path = root / THIRD_PARTY_README
        readme_path.write_text(replace_once(readme_path.read_text(encoding="utf-8"), THIRD_PARTY_README_MARKERS[0]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_THIRD_PARTY_README_MARKER", THIRD_PARTY_README_MARKERS[0]) in issues, issues
        build_sample_root(root)
        checks_run += 1

        makefile_path = root / MAKEFILE
        makefile_path.write_text(replace_once(makefile_path.read_text(encoding="utf-8"), MAKEFILE_MARKERS[0]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_MARKER", MAKEFILE_MARKERS[0]) in issues, issues
        build_sample_root(root)
        checks_run += 1

        manifest = read_json(root, PHASE2_TOOL_MANIFEST)
        manifest["present_surfaces"]["checkers"] = []
        write_json(root, PHASE2_TOOL_MANIFEST, manifest)
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_CHECKER", MANIFEST_CHECKERS[0]) in issues, issues
        build_sample_root(root)
        checks_run += 1

        manifest = read_json(root, PHASE2_TOOL_MANIFEST)
        manifest["repo_reality_gaps"] = ["stale-gap"]
        write_json(root, PHASE2_TOOL_MANIFEST, manifest)
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_REPO_REALITY_GAPS", json.dumps(["stale-gap"])) in issues, issues
        build_sample_root(root)
        checks_run += 1

        policy = read_json(root, TOOLCHAIN_POLICY)
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        write_json(root, TOOLCHAIN_POLICY, policy)
        issues = collect_issues(root)
        assert ("INVALID_POLICY_REQUIRED_ROUTES", json.dumps(["phase2-toolchain"])) in issues, issues
        build_sample_root(root)
        checks_run += 1

        (root / PHASE2_NOTES).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing note file did not abort")
        checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 toolchain bootstrap note aligned with the current shared reminder packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in regression checks")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root for focused replay")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE=pass")
    print(
        "PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_MARKER_COUNT="
        f"{len(PHASE2_NOTES_MARKERS) + len(PHASE2_CLOSURE_MARKERS) + len(THIRD_PARTY_README_MARKERS) + len(MAKEFILE_MARKERS)}"
    )
    print(
        "PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_MANIFEST_MEMBER_COUNT="
        f"{len(MANIFEST_ARCHIVE_SUPPORT) + len(MANIFEST_BOOTSTRAP_HELPERS) + len(MANIFEST_CHECKERS) + len(MANIFEST_MAKE_WRAPPERS) + len(MANIFEST_CLOSURE_NOTES) + len(MANIFEST_REVIEW_SURFACES) + len(MANIFEST_VALIDATORS) + len(MANIFEST_CROSS_ROUTE_SUPPORT) + len(MANIFEST_POLICY)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
