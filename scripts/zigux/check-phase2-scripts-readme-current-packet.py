#!/usr/bin/env python3
"""Guard the current Phase 2 scripts-root reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent

SCRIPTS_README = Path("scripts/zigux/README.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
THIRD_PARTY_README = Path("third_party/README.md")
MAKEFILE = Path("zigux/Makefile")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
ARTIFACT_MANIFEST = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

SCRIPTS_MARKERS = (
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, helper-local kconfig allconfig guard, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

BOOTSTRAP_MARKERS = (
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master`",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master`",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
)

CLOSURE_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-fixdep`",
)

REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

TESTS_MARKERS = (
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "helper-local kconfig allconfig guard",
    "kconfig bridge, genksyms bridge, fixdep packet, make-wrapper, and fixture packet aligned without reviving older missing validator-first or wrapper-only proof?",
)

THIRD_PARTY_MARKERS = (
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "- size: `58159088` bytes",
    "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test",
)

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel": "0.17.0-dev.87+9b177a7d2",
    "minimum_version": "0.17.0-dev.87+9b177a7d2",
    "archive_target_scope": ["x86_64-linux"],
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

REQUIRED_TOOL_MANIFEST_STRINGS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
)

REQUIRED_ARTIFACT_MANIFEST_STRINGS = (
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "text",
    "json",
    "bytes",
)


def read_text(root: Path, path: Path) -> str:
    target = root / path
    try:
        return target.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {target}") from exc


def write_text(root: Path, path: Path, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def read_json(root: Path, path: Path) -> object:
    return json.loads(read_text(root, path))


def collect_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        found: set[str] = set()
        for item in value:
            found.update(collect_strings(item))
        return found
    if isinstance(value, dict):
        found: set[str] = set()
        for item in value.values():
            found.update(collect_strings(item))
        return found
    return set()


def missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def exact_line_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    counts = {marker: 0 for marker in markers}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line in counts:
            counts[line] += 1
    return [(code, f"{count}::{marker}") for marker, count in counts.items() if count != 1]


def policy_issues(payload: object) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return [("INVALID_POLICY", type(payload).__name__)]
    issues: list[tuple[str, str]] = []
    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))
    if payload.get("channel") != EXPECTED_POLICY["channel"]:
        issues.append(("POLICY_CHANNEL_MISMATCH", repr(payload.get("channel"))))
    if payload.get("minimum_version") != EXPECTED_POLICY["minimum_version"]:
        issues.append(("POLICY_MINIMUM_VERSION_MISMATCH", repr(payload.get("minimum_version"))))
    upgrade = payload.get("upgrade_policy")
    if not isinstance(upgrade, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade).__name__)]
    if upgrade.get("archive_target_scope") != EXPECTED_POLICY["archive_target_scope"]:
        issues.append(("POLICY_ARCHIVE_SCOPE_MISMATCH", repr(upgrade.get("archive_target_scope"))))
    if upgrade.get("required_make_routes") != EXPECTED_POLICY[