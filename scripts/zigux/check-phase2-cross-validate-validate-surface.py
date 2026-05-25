#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
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

REQUIRED_PATHS = (
    VALIDATE,
    CONTRACT_CHECKER,
    CONTRACT_ALIGNMENT,
    ROUTE_POLICY_CHECKER,
    ROUTE_POLICY_ALIGNMENT,
    SHARED_SURFACE_CHECKER,
    SHARED_SURFACE_ALIGNMENT,
    WORKFLOW_ORDER_CHECKER,
    WORKFLOW_ORDER_ALIGNMENT,
)

REQUIRED_VALIDATE_MARKERS = (
    '    "scripts/zigux/check-phase2-cross-validate-contract.py",',
    '    "scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py",',
    '    "scripts/zigux/check-phase2-cross-validate-route-policy.py",',
    '    "scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py",',
    '    "scripts/zigux/check-phase2-cross-validate-shared-surface.py",',
    '    "scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py",',
    '    "scripts/zigux/check-phase2-cross-validate-workflow-order.py",',
    '    "scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-workflow-order.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-workflow-order.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-workflow-order-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-workflow-order-selftest-alignment.py",',
)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    normalized = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == normalized)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    validate_path = resolve_path(root, VALIDATE)
    if not validate_path.exists():
        return issues

    validate_text = read_text(validate_path)
    for marker in REQUIRED_VALIDATE_MARKERS:
        count = count_exact_lines(validate_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATE_MARKER", f"{marker}:count={count}"))

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_VALIDATE_VALIDATE_SURFACE_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_VALIDATE_VALIDATE_SURFACE_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_VALIDATE_VALIDATE_SURFACE=pass")
    print(
        f"PHASE2_CROSS_VALIDATE_VALIDATE_SURFACE_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}"
    )
    print(
        f"PHASE2_CROSS_VALIDATE_VALIDATE_SURFACE_VALIDATE_MARKER_COUNT={len(REQUIRED_VALIDATE_MARKERS)}"
    )
    return 0


def build_sample_root(root: Path) -> None:
    validate_lines = ["CHECKS = ("]
    validate_lines.extend(REQUIRED_VALIDATE_MARKERS)
    validate_lines.append(")")
    write_text(resolve_path(root, VALIDATE), "\n".join(validate_lines) + "\n")

    for path in REQUIRED_PATHS[1:]:
        write_text(resolve_path(root, path), "# present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_validate_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert run_check(root) == 0
        checks += 1

        build_sample_root(root)
        write_text(resolve_path(root, VALIDATE), "CHECKS = ()\n")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        write_text(
            resolve_path(root, VALIDATE),
            "CHECKS = (\n"
            + "\n".join(REQUIRED_VALIDATE_MARKERS + (REQUIRED_VALIDATE_MARKERS[0],))
            + "\n)\n",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        resolve_path(root, WORKFLOW_ORDER_ALIGNMENT).unlink()
        assert run_check(root) == 1
        checks += 1

    print("PHASE2_CROSS_VALIDATE_VALIDATE_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_VALIDATE_SURFACE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that validate-phase2.py carries the full Lane 21 cross-validate checker packet."
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
