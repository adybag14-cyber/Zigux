#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"
CONTRACT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-contract.py"
CONTRACT_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-contract-selftest-alignment.py"
)
ROUTE_POLICY_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-route-policy.py"
ROUTE_POLICY_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-route-policy-selftest-alignment.py"
)
SHARED_SURFACE_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface.py"
)
SHARED_SURFACE_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface-selftest-alignment.py"
)
WORKFLOW_ORDER_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-workflow-order.py"
)
WORKFLOW_ORDER_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-workflow-order-selftest-alignment.py"
)
VALIDATOR_ORDER_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-validator-order.py"
)
VALIDATOR_ORDER_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-validator-order-selftest-alignment.py"
)
MAKEFILE_ORDER_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-makefile-order.py"
)
MAKEFILE_ORDER_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-makefile-order-selftest-alignment.py"
)
VALIDATE_SURFACE_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-validate-surface.py"
)

CONTRACT_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross-validate-contract.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-contract.py",
    "run: python3 scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py",
)
ROUTE_POLICY_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy.py",
    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py",
)
SHARED_SURFACE_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface.py",
    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py",
)
WORKFLOW_ORDER_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order.py",
    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py",
)
VALIDATOR_ORDER_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross-validate-validator-order.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-validator-order.py",
    "run: python3 scripts/zigux/check-phase2-cross-validate-validator-order-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-validator-order-selftest-alignment.py",
)
MAKEFILE_ORDER_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order.py",
    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order-selftest-alignment.py",
)
VALIDATE_SURFACE_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross-validate-validate-surface.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-validate-surface.py",
)
PRE_CROSS_LINES = (*CONTRACT_WORKFLOW_LINES, *ROUTE_POLICY_WORKFLOW_LINES)
POST_CROSS_LINES = (
    *SHARED_SURFACE_WORKFLOW_LINES,
    *WORKFLOW_ORDER_WORKFLOW_LINES,
    *VALIDATOR_ORDER_WORKFLOW_LINES,
    *MAKEFILE_ORDER_WORKFLOW_LINES,
    *VALIDATE_SURFACE_WORKFLOW_LINES,
)
REQUIRED_CROSS_ROUTE = "run: make -C zigux phase2-cross"
REQUIRED_VALIDATE_ROUTE = "run: make -C zigux phase2-validate"
REQUIRED_WORKFLOW_LINES = (
    *PRE_CROSS_LINES,
    REQUIRED_CROSS_ROUTE,
    *POST_CROSS_LINES,
    REQUIRED_VALIDATE_ROUTE,
)

REQUIRED_PATHS = (
    WORKFLOW,
    VALIDATE,
    CONTRACT_CHECKER,
    CONTRACT_ALIGNMENT,
    ROUTE_POLICY_CHECKER,
    ROUTE_POLICY_ALIGNMENT,
    SHARED_SURFACE_CHECKER,
    SHARED_SURFACE_ALIGNMENT,
    WORKFLOW_ORDER_CHECKER,
    WORKFLOW_ORDER_ALIGNMENT,
    VALIDATOR_ORDER_CHECKER,
    VALIDATOR_ORDER_ALIGNMENT,
    MAKEFILE_ORDER_CHECKER,
    MAKEFILE_ORDER_ALIGNMENT,
    VALIDATE_SURFACE_CHECKER,
)


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
    normalized = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == normalized)


def line_index_map(text: str, markers: tuple[str, ...]) -> dict[str, int]:
    indices: dict[str, int] = {}
    for index, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if stripped in markers and stripped not in indices:
            indices[stripped] = index
    return indices


