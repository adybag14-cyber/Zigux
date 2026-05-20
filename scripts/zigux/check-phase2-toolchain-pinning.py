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
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
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
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` is directly readable on current `master` and keeps the fixture-backed artifact-support packet explicit beside `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)
¢h­µç