#!/usr/bin/env python3
"""Guard the docs-root Phase 2 toolchain bootstrap note."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

NOTE = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
THIRD_PARTY_README = "third_party/README.md"
TOOL_MANIFEST = "zigux/tests/fixtures/phase2_tool_manifest.json"

ARCHIVE_TARGET = "x86_64-linux"
ARCHIVE_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_SELF_TEST_CASE_COUNT = 8

REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

NOTE_MARKERS = (
    "`scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master`",
    "`third_party/README.md` is directly readable on current `master`",
    "tries `community-mirrors.txt` before the direct Zig download URL",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

NO_GAP_MARKERS = (
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, archive-verification, staged-helper, or direct cross-route surfaces from the current packet.",
)

FOLLOW_THROUGH_MARKERS = (
    "Keep future Phase 2 follow-up inside one current packet surface at a time",
    "Do not widen this note into genksyms parser behavior, conf or confdata bridge semantics, or deeper cross-target execution claims",
)

WORKFLOW_MARKERS = (
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
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
)


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


def collect_missing(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(resolve(root, POLICY)))
    upgrade = payload.get("upgrade_policy")
    issues: list[tuple[str, str]] = []
    if payload.get("phase") != "Phase 2":
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))
    if payload.get("channel") != ARCHIVE_CHANNEL:
        issues.append(("POLICY_CHANNEL_MISMATCH", repr(payload.get("channel"))))
    if payload.get("minimum_version") != ARCHIVE_CHANNEL:
        issues.append(("POLICY_MINIMUM_VERSION_MISMATCH", repr(payload.get("minimum_version"))))
    if not isinstance(upgrade, dict):
        return issues + [("POLICY_UPGRADE_PAYLOAD_INVALID", type(upgrade).__name__)]
    if upgrade.get("channel_minimum_lockstep") is not True:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", repr(upgrade.get("channel_minimum_lockstep"))))
    if upgrade.get("archive_target_scope") != [ARCHIVE_TARGET]:
        issues.append(("POLICY_ARCHIVE_SCOPE_MISMATCH", repr(upgrade.get("archive_target_scope"))))
    if upgrade.get("required_make_routes") != list(REQUIRED_MAKE_ROUTES):
        issues.append(("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", repr(upgrade.get("required_make_routes"))))
    return issues


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(resolve(root, TOOL_MANIFEST)))
    issues: list[tuple[str, str]] = []
    if payload.get("phase") != "Phase 2":
        issues.append(("TOOL_MANIFEST_PHASE_MISMATCH", repr(payload.get("phase"))))
    if payload.get("workflow") != WORKFLOW:
        issues.append(("TOOL_MANIFEST_WORKFLOW_MISMATCH", repr(payload.get("workflow"))))
    if payload.get("repo_reality_gaps") != []:
        issues.append(("TOOL_MANIFEST_REPO_REALITY_GAPS_MISMATCH", repr(payload.get("repo_reality_gaps"))))
    surfaces = payload.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return issues + [("TOOL_MANIFEST_SURFACES_INVALID", type(surfaces).__name__)]
    required_buckets = {
        "policy": [POLICY],
        "closure_notes": ["Documentation/zigux/phase2-closure.md", NOTE],
        "archive_support": [THIRD_PARTY_README],
        "bootstrap_helpers": ["scripts/zigux/install-zig.py", "scripts/zigux/stage-pinned-zig-archive.py"],
        "cross_route_support": ["scripts/zigux/check-phase2-cross.py", "zigux/tests/fixtures/phase2_cross_targets.json"],
        "artifact_support": ["scripts/zigux/artifact_diff.py", "scripts/zigux/check-phase2-artifact-tools-manifest.py"],
        "validators": ["scripts/zigux/validate-phase2.py", "scripts/zigux/validate-phase2-closure.py"],
        "make_wrappers": [f"make -C zigux {route}" for route in (*REQUIRED_MAKE_ROUTES, "phase2")],
        "checkers": [
            "scripts/zigux/check-zig-toolchain.py",
            "scripts/zigux/check-lane05-local-first-archive-workflow.py",
            "scripts/zigux/check-lane05-local-archive-readme.py",
            "scripts/zigux/check-lane05-install-zig-archive-verification.py",
            "scripts/zigux/check-lane05-stage-helper-contract.py",
            "scripts/zigux/check-lane05-stage-helper-selftest.py",
            "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
            "scripts/zigux/check-phase2-cross.py",
            "scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "scripts/zigux/check-phase2-toolchain-pinning.py",
            "scripts/zigux/check-phase2-toolchain-pin-scope.py",
            "scripts/zigux/check-phase2-required-make-routes.py",
            "scripts/zigux/check-phase2-tool-manifest.py",
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        ],
    }
    for bucket, required_values in required_buckets.items():
        present = surfaces.get(bucket)
        if not isinstance(present, list):
            issues.append(("TOOL_MANIFEST_BUCKET_INVALID", bucket))
            continue
        for value in required_values:
            if value not in present:
                issues.append(("TOOL_MANIFEST_BUCKET_MISSING", f"{bucket}:{value}"))
    return issues


def collect_workflow_issues(root: Path) -> list[tuple[str, str]]:
    workflow = read_text(resolve(root, WORKFLOW))
    return collect_missing(workflow, WORKFLOW_MARKERS, "WORKFLOW_MARKER_MISSING")


def collect_makefile_issues(root: Path) -> list[tuple[str, str]]:
    makefile = read_text(resolve(root, MAKEFILE))
    markers = tuple(f".PHONY: {REQUIRED_MAKE_ROUTES[0]}" for _ in range(1)) + tuple(
        f"phase2-{suffix}" for suffix in ("toolchain", "tools", "kconfig", "cross", "genksyms", "fixdep", "validate")
    )
    issues = collect_missing(makefile, markers, "MAKEFILE_MARKER_MISSING")
    if "phase2: phase2-validate" not in makefile:
        issues.append(("MAKEFILE_MARKER_MISSING", "phase2: phase2-validate"))
    return issues


def collect_archive_readme_issues(root: Path) -> list[tuple[str, str]]:
    readme = read_text(resolve(root, THIRD_PARTY_README))
    markers = (
        f"`third_party/zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL}.tar.xz`",
        f"`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL}.tar.xz --archive-target {ARCHIVE_TARGET}`",
        "`scripts/zigux/check-lane05-stage-helper-contract.py`",
        "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    )
    return collect_missing(readme, markers, "ARCHIVE_README_MARKER_MISSING")


def collect_note_issues(root: Path) -> list[tuple[str, str]]:
    note = read_text(resolve(root, NOTE))
    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing(note, NOTE_MARKERS, "NOTE_MARKER_MISSING"))
    issues.extend(collect_missing(note, NO_GAP_MARKERS, "NOTE_REPO_GAP_MARKER_MISSING"))
    issues.extend(collect_missing(note, FOLLOW_THROUGH_MARKERS, "NOTE_FOLLOW_THROUGH_MARKER_MISSING"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_note_issues(root))
    issues.extend(collect_policy_issues(root))
    issues.extend(collect_manifest_issues(root))
    issues.extend(collect_workflow_issues(root))
    issues.extend(collect_makefile_issues(root))
    issues.extend(collect_archive_readme_issues(root))
    return issues


def sample_note() -> str:
    return f"""# Phase 2 Toolchain Bootstrap Notes

