#!/usr/bin/env python3
"""Check that the Phase 2 toolchain policy routes exist in zigux/Makefile."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
MAKEFILE = ROOT / "zigux" / "Makefile"
EXPECTED_SELF_TEST_CASE_COUNT = 9


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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_route_list(payload: object, policy_path: Path) -> list[str]:
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")

    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError(f"invalid required_make_routes in {policy_path}")

    normalized: list[str] = []
    seen: set[str] = set()
    for entry in routes:
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError(f"invalid required_make_routes entry in {policy_path}")
        route = entry.strip()
        if route in seen:
            raise ValueError(f"duplicate required_make_routes entry in {policy_path}: {route}")
        normalized.append(route)
        seen.add(route)

    return normalized


def load_required_make_routes(policy_path: Path = TOOLCHAIN_POLICY) -> list[str]:
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    return require_route_list(payload, policy_path)


def count_route_targets(makefile_text: str, route: str) -> int:
    pattern = re.compile(rf"^{re.escape(route)}:(?:\s|$)", re.MULTILINE)
    return len(pattern.findall(makefile_text))


def collect_route_issues(makefile_text: str, required_routes: list[str]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for route in required_routes:
        count = count_route_targets(makefile_text, route)
        if count == 0:
            issues.append(("MISSING_REQUIRED_ROUTE", route))
        elif count != 1:
            issues.append(("DUPLICATE_REQUIRED_ROUTE", f"{route}:count={count}"))
    return issues


def emit_issues(issues: list[tuple[str, str]], makefile_path: Path, required_routes: list[str]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_REQUIRED_MAKE_ROUTES=fail")
    print(f"PHASE2_REQUIRED_MAKEFILE_PATH={makefile_path}")
    print("PHASE2_REQUIRED_ROUTE_LIST=" + ",".join(required_routes))
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> tuple[Path, Path]:
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    makefile_path = resolve_path(root, MAKEFILE)
    write_text(
        policy_path,
        json.dumps(
            {
                "phase": "Phase 2",
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
        makefile_path,
        "\n".join(
            (
                "PHONY += phase2-toolchain phase2-validate phase2",
                "phase2-toolchain:",
                "\t@true",
                "phase2-validate: phase2-toolchain",
                "\t@true",
                "phase2: phase2-validate",
                "\t@true",
            )
        )
        + "\n",
    )
    return policy_path, makefile_path


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_required_make_routes_") as tmp_dir:
        root = Path(tmp_dir)
        policy_path, makefile_path = build_self_test_root(root)

        required_routes = load_required_make_routes(policy_path)
        assert required_routes == ["phase2-toolchain", "phase2-validate"]
        assert collect_route_issues(read_text(makefile_path), required_routes) == []
        checks_run += 1

        makefile_path.write_text("phase2-validate:\n\t@true\n", encoding="utf-8")
        assert ("MISSING_REQUIRED_ROUTE", "phase2-toolchain") in collect_route_issues(
            read_text(makefile_path), required_routes
        )
        checks_run += 1

        _, makefile_path = build_self_test_root(root)
        makefile_path.write_text(
            read_text(makefile_path) + "phase2-toolchain:\n\t@true\n",
            encoding="utf-8",
        )
        assert ("DUPLICATE_REQUIRED_ROUTE", "phase2-toolchain:count=2") in collect_route_issues(
            read_text(makefile_path), required_routes
        )
        checks_run += 1

        policy_path.write_text("{not-json}\n", encoding="utf-8")
        try:
            load_required_make_routes(policy_path)
        except ValueError as exc:
            assert "invalid toolchain policy JSON" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid JSON did not fail")

        _, _ = build_self_test_root(root)
        payload = json.loads(read_text(policy_path))
        payload["upgrade_policy"]["required_make_routes"] = []
        write_text(policy_path, json.dumps(payload, indent=2) + "\n")
        try:
            load_required_make_routes(policy_path)
        except ValueError as exc:
            assert "invalid required_make_routes" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("empty route list did not fail")

        _, _ = build_self_test_root(root)
        payload = json.loads(read_text(policy_path))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-toolchain"]
        write_text(policy_path, json.dumps(payload, indent=2) + "\n")
        try:
            load_required_make_routes(policy_path)
        except ValueError as exc:
            assert "duplicate required_make_routes entry" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("duplicate route list did not fail")

        _, makefile_path = build_self_test_root(root)
        makefile_path.unlink()
        try:
            read_text(makefile_path)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing makefile did not abort")

        policy_path, makefile_path = build_self_test_root(root)
        policy_path.unlink()
        try:
            load_required_make_routes(policy_path)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing policy did not abort")

        policy_path, makefile_path = build_self_test_root(root)
        payload = json.loads(read_text(policy_path))
        payload["upgrade_policy"] = "bad"
        write_text(policy_path, json.dumps(payload, indent=2) + "\n")
        try:
            load_required_make_routes(policy_path)
        except ValueError as exc:
            assert "invalid upgrade_policy" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid upgrade_policy did not fail")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_REQUIRED_MAKE_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_REQUIRED_MAKE_ROUTES_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 toolchain policy routes exist in zigux/Makefile."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    makefile_path = resolve_path(root, MAKEFILE)
    try:
        required_routes = load_required_make_routes(policy_path)
    except ValueError as exc:
        print("PHASE2_REQUIRED_MAKE_ROUTES=invalid")
        print(f"PHASE2_REQUIRED_MAKEFILE_PATH={makefile_path}")
        print(f"PHASE2_REQUIRED_POLICY_PATH={policy_path}")
        print(f"PHASE2_REQUIRED_MAKE_ROUTES_NOTE={exc}")
        return 1

    issues = collect_route_issues(read_text(makefile_path), required_routes)
    if issues:
        return emit_issues(issues, makefile_path, required_routes)

    print("PHASE2_REQUIRED_MAKE_ROUTES=pass")
    print(f"PHASE2_REQUIRED_MAKEFILE_PATH={makefile_path}")
    print("PHASE2_REQUIRED_ROUTE_LIST=" + ",".join(required_routes))
    print(f"PHASE2_REQUIRED_ROUTE_COUNT={len(required_routes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())