#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
GENKSYMS_BRIDGE_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py"
)
PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
CHECK_KCONFIG_BRIDGE = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
PHASE2_CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
EXPECTED_TOOL_MANIFEST_TOOLS = [
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/mk_elfconfig.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
]
EXPECTED_CROSS_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]
REQUIRED_PHASE2_FILES = [
    CLOSURE_VALIDATOR,
    ROOT / "scripts" / "zigux" / "artifact_diff.py",
    ROOT / "scripts" / "zigux" / "check-artifact-diff-contract.py",
    ROOT / "scripts" / "zigux" / "check-fixdep-diff.py",
    ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py",
    GENKSYMS_BRIDGE_ALIGNMENT_CHECKER,
    ROOT / "scripts" / "zigux" / "check-genksyms-crc-diff.py",
    ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py",
    PHASE2_CROSS_CHECKER,
    ROOT / "scripts" / "zigux" / "check-mk-elfconfig-diff.py",
    ROOT / "scripts" / "zigux" / "fixdep.zig",
    ROOT / "scripts" / "zigux" / "genksyms.zig",
    ROOT / "scripts" / "zigux" / "genksyms_crc.zig",
    ROOT / "scripts" / "zigux" / "mk_elfconfig.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
    ROOT / "Documentation" / "zigux" / "phase2-closure.md",
    ROOT / "zigux" / "Makefile",
    PHASE2_TOOL_MANIFEST,
    PHASE2_CROSS_TARGETS,
]
PHASE2_GENKSYMS_BRIDGE_ALIGNMENT_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=7",
]
PHASE2_CROSS_REQUIRED_SOURCE_MARKERS = [
    "phase2-cross:tool_manifest_path_missing:",
    "print('PHASE2_CROSS_SELF_TEST_CASE_COUNT=9')",
]
PHASE2_KCONFIG_REQUIRED_SOURCE_MARKERS = [
    "assert total_self_test_cases == 6",
]


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_list_manifest(
    path: Path,
    *,
    label: str,
    count_key: str,
    expected_count: int,
    list_key: str,
    expected_items: list[str],
) -> list[str]:
    payload = load_json(path)
    issues: list[str] = []
    if not isinstance(payload, dict):
        return [f"{label}:expected_object"]

    if payload.get("phase") != "Phase 2":
        issues.append(f"{label}:phase={payload.get('phase')!r}:expected='Phase 2'")
    if payload.get("status") != "closed":
        issues.append(f"{label}:status={payload.get('status')!r}:expected='closed'")
    if payload.get(count_key) != expected_count:
        issues.append(f"{label}:{count_key}={payload.get(count_key)!r}:expected={expected_count}")

    items = payload.get(list_key)
    if not isinstance(items, list):
        issues.append(f"{label}:{list_key}:expected_list")
        return issues
    if len(items) != expected_count:
        issues.append(f"{label}:{list_key}_len={len(items)}:expected={expected_count}")
    if items != expected_items:
        issues.append(f"{label}:{list_key}=expected_exact_list")
    for rel in items:
        if not isinstance(rel, str):
            issues.append(f"{label}:{list_key}:non_string_item")
            continue
        if list_key == "tools" and not (ROOT / rel).exists():
            issues.append(f"{label}:missing_tool:{rel}")
    return issues


def validate_source_markers(path: Path, *, label: str, required_markers: list[str]) -> list[str]:
    source = path.read_text(encoding="utf-8")
    issues: list[str] = []
    for marker in required_markers:
        if marker not in source:
            issues.append(f"{label}:missing_marker:{marker}")
    return issues


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_PHASE2_FILES if not path.exists()]
    if missing:
        print("PHASE2_VALIDATION=fail")
        print("MISSING_PHASE2_SHARED_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_SHARED_FILES_END")
        return 1

    issues: list[str] = []
    issues.extend(
        validate_list_manifest(
            PHASE2_TOOL_MANIFEST,
            label="phase2_tool_manifest",
            count_key="tool_count",
            expected_count=6,
            list_key="tools",
            expected_items=EXPECTED_TOOL_MANIFEST_TOOLS,
        )
    )
    issues.extend(
        validate_list_manifest(
            PHASE2_CROSS_TARGETS,
            label="phase2_cross_targets",
            count_key="target_count",
            expected_count=3,
            list_key="targets",
            expected_items=EXPECTED_CROSS_TARGETS,
        )
    )
    issues.extend(
        validate_source_markers(
            GENKSYMS_BRIDGE_ALIGNMENT_CHECKER,
            label="phase2_genksyms_bridge_alignment_checker",
            required_markers=PHASE2_GENKSYMS_BRIDGE_ALIGNMENT_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            PHASE2_CROSS_CHECKER,
            label="phase2_cross_checker",
            required_markers=PHASE2_CROSS_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            CHECK_KCONFIG_BRIDGE,
            label="phase2_kconfig_bridge_checker",
            required_markers=PHASE2_KCONFIG_REQUIRED_SOURCE_MARKERS,
        )
    )

    if issues:
        print("PHASE2_VALIDATION=fail")
        print("INVALID_PHASE2_SHARED_METADATA_START")
        for item in issues:
            print(item)
        print("INVALID_PHASE2_SHARED_METADATA_END")
        return 1

    result = subprocess.run(
        [sys.executable, str(GENKSYMS_BRIDGE_ALIGNMENT_CHECKER)],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print("PHASE2_VALIDATION=fail")
        return result.returncode

    result = subprocess.run([sys.executable, str(CLOSURE_VALIDATOR)], cwd=ROOT)
    if result.returncode == 0:
        print("PHASE2_VALIDATION=pass")
    else:
        print("PHASE2_VALIDATION=fail")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