## Current direct packet

- `scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `{ARCHIVE_CHANNEL}` and names `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, and `phase2-validate` as the required Linux-style make routes.
- `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, and `scripts/zigux/check-fixdep-diff.py` keep the shipped reminder packet explicit.
- `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, `scripts/zigux/check-lane05-local-archive-readme.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, `scripts/zigux/check-lane05-stage-helper-selftest.py`, `scripts/zigux/install-zig.py`, and `scripts/zigux/stage-pinned-zig-archive.py` keep the returned helper-local kconfig, direct cross-route, local-first archive, archive-verification, and staged-helper packet explicit.
- `scripts/zigux/check-zig-toolchain.py` is directly readable on current `master`.
- `third_party/README.md` is directly readable on current `master`.
- `.github/workflows/zigux-bootstrap.yml` tries `community-mirrors.txt` before the direct Zig download URL and reruns the shipped toolchain guards.
- `zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit.
- The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.

## Current repo-reality gaps

- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.
- Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, archive-verification, staged-helper, or direct cross-route surfaces from the current packet.

## Follow-through

- Keep future Phase 2 follow-up inside one current packet surface at a time.
- Do not widen this note into genksyms parser behavior, conf or confdata bridge semantics, or deeper cross-target execution claims beyond the returned `phase2_cross_targets.json` packet.
"""


def sample_policy() -> str:
    return json.dumps(
        {
            "phase": "Phase 2",
            "channel": ARCHIVE_CHANNEL,
            "minimum_version": ARCHIVE_CHANNEL,
            "archive_sha256": {ARCHIVE_TARGET: "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"},
            "upgrade_policy": {
                "channel_minimum_lockstep": True,
                "archive_target_scope": [ARCHIVE_TARGET],
                "required_make_routes": list(REQUIRED_MAKE_ROUTES),
            },
        },
        indent=2,
    ) + "\n"


def sample_manifest() -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "workflow": WORKFLOW,
        "repo_reality_gaps": [],
        "present_surfaces": {
            "policy": [POLICY],
            "closure_notes": ["Documentation/zigux/phase2-closure.md", NOTE],
            "archive_support": [THIRD_PARTY_README, f"third_party/zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL}.tar.xz"],
            "bootstrap_helpers": ["scripts/zigux/install-zig.py", "scripts/zigux/stage-pinned-zig-archive.py"],
            "cross_route_support": ["scripts/zigux/check-phase2-cross.py", "zigux/tests/fixtures/phase2_cross_targets.json"],
            "artifact_support": [
                "scripts/zigux/artifact_diff.py",
                "scripts/zigux/check-phase2-artifact-tools-manifest.py",
                "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
            ],
            "checkers": [
                "scripts/zigux/check-zig-toolchain.py",
                "scripts/zigux/check-lane05-local-first-archive-workflow.py",
                "scripts/zigux/check-lane05-local-archive-readme.py",
                "scripts/zigux/check-lane05-install-zig-archive-verification.py",
                "scripts/zigux/check-lane05-stage-helper-contract.py",
                "scripts/zigux/check-lane05-stage-helper-selftest.py",
                "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
                "scripts/zigux/check-phase2-cross.py",
                "scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "scripts/zigux/check-phase2-toolchain-pinning.py",
                "scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "scripts/zigux/check-phase2-required-make-routes.py",
                "scripts/zigux/check-phase2-tool-manifest.py",
                "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            ],
            "validators": ["scripts/zigux/validate-phase2.py", "scripts/zigux/validate-phase2-closure.py"],
            "make_wrappers": [f"make -C zigux {route}" for route in (*REQUIRED_MAKE_ROUTES, "phase2")],
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def sample_workflow() -> str:
    return "\n".join(
        [
            "name: zigux-bootstrap",
            "jobs:",
            "  bootstrap:",
            "    steps:",
            "      - name: Self-test current Zig toolchain checker",
            "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
            "      - name: Check current Zig toolchain policy packet",
            "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
            "      - name: Check current pinned Zig archive packet",
            "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
            "      - name: Self-test current Lane 05 local-first archive checker",
            "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
            "      - name: Check current Lane 05 local-first archive packet",
            "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
            "      - name: Self-test current Lane 05 local archive README checker",
            "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
            "      - name: Check current Lane 05 local archive README packet",
            "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
            "      - name: Self-test current Lane 05 install-zig archive verification checker",
            "        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
            "      - name: Check current Lane 05 install-zig archive verification packet",
            "        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
            "      - name: Self-test current Zig installer helper",
            "        run: python3 scripts/zigux/install-zig.py --self-test",
            "      - name: Self-test current staged pinned Zig archive helper",
            "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
            "      - name: Self-test current Lane 05 stage helper contract checker",
            "        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
            "      - name: Check current Lane 05 stage helper contract packet",
            "        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
            "      - name: Self-test current Lane 05 stage helper selftest checker",
            "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
            "      - name: Check current Lane 05 stage helper selftest packet",
            "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
            "      - name: Self-test current Phase 2 toolchain pinning checker",
            "        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
            "      - name: Self-test current Phase 2 toolchain pin-scope checker",
            "        run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            "      - name: Self-test current required-make-routes checker",
            "        run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
            "      - name: Self-test current Phase 2 kconfig allconfig helper checker",
            "        run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
            "      - name: Check current Phase 2 kconfig allconfig helper packet",
            "        run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
            "      - name: Self-test current Phase 2 tool manifest checker",
            "        run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
            "      - name: Self-test current Phase 2 artifact tools manifest checker",
            "        run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
            "      - name: Self-test current Phase 2 genksyms selftest-alignment checker",
            "        run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
            "      - name: Self-test current Phase 2 fixdep gate checker",
            "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
            "      - name: Self-test current fixdep parity checker",
            "        run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
            "      - name: Self-test current Phase 2 cross checker",
            "        run: python3 scripts/zigux/check-phase2-cross.py --self-test",
            "      - name: Check current Phase 2 direct cross-route packet",
            "        run: python3 scripts/zigux/check-phase2-cross.py",
            "      - name: Self-test current Phase 2 cross selftest alignment checker",
            "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
            "      - name: Check current Phase 2 cross selftest alignment packet",
            "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "      - name: Run current Phase 2 make wrappers",
            "        run: make -C zigux phase2-toolchain",
            "      - name: Run current Phase 2 tools wrapper",
            "        run: make -C zigux phase2-tools",
            "      - name: Run current Phase 2 kconfig wrapper",
            "        run: make -C zigux phase2-kconfig",
            "      - name: Run current Phase 2 cross wrapper",
            "        run: make -C zigux phase2-cross",
            "      - name: Run current Phase 2 genksyms wrapper",
            "        run: make -C zigux phase2-genksyms",
            "      - name: Run current Phase 2 fixdep wrapper",
            "        run: make -C zigux phase2-fixdep",
            "      - name: Run current Phase 2 validate wrapper",
            "        run: make -C zigux phase2-validate",
        ]
    ) + "\n"


def sample_makefile() -> str:
    return "\n".join(
        [
            ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
            "phase2-toolchain:",
            "\t@true",
            "phase2-tools:",
            "\t@true",
            "phase2-kconfig:",
            "\t@true",
            "phase2-cross:",
            "\t@true",
            "phase2-genksyms:",
            "\t@true",
            "phase2-fixdep:",
            "\t@true",
            "phase2-validate:",
            "\t@true",
            "phase2: phase2-validate",
        ]
    ) + "\n"


def sample_third_party_readme() -> str:
    return f"""# Zigux third-party archives

