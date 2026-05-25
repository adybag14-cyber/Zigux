#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"

REQUIRED_PATHS = (
    VALIDATE,
    WORKFLOW,
    MAKEFILE,
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-contract.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-contract-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-route-policy.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-route-policy-selftest-alignment.py",
)

REQUIRED_VALIDATE_MARKERS = (
    '    "scripts/zigux/check-phase2-cross-validate-contract.py",',
    '    "scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py",',
    '    "scripts/zigux/check-phase2-cross-validate-route-policy.py",',
    '    "scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy-selftest-alignment.py",',
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross-validate-contract.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-contract.py",
    "run: python3 scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy.py",
    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py",
)

REQUIRED_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract-selftest-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy-selftest-alignment.py",
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
    normalized_marker = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == normalized_marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    validate_path = resolve_path(root, VALIDATE)
    if validate_path.exists():
        validate_text = read_text(validate_path)
        for marker in REQUIRED_VALIDATE_MARKERS:
            count = count_exact_lines(validate_text, marker)
            if count == 0:
                issues.append(("MISSING_VALIDATE_MARKER", marker))
            elif count != 1:
                issues.append(("DUPLICATE_VALIDATE_MARKER", f"{marker}:count={count}"))

    workflow_path = resolve_path(root, WORKFLOW)
    if workflow_path.exists():
        workflow_text = read_text(workflow_path)
        for marker in REQUIRED_WORKFLOW_LINES:
            count = count_exact_lines(workflow_text, marker)
            if count == 0:
                issues.append(("MISSING_WORKFLOW_LINE", marker))
            elif count != 1:
                issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    makefile_path = resolve_path(root, MAKEFILE)
    if makefile_path.exists():
        makefile_text = read_text(makefile_path)
        for marker in REQUIRED_MAKEFILE_LINES:
            count = count_exact_lines(makefile_text, marker)
            if count == 0:
                issues.append(("MISSING_MAKEFILE_LINE", marker))
            elif count != 1:
                issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_VALIDATE_SHARED_SURFACE=pass")
    print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_VALIDATE_MARKER_COUNT={len(REQUIRED_VALIDATE_MARKERS)}")
    print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


def build_self_test_root(root: Path) -> None:
    validate_lines = ["CHECKS = ("]
    validate_lines.extend(REQUIRED_VALIDATE_MARKERS)
    validate_lines.append(")")
    write_text(resolve_path(root, VALIDATE), "\n".join(validate_lines) + "\n")

    workflow_lines = ["name: zigux-bootstrap"]
    workflow_lines.extend(REQUIRED_WORKFLOW_LINES)
    write_text(resolve_path(root, WORKFLOW), "\n".join(workflow_lines) + "\n")

    makefile_lines = ["phase2-cross:"]
    makefile_lines.extend(f"\t{line}" for line in REQUIRED_MAKEFILE_LINES)
    write_text(resolve_path(root, MAKEFILE), "\n".join(makefile_lines) + "\n")

    for path in REQUIRED_PATHS[3:]:
        write_text(resolve_path(root, path), "# present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_shared_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert run_check(root) == 0
        checks += 1

        build_self_test_root(root)
        write_text(resolve_path(root, VALIDATE), "CHECKS = ()\n")
        assert run_check(root) == 1
        checks += 1

        build_self_test_root(root)
        write_text(
            resolve_path(root, VALIDATE),
            "CHECKS = (\n"
            + "\n".join(REQUIRED_VALIDATE_MARKERS + (REQUIRED_VALIDATE_MARKERS[0],))
            + "\n)\n",
        )
        assert run_check(root) == 1
        checks += 1

        build_self_test_root(root)
        write_text(
            resolve_path(root, WORKFLOW),
            "name: zigux-bootstrap\n"
            + "\n".join(REQUIRED_WORKFLOW_LINES + (REQUIRED_WORKFLOW_LINES[0],))
            + "\n",
        )
        assert run_check(root) == 1
        checks += 1

        build_self_test_root(root)
        write_text(
            resolve_path(root, MAKEFILE),
            "phase2-cross:\n"
            + "\n".join(f"\t{line}" for line in REQUIRED_MAKEFILE_LINES + (REQUIRED_MAKEFILE_LINES[0],))
            + "\n",
        )
        assert run_check(root) == 1
        checks += 1

        build_self_test_root(root)
        resolve_path(root, VALIDATE).unlink()
        assert run_check(root) == 1
        checks += 1

        build_self_test_root(root)
        resolve_path(root, WORKFLOW).unlink()
        assert run_check(root) == 1
        checks += 1

        build_self_test_root(root)
        resolve_path(root, MAKEFILE).unlink()
        assert run_check(root) == 1
        checks += 1

        build_self_test_root(root)
        resolve_path(root, REQUIRED_PATHS[3]).unlink()
        assert run_check(root) == 1
        checks += 1

    print("PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the Lane 21 shared validation surfaces wire the cross validate-contract checker pair."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
