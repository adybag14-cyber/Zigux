#!/usr/bin/env python3
"""Keep the Lane 21 cross-target replay helper aligned with the live packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
HELPER = ROOT / "scripts" / "zigux" / "check-phase2-cross-target-replay.py"
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_TARGET_ORDER = ("x86_64-linux", "aarch64-linux")
EXPECTED_REQUIRED_MAKE_ROUTES = ("phase2-toolchain", "phase2-validate", "phase2-cross")
EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_STATUS_BY_MODE = {
    "archive_required": "pinned bootstrap archive",
    "route_contract_only": "route contract only",
}
EXPECTED_SELF_TEST_CASE_COUNT = 16

HELPER_MARKERS = (
    'FIXTURE = Path("zigux") / "tests" / "fixtures" / "phase2_cross_targets.json"',
    'POLICY = Path("scripts") / "zigux" / "zig-toolchain-policy.json"',
    'Path("scripts") / "zigux" / "kconfig" / "conf_bridge.zig"',
    'Path("scripts") / "zigux" / "kconfig" / "confdata_bridge.zig"',
    'EXPECTED_TARGET_ORDER = ("x86_64-linux", "aarch64-linux")',
    'EXPECTED_REQUIRED_MAKE_ROUTES = (',
    'DEFAULT_TIMEOUT_SECONDS = 300',
    'EXPECTED_SELF_TEST_CASE_COUNT = 17',
    'print("PHASE2_CROSS_TARGET_REPLAY=pass")',
    'print(f"PHASE2_CROSS_TARGET_REPLAY_MODE={mode}")',
    'print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET_COUNT={len(targets)}")',
    "print(f\"PHASE2_CROSS_TARGET_REPLAY_TARGETS={','.join(targets)}\")",
    'print(f"PHASE2_CROSS_TARGET_REPLAY_FILE_COUNT={len(ZIG_TEST_FILES)}")',
    'print(f"PHASE2_CROSS_TARGET_REPLAY_COMPLETED_TARGET_COUNT={len(completed_targets)}")',
    "print(f\"PHASE2_CROSS_TARGET_REPLAY_COMPLETED_TARGETS={','.join(completed_targets)}\")",
    'parser.add_argument("--zig", help="Zig executable or absolute path to use for target replays")',
    'parser.add_argument("--target", help="Replay one configured target")',
    'parser.add_argument("--all-targets", action="store_true", help="Replay every configured target")',
    'parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample tree and exit")',
    'parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_helper_marker_issues(helper_text: str) -> list[tuple[str, str]]:
    return [("MISSING_HELPER_MARKER", marker) for marker in HELPER_MARKERS if marker not in helper_text]


def load_expected_modes(root: Path) -> dict[str, str]:
    payload = read_json(resolve_path(root, POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, POLICY)}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, POLICY)}")
    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        raise SystemExit(f"invalid required_make_routes in required file: {resolve_path(root, POLICY)}")
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {resolve_path(root, POLICY)}")
    scope: list[str] = []
    seen_targets: set[str] = set()
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"invalid archive_target_scope entry in required file: {resolve_path(root, POLICY)}")
        target = value.strip()
        if target in seen_targets:
            raise SystemExit(
                f"duplicate archive_target_scope entry in required file: {resolve_path(root, POLICY)}: {target}"
            )
        if target not in EXPECTED_TARGET_ORDER:
            raise SystemExit(
                f"unsupported archive_target_scope target in required file: {resolve_path(root, POLICY)}: {target}"
            )
        scope.append(target)
        seen_targets.add(target)
    return {
        target: ("archive_required" if target in seen_targets else "route_contract_only")
        for target in EXPECTED_TARGET_ORDER
    }


def collect_fixture_issues(root: Path) -> list[tuple[str, str]]:
    payload = read_json(resolve_path(root, FIXTURE))
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", type(payload).__name__)]
    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if payload.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if payload.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))

    expected_modes = load_expected_modes(root)
    expected_scope = [target for target, mode in expected_modes.items() if mode == "archive_required"]
    if payload.get("archive_target_scope") != expected_scope:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    seen_targets: set[str] = set()
    target_order: list[str] = []
    actual_modes: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        validation_mode = entry.get("validation_mode")
        review_status = entry.get("review_status")
        route = entry.get("route")
        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        target = target.strip()
        target_order.append(target)
        if target in seen_targets:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        seen_targets.add(target)
        if route != EXPECTED_ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if validation_mode not in EXPECTED_STATUS_BY_MODE:
            issues.append(("INVALID_CROSS_TARGET_MODE", target))
            continue
        if review_status != EXPECTED_STATUS_BY_MODE[validation_mode]:
            issues.append(("INVALID_CROSS_TARGET_STATUS", target))
        actual_modes[target] = validation_mode

    if target_order != list(EXPECTED_TARGET_ORDER):
        issues.append(("INVALID_TARGET_ORDER", ",".join(target_order)))
    if actual_modes != expected_modes:
        issues.append(("INVALID_TARGET_MODE_MAP", json.dumps(actual_modes, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    helper_text = read_text(resolve_path(root, HELPER))
    issues = collect_helper_marker_issues(helper_text)
    issues.extend(collect_fixture_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CROSS_TARGET_REPLAY_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, HELPER),
        "\n".join(
            (
                '#!/usr/bin/env python3',
                'FIXTURE = Path("zigux") / "tests" / "fixtures" / "phase2_cross_targets.json"',
                'POLICY = Path("scripts") / "zigux" / "zig-toolchain-policy.json"',
                'ZIG_TEST_FILES = (',
                '    Path("scripts") / "zigux" / "kconfig" / "conf_bridge.zig",',
                '    Path("scripts") / "zigux" / "kconfig" / "confdata_bridge.zig",',
                ')',
                'EXPECTED_TARGET_ORDER = ("x86_64-linux", "aarch64-linux")',
                'EXPECTED_REQUIRED_MAKE_ROUTES = (',
                '    "phase2-toolchain",',
                '    "phase2-validate",',
                '    "phase2-cross",',
                ')',
                'DEFAULT_TIMEOUT_SECONDS = 300',
                'EXPECTED_SELF_TEST_CASE_COUNT = 17',
                'print("PHASE2_CROSS_TARGET_REPLAY=pass")',
                'print(f"PHASE2_CROSS_TARGET_REPLAY_MODE={mode}")',
                'print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET_COUNT={len(targets)}")',
                "print(f\"PHASE2_CROSS_TARGET_REPLAY_TARGETS={','.join(targets)}\")",
                'print(f"PHASE2_CROSS_TARGET_REPLAY_FILE_COUNT={len(ZIG_TEST_FILES)}")',
                'print(f"PHASE2_CROSS_TARGET_REPLAY_COMPLETED_TARGET_COUNT={len(completed_targets)}")',
                "print(f\"PHASE2_CROSS_TARGET_REPLAY_COMPLETED_TARGETS={','.join(completed_targets)}\")",
                'parser.add_argument("--zig", help="Zig executable or absolute path to use for target replays")',
                'parser.add_argument("--target", help="Replay one configured target")',
                'parser.add_argument("--all-targets", action="store_true", help="Replay every configured target")',
                'parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample tree and exit")',
                'parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")',
                "",
            )
        ),
    )
    write_text(
        resolve_path(root, POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, FIXTURE),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": EXPECTED_ROUTE,
                "archive_target_scope": ["x86_64-linux"],
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": EXPECTED_ROUTE,
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": EXPECTED_ROUTE,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_target_replay_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        helper_path = resolve_path(root, HELPER)
        policy_path = resolve_path(root, POLICY)
        fixture_path = resolve_path(root, FIXTURE)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in HELPER_MARKERS[:5]:
            build_self_test_root(root)
            helper_path.write_text(helper_path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_HELPER_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["review_status"] = "later"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_STATUS", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"].reverse()
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_TARGET_ORDER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_TARGET_MODE_MAP" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing required_make_routes did not abort")

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        payload["archive_sha256"] = {"aarch64-linux": "4" * 64}
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        payload["cross_targets"][0]["validation_mode"] = "route_contract_only"
        payload["cross_targets"][0]["review_status"] = "route contract only"
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        payload["cross_targets"][1]["review_status"] = "pinned bootstrap archive"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["riscv64-linux"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "unsupported archive_target_scope target" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("unsupported archive target did not abort")

        build_self_test_root(root)
        helper_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing helper did not abort")

        build_self_test_root(root)
        fixture_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing fixture did not abort")

        build_self_test_root(root)
        policy_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing policy did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_TARGET_REPLAY_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TARGET_REPLAY_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 21 cross-target replay helper aligned with its live packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    expected_modes = load_expected_modes(args.root.resolve())
    print("PHASE2_CROSS_TARGET_REPLAY_ALIGNMENT=pass")
    print(f"PHASE2_CROSS_TARGET_REPLAY_ALIGNMENT_HELPER_MARKER_COUNT={len(HELPER_MARKERS)}")
    print(f"PHASE2_CROSS_TARGET_REPLAY_ALIGNMENT_TARGET_COUNT={len(expected_modes)}")
    print(
        "PHASE2_CROSS_TARGET_REPLAY_ALIGNMENT_ARCHIVE_REQUIRED_COUNT="
        f"{sum(1 for mode in expected_modes.values() if mode == 'archive_required')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
