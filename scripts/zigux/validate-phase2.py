#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

CHECK_ZIG_TOOLCHAIN = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"
FIXDEP_GATE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py"
FIXDEP_DIFF_CHECKER = ROOT / "scripts" / "zigux" / "check-fixdep-diff.py"
GENKSYMS_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py"
PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
PHASE2_CROSS_SELFTEST_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
)
PHASE2_KCONFIG_SELFTEST_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py"
)
PHASE2_CONFDATA_HELPER_ANCHOR_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-confdata-helper-anchor-alignment.py"
)
PHASE2_TOOL_MANIFEST_PACKET_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py"
)
TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
TESTS_README_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
)
KCONFIG_README_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-readme-alignment.py"
)
KCONFIG_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"

PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_MARKER = "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass"
PHASE2_TOOLCHAIN_PIN_SCOPE_MARKER = "PHASE2_TOOLCHAIN_PIN_SCOPE=pass"
PHASE2_VALIDATION_TOOLCHAIN_PY_COMMAND_SPECS: tuple[tuple[Path | str, ...], ...] = (
    (CHECK_ZIG_TOOLCHAIN, "--self-test"),
    (CHECK_ZIG_TOOLCHAIN,),
)
PHASE2_VALIDATION_PY_COMMAND_SPECS: tuple[tuple[Path | str, ...], ...] = (
    (TESTS_README_ALIGNMENT_CHECKER, "--self-test"),
    (TESTS_README_ALIGNMENT_CHECKER,),
    (KCONFIG_README_ALIGNMENT_CHECKER, "--self-test"),
    (KCONFIG_README_ALIGNMENT_CHECKER,),
    (PHASE2_KCONFIG_SELFTEST_ALIGNMENT_CHECKER, "--self-test"),
    (PHASE2_KCONFIG_SELFTEST_ALIGNMENT_CHECKER,),
    (KCONFIG_BRIDGE_CHECKER, "--self-test"),
    (KCONFIG_BRIDGE_CHECKER,),
    (PHASE2_CONFDATA_HELPER_ANCHOR_ALIGNMENT_CHECKER, "--self-test"),
    (PHASE2_CONFDATA_HELPER_ANCHOR_ALIGNMENT_CHECKER,),
    (FIXDEP_GATE_CHECKER, "--self-test"),
    (FIXDEP_GATE_CHECKER,),
    (FIXDEP_DIFF_CHECKER, "--self-test"),
    (FIXDEP_DIFF_CHECKER,),
    (GENKSYMS_BRIDGE_CHECKER, "--self-test"),
    (GENKSYMS_BRIDGE_CHECKER,),
    (PHASE2_CROSS_CHECKER, "--self-test"),
    (PHASE2_CROSS_CHECKER,),
    (PHASE2_CROSS_SELFTEST_ALIGNMENT_CHECKER, "--self-test"),
    (PHASE2_CROSS_SELFTEST_ALIGNMENT_CHECKER,),
    (PHASE2_TOOL_MANIFEST_PACKET_CHECKER, "--self-test"),
    (PHASE2_TOOL_MANIFEST_PACKET_CHECKER,),
    (TOOLCHAIN_PIN_SCOPE_CHECKER, "--self-test"),
    (TOOLCHAIN_PIN_SCOPE_CHECKER,),
)
PHASE2_VALIDATION_DIRECT_COMMAND_SPECS: tuple[tuple[Path | str, ...], ...] = (
    ("zig", "test", ROOT / "scripts" / "zigux" / "fixdep.zig"),
    ("zig", "test", ROOT / "scripts" / "zigux" / "genksyms.zig"),
    ("zig", "test", ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"),
    ("zig", "test", ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"),
)
PHASE2_VALIDATION_TOOLCHAIN_EXPECTED_COMMAND_TAILS = frozenset(
    {
        "scripts/zigux/check-zig-toolchain.py --self-test",
        "scripts/zigux/check-zig-toolchain.py",
    }
)
PHASE2_VALIDATION_EXPECTED_COMMAND_TAILS = frozenset(
    {
        "scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test",
        "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-kconfig-bridge.py --self-test",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py --self-test",
        "scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py",
        "scripts/zigux/check-phase2-fixdep-gate.py --self-test",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py --self-test",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/check-genksyms-bridge.py --self-test",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-cross.py --self-test",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
        "scripts/zigux/check-phase2-tool-manifest-packets.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "zig test scripts/zigux/fixdep.zig",
        "zig test scripts/zigux/genksyms.zig",
        "zig test scripts/zigux/kconfig/conf_bridge.zig",
        "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    }
)
PHASE2_VALIDATION_TOOLCHAIN_EXPECTED_COMMAND_COUNT = 2
PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 28
ARTIFACT_DIFF_REQUIRED_RELATIVE_PATHS = (
    "Documentation/zigux/artifact-diff.md",
    "scripts/zigux/artifact_diff.py",
)
PHASE2_REQUIRED_RELATIVE_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-fixdep-next-step-note.md",
    "Documentation/zigux/phase2-confdata-bridge-survey.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/zig-toolchain-policy.json",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
)
PHASE2_VALIDATION_EXPECTED_REQUIRED_TAILS = frozenset(PHASE2_REQUIRED_RELATIVE_PATHS)
PHASE2_VALIDATION_EXPECTED_REQUIRED_FILE_COUNT = 37
ARTIFACT_DIFF_EXPECTED_REQUIRED_TAILS = frozenset(ARTIFACT_DIFF_REQUIRED_RELATIVE_PATHS)
ARTIFACT_DIFF_EXPECTED_REQUIRED_FILE_COUNT = 2
PHASE2_VALIDATION_SELF_TEST_CASE_COUNT = 54


def load_pinned_channel(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:
    if not policy_path.exists():
        return None
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        return None
    return channel.strip()


def iter_repo_local_zig_candidates(
    *,
    root: Path = ROOT,
    pinned_channel: str | None = None,
) -> list[Path]:
    toolchain_root = root / ".zig-toolchain"
    candidates: list[Path] = []

    def add_candidate(path: Path) -> None:
        if path not in candidates:
            candidates.append(path)

    if pinned_channel is not None:
        pinned_root = toolchain_root / f"zig-x86_64-linux-{pinned_channel}"
        add_candidate(pinned_root / "zig")
        add_candidate(pinned_root / "bin" / "zig")

    if toolchain_root.exists():
        for child in sorted(toolchain_root.iterdir()):
            add_candidate(child / "zig")
            add_candidate(child / "bin" / "zig")
    return candidates


def resolve_zig_executable(
    explicit_zig: str | None = None,
    *,
    root: Path = ROOT,
    policy_path: Path = TOOLCHAIN_POLICY,
) -> str:
    if explicit_zig is not None:
        return explicit_zig
    env_zig = os.environ.get("ZIG")
    if env_zig:
        return env_zig
    pinned_channel = load_pinned_channel(policy_path)
    for candidate in iter_repo_local_zig_candidates(
        root=root,
        pinned_channel=pinned_channel,
    ):
        if candidate.is_file():
            return str(candidate)
    return shutil.which("zig") or "zig"


def build_python_commands(
    py_command_specs: tuple[tuple[Path | str, ...], ...],
) -> list[list[str]]:
    return [[sys.executable, str(spec[0]), *[str(part) for part in spec[1:]]] for spec in py_command_specs]


def build_toolchain_validation_commands(
    py_command_specs: tuple[tuple[Path | str, ...], ...] = PHASE2_VALIDATION_TOOLCHAIN_PY_COMMAND_SPECS,
) -> list[list[str]]:
    return build_python_commands(py_command_specs)


def build_validation_commands(
    py_command_specs: tuple[tuple[Path | str, ...], ...] = PHASE2_VALIDATION_PY_COMMAND_SPECS,
    direct_command_specs: tuple[tuple[Path | str, ...], ...] = PHASE2_VALIDATION_DIRECT_COMMAND_SPECS,
    *,
    zig_executable: str = "zig",
) -> list[list[str]]:
    commands = build_python_commands(py_command_specs)
    for spec in direct_command_specs:
        executable = zig_executable if spec and spec[0] == "zig" else str(spec[0])
        commands.append([executable, *[str(part) for part in spec[1:]]])
    return commands


def build_required_paths(
    required_relative_paths: tuple[str, ...] = PHASE2_REQUIRED_RELATIVE_PATHS,
) -> list[Path]:
    return [ROOT / rel_path for rel_path in required_relative_paths]


def command_tail_from_parts(parts: tuple[Path | str, ...]) -> str:
    tail_parts: list[str] = []
    for part in parts:
        path = Path(part)
        if path.is_absolute():
            try:
                tail_parts.append(str(path.relative_to(ROOT)))
                continue
            except ValueError:
                pass
        tail_parts.append(str(part))
    return " ".join(tail_parts)


def collect_toolchain_command_inventory_issues(
    py_command_specs: tuple[tuple[Path | str, ...], ...] = PHASE2_VALIDATION_TOOLCHAIN_PY_COMMAND_SPECS,
    *,
    expected_count: int = PHASE2_VALIDATION_TOOLCHAIN_EXPECTED_COMMAND_COUNT,
    expected_tails: frozenset[str] = PHASE2_VALIDATION_TOOLCHAIN_EXPECTED_COMMAND_TAILS,
) -> list[str]:
    issues: list[str] = []
    commands = build_toolchain_validation_commands(py_command_specs)
    if len(commands) != expected_count:
        issues.append(
            "phase2_validation_toolchain_commands:count="
            f"{len(commands)}:expected={expected_count}"
        )

    tails: list[str] = []
    for command in commands:
        parts = tuple(command[1:])
        tails.append(command_tail_from_parts(parts))
    if len(set(tails)) != len(tails):
        issues.append("phase2_validation_toolchain_commands:duplicate_command_tail")

    for tail in sorted(expected_tails):
        if tail not in tails:
            issues.append(f"phase2_validation_toolchain_commands:missing:{tail}")
    for tail in sorted(set(tails) - expected_tails):
        issues.append(f"phase2_validation_toolchain_commands:unexpected:{tail}")
    return issues


def collect_command_inventory_issues(
    py_command_specs: tuple[tuple[Path | str, ...], ...] = PHASE2_VALIDATION_PY_COMMAND_SPECS,
    *,
    direct_command_specs: tuple[tuple[Path | str, ...], ...] = PHASE2_VALIDATION_DIRECT_COMMAND_SPECS,
    expected_count: int = PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT,
    expected_tails: frozenset[str] = PHASE2_VALIDATION_EXPECTED_COMMAND_TAILS,
) -> list[str]:
    issues: list[str] = []
    commands = build_validation_commands(py_command_specs, direct_command_specs)
    if len(commands) != expected_count:
        issues.append(
            "phase2_validation_commands:count="
            f"{len(commands)}:expected={expected_count}"
        )

    tails: list[str] = []
    for command in commands:
        parts: tuple[Path | str, ...]
        if command and command[0] == sys.executable:
            parts = tuple(command[1:])
        else:
            parts = tuple(command)
        tails.append(command_tail_from_parts(parts))
    if len(set(tails)) != len(tails):
        issues.append("phase2_validation_commands:duplicate_command_tail")

    for tail in sorted(expected_tails):
        if tail not in tails:
            issues.append(f"phase2_validation_commands:missing:{tail}")
    for tail in sorted(set(tails) - expected_tails):
        issues.append(f"phase2_validation_commands:unexpected:{tail}")
    return issues


def collect_required_file_inventory_issues(
    required_relative_paths: tuple[str, ...] = PHASE2_REQUIRED_RELATIVE_PATHS,
    *,
    expected_count: int = PHASE2_VALIDATION_EXPECTED_REQUIRED_FILE_COUNT,
    expected_tails: frozenset[str] = PHASE2_VALIDATION_EXPECTED_REQUIRED_TAILS,
) -> list[str]:
    issues: list[str] = []
    count = len(required_relative_paths)
    if count != expected_count:
        issues.append(
            "phase2_validation_required_files:count="
            f"{count}:expected={expected_count}"
        )
    if len(set(required_relative_paths)) != count:
        issues.append("phase2_validation_required_files:duplicate_relative_path")
    for tail in sorted(expected_tails):
        if tail not in required_relative_paths:
            issues.append(f"phase2_validation_required_files:missing:{tail}")
    for tail in sorted(set(required_relative_paths) - expected_tails):
        issues.append(f"phase2_validation_required_files:unexpected:{tail}")
    return issues


def collect_artifact_diff_inventory_issues(
    required_relative_paths: tuple[str, ...] = ARTIFACT_DIFF_REQUIRED_RELATIVE_PATHS,
    *,
    expected_count: int = ARTIFACT_DIFF_EXPECTED_REQUIRED_FILE_COUNT,
    expected_tails: frozenset[str] = ARTIFACT_DIFF_EXPECTED_REQUIRED_TAILS,
) -> list[str]:
    issues: list[str] = []
    count = len(required_relative_paths)
    if count != expected_count:
        issues.append(
            "phase2_validation_artifact_diff_files:count="
            f"{count}:expected={expected_count}"
        )
    if len(set(required_relative_paths)) != count:
        issues.append("phase2_validation_artifact_diff_files:duplicate_relative_path")
    for tail in sorted(expected_tails):
        if tail not in required_relative_paths:
            issues.append(f"phase2_validation_artifact_diff_files:missing:{tail}")
    for tail in sorted(set(required_relative_paths) - expected_tails):
        issues.append(f"phase2_validation_artifact_diff_files:unexpected:{tail}")
    return issues


def run_self_test() -> list[str]:
    checks = [
        (
            "toolchain_command_inventory_ok",
            collect_toolchain_command_inventory_issues(),
            [],
        ),
        (
            "toolchain_command_inventory_missing_self_test",
            collect_toolchain_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_TOOLCHAIN_PY_COMMAND_SPECS
                    if spec != (CHECK_ZIG_TOOLCHAIN, "--self-test")
                )
            ),
            [
                "phase2_validation_toolchain_commands:count=1:expected=2",
                "phase2_validation_toolchain_commands:missing:scripts/zigux/check-zig-toolchain.py --self-test",
            ],
        ),
        (
            "toolchain_command_inventory_missing_gate",
            collect_toolchain_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_TOOLCHAIN_PY_COMMAND_SPECS
                    if spec != (CHECK_ZIG_TOOLCHAIN,)
                )
            ),
            [
                "phase2_validation_toolchain_commands:count=1:expected=2",
                "phase2_validation_toolchain_commands:missing:scripts/zigux/check-zig-toolchain.py",
            ],
        ),
        (
            "toolchain_command_inventory_duplicate_gate",
            collect_toolchain_command_inventory_issues(
                PHASE2_VALIDATION_TOOLCHAIN_PY_COMMAND_SPECS + ((CHECK_ZIG_TOOLCHAIN,),)
            ),
            [
                "phase2_validation_toolchain_commands:count=3:expected=2",
                "phase2_validation_toolchain_commands:duplicate_command_tail",
            ],
        ),
        (
            "command_inventory_ok",
            collect_command_inventory_issues(),
            [],
        ),
        (
            "command_inventory_resolved_zig_path",
            build_validation_commands(
                py_command_specs=(),
                direct_command_specs=(("zig", "test", ROOT / "scripts" / "zigux" / "fixdep.zig"),),
                zig_executable="/tmp/pinned-zig",
            ),
            [["/tmp/pinned-zig", "test", str(ROOT / "scripts" / "zigux" / "fixdep.zig")]],
        ),
        (
            "command_inventory_missing_kconfig_bridge_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (KCONFIG_BRIDGE_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-kconfig-bridge.py",
            ],
        ),
        (
            "command_inventory_missing_kconfig_bridge_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (KCONFIG_BRIDGE_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-kconfig-bridge.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_confdata_helper_anchor_alignment_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (PHASE2_CONFDATA_HELPER_ANCHOR_ALIGNMENT_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_confdata_helper_anchor_alignment_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (PHASE2_CONFDATA_HELPER_ANCHOR_ALIGNMENT_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py",
            ],
        ),
        (
            "command_inventory_missing_tests_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (TESTS_README_ALIGNMENT_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_tests_gate",
            collect_command_inventory_issues(
                tuple(spec for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS if spec != (TESTS_README_ALIGNMENT_CHECKER,))
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-tests-readme-alignment.py",
            ],
        ),
        (
            "command_inventory_missing_fixdep_gate_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (FIXDEP_GATE_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-fixdep-gate.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_fixdep_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (FIXDEP_GATE_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-fixdep-gate.py",
            ],
        ),
        (
            "command_inventory_missing_fixdep_diff_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (FIXDEP_DIFF_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-fixdep-diff.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_fixdep_diff_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (FIXDEP_DIFF_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-fixdep-diff.py",
            ],
        ),
        (
            "command_inventory_missing_kconfig_readme_alignment_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (KCONFIG_README_ALIGNMENT_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_kconfig_readme_alignment_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (KCONFIG_README_ALIGNMENT_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-kconfig-readme-alignment.py",
            ],
        ),
        (
            "command_inventory_missing_kconfig_selftest_alignment_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (PHASE2_KCONFIG_SELFTEST_ALIGNMENT_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_kconfig_selftest_alignment_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (PHASE2_KCONFIG_SELFTEST_ALIGNMENT_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
            ],
        ),
        (
            "command_inventory_missing_phase2_cross_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (PHASE2_CROSS_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-cross.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_phase2_cross_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (PHASE2_CROSS_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-cross.py",
            ],
        ),
        (
            "command_inventory_missing_phase2_cross_selftest_alignment_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (PHASE2_CROSS_SELFTEST_ALIGNMENT_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_phase2_cross_selftest_alignment_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (PHASE2_CROSS_SELFTEST_ALIGNMENT_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-cross-selftest-alignment.py",
            ],
        ),
        (
            "command_inventory_missing_fixdep_direct_replay",
            collect_command_inventory_issues(
                direct_command_specs=(
                    ("zig", "test", ROOT / "scripts" / "zigux" / "genksyms.zig"),
                    ("zig", "test", ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"),
                    ("zig", "test", ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"),
                ),
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:zig test scripts/zigux/fixdep.zig",
            ],
        ),
        (
            "command_inventory_missing_genksyms_direct_replay",
            collect_command_inventory_issues(
                direct_command_specs=(
                    ("zig", "test", ROOT / "scripts" / "zigux" / "fixdep.zig"),
                    ("zig", "test", ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"),
                    ("zig", "test", ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"),
                ),
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:zig test scripts/zigux/genksyms.zig",
            ],
        ),
        (
            "command_inventory_missing_conf_bridge_direct_replay",
            collect_command_inventory_issues(
                direct_command_specs=(
                    ("zig", "test", ROOT / "scripts" / "zigux" / "fixdep.zig"),
                    ("zig", "test", ROOT / "scripts" / "zigux" / "genksyms.zig"),
                    ("zig", "test", ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"),
                ),
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:zig test scripts/zigux/kconfig/conf_bridge.zig",
            ],
        ),
        (
            "command_inventory_missing_confdata_bridge_direct_replay",
            collect_command_inventory_issues(
                direct_command_specs=(
                    ("zig", "test", ROOT / "scripts" / "zigux" / "fixdep.zig"),
                    ("zig", "test", ROOT / "scripts" / "zigux" / "genksyms.zig"),
                    ("zig", "test", ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"),
                ),
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:zig test scripts/zigux/kconfig/confdata_bridge.zig",
            ],
        ),
        (
            "command_inventory_duplicate_toolchain_scope_gate",
            collect_command_inventory_issues(
                PHASE2_VALIDATION_PY_COMMAND_SPECS + ((TOOLCHAIN_PIN_SCOPE_CHECKER,),)
            ),
            [
                "phase2_validation_commands:count=29:expected=28",
                "phase2_validation_commands:duplicate_command_tail",
            ],
        ),
        (
            "command_inventory_missing_tool_manifest_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (PHASE2_TOOL_MANIFEST_PACKET_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_tool_manifest_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (PHASE2_TOOL_MANIFEST_PACKET_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-tool-manifest-packets.py",
            ],
        ),
        (
            "command_inventory_missing_toolchain_pin_scope_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (TOOLCHAIN_PIN_SCOPE_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            ],
        ),
        (
            "command_inventory_missing_toolchain_pin_scope_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (TOOLCHAIN_PIN_SCOPE_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-phase2-toolchain-pin-scope.py",
            ],
        ),
        (
            "command_inventory_missing_genksyms_bridge_gate",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (GENKSYMS_BRIDGE_CHECKER,)
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-genksyms-bridge.py",
            ],
        ),
        (
            "command_inventory_missing_genksyms_bridge_self_test",
            collect_command_inventory_issues(
                tuple(
                    spec
                    for spec in PHASE2_VALIDATION_PY_COMMAND_SPECS
                    if spec != (GENKSYMS_BRIDGE_CHECKER, "--self-test")
                )
            ),
            [
                "phase2_validation_commands:count=27:expected=28",
                "phase2_validation_commands:missing:scripts/zigux/check-genksyms-bridge.py --self-test",
            ],
        ),
        (
            "required_file_inventory_ok",
            collect_required_file_inventory_issues(),
            [],
        ),
        (
            "artifact_diff_inventory_ok",
            collect_artifact_diff_inventory_issues(),
            [],
        ),
        (
            "artifact_diff_inventory_missing_doc",
            collect_artifact_diff_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in ARTIFACT_DIFF_REQUIRED_RELATIVE_PATHS
                    if rel_path != "Documentation/zigux/artifact-diff.md"
                )
            ),
            [
                "phase2_validation_artifact_diff_files:count=1:expected=2",
                "phase2_validation_artifact_diff_files:missing:Documentation/zigux/artifact-diff.md",
            ],
        ),
        (
            "artifact_diff_inventory_missing_helper",
            collect_artifact_diff_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in ARTIFACT_DIFF_REQUIRED_RELATIVE_PATHS
                    if rel_path != "scripts/zigux/artifact_diff.py"
                )
            ),
            [
                "phase2_validation_artifact_diff_files:count=1:expected=2",
                "phase2_validation_artifact_diff_files:missing:scripts/zigux/artifact_diff.py",
            ],
        ),
        (
            "artifact_diff_inventory_unexpected_path",
            collect_artifact_diff_inventory_issues(
                ARTIFACT_DIFF_REQUIRED_RELATIVE_PATHS
                + ("Documentation/zigux/phase2-fixdep-next-step-note.md",)
            ),
            [
                "phase2_validation_artifact_diff_files:count=3:expected=2",
                "phase2_validation_artifact_diff_files:unexpected:Documentation/zigux/phase2-fixdep-next-step-note.md",
            ],
        ),
        (
            "required_file_inventory_missing_fixdep_next_step_note",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "Documentation/zigux/phase2-fixdep-next-step-note.md"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:Documentation/zigux/phase2-fixdep-next-step-note.md",
            ],
        ),
        (
            "required_file_inventory_missing_confdata_bridge_survey",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "Documentation/zigux/phase2-confdata-bridge-survey.md"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:Documentation/zigux/phase2-confdata-bridge-survey.md",
            ],
        ),
        (
            "required_file_inventory_missing_confdata_helper_anchor_alignment_script",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py",
            ],
        ),
        (
            "required_file_inventory_missing_workflow_marker",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != ".github/workflows/zigux-bootstrap.yml"
                )
                + ("scripts/zigux/extra-phase2-checker.py",)
            ),
            [
                "phase2_validation_required_files:missing:.github/workflows/zigux-bootstrap.yml",
                "phase2_validation_required_files:unexpected:scripts/zigux/extra-phase2-checker.py",
            ],
        ),
        (
            "required_file_inventory_duplicate_makefile_entry",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "zigux/tests/fixtures/phase2_tool_manifest.json"
                )
                + ("zigux/Makefile",)
            ),
            [
                "phase2_validation_required_files:duplicate_relative_path",
                "phase2_validation_required_files:missing:zigux/tests/fixtures/phase2_tool_manifest.json",
            ],
        ),
        (
            "required_file_inventory_missing_phase2_validator_script",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "scripts/zigux/validate-phase2.py"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:scripts/zigux/validate-phase2.py",
            ],
        ),
        (
            "required_file_inventory_missing_kconfig_bridge_script",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "scripts/zigux/check-kconfig-bridge.py"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:scripts/zigux/check-kconfig-bridge.py",
            ],
        ),
        (
            "required_file_inventory_missing_kconfig_selftest_alignment_script",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "scripts/zigux/check-phase2-kconfig-selftest-alignment.py"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
            ],
        ),
        (
            "required_file_inventory_missing_genksyms_script",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "scripts/zigux/check-genksyms-bridge.py"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:scripts/zigux/check-genksyms-bridge.py",
            ],
        ),
        (
            "required_file_inventory_missing_conf_bridge_source",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "scripts/zigux/kconfig/conf_bridge.zig"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:scripts/zigux/kconfig/conf_bridge.zig",
            ],
        ),
        (
            "required_file_inventory_missing_confdata_bridge_source",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "scripts/zigux/kconfig/confdata_bridge.zig"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:scripts/zigux/kconfig/confdata_bridge.zig",
            ],
        ),
        (
            "required_file_inventory_missing_genksyms_bridge_manifest",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "zigux/tests/fixtures/genksyms_bridge/manifest.json"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:zigux/tests/fixtures/genksyms_bridge/manifest.json",
            ],
        ),
        (
            "required_file_inventory_missing_conf_manifest",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
            ],
        ),
        (
            "required_file_inventory_missing_confdata_manifest",
            collect_required_file_inventory_issues(
                tuple(
                    rel_path
                    for rel_path in PHASE2_REQUIRED_RELATIVE_PATHS
                    if rel_path != "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json"
                )
            ),
            [
                "phase2_validation_required_files:count=36:expected=37",
                "phase2_validation_required_files:missing:zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
            ],
        ),
    ]

    issues: list[str] = []
    for name, actual, expected in checks:
        if actual != expected:
            issues.append(f"phase2_validation_self_test:{name}:actual={actual}:expected={expected}")
    if len(checks) != PHASE2_VALIDATION_SELF_TEST_CASE_COUNT:
        issues.append(
            "phase2_validation_self_test:case_count:"
            f"actual={len(checks)}:expected={PHASE2_VALIDATION_SELF_TEST_CASE_COUNT}"
        )
    return issues


