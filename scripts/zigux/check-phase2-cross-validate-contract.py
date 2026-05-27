#!/usr/bin/env python3
"""Guard the Phase 2 cross packet inside the shared validator contract."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
DIRECT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_ROUTE_NAME = "phase2-cross"
EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_DIRECT_CHECKER_ROUTE_LINE = 'ROUTE = "make -C zigux phase2-cross"'
EXPECTED_VALIDATOR_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: make -C zigux phase2-cross",
)
EXPECTED_VALIDATOR_MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)
EXPECTED_VALIDATOR_PATHS = (
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)
EXPECTED_FIXTURE_TARGETS = {
    "x86_64-linux": "archive_required",
    "aarch64-linux": "route_contract_only",
}


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


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def remove_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def find_cross_targets(fixture: object) -> dict[str, str]:
    if not isinstance(fixture, dict):
        raise SystemExit(f"invalid json shape in required file: {FIXTURE}")
    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list):
        raise SystemExit(f"invalid cross_targets in required file: {FIXTURE}")
    mapping: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            raise SystemExit(f"invalid cross_targets in required file: {FIXTURE}")
        target = entry.get("target")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")
        if not isinstance(target, str) or not isinstance(validation_mode, str):
            raise SystemExit(f"invalid cross_targets in required file: {FIXTURE}")
        if route != EXPECTED_ROUTE:
            raise SystemExit(f"invalid cross-target route in required file: {FIXTURE}")
        if target in mapping:
            raise SystemExit(f"duplicate cross target in required file: {FIXTURE}: {target}")
        mapping[target] = validation_mode
    return mapping


def load_policy_routes(policy_path: Path) -> list[str]:
    payload = read_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {policy_path}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list):
        raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")
    normalized: list[str] = []
    seen: set[str] = set()
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")
        route = route.strip()
        if route in seen:
            raise SystemExit(f"duplicate required_make_routes in required file: {policy_path}: {route}")
        seen.add(route)
        normalized.append(route)
    return normalized


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    validator_text = read_text(resolve_path(root, VALIDATOR))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    direct_checker_text = read_text(resolve_path(root, DIRECT_CHECKER))
    policy_routes = load_policy_routes(resolve_path(root, TOOLCHAIN_POLICY))

    if EXPECTED_ROUTE_NAME not in policy_routes:
        issues.append(("MISSING_POLICY_ROUTE", EXPECTED_ROUTE_NAME))
    elif policy_routes.count(EXPECTED_ROUTE_NAME) != 1:
        issues.append(("DUPLICATE_POLICY_ROUTE", EXPECTED_ROUTE_NAME))

    for marker in EXPECTED_VALIDATOR_WORKFLOW_LINES:
        live_count = count_exact_lines(workflow_text, marker)
        if live_count == 0:
            issues.append(("MISSING_LIVE_WORKFLOW_LINE", marker))
        elif live_count != 1:
            issues.append(("DUPLICATE_LIVE_WORKFLOW_LINE", f"{marker}:count={live_count}"))

        validator_count = validator_text.count(f'"{marker}"')
        if validator_count == 0:
            issues.append(("MISSING_VALIDATOR_WORKFLOW_LINE", marker))
        elif validator_count != 1:
            issues.append(("DUPLICATE_VALIDATOR_WORKFLOW_LINE", f"{marker}:count={validator_count}"))

    for marker in EXPECTED_VALIDATOR_MAKEFILE_LINES:
        live_count = count_exact_lines(makefile_text, marker)
        if live_count == 0:
            issues.append(("MISSING_LIVE_MAKEFILE_LINE", marker))
        elif live_count != 1:
            issues.append(("DUPLICATE_LIVE_MAKEFILE_LINE", f"{marker}:count={live_count}"))

        validator_count = validator_text.count(f'"{marker}"')
        if validator_count == 0:
            issues.append(("MISSING_VALIDATOR_MAKEFILE_LINE", marker))
        elif validator_count != 1:
            issues.append(("DUPLICATE_VALIDATOR_MAKEFILE_LINE", f"{marker}:count={validator_count}"))

    for rel in EXPECTED_VALIDATOR_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_LIVE_REQUIRED_PATH", rel))

        validator_count = validator_text.count(f'"{rel}"')
        if validator_count == 0:
            issues.append(("MISSING_VALIDATOR_REQUIRED_PATH", rel))
        elif validator_count != 1:
            issues.append(("DUPLICATE_VALIDATOR_REQUIRED_PATH", f"{rel}:count={validator_count}"))

    direct_checker_route_count = direct_checker_text.count(EXPECTED_DIRECT_CHECKER_ROUTE_LINE)
    if direct_checker_route_count == 0:
        issues.append(("MISSING_DIRECT_CHECKER_ROUTE", EXPECTED_ROUTE))
    elif direct_checker_route_count != 1:
        issues.append(("DUPLICATE_DIRECT_CHECKER_ROUTE", f"{EXPECTED_ROUTE}:count={direct_checker_route_count}"))

    alignment_path = resolve_path(root, ALIGNMENT_CHECKER)
    if not alignment_path.exists():
        issues.append(("MISSING_LIVE_REQUIRED_PATH", str(ALIGNMENT_CHECKER.relative_to(ROOT))))

    fixture_path = resolve_path(root, FIXTURE)
    if not fixture_path.exists():
        return issues

    fixture = read_json(fixture_path)
    if not isinstance(fixture, dict):
        issues.append(("INVALID_FIXTURE_SHAPE", "root"))
        return issues
    if fixture.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_ROUTE", EXPECTED_ROUTE))

    target_modes = find_cross_targets(fixture)
    for target, mode in EXPECTED_FIXTURE_TARGETS.items():
        if target_modes.get(target) != mode:
            issues.append(("INVALID_FIXTURE_TARGET_MODE", f"{target}:{mode}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_VALIDATE_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        resolve_path(root, VALIDATOR),
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "REQUIRED_WORKFLOW_LINES = (",
                *[f'    "{line}",' for line in EXPECTED_VALIDATOR_WORKFLOW_LINES],
                ")",
                "REQUIRED_MAKEFILE_LINES = (",
                *[f'    "{line}",' for line in EXPECTED_VALIDATOR_MAKEFILE_LINES],
                ")",
                "REQUIRED_PATHS = (",
                *[f'    "{path}",' for path in EXPECTED_VALIDATOR_PATHS],
                ")",
            )
        )
        + "\n",
    )
    write_text(
        resolve_path(root, WORKFLOW),
        "name: zigux-bootstrap\n" + "\n".join(EXPECTED_VALIDATOR_WORKFLOW_LINES) + "\n",
    )
    write_text(resolve_path(root, MAKEFILE), "\n".join(EXPECTED_VALIDATOR_MAKEFILE_LINES) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "upgrade_policy": {
                    "required_make_routes": [
                        "phase2-toolchain",
                        "phase2-tools",
                        "phase2-kconfig",
                        "phase2-cross",
                        "phase2-genksyms",
                        "phase2-fixdep",
                        "phase2-validate",
                    ]
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, DIRECT_CHECKER),
        "#!/usr/bin/env python3\n"
        + EXPECTED_DIRECT_CHECKER_ROUTE_LINE
        + "\n",
    )
    write_text(resolve_path(root, ALIGNMENT_CHECKER), "#!/usr/bin/env python3\n")
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
    expected_case_count = 15
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            remove_exact_line(workflow_path.read_text(encoding="utf-8"), EXPECTED_VALIDATOR_WORKFLOW_LINES[4]),
            encoding="utf-8",
        )
        assert ("MISSING_LIVE_WORKFLOW_LINE", EXPECTED_VALIDATOR_WORKFLOW_LINES[4]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        validator_path = resolve_path(root, VALIDATOR)
        validator_path.write_text(
            validator_path.read_text(encoding="utf-8").replace(
                f'    "{EXPECTED_VALIDATOR_WORKFLOW_LINES[4]}",\n', "",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_WORKFLOW_LINE", EXPECTED_VALIDATOR_WORKFLOW_LINES[4]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), EXPECTED_VALIDATOR_MAKEFILE_LINES[0], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_LIVE_MAKEFILE_LINE", EXPECTED_VALIDATOR_MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        validator_path = resolve_path(root, VALIDATOR)
        validator_path.write_text(
            validator_path.read_text(encoding="utf-8").replace(
                f'    "{EXPECTED_VALIDATOR_MAKEFILE_LINES[1]}",\n', "",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_MAKEFILE_LINE", EXPECTED_VALIDATOR_MAKEFILE_LINES[1]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        validator_path = resolve_path(root, VALIDATOR)
        validator_text = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            validator_text.replace(
                f'    "{EXPECTED_VALIDATOR_PATHS[2]}",\n', "",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_REQUIRED_PATH", EXPECTED_VALIDATOR_PATHS[2]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture_path.unlink()
        assert ("MISSING_LIVE_REQUIRED_PATH", EXPECTED_VALIDATOR_PATHS[2]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"].remove("phase2-cross")
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_POLICY_ROUTE", EXPECTED_ROUTE_NAME) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"].append("phase2-cross")
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate required_make_routes" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("duplicate required_make_routes did not abort")

        build_sample_root(root)
        direct_checker_path = resolve_path(root, DIRECT_CHECKER)
        direct_checker_path.write_text("#!/usr/bin/env python3\nROUTE = \"make -C zigux phase2\"\n", encoding="utf-8")
        assert ("MISSING_DIRECT_CHECKER_ROUTE", EXPECTED_ROUTE) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["route"] = "make -C zigux phase2"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_ROUTE", EXPECTED_ROUTE) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_TARGET_MODE", "aarch64-linux:route_contract_only") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        alignment_path = resolve_path(root, ALIGNMENT_CHECKER)
        alignment_path.unlink()
        assert (
            "MISSING_LIVE_REQUIRED_PATH",
            "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), EXPECTED_VALIDATOR_WORKFLOW_LINES[0]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_LIVE_WORKFLOW_LINE",
            f"{EXPECTED_VALIDATOR_WORKFLOW_LINES[0]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        validator_path = resolve_path(root, VALIDATOR)
        validator_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing validator did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(destination: Path) -> int:
    build_sample_root(destination.resolve())
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SAMPLE_ROOT={destination.resolve()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that validate-phase2.py keeps the current Phase 2 cross packet fail-closed."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a minimal passing sample root for focused replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_VALIDATE_CONTRACT=pass")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_WORKFLOW_LINE_COUNT={len(EXPECTED_VALIDATOR_WORKFLOW_LINES)}")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_REQUIRED_PATH_COUNT={len(EXPECTED_VALIDATOR_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
