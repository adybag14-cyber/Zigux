#!/usr/bin/env python3
"""Guard the live kconfig helper surface behind the Phase 2 cross-route packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
CROSS_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
CROSS_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
KCONFIG_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"

ROUTE = "make -C zigux phase2-cross"
EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
SUPPORTED_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_SELF_TEST_CASE_COUNT = 25

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-kconfig:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

REQUIRED_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
)

CONF_BRIDGE_MARKERS = (
    "pub const Mode = enum {",
    "pub const Request = struct {",
    "test ",
)

CONFDATA_BRIDGE_MARKERS = (
    "pub const Entry = struct {",
    "pub const Summary = struct {",
    "test ",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_exact_line_issues(
    text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def load_archive_target_scope(root: Path) -> list[str]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(
            f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )

    normalized: list[str] = []
    for target in archive_target_scope:
        if not isinstance(target, str) or target not in SUPPORTED_TARGETS:
            raise SystemExit(
                f"unsupported archive_target_scope targets in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized.append(target)
    if len(set(normalized)) != len(normalized):
        raise SystemExit(
            f"duplicate archive_target_scope entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )
    return normalized


def collect_fixture_issues(payload: object, root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    archive_target_scope = load_archive_target_scope(root)

    if not isinstance(payload, dict):
        return [("INVALID_CROSS_FIXTURE_SHAPE", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_CROSS_FIXTURE_FIELD", "phase"))
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(("INVALID_CROSS_FIXTURE_FIELD", "status"))
    if payload.get("route") != ROUTE:
        issues.append(("INVALID_CROSS_FIXTURE_FIELD", "route"))
    if payload.get("archive_target_scope") != archive_target_scope:
        issues.append(("INVALID_CROSS_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_CROSS_FIXTURE_FIELD", "cross_targets"))
        return issues

    expected_modes = {
        "x86_64-linux": "archive_required" if "x86_64-linux" in archive_target_scope else "route_contract_only",
        "aarch64-linux": "archive_required" if "aarch64-linux" in archive_target_scope else "route_contract_only",
    }
    actual_modes: dict[str, str] = {}

    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")
        review_status = entry.get("review_status")
        if not isinstance(target, str) or target not in SUPPORTED_TARGETS:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        if target in actual_modes:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if not isinstance(review_status, str) or not review_status:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        if validation_mode not in ("archive_required", "route_contract_only"):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        actual_modes[target] = validation_mode

    if actual_modes != expected_modes:
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_modes, sort_keys=True)))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, WORKFLOW)),
            REQUIRED_WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINE",
            "DUPLICATE_WORKFLOW_LINE",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, MAKEFILE)),
            REQUIRED_MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, PHASE2_NOTES)),
            REQUIRED_NOTES_MARKERS,
            "MISSING_PHASE2_NOTES_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, CONF_BRIDGE)),
            CONF_BRIDGE_MARKERS,
            "MISSING_CONF_BRIDGE_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, CONFDATA_BRIDGE)),
            CONFDATA_BRIDGE_MARKERS,
            "MISSING_CONFDATA_BRIDGE_MARKER",
        )
    )

    for path in (CROSS_CHECKER, CROSS_ALIGNMENT, KCONFIG_CHECKER):
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_PATH", str(path.relative_to(ROOT))))

    issues.extend(collect_fixture_issues(read_json(resolve_path(root, CROSS_FIXTURE)), root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_KCONFIG_SURFACE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(REQUIRED_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, CROSS_CHECKER), "present\n")
    write_text(resolve_path(root, CROSS_ALIGNMENT), "present\n")
    write_text(resolve_path(root, KCONFIG_CHECKER), "present\n")
    write_text(resolve_path(root, CONF_BRIDGE), "\n".join(CONF_BRIDGE_MARKERS) + "\n")
    write_text(resolve_path(root, CONFDATA_BRIDGE), "\n".join(CONFDATA_BRIDGE_MARKERS) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, CROSS_FIXTURE),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "status": EXPECTED_STATUS,
                "route": ROUTE,
                "archive_target_scope": ["x86_64-linux"],
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": ROUTE,
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": ROUTE,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_kconfig_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[3], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[3]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        notes_path = resolve_path(root, PHASE2_NOTES)
        notes_path.write_text(
            remove_marker(notes_path.read_text(encoding="utf-8"), REQUIRED_NOTES_MARKERS[2]),
            encoding="utf-8",
        )
        assert ("MISSING_PHASE2_NOTES_MARKER", REQUIRED_NOTES_MARKERS[2]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        conf_bridge_path = resolve_path(root, CONF_BRIDGE)
        conf_bridge_path.write_text(
            remove_marker(conf_bridge_path.read_text(encoding="utf-8"), CONF_BRIDGE_MARKERS[1]),
            encoding="utf-8",
        )
        assert ("MISSING_CONF_BRIDGE_MARKER", CONF_BRIDGE_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        confdata_path = resolve_path(root, CONFDATA_BRIDGE)
        confdata_path.write_text(
            remove_marker(confdata_path.read_text(encoding="utf-8"), CONFDATA_BRIDGE_MARKERS[1]),
            encoding="utf-8",
        )
        assert ("MISSING_CONFDATA_BRIDGE_MARKER", CONFDATA_BRIDGE_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["phase"] = "Phase X"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_FIXTURE_FIELD", "phase") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["validation_mode"] = "route_contract_only"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["route"] = "make -C zigux phase2-kconfig"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["review_status"] = ""
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ENTRY", "x86_64-linux:review_status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"].append(payload["cross_targets"][0].copy())
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("DUPLICATE_CROSS_TARGET_ENTRY", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["target"] = "riscv64-linux"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ENTRY", "target") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        policy_payload["archive_sha256"] = {"aarch64-linux": "4" * 64}
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        payload["cross_targets"][0]["validation_mode"] = "route_contract_only"
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_payload["upgrade_policy"]["archive_target_scope"] = ["riscv64-linux"]
        policy_payload["archive_sha256"] = {"riscv64-linux": "4" * 64}
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "unsupported archive_target_scope targets" in str(exc)
        else:
            raise AssertionError("unsupported archive target did not abort")
        checks_run += 1

        build_self_test_root(root)
        for path in (
            WORKFLOW,
            MAKEFILE,
            TOOLCHAIN_POLICY,
            CROSS_FIXTURE,
            CONF_BRIDGE,
            CONFDATA_BRIDGE,
            PHASE2_NOTES,
        ):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
            else:
                raise AssertionError(f"missing file did not abort: {path}")
            checks_run += 1

        for path in (CROSS_CHECKER, CROSS_ALIGNMENT, KCONFIG_CHECKER):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            assert ("MISSING_REQUIRED_PATH", str(path.relative_to(ROOT))) in collect_issues(root)
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_KCONFIG_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_CROSS_KCONFIG_SURFACE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 cross-route packet tied to the live kconfig helper surface."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    archive_target_scope = load_archive_target_scope(root)
    fixture = read_json(resolve_path(root, CROSS_FIXTURE))
    assert isinstance(fixture, dict)
    cross_targets = fixture.get("cross_targets")
    assert isinstance(cross_targets, list)

    print("PHASE2_CROSS_KCONFIG_SURFACE=pass")
    print(f"PHASE2_CROSS_KCONFIG_SURFACE_ARCHIVE_SCOPE_COUNT={len(archive_target_scope)}")
    print(f"PHASE2_CROSS_KCONFIG_SURFACE_TARGET_COUNT={len(cross_targets)}")
    print(f"PHASE2_CROSS_KCONFIG_SURFACE_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
