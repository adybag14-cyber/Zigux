#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 toolchain pinning packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
THIRD_PARTY_README = "third_party/README.md"
BOOTSTRAP_NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
PHASE2_CLOSURE = "Documentation/zigux/phase2-closure.md"
REVIEW_CHECKLIST = "Documentation/zigux/review-checklist.md"
SCRIPTS_README = "scripts/zigux/README.md"
TESTS_README = "zigux/tests/README.md"
TOOL_MANIFEST = "zigux/tests/fixtures/phase2_tool_manifest.json"
ARCHIVE_TARGET = "x86_64-linux"
ARCHIVE_CHANNEL = "0.17.0-dev.87+9b177a7d2"
ARCHIVE_SIZE = 58_159_088
EXPECTED_SELF_TEST_CASE_COUNT = 51

GENKSYMS_EXPECTED = (
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
)

SURFACE_PATHS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "scripts/zigux/fixdep.zig",
    THIRD_PARTY_README,
    "zigux/Makefile",
    POLICY,
    BOOTSTRAP_NOTES,
    PHASE2_CLOSURE,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    TOOL_MANIFEST,
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/fixdep/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    *GENKSYMS_EXPECTED,
)

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
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "run: make -C zigux phase2-fixdep",
    "run: python3 scripts/zigux/validate-phase2.py",
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
)

REVIEW_MARKERS = SCRIPTS_MARKERS + ("`make -C zigux phase2-fixdep`",)
PHASE2_CLOSURE_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-fixdep`",
)
BOOTSTRAP_PRESENT = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2`",
)
BOOTSTRAP_GAPS = (
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, archive-verification, staged-helper, or direct cross-route surfaces from the current packet.",
)

MANIFEST_BUCKETS = {
    "archive_support": ("third_party/README.md", f"third_party/zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL}.tar.xz"),
    "bootstrap_helpers": ("scripts/zigux/install-zig.py", "scripts/zigux/stage-pinned-zig-archive.py"),
    "bridge_helpers": (
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "scripts/zigux/genksyms.zig",
        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
        "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    ),
    "checkers": ("scripts/zigux/check-phase2-bootstrap-workflow-routes.py",),
    "artifact_support": (
        "scripts/zigux/artifact_diff.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    ),
    "cross_route_support": ("scripts/zigux/check-phase2-cross.py", "zigux/tests/fixtures/phase2_cross_targets.json"),
    "validators": ("scripts/zigux/validate-phase2.py", "scripts/zigux/validate-phase2-closure.py"),
    "make_wrappers": (
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ),
    "fixture_roster": (
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
        "zigux/tests/fixtures/genksyms_bridge/cases.json",
        *GENKSYMS_EXPECTED,
    ),
}

POLICY_EXPECTED = {
    "phase": "Phase 2",
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
}


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    start = text.find("\n", start)
    if start == -1:
        return ""
    end = text.find("\n## ", start + 1)
    return text[start + 1 :] if end == -1 else text[start + 1 : end]


def archive_markers() -> tuple[str, ...]:
    filename = f"zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL}.tar.xz"
    return (
        f"`third_party/{filename}`",
        f"`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/{filename} --archive-target {ARCHIVE_TARGET}`",
        "`" + ("3" * 64) + "`",
        f"`{ARCHIVE_SIZE}`",
        f"`zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL} (1).tar.xz`",
        "repo-local pinned archive filename",
        "digest",
        "size",
        "duplicate-copy boundary",
        "archive-only",
    )


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(resolve(root, POLICY)))
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]
    upgrade = payload.get("upgrade_policy")
    issues = []
    if payload.get("phase") != POLICY_EXPECTED["phase"]:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))
    if not isinstance(upgrade, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade).__name__)]
    if upgrade.get("channel_minimum_lockstep") is not POLICY_EXPECTED["channel_minimum_lockstep"]:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", repr(upgrade.get("channel_minimum_lockstep"))))
    if upgrade.get("archive_target_scope") != POLICY_EXPECTED["archive_target_scope"]:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", repr(upgrade.get("archive_target_scope"))))
    if upgrade.get("required_make_routes") != POLICY_EXPECTED["required_make_routes"]:
        issues.append(("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", repr(upgrade.get("required_make_routes"))))
    return issues