- file: `third_party/zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL}.tar.xz`
- validation: `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL}.tar.xz --archive-target {ARCHIVE_TARGET}`
- companion checks: `scripts/zigux/check-lane05-stage-helper-contract.py` and `scripts/zigux/check-lane05-stage-helper-selftest.py`
"""


def write_sample_root(root: Path) -> None:
    write_text(resolve(root, NOTE), sample_note())
    write_text(resolve(root, POLICY), sample_policy())
    write_text(resolve(root, TOOL_MANIFEST), sample_manifest())
    write_text(resolve(root, WORKFLOW), sample_workflow())
    write_text(resolve(root, MAKEFILE), sample_makefile())
    write_text(resolve(root, THIRD_PARTY_README), sample_third_party_readme())


def mutate_file(root: Path, rel: str, before: str, after: str) -> None:
    path = resolve(root, rel)
    write_text(path, read_text(path).replace(before, after, 1))


def run_self_test() -> int:
    cases = (
        ("baseline", None, True),
        ("note-marker-missing", lambda root: mutate_file(root, NOTE, "`scripts/zigux/check-phase2-toolchain-pinning.py`", "`scripts/zigux/check-phase2-toolchain-pinning-old.py`"), False),
        ("repo-gap-marker-missing", lambda root: mutate_file(root, NOTE, NO_GAP_MARKERS[0], "repo gaps remain"), False),
        ("follow-through-marker-missing", lambda root: mutate_file(root, NOTE, FOLLOW_THROUGH_MARKERS[1], "Do not widen this note into side quests."), False),
        ("policy-routes-mismatch", lambda root: mutate_file(root, POLICY, '"phase2-fixdep",\n      "phase2-validate"', '"phase2-validate"'), False),
        ("manifest-gap-mismatch", lambda root: mutate_file(root, TOOL_MANIFEST, '"repo_reality_gaps": []', '"repo_reality_gaps": ["gap"]'), False),
        ("workflow-marker-missing", lambda root: mutate_file(root, WORKFLOW, "python3 scripts/zigux/check-phase2-tool-manifest.py --self-test\n", ""), False),
        ("makefile-marker-missing", lambda root: mutate_file(root, MAKEFILE, "phase2: phase2-validate", "phase2:"), False),
    )
    for _, mutate, should_pass in cases:
        with tempfile.TemporaryDirectory(prefix="phase2_toolchain_bootstrap_notes_selftest_") as tmp:
            root = Path(tmp)
            write_sample_root(root)
            if mutate is not None:
                mutate(root)
            passed = not collect_issues(root)
            if passed != should_pass:
                return 1
    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTES_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_BOOTSTRAP_NOTES_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample tree")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(args.write_sample_root)
        return 0

    issues = collect_issues(args.root)
    if issues:
        for code, detail in issues:
            print(f"{code}: {detail}")
        return 1

    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTES=pass")
    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTES_REQUIRED_FILE_COUNT=6")
    print(f"PHASE2_TOOLCHAIN_BOOTSTRAP_NOTES_REQUIRED_MAKE_ROUTE_COUNT={len(REQUIRED_MAKE_ROUTES) + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