def run(cmd: list[str]) -> int:
    completed = subprocess.run(cmd, cwd=ROOT, check=False)
    return completed.returncode


def require_files(paths: list[Path]) -> list[str]:
    missing: list[str] = []
    for path in paths:
        if not path.exists():
            missing.append(str(path.relative_to(ROOT)))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current live Phase 2 deterministic gate packet on current master."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Check that the live Phase 2 validator packet inventory is internally consistent.",
    )
    args = parser.parse_args()

    toolchain_command_issues = collect_toolchain_command_inventory_issues()
    command_issues = collect_command_inventory_issues()
    file_inventory_issues = collect_required_file_inventory_issues()
    artifact_diff_inventory_issues = collect_artifact_diff_inventory_issues()
    if (
        toolchain_command_issues
        or command_issues
        or file_inventory_issues
        or artifact_diff_inventory_issues
    ):
        label = "PHASE2_VALIDATION_SELF_TEST" if args.self_test else "PHASE2_VALIDATION"
        print(f"{label}=fail")
        for issue in [
            *toolchain_command_issues,
            *command_issues,
            *file_inventory_issues,
            *artifact_diff_inventory_issues,
        ]:
            print(issue)
        return 1

    if args.self_test:
        self_test_issues = run_self_test()
        if self_test_issues:
            print("PHASE2_VALIDATION_SELF_TEST=fail")
            for issue in self_test_issues:
                print(issue)
            return 1
        print("PHASE2_VALIDATION_SELF_TEST=pass")
        print(
            "PHASE2_VALIDATION_SELF_TEST_REQUIRED_FILE_COUNT="
            f"{PHASE2_VALIDATION_EXPECTED_REQUIRED_FILE_COUNT}"
        )
        print(
            "PHASE2_VALIDATION_SELF_TEST_TOOLCHAIN_COMMAND_COUNT="
            f"{PHASE2_VALIDATION_TOOLCHAIN_EXPECTED_COMMAND_COUNT}"
        )
        print(
            "PHASE2_VALIDATION_SELF_TEST_COMMAND_COUNT="
            f"{PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT}"
        )
        print(
            "PHASE2_VALIDATION_SELF_TEST_CASE_COUNT="
            f"{PHASE2_VALIDATION_SELF_TEST_CASE_COUNT}"
        )
        print(PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_MARKER)
        print(PHASE2_TOOLCHAIN_PIN_SCOPE_MARKER)
        return 0

    missing = require_files(build_required_paths())
    if missing:
        print("PHASE2_VALIDATION=fail")
        print("PHASE2_VALIDATION_MISSING_FILES_START")
        for item in missing:
            print(item)
        print("PHASE2_VALIDATION_MISSING_FILES_END")
        return 1

    zig_executable = resolve_zig_executable()
    commands = build_toolchain_validation_commands() + build_validation_commands(
        zig_executable=zig_executable
    )
    for command in commands:
        if run(command) != 0:
            print("PHASE2_VALIDATION=fail")
            print(f"PHASE2_VALIDATION_FAILED_COMMAND={' '.join(command[1:] if command[0] == sys.executable else command)}")
            return 1

    print("PHASE2_VALIDATION=pass")
    print(
        "PHASE2_VALIDATION_COMMAND_COUNT="
        f"{PHASE2_VALIDATION_TOOLCHAIN_EXPECTED_COMMAND_COUNT + PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
