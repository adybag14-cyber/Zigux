#!/usr/bin/env python3
"""Guard the policy-required Phase 2 bootstrap make-route packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def load_required_make_routes(policy_path: Path) -> tuple[str, ...]:
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc

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
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise ValueError(f"invalid required_make_routes in {policy_path}")
        route_name = route.strip()
        if route_name in seen:
            raise ValueError(f"duplicate required_make_routes entry in {policy_path}: {route_name}")
        seen.add(route_name)
        normalized.append(route_name)
    return tuple(normalized)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def count_makefile_targets(text: str, route: str) -> int:
    prefix = f"{route}:"
    return sum(1 for line in text.splitlines() if line.strip().startswith(prefix))


def phony_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(".PHONY:"):
            continue
        _, suffix = stripped.split(":", 1)
        targets.update(token for token in suffix.strip().split() if token)
    return targets


def collect_issues(root: Path) -> list[tuple[str, str]]:
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    workflow_path = resolve_path(root, WORKFLOW)
    makefile_path = resolve_path(root, MAKEFILE)

    required_routes = load_required_make_routes(policy_path)
    workflow_text = read_text(workflow_path)
    makefile_text = read_text(makefile_path)
    makefile_phony_targets = phony_targets(makefile_text)

    issues: list[tuple[str, str]] = []
    for route in required_routes:
        workflow_line = f"run: make -C zigux {route}"
        workflow_count = count_exact_lines(workflow_text, workflow_line)
        if workflow_count == 0:
            issues.append(("MISSING_WORKFLOW_ROUTE", workflow_line))
        elif workflow_count != 1:
            issues.append(("DUPLICATE_WORKFLOW_ROUTE", f"{workflow_line}:count={workflow_count}"))

        if route not in makefile_phony_targets:
            issues.append(("MISSING_MAKEFILE_PHONY", route))

        target_count = count_makefile_targets(makefile_text, route)
        target_line = f"{route}:"
        if target_count == 0:
            issues.append(("MISSING_MAKEFILE_TARGET", target_line))
        elif target_count != 1:
            issues.append(("DUPLICATE_MAKEFILE_TARGET", f"{target_line}:count={target_count}"))

    return issues


def build_self_test_root(root: Path) -> tuple[str, ...]:
    required_routes = (
        "phase2-toolchain",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2-genksyms",
        "phase2-fixdep",
        "phase2-validate",
    )
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(required_routes),
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(f"run: make -C zigux {route}" for route in required_routes) + "\n",
    )
    write_text(
        resolve_path(root, MAKEFILE),
        ".PHONY: " + " ".join(required_routes) + "\n\n"
        + "\n".join(f"{route}:\n\t@true\n" for route in required_routes),
    )
    return required_routes


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_policy_routes_") as tmp_dir:
        root = Path(tmp_dir)
        required_routes = build_self_test_root(root)

        assert collect_issues(root) == []
        checks += 1

        workflow_path = resolve_path(root, WORKFLOW)
        makefile_path = resolve_path(root, MAKEFILE)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)

        first_route = required_routes[0]
        first_workflow_line = f"run: make -C zigux {first_route}"

        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), first_workflow_line),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_ROUTE", first_workflow_line) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), first_workflow_line),
            encoding="utf-8",
        )
        assert ("DUPLICATE_WORKFLOW_ROUTE", f"{first_workflow_line}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        phony_line = ".PHONY: " + " ".join(required_routes)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), phony_line, f".PHONY: {' '.join(required_routes[1:])}"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_PHONY", first_route) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        first_target_line = f"{first_route}:"
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), first_target_line),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_TARGET", first_target_line) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        makefile_path.write_text(
            duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), first_target_line),
            encoding="utf-8",
        )
        assert ("DUPLICATE_MAKEFILE_TARGET", f"{first_target_line}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        try:
            collect_issues(root)
        except ValueError as exc:
            assert "invalid toolchain policy JSON" in str(exc)
            checks += 1
        else:
            raise AssertionError("invalid JSON did not fail")

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"] = "broken"
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except ValueError as exc:
            assert "invalid upgrade_policy" in str(exc)
            checks += 1
        else:
            raise AssertionError("invalid upgrade_policy did not fail")

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = []
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except ValueError as exc:
            assert "invalid required_make_routes" in str(exc)
            checks += 1
        else:
            raise AssertionError("empty required_make_routes did not fail")

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = [first_route, first_route]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except ValueError as exc:
            assert "duplicate required_make_routes entry" in str(exc)
            checks += 1
        else:
            raise AssertionError("duplicate required_make_routes did not fail")

    print("PHASE2_BOOTSTRAP_POLICY_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_POLICY_ROUTES_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the bootstrap workflow still runs every Phase 2 make route required by the pinned Zig toolchain policy."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    try:
        required_routes = load_required_make_routes(policy_path)
    except ValueError as exc:
        print("PHASE2_BOOTSTRAP_POLICY_ROUTES=invalid")
        print(f"PHASE2_BOOTSTRAP_POLICY_PATH={policy_path}")
        print(f"PHASE2_BOOTSTRAP_POLICY_ROUTES_NOTE={exc}")
        return 1

    issues = collect_issues(root)
    if issues:
        print("PHASE2_BOOTSTRAP_POLICY_ROUTES=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_BOOTSTRAP_POLICY_ROUTES=pass")
    print(f"PHASE2_BOOTSTRAP_POLICY_PATH={policy_path}")
    print(f"PHASE2_BOOTSTRAP_REQUIRED_ROUTE_COUNT={len(required_routes)}")
    print("PHASE2_BOOTSTRAP_REQUIRED_ROUTE_LIST=" + ",".join(required_routes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