def collect_block_order_issues(
    issue_prefix: str,
    block: tuple[str, ...],
    index_map: dict[str, int],
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    positions = [index_map[line] for line in block]
    if positions != sorted(positions):
        issues.append((f"INVALID_{issue_prefix}_ORDER", ",".join(block)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    workflow_path = resolve_path(root, WORKFLOW)
    if not workflow_path.exists():
        return issues

    workflow_text = read_text(workflow_path)
    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    if issues:
        return issues

    index_map = line_index_map(workflow_text, REQUIRED_WORKFLOW_LINES)
    issues.extend(collect_block_order_issues("CONTRACT_BLOCK", CONTRACT_WORKFLOW_LINES, index_map))
    issues.extend(collect_block_order_issues("ROUTE_POLICY_BLOCK", ROUTE_POLICY_WORKFLOW_LINES, index_map))
    issues.extend(collect_block_order_issues("SHARED_SURFACE_BLOCK", SHARED_SURFACE_WORKFLOW_LINES, index_map))
    issues.extend(collect_block_order_issues("WORKFLOW_ORDER_BLOCK", WORKFLOW_ORDER_WORKFLOW_LINES, index_map))
    issues.extend(collect_block_order_issues("VALIDATOR_ORDER_BLOCK", VALIDATOR_ORDER_WORKFLOW_LINES, index_map))
    issues.extend(collect_block_order_issues("MAKEFILE_ORDER_BLOCK", MAKEFILE_ORDER_WORKFLOW_LINES, index_map))
    issues.extend(collect_block_order_issues("VALIDATE_SURFACE_BLOCK", VALIDATE_SURFACE_WORKFLOW_LINES, index_map))

    cross_index = index_map[REQUIRED_CROSS_ROUTE]
    validate_index = index_map[REQUIRED_VALIDATE_ROUTE]
    if validate_index <= cross_index:
        issues.append(("INVALID_ROUTE_ANCHOR_ORDER", f"{REQUIRED_CROSS_ROUTE},{REQUIRED_VALIDATE_ROUTE}"))

    for marker in PRE_CROSS_LINES:
        if index_map[marker] >= cross_index:
            issues.append(("INVALID_PRE_CROSS_PLACEMENT", marker))

    for marker in POST_CROSS_LINES:
        if index_map[marker] <= cross_index or index_map[marker] >= validate_index:
            issues.append(("INVALID_POST_CROSS_PLACEMENT", marker))

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_VALIDATE_WORKFLOW_SURFACE_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_VALIDATE_WORKFLOW_SURFACE_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_VALIDATE_WORKFLOW_SURFACE=pass")
    print(f"PHASE2_CROSS_VALIDATE_WORKFLOW_SURFACE_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_CROSS_VALIDATE_WORKFLOW_SURFACE_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(("name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES)) + "\n")
    for path in REQUIRED_PATHS[1:]:
        write_text(resolve_path(root, path), "# present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_workflow_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert run_check(root) == 0
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            read_text(workflow_path).replace(CONTRACT_WORKFLOW_LINES[0] + "\n", "", 1),
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            read_text(workflow_path) + VALIDATE_SURFACE_WORKFLOW_LINES[0] + "\n",
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_lines = read_text(workflow_path).splitlines()
        cross_index = workflow_lines.index(REQUIRED_CROSS_ROUTE)
        validate_index = workflow_lines.index(REQUIRED_VALIDATE_ROUTE)
        workflow_lines[cross_index], workflow_lines[validate_index] = (
            workflow_lines[validate_index],
            workflow_lines[cross_index],
        )
        workflow_path.write_text("\n".join(workflow_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_lines = read_text(workflow_path).splitlines()
        shared_index = workflow_lines.index(SHARED_SURFACE_WORKFLOW_LINES[0])
        route_index = workflow_lines.index(ROUTE_POLICY_WORKFLOW_LINES[1])
        workflow_lines[shared_index], workflow_lines[route_index] = (
            workflow_lines[route_index],
            workflow_lines[shared_index],
        )
        workflow_path.write_text("\n".join(workflow_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_lines = read_text(workflow_path).splitlines()
        validate_surface_index = workflow_lines.index(VALIDATE_SURFACE_WORKFLOW_LINES[0])
        pre_cross_index = workflow_lines.index(CONTRACT_WORKFLOW_LINES[1])
        workflow_lines[validate_surface_index], workflow_lines[pre_cross_index] = (
            workflow_lines[pre_cross_index],
            workflow_lines[validate_surface_index],
        )
        workflow_path.write_text("\n".join(workflow_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        resolve_path(root, VALIDATE_SURFACE_CHECKER).unlink()
        assert run_check(root) == 1
        checks += 1

    print("PHASE2_CROSS_VALIDATE_WORKFLOW_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_WORKFLOW_SURFACE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that the Lane 21 workflow-side cross-validate packet keeps the "
            "full checker family wired between the phase2-cross and phase2-validate anchors."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like root for focused contract replays",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0
    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
