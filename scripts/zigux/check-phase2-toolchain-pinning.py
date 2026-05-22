#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 toolchain pinning packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
POLICY_PATH = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST_PATH = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}
ARCHIVE_README_REQUIRED_MARKER_COUNT = 10
SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
    ROOT / "scripts" / "zigux" / "install-zig.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-first-archive-workflow.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-archive-readme.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-required-make-routes.py",
    ROOT / "scripts" / "zigux" / "check-phase2-docs-shared-reminder.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-artifact-tools-manifest.py",
    ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py",
    ROOT / "scripts" / "zigux" / "check-fixdep-diff.py",
    ROOT / "scripts" / "zigux" / "validate-phase2.py",
    ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    ROOT / "scripts" / "zigux" / "genksyms.zig",
    ROOT / "scripts" / "zigux" / "fixdep.zig",
    THIRD_PARTY_README,
    ROOT / "zigux" / "Makefile",
    POLICY_PATH,
    BOOTSTRAP_NOTES,
    PHASE2_CLOSURE,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    TOOL_MANIFEST_PATH,
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "help_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "minimal_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "debug_reference_types_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "long_options_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "abbreviated_long_options_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "quiet_overrides_warning_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "explicit_option_terminator_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "positional_passthrough_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "lone_dash_passthrough_expected.json",
)

WORKFLOW_SETUP_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'if try_local_archive; then',
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
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
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: make -C zigux phase2-fixdep",
    "run: python3 scripts/zigux/validate-phase2.py",
)

BOOTSTRAP_PRESENT_MARKERS = (
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`third_party/README.md`",
    ".github/workflows/zigux-bootstrap.yml",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "the `zigux/tests/fixtures/kconfig_bridge/` manifest roster",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` is directly readable on current `master` and keeps the fixture-backed artifact-support packet explicit beside `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`.",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

BOOTSTRAP_GAP_MARKERS = (
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
    "Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, or direct cross-route surfaces from the current packet.",
)

PHASE2_CLOSURE_MARKERS = (
    "`third_party/README.md`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "The current closure-side packet keeps the fixdep governance and parity checker pair explicit through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`, so same-lane follow-through should stay tied to the toolchain, local-first archive, cross-route, kconfig, manifest-guard, genksyms, make-wrapper, fixdep, and validator packet that the repo still ships directly.",
    "- `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "- `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "- `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "- `python3 scripts/zigux/check-lane05-local-archive-readme.py`",
    "- `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-fixdep-gate.py`",
    "- `python3 scripts/zigux/check-fixdep-diff.py --self-test`",
    "- `python3 scripts/zigux/check-fixdep-diff.py`",
    "- `make -C zigux phase2-fixdep`",
    "`PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`",
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
)

REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-fixdep`",
)

TESTS_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
)

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel_minimum_lockstep": True,
    "archive_target_scope": ["x86_64-linux"],
    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
}

EXPECTED_TOOL_MANIFEST = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
    "present_surfaces": {
        "review_surfaces": [
            "Documentation/zigux/README.md",
            "Documentation/zigux/phase2-closure.md",
            "Documentation/zigux/review-checklist.md",
            "zigux/tests/README.md",
        ],
        "closure_notes": [
            "Documentation/zigux/phase2-closure.md",
            "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        ],
        "validators": [
            "scripts/zigux/validate-phase2.py",
            "scripts/zigux/validate-phase2-closure.py",
        ],
        "checkers": [
            "scripts/zigux/check-zig-toolchain.py",
            "scripts/zigux/check-lane05-local-first-archive-workflow.py",
            "scripts/zigux/check-lane05-local-archive-readme.py",
            "scripts/zigux/check-kconfig-bridge.py",
            "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
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
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "scripts/zigux/check-fixdep-diff.py",
        ],
        "bootstrap_helpers": [
            "scripts/zigux/install-zig.py",
        ],
        "bridge_helpers": [
            "scripts/zigux/kconfig/conf_bridge.zig",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            "scripts/zigux/genksyms.zig",
        ],
        "policy": [
            "scripts/zigux/zig-toolchain-policy.json",
        ],
        "archive_support": [
            "third_party/README.md",
            "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
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
        "cross_route_support": [
            "scripts/zigux/check-phase2-cross.py",
            "zigux/tests/fixtures/phase2_cross_targets.json",
        ],
        "artifact_support": [
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        ],
        "fixdep_support": [
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "scripts/zigux/check-fixdep-diff.py",
            "scripts/zigux/fixdep.zig",
            "zigux/tests/fixtures/fixdep/cases.json",
        ],
        "fixture_roster": [
            "zigux/tests/fixtures/kconfig_bridge/cases.json",
            "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
            "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
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
    "repo_reality_gaps": [],
    "notes": [
        "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, the returned local-first archive workflow and archive README contract checkers, the shipped toolchain-pinning and pin-scope guards, the returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, kbuild routes checker, the live kconfig bridge checker and fixture roster, the bounded genksyms bridge checker and fixture packet, the fixdep governance and parity checker pair, and the restored tranche-closure note.",
        "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose.",
        "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
        "Keep the dedicated manifest guards explicit through scripts/zigux/check-phase2-tool-manifest.py and scripts/zigux/check-phase2-artifact-tools-manifest.py so Phase 2 packet drift fails closed beside the other reminder checkers.",
        "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, bounded genksyms fixture packet, fixdep helper packet, and artifact-support manifest checker explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
    ],
}

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_SETUP_MARKERS)
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_LINES)
    + len(BOOTSTRAP_PRESENT_MARKERS)
    + len(BOOTSTRAP_GAP_MARKERS)
    + len(PHASE2_CLOSURE_MARKERS)
    + ARCHIVE_README_REQUIRED_MARKER_COUNT
    + len(SCRIPTS_MARKERS)
    + len(REVIEW_MARKERS)
    + len(TESTS_MARKERS)
    + 6
    + (len(SURFACE_PATHS) - 5)
    + 4
    + 1
    + 1
    + 1
    + 4
    + 1
    + 1
    + 1
    + 1
    + 1
    + 1
    + 1
    + 1
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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def extract_markdown_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    start = text.find("\n", start)
    if start == -1:
        return ""
    start += 1
    end = text.find("\n## ", start)
    if end == -1:
        end = len(text)
    return text[start:end]


def load_policy(root: Path) -> object:
    return json.loads(read_text(resolve_path(root, POLICY_PATH)))


def load_tool_manifest(root: Path) -> object:
    return json.loads(read_text(resolve_path(root, TOOL_MANIFEST_PATH)))


def expected_archive_filename(target: str, channel: str) -> str:
    return f"zig-{target}-{channel}.tar.xz"


def duplicate_archive_name(expected_filename: str) -> str:
    stem = expected_filename[: -len(".tar.xz")]
    return f"{stem} (1).tar.xz"


def archive_readme_markers(
    target: str,
    channel: str,
    expected_sha: str,
    expected_size: int,
) -> tuple[str, ...]:
    expected_filename = expected_archive_filename(target, channel)
    expected_path = f"third_party/{expected_filename}"
    validation_command = (
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
        f"{expected_path} --archive-target {target}"
    )
    return (
        "# Zigux third-party archives",
        "Lane 05 bootstrap CI",
        f"`{target}`",
        f"`{channel}`",
        f"`{expected_path}`",
        f"`{expected_sha}`",
        f"`{expected_size}` bytes",
        f"`{validation_command}`",
        f"`{duplicate_archive_name(expected_filename)}`",
        f"`{POLICY_PATH.relative_to(ROOT).as_posix()}`",
    )


def render_archive_readme(
    target: str,
    channel: str,
    expected_sha: str,
    expected_size: int,
) -> str:
    expected_filename = expected_archive_filename(target, channel)
    expected_path = f"third_party/{expected_filename}"
    validation_command = (
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
        f"{expected_path} --archive-target {target}"
    )
    duplicate_copy = duplicate_archive_name(expected_filename)
    return "\n".join(
        (
            "# Zigux third-party archives",
            "",
            "This directory is reserved for trusted archive payloads that Lane 05 bootstrap CI",
            "can validate locally before it falls back to network downloads.",
            "",
            "## Current pinned Zig archive contract",
            "",
            f"- target: `{target}`",
            f"- channel: `{channel}`",
            f"- file: `{expected_path}`",
            f"- sha256: `{expected_sha}`",
            f"- size: `{expected_size}` bytes",
            "",
            "## Validation",
            "",
            f"- `{validation_command}`",
            "",
            "## Rules",
            "",
            "- keep the filename exact so bootstrap can resolve the pinned archive without",
            "  guessing",
            f"- do not keep duplicate-suffix copies such as `{duplicate_copy}` in this directory",
            f"- update this README and its checker whenever `{POLICY_PATH.relative_to(ROOT).as_posix()}`",
            "  changes the pinned target, channel, digest, or expected payload size",
            "",
        )
    )


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        payload = load_policy(root)
    except json.JSONDecodeError as exc:
        return [("INVALID_POLICY_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return issues + [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(("POLICY_PHASE_MISMATCH", f"actual={payload.get('phase')!r}:expected={EXPECTED_POLICY['phase']!r}"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__)]

    if upgrade_policy.get("channel_minimum_lockstep") is not EXPECTED_POLICY["channel_minimum_lockstep"]:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", f"actual={upgrade_policy.get('channel_minimum_lockstep')!r}:expected={EXPECTED_POLICY['channel_minimum_lockstep']!r}"))

    if upgrade_policy.get("archive_target_scope") != EXPECTED_POLICY["archive_target_scope"]:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", f"actual={upgrade_policy.get('archive_target_scope')!r}:expected={EXPECTED_POLICY['archive_target_scope']!r}"))

    if upgrade_policy.get("required_make_routes") != EXPECTED_POLICY["required_make_routes"]:
        issues.append(("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", f"actual={upgrade_policy.get('required_make_routes')!r}:expected={EXPECTED_POLICY['required_make_routes']!r}"))

    return issues


def collect_archive_readme_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = load_policy(root)
    if not isinstance(payload, dict):
        return [("INVALID_ARCHIVE_README_POLICY_PAYLOAD", type(payload).__name__)]

    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        return [("INVALID_ARCHIVE_README_CHANNEL", repr(channel))]
    channel = channel.strip()

    archives = payload.get("archive_sha256")
    if not isinstance(archives, dict) or not archives:
        return [("INVALID_ARCHIVE_README_SHA_MAP", repr(archives))]

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return [("INVALID_ARCHIVE_README_UPGRADE_POLICY", type(upgrade_policy).__name__)]
    targets = upgrade_policy.get("archive_target_scope")
    if not isinstance(targets, list) or len(targets) != 1 or not isinstance(targets[0], str) or not targets[0].strip():
        return [("INVALID_ARCHIVE_README_TARGET_SCOPE", repr(targets))]
    target = targets[0].strip()

    expected_sha = archives.get(target)
    if not isinstance(expected_sha, str) or not expected_sha.strip():
        return [("INVALID_ARCHIVE_README_SHA", f"target={target!r}:actual={expected_sha!r}")]
    expected_sha = expected_sha.strip()

    expected_size = EXPECTED_ARCHIVE_SIZES.get(target)
    if expected_size is None:
        return [("UNSUPPORTED_ARCHIVE_README_TARGET", target)]

    readme_text = read_text(resolve_path(root, THIRD_PARTY_README))
    issues.extend(
        collect_missing_markers(
            readme_text,
            archive_readme_markers(target, channel, expected_sha, expected_size),
            "MISSING_ARCHIVE_README_MARKERS",
        )
    )

    duplicate_path = resolve_path(root, THIRD_PARTY_README).parent / duplicate_archive_name(
        expected_archive_filename(target, channel)
    )
    if duplicate_path.exists():
        issues.append(("DUPLICATE_ARCHIVE_COPY", duplicate_path.name))

    return issues


def collect_tool_manifest_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        payload = load_tool_manifest(root)
    except json.JSONDecodeError as exc:
        return [("INVALID_TOOL_MANIFEST_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return [("INVALID_TOOL_MANIFEST_PAYLOAD", type(payload).__name__)]

    for key in ("phase", "status", "scope", "workflow"):
        if payload.get(key) != EXPECTED_TOOL_MANIFEST[key]:
            issues.append(("TOOL_MANIFEST_FIELD_MISMATCH", f"{key}:actual={payload.get(key)!r}:expected={EXPECTED_TOOL_MANIFEST[key]!r}"))

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return issues + [("INVALID_TOOL_MANIFEST_PRESENT_SURFACES", type(present_surfaces).__name__)]

    expected_present_surfaces = EXPECTED_TOOL_MANIFEST["present_surfaces"]
    for key, expected_value in expected_present_surfaces.items():
        if present_surfaces.get(key) != expected_value:
            issues.append(("TOOL_MANIFEST_PRESENT_SURFACES_MISMATCH", f"{key}:actual={present_surfaces.get(key)!r}:expected={expected_value!r}"))

    if payload.get("repo_reality_gaps") != EXPECTED_TOOL_MANIFEST["repo_reality_gaps"]:
        issues.append(("TOOL_MANIFEST_REPO_GAPS_MISMATCH", f"actual={payload.get('repo_reality_gaps')!r}:expected={EXPECTED_TOOL_MANIFEST['repo_reality_gaps']!r}"))

    if payload.get("notes") != EXPECTED_TOOL_MANIFEST["notes"]:
        issues.append(("TOOL_MANIFEST_NOTES_MISMATCH", f"actual={payload.get('notes')!r}:expected={EXPECTED_TOOL_MANIFEST['notes']!r}"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    bootstrap_notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    phase2_closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    review_checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    bootstrap_present_text = extract_markdown_section(bootstrap_notes_text, "## Current direct packet")
    bootstrap_gap_text = extract_markdown_section(bootstrap_notes_text, "## Current repo-reality gaps")

    issues.extend(collect_missing_markers(scripts_readme_text, SCRIPTS_MARKERS, "MISSING_SCRIPTS_MARKERS"))
    issues.extend(collect_missing_markers(review_checklist_text, REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"))
    issues.extend(collect_missing_markers(tests_readme_text, TESTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(collect_missing_markers(workflow_text, WORKFLOW_SETUP_MARKERS, "MISSING_WORKFLOW_SETUP_MARKERS"))
    issues.extend(collect_missing_markers(phase2_closure_text, PHASE2_CLOSURE_MARKERS, "MISSING_PHASE2_CLOSURE_MARKERS"))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    issues.extend(collect_missing_markers(bootstrap_present_text, BOOTSTRAP_PRESENT_MARKERS, "MISSING_BOOTSTRAP_PRESENT_MARKERS"))
    issues.extend(collect_missing_markers(bootstrap_gap_text, BOOTSTRAP_GAP_MARKERS, "MISSING_BOOTSTRAP_GAP_MARKERS"))

    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))

    archive_readme_path = resolve_path(root, THIRD_PARTY_README)
    policy_issues: list[tuple[str, str]] = []
    policy_path = resolve_path(root, POLICY_PATH)
    if policy_path.exists():
        policy_issues = collect_policy_issues(root)
        issues.extend(policy_issues)
    if archive_readme_path.exists() and policy_path.exists() and not policy_issues:
        issues.extend(collect_archive_readme_issues(root))
    if resolve_path(root, TOOL_MANIFEST_PATH).exists():
        issues.extend(collect_tool_manifest_issues(root))
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    archive_target = "x86_64-linux"
    archive_channel = "0.17.0-dev.87+9b177a7d2"
    archive_sha = "3" * 64
    write_text(resolve_path(root, WORKFLOW), "\n".join((*WORKFLOW_SETUP_MARKERS, *WORKFLOW_LINES)) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(["# scripts", *SCRIPTS_MARKERS]) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(["# review", *REVIEW_MARKERS]) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(["# tests", *TESTS_MARKERS]) + "\n")
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(["# Phase 2 Closure", *PHASE2_CLOSURE_MARKERS]) + "\n")
    bootstrap_lines = [
        "# Phase 2 Toolchain Bootstrap Notes",
        "",
        "## Current direct packet",
        "",
        *BOOTSTRAP_PRESENT_MARKERS,
        "",
        "## Current repo-reality gaps",
        "",
        *BOOTSTRAP_GAP_MARKERS,
    ]
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(bootstrap_lines) + "\n")
    for path in SURFACE_PATHS:
        if path == POLICY_PATH:
            write_text(resolve_path(root, path), json.dumps({"phase": EXPECTED_POLICY["phase"], "channel": archive_channel, "minimum_version": archive_channel, "archive_sha256": {archive_target: archive_sha}, "upgrade_policy": {"channel_minimum_lockstep": EXPECTED_POLICY["channel_minimum_lockstep"], "archive_target_scope": EXPECTED_POLICY["archive_target_scope"], "required_make_routes": EXPECTED_POLICY["required_make_routes"]}}, indent=2) + "\n")
        elif path == TOOL_MANIFEST_PATH:
            write_text(resolve_path(root, path), json.dumps(EXPECTED_TOOL_MANIFEST, indent=2) + "\n")
        elif path == THIRD_PARTY_README:
            write_text(
                resolve_path(root, path),
                render_archive_readme(
                    archive_target,
                    archive_channel,
                    archive_sha,
                    EXPECTED_ARCHIVE_SIZES[archive_target],
                ),
            )
        elif path in (BOOTSTRAP_NOTES, PHASE2_CLOSURE, SCRIPTS_README, REVIEW_CHECKLIST, TESTS_README):
            continue
        else:
            write_text(resolve_path(root, path), "present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_all(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def mutate_json(path: Path, mutator) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_pinning_") as tmp_dir:
        root = Path(tmp_dir)
        archive_target = "x86_64-linux"
        archive_channel = "0.17.0-dev.87+9b177a7d2"
        archive_sha = "3" * 64
        archive_markers = archive_readme_markers(
            archive_target,
            archive_channel,
            archive_sha,
            EXPECTED_ARCHIVE_SIZES[archive_target],
        )
        duplicate_archive = duplicate_archive_name(expected_archive_filename(archive_target, archive_channel))

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        repeated_marker = BOOTSTRAP_PRESENT_MARKERS[0]
        repeated_text = "\n".join((repeated_marker, repeated_marker, "tail")) + "\n"
        replaced_text = replace_once(repeated_text, repeated_marker)
        assert replaced_text == f"\n{repeated_marker}\ntail\n"
        checks_run += 1

        for marker_set, path_ref, expected_code in (
            (SCRIPTS_MARKERS, SCRIPTS_README, "MISSING_SCRIPTS_MARKERS"),
            (REVIEW_MARKERS, REVIEW_CHECKLIST, "MISSING_REVIEW_MARKERS"),
            (TESTS_MARKERS, TESTS_README, "MISSING_TESTS_MARKERS"),
        ):
            for marker in marker_set:
                build_self_test_root(root)
                path = resolve_path(root, path_ref)
                path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                issues = collect_issues(root)
                assert (expected_code, marker) in issues
                checks_run += 1

        for marker in WORKFLOW_SETUP_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_SETUP_MARKERS", marker) in issues
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_HOOKS", marker) in issues
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count=2") in issues
            checks_run += 1

        for marker in BOOTSTRAP_PRESENT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_BOOTSTRAP_PRESENT_MARKERS", marker) in issues
            checks_run += 1

        for marker in BOOTSTRAP_GAP_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_BOOTSTRAP_GAP_MARKERS", marker) in issues
            checks_run += 1

        for marker in PHASE2_CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_PHASE2_CLOSURE_MARKERS", marker) in issues
            checks_run += 1

        for marker in archive_markers:
            build_self_test_root(root)
            path = resolve_path(root, THIRD_PARTY_README)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_ARCHIVE_README_MARKERS", marker) in issues
            checks_run += 1

        build_self_test_root(root)
        write_text(resolve_path(root, THIRD_PARTY_README).parent / duplicate_archive, "duplicate\n")
        issues = collect_issues(root)
        assert ("DUPLICATE_ARCHIVE_COPY", duplicate_archive) in issues
        checks_run += 1

        for primary_path in (WORKFLOW, BOOTSTRAP_NOTES, PHASE2_CLOSURE, SCRIPTS_README, REVIEW_CHECKLIST, TESTS_README):
            build_self_test_root(root)
            resolve_path(root, primary_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                assert str(resolve_path(root, primary_path)) in str(exc)
            else:
                raise AssertionError("missing primary surface did not abort")
            checks_run += 1

        for rel_path in SURFACE_PATHS:
            if rel_path in (BOOTSTRAP_NOTES, PHASE2_CLOSURE, SCRIPTS_README, REVIEW_CHECKLIST, TESTS_README):
                continue
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_SURFACE_PATHS", rel_path.relative_to(ROOT).as_posix()) in issues
            checks_run += 1

        policy_mutations = (("phase", "Phase 3", "POLICY_PHASE_MISMATCH"), ("lockstep", False, "POLICY_LOCKSTEP_MISMATCH"), ("archive_target_scope", ["aarch64-linux"], "POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH"), ("required_make_routes", ["phase2-toolchain"], "POLICY_REQUIRED_MAKE_ROUTES_MISMATCH"))
        for field_name, replacement, expected_code in policy_mutations:
            build_self_test_root(root)
            path = resolve_path(root, POLICY_PATH)
            payload = json.loads(path.read_text(encoding="utf-8"))
            if field_name == "phase":
                payload["phase"] = replacement
            elif field_name == "lockstep":
                payload["upgrade_policy"]["channel_minimum_lockstep"] = replacement
            else:
                payload["upgrade_policy"][field_name] = replacement
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert any(issue[0] == expected_code for issue in issues)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, POLICY_PATH)
        path.write_text("{\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue[0] == "INVALID_POLICY_JSON" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, POLICY_PATH)
        path.write_text("[]\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_POLICY_PAYLOAD", "list") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, POLICY_PATH)
        mutate_json(path, lambda payload: payload.__setitem__("upgrade_policy", []))
        issues = collect_issues(root)
        assert ("INVALID_UPGRADE_POLICY", "list") in issues
        checks_run += 1

        for key in ("phase", "status", "scope", "workflow"):
            build_self_test_root(root)
            path = resolve_path(root, TOOL_MANIFEST_PATH)
            mutate_json(path, lambda payload, key=key: payload.__setitem__(key, "broken"))
            issues = collect_issues(root)
            assert any(issue[0] == "TOOL_MANIFEST_FIELD_MISMATCH" and issue[1].startswith(f"{key}:") for issue in issues)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        mutate_json(path, lambda payload: payload.__setitem__("present_surfaces", []))
        issues = collect_issues(root)
        assert ("INVALID_TOOL_MANIFEST_PRESENT_SURFACES", "list") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        mutate_json(path, lambda payload: payload["present_surfaces"].__setitem__("checkers", []))
        issues = collect_issues(root)
        assert any(issue[0] == "TOOL_MANIFEST_PRESENT_SURFACES_MISMATCH" and issue[1].startswith("checkers:") for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        mutate_json(path, lambda payload: payload.__setitem__("repo_reality_gaps", ["gap"]))
        issues = collect_issues(root)
        assert any(issue[0] == "TOOL_MANIFEST_REPO_GAPS_MISMATCH" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        mutate_json(path, lambda payload: payload.__setitem__("notes", []))
        issues = collect_issues(root)
        assert any(issue[0] == "TOOL_MANIFEST_NOTES_MISMATCH" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        path.write_text("{\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue[0] == "INVALID_TOOL_MANIFEST_JSON" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        path.write_text("[]\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_TOOL_MANIFEST_PAYLOAD", "list") in issues
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_PINNING_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current directly readable Phase 2 toolchain pinning packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE2_TOOLCHAIN_PINNING=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_REQUIRED_MARKER_COUNT={len(BOOTSTRAP_PRESENT_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_PINNING_GAP_MARKER_COUNT={len(BOOTSTRAP_GAP_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_PINNING_ARCHIVE_README_MARKER_COUNT={ARCHIVE_README_REQUIRED_MARKER_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
