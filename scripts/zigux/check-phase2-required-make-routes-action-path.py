#!/usr/bin/env python3
"""Guard the Phase 2 required make-routes action path."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
VALIDATE = Path("scripts/zigux/validate-phase2.py")
CHECKER = Path("scripts/zigux/check-phase2-required-make-routes.py")

ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)
VALIDATE_MARKERS = (
    f'"{CHECKER.as_posix()}",',
    '"run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-required-make-routes.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",',
)
WORKFLOW_CHECKER_LINES = (
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
)
WORKFLOW_ROUTE_LINES = tuple(f"run: make -C zigux {route}" for route in ROUTES)
MAKEFILE_CHECKER_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
)
MAKEFILE_ROUTE_PREFIXES = tuple(f"{route}:" for route in ROUTES)
REQUIRED_FILES = (WORKFLOW, MAKEFILE, POLICY, VALIDATE, CHECKER)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def exact_count(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def prefix_count(text: str, prefix: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip().startswith(prefix))


def ordered_exact(text: str, markers: tuple[str, ...]) -> bool:
    lines = [line.strip() for line in text.splitlines()]
    cursor = 0
    for marker in markers:
        try:
            cursor = lines.index(marker, cursor) + 1
        except ValueError:
            return False
    return True


def ordered_prefix(text: str, prefixes: tuple[str, ...]) -> bool:
    lines = [line.strip() for line in text.splitlines()]
    cursor = 0
    for prefix in prefixes:
        found = False
        for index in range(cursor, len(lines)):
            if lines[index].startswith(prefix):
                cursor = index + 1
                found = True
                break
        if not found:
            return False
    return True


def collect_exact(
    issues: list[tuple[str, str]],
    text: str,
    markers: tuple[str, ...],
    missing: str,
    duplicate: str,
    order: str | None = None,
) -> None:
    before = len(issues)
    for marker in markers:
        count = exact_count(text, marker)
        if count == 0:
            issues.append((missing, marker))
        elif count > 1:
            issues.append((duplicate, f"{marker}:count={count}"))
    if order is not None and len(issues) == before and not ordered_exact(text, markers):
        issues.append((order, order.lower()))


def collect_prefix(
    issues: list[tuple[str, str]],
    text: str,
    prefixes: tuple[str, ...],
    missing: str,
    duplicate: str,
    order: str,
) -> None:
    before = len(issues)
    for prefix in prefixes:
        count = prefix_count(text, prefix)
        if count == 0:
            issues.append((missing, prefix))
        elif count > 1:
            issues.append((duplicate, f"{prefix}:count={count}"))
    if len(issues) == before and not ordered_prefix(text, prefixes):
        issues.append((order, order.lower()))


def policy_routes(path: Path) -> tuple[str, ...] | None:
    payload = json.loads(read_text(path))
    upgrade_policy = payload.get("upgrade_policy") if isinstance(payload, dict) else None
    routes = upgrade_policy.get("required_make_routes") if isinstance(upgrade_policy, dict) else None
    if not isinstance(routes, list) or not all(isinstance(route, str) for route in routes):
        return None
    return tuple(routes)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    validate_text = read_text(root / VALIDATE)
    workflow_text = read_text(root / WORKFLOW)
    makefile_text = read_text(root / MAKEFILE)

    collect_exact(
        issues,
        validate_text,
        VALIDATE_MARKERS,
        "MISSING_VALIDATE_MARKER",
        "DUPLICATE_VALIDATE_MARKER",
        "VALIDATE_MARKER_ORDER_MISMATCH",
    )
    collect_exact(
        issues,
        workflow_text,
        WORKFLOW_CHECKER_LINES,
        "MISSING_WORKFLOW_CHECKER_LINE",
        "DUPLICATE_WORKFLOW_CHECKER_LINE",
        "WORKFLOW_CHECKER_ORDER_MISMATCH",
    )
    collect_exact(
        issues,
        workflow_text,
        WORKFLOW_ROUTE_LINES,
        "MISSING_WORKFLOW_ROUTE_LINE",
        "DUPLICATE_WORKFLOW_ROUTE_LINE",
    )
    collect_exact(
        issues,
        makefile_text,
        MAKEFILE_CHECKER_LINES,
        "MISSING_MAKEFILE_CHECKER_LINE",
        "DUPLICATE_MAKEFILE_CHECKER_LINE",
        "MAKEFILE_CHECKER_ORDER_MISMATCH",
    )
    collect_prefix(
        issues,
        makefile_text,
        MAKEFILE_ROUTE_PREFIXES,
        "MISSING_MAKEFILE_ROUTE_TARGET",
        "DUPLICATE_MAKEFILE_ROUTE_TARGET",
        "MAKEFILE_ROUTE_ORDER_MISMATCH",
    )

    routes = policy_routes(root / POLICY)
    if routes is None:
        issues.append(("INVALID_POLICY_SHAPE", "required_make_routes"))
    elif routes != ROUTES:
        issues.append(("REQUIRED_MAKE_ROUTE_POLICY_DRIFT", ",".join(routes)))
    return issues


def write_sample_root(root: Path) -> None:
    write_text(root / CHECKER, "#!/usr/bin/env python3\n")
    write_text(
        root / VALIDATE,
        "\n".join(
            (
                "REQUIRED_PATHS = (",
                VALIDATE_MARKERS[0],
                ")",
                "STATIC_REQUIRED_WORKFLOW_LINES = (",
                *VALIDATE_MARKERS[1:3],
                ")",
                "STATIC_REQUIRED_MAKEFILE_LINES = (",
                VALIDATE_MARKERS[3],
                ")",
            )
        )
        + "\n",
    )
    write_text(root / WORKFLOW, "\n".join((*WORKFLOW_CHECKER_LINES, *WORKFLOW_ROUTE_LINES)) + "\n")
    makefile_lines: list[str] = []
    for route in ROUTES:
        makefile_lines.append(f"{route}:")
        if route == "phase2-tools":
            makefile_lines.extend(MAKEFILE_CHECKER_LINES)
    write_text(root / MAKEFILE, "\n".join(makefile_lines) + "\n")
    write_text(root / POLICY, json.dumps({"upgrade_policy": {"required_make_routes": list(ROUTES)}}, indent=2) + "\n")


def replace_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(marker)


def duplicate_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(marker)


def swap_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = next(index for index, line in enumerate(lines) if line.strip() == first)
    second_index = next(index for index, line in enumerate(lines) if line.strip() == second)
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_required_make_routes_action_path_") as tmp_dir:
        root = Path(tmp_dir)

        write_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        write_sample_root(root)
        (root / CHECKER).unlink()
        expect_issue(root, ("MISSING_REQUIRED_FILE", CHECKER.as_posix()))
        checks += 1

        write_sample_root(root)
        write_text(root / VALIDATE, replace_line(read_text(root / VALIDATE), VALIDATE_MARKERS[0], '"placeholder",'))
        expect_issue(root, ("MISSING_VALIDATE_MARKER", VALIDATE_MARKERS[0]))
        checks += 1

        write_sample_root(root)
        write_text(root / VALIDATE, duplicate_line(read_text(root / VALIDATE), VALIDATE_MARKERS[0]))
        expect_issue(root, ("DUPLICATE_VALIDATE_MARKER", f"{VALIDATE_MARKERS[0]}:count=2"))
        checks += 1

        write_sample_root(root)
        write_text(root / VALIDATE, swap_lines(read_text(root / VALIDATE), VALIDATE_MARKERS[0], VALIDATE_MARKERS[1]))
        assert any(code == "VALIDATE_MARKER_ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        write_sample_root(root)
        write_text(root / WORKFLOW, replace_line(read_text(root / WORKFLOW), WORKFLOW_CHECKER_LINES[0]))
        expect_issue(root, ("MISSING_WORKFLOW_CHECKER_LINE", WORKFLOW_CHECKER_LINES[0]))
        checks += 1

        write_sample_root(root)
        write_text(root / WORKFLOW, duplicate_line(read_text(root / WORKFLOW), WORKFLOW_ROUTE_LINES[0]))
        expect_issue(root, ("DUPLICATE_WORKFLOW_ROUTE_LINE", f"{WORKFLOW_ROUTE_LINES[0]}:count=2"))
        checks += 1

        write_sample_root(root)
        write_text(root / WORKFLOW, replace_line(read_text(root / WORKFLOW), WORKFLOW_ROUTE_LINES[0]))
        expect_issue(root, ("MISSING_WORKFLOW_ROUTE_LINE", WORKFLOW_ROUTE_LINES[0]))
        checks += 1

        write_sample_root(root)
        write_text(root / MAKEFILE, replace_line(read_text(root / MAKEFILE), MAKEFILE_CHECKER_LINES[0]))
        expect_issue(root, ("MISSING_MAKEFILE_CHECKER_LINE", MAKEFILE_CHECKER_LINES[0]))
        checks += 1

        write_sample_root(root)
        write_text(root / MAKEFILE, swap_lines(read_text(root / MAKEFILE), "phase2-toolchain:", "phase2-tools:"))
        assert any(code == "MAKEFILE_ROUTE_ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        write_sample_root(root)
        write_text(root / POLICY, json.dumps({"upgrade_policy": {"required_make_routes": ["phase2-toolchain"]}}, indent=2) + "\n")
        expect_issue(root, ("REQUIRED_MAKE_ROUTE_POLICY_DRIFT", "phase2-toolchain"))
        checks += 1

    assert checks == 11
    print("PHASE2_REQUIRED_MAKE_ROUTES_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_REQUIRED_MAKE_ROUTES_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Phase 2 required make-routes action path.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_REQUIRED_MAKE_ROUTES_ACTION_PATH=fail")
        for code, detail in issues:
            print(f"{code}={detail}")
        return 1

    print("PHASE2_REQUIRED_MAKE_ROUTES_ACTION_PATH=pass")
    print(f"PHASE2_REQUIRED_MAKE_ROUTES_ACTION_PATH_VALIDATE_MARKER_COUNT={len(VALIDATE_MARKERS)}")
    print(f"PHASE2_REQUIRED_MAKE_ROUTES_ACTION_PATH_WORKFLOW_CHECKER_COUNT={len(WORKFLOW_CHECKER_LINES)}")
    print(f"PHASE2_REQUIRED_MAKE_ROUTES_ACTION_PATH_WORKFLOW_ROUTE_COUNT={len(WORKFLOW_ROUTE_LINES)}")
    print(f"PHASE2_REQUIRED_MAKE_ROUTES_ACTION_PATH_MAKEFILE_CHECKER_COUNT={len(MAKEFILE_CHECKER_LINES)}")
    print(f"PHASE2_REQUIRED_MAKE_ROUTES_ACTION_PATH_REQUIRED_ROUTE_COUNT={len(ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
