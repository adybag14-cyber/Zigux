#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

EXPECTED_PACKET_FIELDS = {
    "fixdep_packet": "zigux/tests/fixtures/fixdep/manifest.json",
    "genksyms_bridge_packet": "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "kconfig_conf_bridge_packet": "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "kconfig_confdata_bridge_packet": "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
}

EXPECTED_PACKET_TOOL_FIELDS = {
    "fixdep_packet": "scripts/zigux/fixdep.zig",
    "genksyms_bridge_packet": "scripts/zigux/genksyms.zig",
    "kconfig_conf_bridge_packet": "scripts/zigux/kconfig/conf_bridge.zig",
    "kconfig_confdata_bridge_packet": "scripts/zigux/kconfig/confdata_bridge.zig",
}

EXPECTED_TOOLS = [
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/mk_elfconfig.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
]
EXPECTED_TOOL_COUNT = len(EXPECTED_TOOLS)
EXPECTED_PACKET_STATUS = "closed"


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def required_files_for(root: Path) -> list[Path]:
    files = [root / PHASE2_TOOL_MANIFEST.relative_to(ROOT)]
    for rel_path in EXPECTED_PACKET_FIELDS.values():
        files.append(root / rel_path)
    return files


def validate_root(root: Path) -> list[str]:
    missing = [str(path.relative_to(root)) for path in required_files_for(root) if not path.exists()]
    if missing:
        return [f"missing_file:{item}" for item in missing]

    manifest = load_json_object(root / PHASE2_TOOL_MANIFEST.relative_to(ROOT), label="phase2_tool_manifest")
    issues: list[str] = []
    seen_paths: set[str] = set()

    if manifest.get("tool_count") != EXPECTED_TOOL_COUNT:
        issues.append(
            f"manifest_tool_count:value={manifest.get('tool_count')!r}:expected={EXPECTED_TOOL_COUNT}"
        )

    tools = manifest.get("tools")
    if tools != EXPECTED_TOOLS:
        issues.append(f"manifest_tools:value={tools!r}:expected={EXPECTED_TOOLS!r}")

    for field_name, expected_path in EXPECTED_PACKET_FIELDS.items():
        value = manifest.get(field_name)
        if value != expected_path:
            issues.append(f"manifest_field:{field_name}:value={value!r}:expected={expected_path!r}")
            continue
        if value in seen_paths:
            issues.append(f"manifest_field:{field_name}:duplicate_packet_path:{value}")
            continue
        seen_paths.add(value)
        packet_path = root / value
        packet = load_json_object(packet_path, label=field_name)
        expected_tool = EXPECTED_PACKET_TOOL_FIELDS[field_name]
        if packet.get("tool") != expected_tool:
            issues.append(
                f"packet_tool:{field_name}:value={packet.get('tool')!r}:expected={expected_tool!r}"
            )
        if packet.get("status") != EXPECTED_PACKET_STATUS:
            issues.append(
                f"packet_status:{field_name}:value={packet.get('status')!r}:expected={EXPECTED_PACKET_STATUS!r}"
            )

    unexpected_fields = sorted(
        field_name
        for field_name in manifest
        if field_name.endswith("_packet") and field_name not in EXPECTED_PACKET_FIELDS
    )
    for field_name in unexpected_fields:
        issues.append(f"unexpected_packet_field:{field_name}")

    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict[str, object]) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=False) + "\n")


