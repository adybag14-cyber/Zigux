#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONF_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"

EXPECTED_IMPLICIT_OMISSION_MODES = [
    "allmodconfig",
    "randconfig",
]

EXPECTED_EXPLICIT_OVERRIDE_MODES = [
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "randconfig",
]

REQUIRED_HELPER_ANCHORS = [
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits explicit randconfig allconfig override when present",
    "conf bridge omits randconfig allconfig sentinel without explicit override",
]

EXPECTED_SELF_TEST_CASE_COUNT = 4


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    manifest_path = root / CONF_MANIFEST.relative_to(ROOT)
    bridge_path = root / CONF_BRIDGE.relative_to(ROOT)

    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        return [("INVALID_CONF_MANIFEST_PAYLOAD", type(manifest).__name__)]

    implicit_modes = manifest.get("helper_local_allconfig_implicit_omission_modes")
    if implicit_modes != EXPECTED_IMPLICIT_OMISSION_MODES:
        issues.append(
            (
                "CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES_MISMATCH",
                f"actual={implicit_modes!r}:expected={EXPECTED_IMPLICIT_OMISSION_MODES!r}",
            )
        )

    explicit_modes = manifest.get("helper_local_allconfig_explicit_override_modes")
    if explicit_modes != EXPECTED_EXPLICIT_OVERRIDE_MODES:
        issues.append(
            (
                "CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES_MISMATCH",
                f"actual={explicit_modes!r}:expected={EXPECTED_EXPLICIT_OVERRIDE_MODES!r}",
            )
        )

    bridge_text = read_text(bridge_path)
    for anchor in REQUIRED_HELPER_ANCHORS:
        if anchor not in bridge_text:
            issues.append(("MISSING_CONF_BRIDGE_HELPER_ANCHOR", anchor))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET=fail")
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
    write_text(
        root / CONF_MANIFEST.relative_to(ROOT),
        json.dumps(
            {
                "helper_local_allconfig_implicit_omission_modes": EXPECTED_IMPLICIT_OMISSION_MODES,
                "helper_local_allconfig_explicit_override_modes": EXPECTED_EXPLICIT_OVERRIDE_MODES,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / CONF_BRIDGE.relative_to(ROOT),
        "\n".join(f'test "{anchor}" {{}}' for anchor in REQUIRED_HELPER_ANCHORS) + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_allconfig_helper_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / CONF_MANIFEST.relative_to(ROOT)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["helper_local_allconfig_implicit_omission_modes"] = ["randconfig"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(
            code == "CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES_MISMATCH"
            for code, _ in collect_issues(root)
        )
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / CONF_MANIFEST.relative_to(ROOT)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["helper_local_allconfig_explicit_override_modes"] = ["randconfig"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(
            code == "CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES_MISMATCH"
            for code, _ in collect_issues(root)
        )
        checks_run += 1

        build_self_test_root(root)
        bridge_path = root / CONF_BRIDGE.relative_to(ROOT)
        bridge_text = read_text(bridge_path).replace(REQUIRED_HELPER_ANCHORS[-1], "drifted anchor", 1)
        write_text(bridge_path, bridge_text)
        assert ("MISSING_CONF_BRIDGE_HELPER_ANCHOR", REQUIRED_HELPER_ANCHORS[-1]) in collect_issues(root)
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        print("PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST=fail")
        print(f"PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST_CASE_COUNT_EXPECTED={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 1

    print("PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the helper-local conf_bridge allconfig packet against the manifest."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET=pass")
    print(
        f"PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_IMPLICIT_OMISSION_MODE_COUNT={len(EXPECTED_IMPLICIT_OMISSION_MODES)}"
    )
    print(
        f"PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_EXPLICIT_OVERRIDE_MODE_COUNT={len(EXPECTED_EXPLICIT_OVERRIDE_MODES)}"
    )
    print(f"PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_HELPER_ANCHOR_COUNT={len(REQUIRED_HELPER_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