def collect_archive_issues(root: Path) -> list[tuple[str, str]]:
    readme = read_text(resolve(root, THIRD_PARTY_README))
    issues = collect_missing_markers(readme, archive_markers(), "MISSING_ARCHIVE_README_MARKERS")
    duplicate = resolve(root, "third_party") / f"zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL} (1).tar.xz"
    if duplicate.exists():
        issues.append(("DUPLICATE_ARCHIVE_COPY", duplicate.name))
    return issues


def expected_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 2",
        "status": "active",
        "workflow": WORKFLOW,
        "repo_reality_gaps": [],
        "present_surfaces": {key: list(values) for key, values in MANIFEST_BUCKETS.items()},
    }


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(resolve(root, TOOL_MANIFEST)))
    if not isinstance(payload, dict):
        return [("INVALID_TOOL_MANIFEST_PAYLOAD", type(payload).__name__)]
    issues = []
    for key in ("phase", "status", "workflow", "repo_reality_gaps"):
        if payload.get(key) != expected_manifest()[key]:
            issues.append(("TOOL_MANIFEST_FIELD_MISMATCH", key))
    surfaces = payload.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return issues + [("TOOL_MANIFEST_FIELD_MISMATCH", "present_surfaces")]
    for bucket, required in MANIFEST_BUCKETS.items():
        present = surfaces.get(bucket)
        if not isinstance(present, list):
            issues.append(("TOOL_MANIFEST_BUCKET_MISMATCH", bucket))
            continue
        missing = next((item for item in required if item not in present), None)
        if missing:
            issues.append(("TOOL_MANIFEST_BUCKET_MISMATCH", f"{bucket}:{missing}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues = []
    workflow = read_text(resolve(root, WORKFLOW))
    notes = read_text(resolve(root, BOOTSTRAP_NOTES))
    issues.extend(collect_missing_markers(read_text(resolve(root, SCRIPTS_README)), SCRIPTS_MARKERS, "MISSING_SCRIPTS_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve(root, REVIEW_CHECKLIST)), REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve(root, TESTS_README)), SCRIPTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve(root, PHASE2_CLOSURE)), PHASE2_CLOSURE_MARKERS, "MISSING_PHASE2_CLOSURE_MARKERS"))
    issues.extend(collect_missing_markers(workflow, WORKFLOW_SETUP, "MISSING_WORKFLOW_SETUP_MARKERS"))
    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))
    issues.extend(collect_missing_markers(section(notes, "## Current direct packet"), BOOTSTRAP_PRESENT, "MISSING_BOOTSTRAP_PRESENT_MARKERS"))
    issues.extend(collect_missing_markers(section(notes, "## Current repo-reality gaps"), BOOTSTRAP_GAPS, "MISSING_BOOTSTRAP_GAP_MARKERS"))
    for rel in SURFACE_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_SURFACE_PATHS", rel))
    issues.extend(collect_policy_issues(root))
    issues.extend(collect_archive_issues(root))
    issues.extend(collect_manifest_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
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
    write_text(resolve(root, WORKFLOW), "\n".join((*WORKFLOW_SETUP, *WORKFLOW_LINES)) + "\n")
    write_text(resolve(root, SCRIPTS_README), "\n".join(["# scripts", *SCRIPTS_MARKERS]) + "\n")
    write_text(resolve(root, REVIEW_CHECKLIST), "\n".join(["# review", *REVIEW_MARKERS]) + "\n")
    write_text(resolve(root, TESTS_README), "\n".join(["# tests", *SCRIPTS_MARKERS]) + "\n")
    write_text(resolve(root, PHASE2_CLOSURE), "\n".join(["# closure", *PHASE2_CLOSURE_MARKERS]) + "\n")
    write_text(
        resolve(root, BOOTSTRAP_NOTES),
        "\n".join(["# notes", "", "## Current direct packet", "", *BOOTSTRAP_PRESENT, "", "## Current repo-reality gaps", "", *BOOTSTRAP_GAPS, ""]),
    )
    for rel in SURFACE_PATHS:
        if rel == POLICY:
            write_text(
                resolve(root, rel),
                json.dumps(
                    {
                        "phase": "Phase 2",
                        "channel": ARCHIVE_CHANNEL,
                        "minimum_version": ARCHIVE_CHANNEL,
                        "archive_sha256": {ARCHIVE_TARGET: "3" * 64},
                        "upgrade_policy": {
                            "channel_minimum_lockstep": True,
                            "archive_target_scope": [ARCHIVE_TARGET],
                            "required_make_routes": POLICY_EXPECTED["required_make_routes"],
                        },
                    },
                    indent=2,
                )
                + "\n",
            )
        elif rel == TOOL_MANIFEST:
            write_text(resolve(root, rel), json.dumps(expected_manifest(), indent=2) + "\n")
        elif rel == THIRD_PARTY_README:
            write_text(resolve(root, rel), "\n".join(("# third_party", "", *archive_markers(), "")))
        elif rel in {BOOTSTRAP_NOTES, PHASE2_CLOSURE, REVIEW_CHECKLIST, SCRIPTS_README, TESTS_README}:
            continue
        else:
            write_text(resolve(root, rel), "present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_pinning_") as tmp:
        root = Path(tmp)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in WORKFLOW_SETUP:
            build_self_test_root(root)
            path = resolve(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_SETUP_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_HOOKS", marker) in collect_issues(root)
            checks += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, marker + "\n" + marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        manifest = json.loads(read_text(resolve(root, TOOL_MANIFEST)))
        manifest["present_surfaces"]["fixture_roster"].remove(GENKSYMS_EXPECTED[10])
        write_text(resolve(root, TOOL_MANIFEST), json.dumps(manifest, indent=2) + "\n")
        assert any(code == "TOOL_MANIFEST_BUCKET_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        manifest = json.loads(read_text(resolve(root, TOOL_MANIFEST)))
        manifest["present_surfaces"]["checkers"].remove("scripts/zigux/check-phase2-bootstrap-workflow-routes.py")
        write_text(resolve(root, TOOL_MANIFEST), json.dumps(manifest, indent=2) + "\n")
        assert ("TOOL_MANIFEST_BUCKET_MISMATCH", "checkers:scripts/zigux/check-phase2-bootstrap-workflow-routes.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        policy = json.loads(read_text(resolve(root, POLICY)))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        write_text(resolve(root, POLICY), json.dumps(policy, indent=2) + "\n")
        assert any(code == "POLICY_REQUIRED_MAKE_ROUTES_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        readme = resolve(root, THIRD_PARTY_README)
        readme.write_text(readme.read_text(encoding="utf-8").replace("duplicate-copy boundary", ""), encoding="utf-8")
        assert any(code == "MISSING_ARCHIVE_README_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(resolve(root, "third_party") / f"zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL} (1).tar.xz", "duplicate\n")
        assert any(code == "DUPLICATE_ARCHIVE_COPY" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        resolve(root, "scripts/zigux/check-phase2-tool-manifest.py").unlink()
        assert ("MISSING_SURFACE_PATHS", "scripts/zigux/check-phase2-tool-manifest.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        resolve(root, "scripts/zigux/check-phase2-bootstrap-workflow-routes.py").unlink()
        assert ("MISSING_SURFACE_PATHS", "scripts/zigux/check-phase2-bootstrap-workflow-routes.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        resolve(root, "scripts/zigux/check-phase2-kconfig-selftest-alignment.py").unlink()
        assert ("MISSING_SURFACE_PATHS", "scripts/zigux/check-phase2-kconfig-selftest-alignment.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        resolve(root, "scripts/zigux/check-phase2-cross.py").unlink()
        assert ("MISSING_SURFACE_PATHS", "scripts/zigux/check-phase2-cross.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        resolve(root, "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig").unlink()
        assert ("MISSING_SURFACE_PATHS", "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        resolve(root, "scripts/zigux/artifact_diff.py").unlink()
        assert ("MISSING_SURFACE_PATHS", "scripts/zigux/artifact_diff.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        resolve(root, GENKSYMS_EXPECTED[10]).unlink()
        assert ("MISSING_SURFACE_PATHS", GENKSYMS_EXPECTED[10]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        notes = resolve(root, BOOTSTRAP_NOTES)
        notes.write_text(
            notes.read_text(encoding="utf-8").replace("`scripts/zigux/check-phase2-tool-manifest.py`", ""),
            encoding="utf-8",
        )
        assert any(code == "MISSING_BOOTSTRAP_PRESENT_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        notes = resolve(root, BOOTSTRAP_NOTES)
        notes.write_text(
            notes.read_text(encoding="utf-8").replace("`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`", ""),
            encoding="utf-8",
        )
        assert ("MISSING_BOOTSTRAP_PRESENT_MARKERS", "`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        notes = resolve(root, BOOTSTRAP_NOTES)
        notes.write_text(
            notes.read_text(encoding="utf-8").replace("`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`", ""),
            encoding="utf-8",
        )
        assert ("MISSING_BOOTSTRAP_PRESENT_MARKERS", "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        notes = resolve(root, BOOTSTRAP_NOTES)
        notes.write_text(notes.read_text(encoding="utf-8").replace(BOOTSTRAP_GAPS[0], ""), encoding="utf-8")
        assert any(code == "MISSING_BOOTSTRAP_GAP_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        review = resolve(root, REVIEW_CHECKLIST)
        review.write_text(review.read_text(encoding="utf-8").replace(REVIEW_MARKERS[-1], ""), encoding="utf-8")
        assert any(code == "MISSING_REVIEW_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        closure = resolve(root, PHASE2_CLOSURE)
        closure.write_text(closure.read_text(encoding="utf-8").replace(PHASE2_CLOSURE_MARKERS[-1], ""), encoding="utf-8")
        assert any(code == "MISSING_PHASE2_CLOSURE_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        tests = resolve(root, TESTS_README)
        tests.write_text(tests.read_text(encoding="utf-8").replace(SCRIPTS_MARKERS[0], ""), encoding="utf-8")
        assert any(code == "MISSING_TESTS_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        tests = resolve(root, TESTS_README)
        tests.write_text(tests.read_text(encoding="utf-8").replace(SCRIPTS_MARKERS[2], ""), encoding="utf-8")
        assert ("MISSING_TESTS_MARKERS", SCRIPTS_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        scripts = resolve(root, SCRIPTS_README)
        scripts.write_text(scripts.read_text(encoding="utf-8").replace(SCRIPTS_MARKERS[0], ""), encoding="utf-8")
        assert any(code == "MISSING_SCRIPTS_MARKERS" for code, _ in collect_issues(root))
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_PINNING_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_SELF_TEST_CASE_COUNT={checks}")
    print("PHASE2_TOOLCHAIN_PINNING_MANIFEST_SYNC=pass")
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
        return emit_issues(issues)
    print("PHASE2_TOOLCHAIN_PINNING=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_REQUIRED_MARKER_COUNT={len(BOOTSTRAP_PRESENT)}")
    print(f"PHASE2_TOOLCHAIN_PINNING_GAP_MARKER_COUNT={len(BOOTSTRAP_GAPS)}")
    print("PHASE2_TOOLCHAIN_PINNING_ARCHIVE_README_MARKER_COUNT=10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
