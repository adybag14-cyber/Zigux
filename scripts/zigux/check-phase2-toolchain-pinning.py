#!/usr/bin/env python3
"""Keep the current Phase 2 toolchain reminder packet aligned."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
ARCHIVE_README = "third_party/README.md"
BOOTSTRAP_NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
PHASE2_CLOSURE = "Documentation/zigux/phase2-closure.md"
REVIEW_CHECKLIST = "Documentation/zigux/review-checklist.md"
SCRIPTS_README = "scripts/zigux/README.md"
TESTS_README = "zigux/tests/README.md"
TOOL_MANIFEST = "zigux/tests/fixtures/phase2_tool_manifest.json"

ARCHIVE_TARGET = "x86_64-linux"
ARCHIVE_CHANNEL = "0.17.0-dev.87+9b177a7d2"
ARCHIVE_SIZE = 58_159_088
ARCHIVE_DIGEST = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"

WORKFLOW_SETUP = (
    "- name: Setup pinned Zig toolchain",
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    "if try_local_archive; then",
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    "echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
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
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

SURFACE_PATHS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    POLICY,
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "Documentation/zigux/README.md",
    "zigux/Makefile",
    TOOL_MANIFEST,
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
)
REVIEW_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`make -C zigux phase2-fixdep`",
)
PHASE2_CLOSURE_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-fixdep`",
)
BOOTSTRAP_PRESENT = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2`",
)
BOOTSTRAP_GAPS = (
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, archive-verification, staged-helper, or direct cross-route surfaces from the current packet.",
)

MANIFEST_CHECKS = {
    "archive_support": [
        "third_party/README.md",
        f"third_party/zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL}.tar.xz",
    ],
    "artifact_support": [
        "scripts/zigux/artifact_diff.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    ],
    "bootstrap_helpers": [
        "scripts/zigux/install-zig.py",
        "scripts/zigux/stage-pinned-zig-archive.py",
    ],
    "bridge_helpers": [
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "scripts/zigux/genksyms.zig",
        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
        "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    ],
    "checkers": [
        "scripts/zigux/check-zig-toolchain.py",
        "scripts/zigux/check-lane05-local-first-archive-workflow.py",
        "scripts/zigux/check-lane05-local-archive-readme.py",
        "scripts/zigux/check-lane05-install-zig-archive-verification.py",
        "scripts/zigux/check-lane05-stage-helper-contract.py",
        "scripts/zigux/check-lane05-stage-helper-selftest.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
        "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
        "scripts/zigux/check-phase2-kbuild-routes.py",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "scripts/zigux/check-phase2-toolchain-pinning.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "scripts/zigux/check-phase2-required-make-routes.py",
        "scripts/zigux/check-phase2-docs-shared-reminder.py",
        "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
        "scripts/zigux/check-phase2-tool-manifest.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
    ],
    "closure_notes": [
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    ],
    "cross_route_support": [
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    ],
    "make_wrappers": [
        "zigux/Makefile",
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ],
    "policy": [
        "scripts/zigux/zig-toolchain-policy.json",
    ],
    "review_surfaces": [
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/README.md",
        "zigux/tests/README.md",
    ],
    "validators": [
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
    ],
}

EXPECTED_SELF_TEST_CASE_COUNT = 126


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    start = text.find("\n", start)
    if start == -1:
        return ""
    end = text.find("\n## ", start + 1)
    return text[start + 1 :] if end == -1 else text[start + 1 : end]


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def archive_markers() -> tuple[str, ...]:
    filename = f"zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL}.tar.xz"
    return (
        f"`third_party/{filename}`",
        f"`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/{filename} --archive-target {ARCHIVE_TARGET}`",
        f"`{ARCHIVE_DIGEST}`",
        f"`{ARCHIVE_SIZE}`",
        f"`zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL} (1).tar.xz`",
        "repo-local pinned archive filename",
        "digest",
        "size",
        "duplicate-copy boundary",
        "archive-only",
    )


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow = read(root / WORKFLOW)
    lines = [line.strip() for line in workflow.splitlines()]
    for marker in WORKFLOW_SETUP:
        if marker not in workflow:
            issues.append(("MISSING_WORKFLOW_SETUP_MARKERS", marker))
    for marker in WORKFLOW_LINES:
        count = sum(1 for line in lines if line == marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in SCRIPTS_MARKERS:
        if marker not in read(root / SCRIPTS_README):
            issues.append(("MISSING_SCRIPTS_MARKERS", marker))
        if marker not in read(root / TESTS_README):
            issues.append(("MISSING_TESTS_MARKERS", marker))
    for marker in REVIEW_MARKERS:
        if marker not in read(root / REVIEW_CHECKLIST):
            issues.append(("MISSING_REVIEW_MARKERS", marker))
    for marker in PHASE2_CLOSURE_MARKERS:
        if marker not in read(root / PHASE2_CLOSURE):
            issues.append(("MISSING_PHASE2_CLOSURE_MARKERS", marker))

    notes = read(root / BOOTSTRAP_NOTES)
    for marker in BOOTSTRAP_PRESENT:
        if marker not in section(notes, "## Current direct packet"):
            issues.append(("MISSING_BOOTSTRAP_PRESENT_MARKERS", marker))
    for marker in BOOTSTRAP_GAPS:
        if marker not in section(notes, "## Current repo-reality gaps"):
            issues.append(("MISSING_BOOTSTRAP_GAP_MARKERS", marker))

    for path in SURFACE_PATHS:
        if not (root / path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path))

    policy = json.loads(read(root / POLICY))
    upgrade = policy.get("upgrade_policy", {})
    if policy.get("phase") != "Phase 2":
        issues.append(("POLICY_PHASE_MISMATCH", repr(policy.get("phase"))))
    if upgrade.get("channel_minimum_lockstep") is not True:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", repr(upgrade.get("channel_minimum_lockstep"))))
    if upgrade.get("archive_target_scope") != [ARCHIVE_TARGET]:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", repr(upgrade.get("archive_target_scope"))))
    if upgrade.get("required_make_routes") != [
        "phase2-toolchain",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2-genksyms",
        "phase2-fixdep",
        "phase2-validate",
    ]:
        issues.append(("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", repr(upgrade.get("required_make_routes"))))

    archive_readme = read(root / ARCHIVE_README)
    for marker in archive_markers():
        if marker not in archive_readme:
            issues.append(("MISSING_ARCHIVE_README_MARKERS", marker))
    duplicate = root / "third_party" / f"zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL} (1).tar.xz"
    if duplicate.exists():
        issues.append(("DUPLICATE_ARCHIVE_COPY", duplicate.name))

    manifest = json.loads(read(root / TOOL_MANIFEST))
    if manifest.get("phase") != "Phase 2":
        issues.append(("TOOL_MANIFEST_FIELD_MISMATCH", "phase"))
    if manifest.get("status") != "active":
        issues.append(("TOOL_MANIFEST_FIELD_MISMATCH", "status"))
    if manifest.get("workflow") != WORKFLOW:
        issues.append(("TOOL_MANIFEST_FIELD_MISMATCH", "workflow"))
    if manifest.get("repo_reality_gaps") != []:
        issues.append(("TOOL_MANIFEST_FIELD_MISMATCH", "repo_reality_gaps"))
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("TOOL_MANIFEST_FIELD_MISMATCH", "present_surfaces"))
    else:
        for bucket, required in MANIFEST_CHECKS.items():
            present = surfaces.get(bucket)
            if not isinstance(present, list):
                issues.append(("TOOL_MANIFEST_BUCKET_MISMATCH", bucket))
                continue
            for item in required:
                if item not in present:
                    issues.append(("TOOL_MANIFEST_BUCKET_MISMATCH", f"{bucket}:{item}"))
    return issues


def emit(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_PINNING=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write(root / WORKFLOW, "\n".join((*WORKFLOW_SETUP, *WORKFLOW_LINES)) + "\n")
    write(root / SCRIPTS_README, "\n".join(["# scripts", *SCRIPTS_MARKERS]) + "\n")
    write(root / TESTS_README, "\n".join(["# tests", *SCRIPTS_MARKERS]) + "\n")
    write(root / REVIEW_CHECKLIST, "\n".join(["# review", *REVIEW_MARKERS]) + "\n")
    write(root / PHASE2_CLOSURE, "\n".join(["# closure", *PHASE2_CLOSURE_MARKERS]) + "\n")
    write(root / BOOTSTRAP_NOTES, "\n".join(["# notes", "", "## Current direct packet", "", *BOOTSTRAP_PRESENT, "", "## Current repo-reality gaps", "", *BOOTSTRAP_GAPS, ""]))
    write(
        root / POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": ARCHIVE_CHANNEL,
                "minimum_version": ARCHIVE_CHANNEL,
                "archive_sha256": {ARCHIVE_TARGET: ARCHIVE_DIGEST},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [ARCHIVE_TARGET],
                    "required_make_routes": [
                        "phase2-toolchain",
                        "phase2-tools",
                        "phase2-kconfig",
                        "phase2-cross",
                        "phase2-genksyms",
                        "phase2-fixdep",
                        "phase2-validate",
                    ],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write(root / ARCHIVE_README, "\n".join(("# third_party", "", *archive_markers(), "")))
    for path in SURFACE_PATHS:
        if path in {POLICY, WORKFLOW, ARCHIVE_README, BOOTSTRAP_NOTES, PHASE2_CLOSURE, REVIEW_CHECKLIST, SCRIPTS_README, TESTS_README, TOOL_MANIFEST}:
            continue
        write(root / path, "present\n")
    write(
        root / TOOL_MANIFEST,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "workflow": WORKFLOW,
                "repo_reality_gaps": [],
                "present_surfaces": MANIFEST_CHECKS,
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_pinning_") as tmp:
        root = Path(tmp)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        workflow_path = root / WORKFLOW
        for marker in WORKFLOW_SETUP:
            build_self_test_root(root)
            workflow_path.write_text(replace_exact_line(read(workflow_path), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_SETUP_MARKERS", marker) in collect_issues(root)
            checks += 1
        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path.write_text(replace_exact_line(read(workflow_path), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_HOOKS", marker) in collect_issues(root)
            checks += 1
        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path.write_text(replace_exact_line(read(workflow_path), marker, marker + "\n" + marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        manifest_path = root / TOOL_MANIFEST
        manifest = json.loads(read(manifest_path))
        manifest["present_surfaces"]["bridge_helpers"].pop()
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "TOOL_MANIFEST_BUCKET_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        manifest_path = root / TOOL_MANIFEST
        manifest = json.loads(read(manifest_path))
        manifest["present_surfaces"]["checkers"].pop()
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "TOOL_MANIFEST_BUCKET_MISMATCH" and value.startswith("checkers:") for code, value in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        manifest_path = root / TOOL_MANIFEST
        manifest = json.loads(read(manifest_path))
        manifest["present_surfaces"]["make_wrappers"].pop()
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "TOOL_MANIFEST_BUCKET_MISMATCH" and value.startswith("make_wrappers:") for code, value in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        manifest_path = root / TOOL_MANIFEST
        manifest = json.loads(read(manifest_path))
        manifest["present_surfaces"]["review_surfaces"].pop()
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "TOOL_MANIFEST_BUCKET_MISMATCH" and value.startswith("review_surfaces:") for code, value in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        policy_path = root / POLICY
        policy = json.loads(read(policy_path))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        write(policy_path, json.dumps(policy, indent=2) + "\n")
        assert any(code == "POLICY_REQUIRED_MAKE_ROUTES_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write(root / "third_party" / f"zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL} (1).tar.xz", "dup\n")
        assert any(code == "DUPLICATE_ARCHIVE_COPY" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux/check-phase2-tool-manifest.py").unlink()
        assert ("MISSING_SURFACE_PATHS", "scripts/zigux/check-phase2-tool-manifest.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        notes_path = root / BOOTSTRAP_NOTES
        notes_path.write_text(read(notes_path).replace(BOOTSTRAP_GAPS[0], "", 1), encoding="utf-8")
        assert any(code == "MISSING_BOOTSTRAP_GAP_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        review_path = root / REVIEW_CHECKLIST
        review_path.write_text(read(review_path).replace(REVIEW_MARKERS[-1], "", 1), encoding="utf-8")
        assert any(code == "MISSING_REVIEW_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        scripts_path = root / SCRIPTS_README
        scripts_path.write_text(read(scripts_path).replace(SCRIPTS_MARKERS[0], "", 1), encoding="utf-8")
        assert any(code == "MISSING_SCRIPTS_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        scripts_path = root / SCRIPTS_README
        scripts_path.write_text(read(scripts_path).replace(SCRIPTS_MARKERS[1], "", 1), encoding="utf-8")
        assert ("MISSING_SCRIPTS_MARKERS", SCRIPTS_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        tests_path = root / TESTS_README
        tests_path.write_text(read(tests_path).replace(SCRIPTS_MARKERS[3], "", 1), encoding="utf-8")
        assert ("MISSING_TESTS_MARKERS", SCRIPTS_MARKERS[3]) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_PINNING_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_SELF_TEST_CASE_COUNT={checks}")
    print(f"PHASE2_TOOLCHAIN_PINNING_SURFACE_PATH_COUNT={len(SURFACE_PATHS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the current directly readable Phase 2 toolchain pinning packet aligned.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit(issues)
    print("PHASE2_TOOLCHAIN_PINNING=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_REQUIRED_MARKER_COUNT={len(BOOTSTRAP_PRESENT)}")
    print(f"PHASE2_TOOLCHAIN_PINNING_GAP_MARKER_COUNT={len(BOOTSTRAP_GAPS)}")
    print("PHASE2_TOOLCHAIN_PINNING_ARCHIVE_README_MARKER_COUNT=10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
