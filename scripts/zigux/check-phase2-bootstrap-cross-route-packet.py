#!/usr/bin/env python3
"""Guard the bootstrap Phase 2 cross-route packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
CROSS_ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: make -C zigux phase2-cross",
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

REQUIRED_PATHS = (
    WORKFLOW,
    MAKEFILE,
    TOOLCHAIN_POLICY,
    CROSS_CHECKER,
    CROSS_ALIGNMENT_CHECKER,
)

EXPECTED_REQUIRED_ROUTE = "phase2-cross"
EXPECTED_REQUIRED_ROUTE_COUNT = 3
EXPECTED_SELF_TEST_CASE_COUNT = 28


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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


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


def load_required_make_routes(root: Path) -> list[str]:
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {policy_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {policy_path}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")

    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")

    normalized: list[str] = []
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")
        normalized.append(route.strip())
    return normalized


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        resolved = resolve_path(root, path)
        if not resolved.is_file():
            issues.append(("MISSING_REQUIRED_PATH", str(path.relative_to(ROOT))))

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    required_routes = load_required_make_routes(root)
    if len(required_routes) != EXPECTED_REQUIRED_ROUTE_COUNT:
        issues.append(("INVALID_REQUIRED_ROUTE_COUNT", str(len(required_routes))))
    if EXPECTED_REQUIRED_ROUTE not in required_routes:
        issues.append(("MISSING_REQUIRED_ROUTE", EXPECTED_REQUIRED_ROUTE))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_CROSS_ROUTE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_sample_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
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
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve_path(root, CROSS_CHECKER), "# current cross checker stub\n")
    write_text(resolve_path(root, CROSS_ALIGNMENT_CHECKER), "# current cross alignment checker stub\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_cross_route_") as tmp_dir:
        root = Path(tmp_dir)

        write_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            write_sample_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            write_sample_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            write_sample_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            write_sample_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(
                duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        write_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_REQUIRED_ROUTE", EXPECTED_REQUIRED_ROUTE) in collect_issues(root)
        checks_run += 1

        write_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"].append("phase2-tools")
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_REQUIRED_ROUTE_COUNT", "4") in collect_issues(root)
        checks_run += 1

        for path in REQUIRED_PATHS:
            write_sample_root(root)
            resolve_path(root, path).unlink()
            try:
                issues = collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
            else:
                assert ("MISSING_REQUIRED_PATH", str(path.relative_to(ROOT))) in issues
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_CROSS_ROUTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_CROSS_ROUTE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the bootstrap Phase 2 cross-route packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root for focused validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    required_routes = load_required_make_routes(args.root.resolve())
    print("PHASE2_BOOTSTRAP_CROSS_ROUTE_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_CROSS_ROUTE_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_CROSS_ROUTE_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_BOOTSTRAP_CROSS_ROUTE_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print("PHASE2_BOOTSTRAP_CROSS_ROUTE_PACKET_REQUIRED_ROUTE_LIST=" + ",".join(required_routes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