def build_self_test_root(root: Path) -> None:
    write_json(
        root / "zigux/tests/fixtures/phase2_tool_manifest.json",
        {
            "phase": "Phase 2",
            "status": "closed",
            "tool_count": EXPECTED_TOOL_COUNT,
            "tools": EXPECTED_TOOLS,
            **EXPECTED_PACKET_FIELDS,
        },
    )
    write_json(
        root / EXPECTED_PACKET_FIELDS["fixdep_packet"],
        {
            "tool": EXPECTED_PACKET_TOOL_FIELDS["fixdep_packet"],
            "status": EXPECTED_PACKET_STATUS,
        },
    )
    write_json(
        root / EXPECTED_PACKET_FIELDS["genksyms_bridge_packet"],
        {
            "tool": EXPECTED_PACKET_TOOL_FIELDS["genksyms_bridge_packet"],
            "status": EXPECTED_PACKET_STATUS,
        },
    )
    write_json(
        root / EXPECTED_PACKET_FIELDS["kconfig_conf_bridge_packet"],
        {
            "tool": EXPECTED_PACKET_TOOL_FIELDS["kconfig_conf_bridge_packet"],
            "status": EXPECTED_PACKET_STATUS,
        },
    )
    write_json(
        root / EXPECTED_PACKET_FIELDS["kconfig_confdata_bridge_packet"],
        {
            "tool": EXPECTED_PACKET_TOOL_FIELDS["kconfig_confdata_bridge_packet"],
            "status": EXPECTED_PACKET_STATUS,
        },
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase2_tool_manifest_packets_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert validate_root(root) == []

        build_self_test_root(root)
        manifest_path = root / "zigux/tests/fixtures/phase2_tool_manifest.json"
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        del manifest["fixdep_packet"]
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert "manifest_field:fixdep_packet:value=None:expected='zigux/tests/fixtures/fixdep/manifest.json'" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["tool_count"] = EXPECTED_TOOL_COUNT - 1
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert f"manifest_tool_count:value={EXPECTED_TOOL_COUNT - 1}:expected={EXPECTED_TOOL_COUNT}" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["tools"] = EXPECTED_TOOLS[:-1]
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert f"manifest_tools:value={EXPECTED_TOOLS[:-1]!r}:expected={EXPECTED_TOOLS!r}" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["tools"] = list(reversed(EXPECTED_TOOLS))
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert f"manifest_tools:value={list(reversed(EXPECTED_TOOLS))!r}:expected={EXPECTED_TOOLS!r}" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["kconfig_confdata_bridge_packet"] = EXPECTED_PACKET_FIELDS["kconfig_conf_bridge_packet"]
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert (
            "manifest_field:kconfig_confdata_bridge_packet:value='zigux/tests/fixtures/kconfig_bridge/conf_manifest.json':expected='zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json'"
            in issues
        )

        build_self_test_root(root)
        packet_path = root / EXPECTED_PACKET_FIELDS["genksyms_bridge_packet"]
        packet = load_json_object(packet_path, label="genksyms_bridge_packet")
        packet["tool"] = "scripts/zigux/genksyms_crc.zig"
        write_json(packet_path, packet)
        issues = validate_root(root)
        assert (
            "packet_tool:genksyms_bridge_packet:value='scripts/zigux/genksyms_crc.zig':expected='scripts/zigux/genksyms.zig'"
            in issues
        )

        build_self_test_root(root)
        packet_path = root / EXPECTED_PACKET_FIELDS["kconfig_conf_bridge_packet"]
        packet = load_json_object(packet_path, label="kconfig_conf_bridge_packet")
        packet["status"] = "open"
        write_json(packet_path, packet)
        issues = validate_root(root)
        assert "packet_status:kconfig_conf_bridge_packet:value='open':expected='closed'" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["extra_packet"] = "zigux/tests/fixtures/phase2_extra/manifest.json"
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert "unexpected_packet_field:extra_packet" in issues

        build_self_test_root(root)
        missing_path = root / EXPECTED_PACKET_FIELDS["kconfig_confdata_bridge_packet"]
        missing_path.unlink()
        issues = validate_root(root)
        assert "missing_file:zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json" in issues

    print("PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST=pass")
    print("PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST_CASE_COUNT=9")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 2 tool manifest keeps the committed packet links explicit."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checkout-free self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE2_TOOL_MANIFEST_PACKETS=fail")
        print("PHASE2_TOOL_MANIFEST_PACKETS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_TOOL_MANIFEST_PACKETS_ISSUES_END")
        return 1

    print("PHASE2_TOOL_MANIFEST_PACKETS=pass")
    print(f"PHASE2_TOOL_MANIFEST_PACKET_FIELD_COUNT={len(EXPECTED_PACKET_FIELDS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
