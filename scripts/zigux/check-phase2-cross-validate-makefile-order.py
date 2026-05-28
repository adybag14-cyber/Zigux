#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "zigux" / "Makefile"
CONTRACT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-contract.py"
CONTRACT_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-contract-selftest-alignment.py"
)
ROUTE_POLICY_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-route-policy.py"
ROUTE_POLICY_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-route-policy-selftest-alignment.py"
)
DIRECT_WORKFLOW_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-direct-tool-manifest-workflow.py"
)
DIRECT_WORKFLOW_ALIGNMENT = (
    ROOT
    / "scripts"
    / "zigux"
    / "check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py"
)
SHARED_SURFACE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface.py"
SHARED_SURFACE_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface-selftest-alignment.py"
)

CONTRACT_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract-selftest-alignment.py",
)
ROUTE_POLICY_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy-selftest-alignment.py",
)
DIRECT_WORKFLOW_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-workflow.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-workflow.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py",
)
SHARED_SURFACE_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface-selftest-alignment.py",
)

REQUIRED_PATHS = (
    MAKEFILE,
    CONTRACT_CHECKER,
    CONTRACT_ALIGNMENT,
    ROUTE_POLICY_CHECKER,
    ROUTE_POLICY_ALIGNMENT,
    DIRECT_WORKFLOW_CHECKER,
    DIRECT_WORKFLOW_ALIGNMENT,
    SHARED_SURFACE_CHECKER,
    SHARED_SURFACE_ALIGNMENT,
)
REQUIRED_MAKEFILE_LINES = (
    "phase2-cross:",
    *CONTRACT_MAKEFILE_LINES,
    *ROUTE_POLICY_MAKEFILE_LINES,
    "phase2-genksyms:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    *DIRECT_WORKFLOW_MAKEFILE_LINES,
    *SHARED_SURFACE_MAKEFILE_LINES,
)
REQUIRED_CROSS_TARGET = "phase2-cross:"
REQUIRED_VALIDATE_TARGET = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep"
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


def find_line_index(text: str, marker: str) -> int:
    normalized_marker = marker.strip()
    for index, line in enumerate(text.splitlines()):
        if line.strip() == normalized_marker:
            return index
    raise KeyError(marker)


def collect_makefile_target_commands(text: str, header: str) -> list[str]:
    commands: list[str] = []
    in_target = False
    for line in text.splitlines():
        stripped = line.strip()
        if not in_target:
            if stripped == header:
                in_target = True
            continue
        if stripped and not line.startswith((" ", "\t")) and ":" in stripped:
            break
        if line.startswith("\t"):
            commands.append(stripped)
    return commands


def collect_block_order_issues(
    issue_prefix: str,
    block: tuple[str, ...],
    commands: list[str],
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    positions = [commands.index(marker) for marker in block]
    if positions != sorted(positions):
        issues.append((f"INVALID_{issue_prefix}_ORDER", ",".join(block)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    makefile_path = resolve_path(root, MAKEFILE)
    if not makefile_path.exists():
        return issues

    makefile_text = read_text(makefile_path)
    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    if issues:
        return issues

    cross_header_index = find_line_index(makefile_text, REQUIRED_CROSS_TARGET)
    validate_header_index = find_line_index(makefile_text, REQUIRED_VALIDATE_TARGET)
    if validate_header_index <= cross_header_index:
        issues.append(("INVALID_TARGET_HEADER_ORDER", f"{REQUIRED_CROSS_TARGET},{REQUIRED_VALIDATE_TARGET}"))

    cross_commands = collect_makefile_target_commands(makefile_text, REQUIRED_CROSS_TARGET)
    validate_commands = collect_makefile_target_commands(makefile_text, REQUIRED_VALIDATE_TARGET)

    for marker in (*CONTRACT_MAKEFILE_LINES, *ROUTE_POLICY_MAKEFILE_LINES):
        if marker not in cross_commands:
            issues.append(("MISSING_CROSS_TARGET_COMMAND", marker))
    for marker in (*DIRECT_WORKFLOW_MAKEFILE_LINES, *SHARED_SURFACE_MAKEFILE_LINES):
        if marker not in validate_commands:
            issues.append(("MISSING_VALIDATE_TARGET_COMMAND", marker))

    if issues:
        return issues

    issues.extend(collect_block_order_issues("CONTRACT_BLOCK", CONTRACT_MAKEFILE_LINES, cross_commands))
    issues.extend(collect_block_order_issues("ROUTE_POLICY_BLOCK", ROUTE_POLICY_MAKEFILE_LINES, cross_commands))
    issues.extend(
        collect_block_order_issues("DIRECT_WORKFLOW_BLOCK", DIRECT_WORKFLOW_MAKEFILE_LINES, validate_commands)
    )
    issues.extend(
        collect_block_order_issues("SHARED_SURFACE_BLOCK", SHARED_SURFACE_MAKEFILE_LINES, validate_commands)
    )

    contract_end = max(cross_commands.index(marker) for marker in CONTRACT_MAKEFILE_LINES)
    route_policy_start = min(cross_commands.index(marker) for marker in ROUTE_POLICY_MAKEFILE_LINES)
    if route_policy_start <= contract_end:
        issues.append(("INVALID_ROUTE_POLICY_PLACEMENT", ",".join(ROUTE_POLICY_MAKEFILE_LINES)))

    direct_workflow_end = max(validate_commands.index(marker) for marker in DIRECT_WORKFLOW_MAKEFILE_LINES)
    shared_surface_start = min(validate_commands.index(marker) for marker in SHARED_SURFACE_MAKEFILE_LINES)
    if shared_surface_start <= direct_workflow_end:
        issues.append(("INVALID_SHARED_SURFACE_PLACEMENT", ",".join(SHARED_SURFACE_MAKEFILE_LINES)))

    for marker in SHARED_SURFACE_MAKEFILE_LINES:
        if marker in cross_commands:
            issues.append(("INVALID_SHARED_SURFACE_TARGET_PLACEMENT", marker))

    for marker in (*CONTRACT_MAKEFILE_LINES, *ROUTE_POLICY_MAKEFILE_LINES):
        if marker in validate_commands:
            issues.append(("INVALID_CROSS_TARGET_PLACEMENT", marker))

    for marker in DIRECT_WORKFLOW_MAKEFILE_LINES:
        if marker in cross_commands:
            issues.append(("INVALID_DIRECT_WORKFLOW_TARGET_PLACEMENT", marker))

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER=pass")
    print(f"PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    return 0


def build_sample_root(root: Path) -> None:
    makefile_lines = [
        REQUIRED_CROSS_TARGET,
        *[f"\t{line}" for line in CONTRACT_MAKEFILE_LINES],
        *[f"\t{line}" for line in ROUTE_POLICY_MAKEFILE_LINES],
        "phase2-genksyms:",
        "\t@true",
        REQUIRED_VALIDATE_TARGET,
        *[f"\t{line}" for line in DIRECT_WORKFLOW_MAKEFILE_LINES],
        *[f"\t{line}" for line in SHARED_SURFACE_MAKEFILE_LINES],
    ]
    write_text(resolve_path(root, MAKEFILE), "\n".join(makefile_lines) + "\n")
    for path in REQUIRED_PATHS[1:]:
        write_text(resolve_path(root, path), "# present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_makefile_order_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert run_check(root) == 0
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            read_text(makefile_path).replace(CONTRACT_MAKEFILE_LINES[0] + "\n", "", 1),
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            read_text(makefile_path).replace(DIRECT_WORKFLOW_MAKEFILE_LINES[0] + "\n", "", 1),
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            read_text(makefile_path) + f"\t{SHARED_SURFACE_MAKEFILE_LINES[0]}\n",
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_lines = read_text(makefile_path).splitlines()
        first = makefile_lines.index(f"\t{CONTRACT_MAKEFILE_LINES[0]}")
        second = makefile_lines.index(f"\t{CONTRACT_MAKEFILE_LINES[1]}")
        makefile_lines[first], makefile_lines[second] = makefile_lines[second], makefile_lines[first]
        makefile_path.write_text("\n".join(makefile_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_lines = read_text(makefile_path).splitlines()
        contract_index = makefile_lines.index(f"\t{CONTRACT_MAKEFILE_LINES[-1]}")
        route_index = makefile_lines.index(f"\t{ROUTE_POLICY_MAKEFILE_LINES[0]}")
        makefile_lines[contract_index], makefile_lines[route_index] = (
            makefile_lines[route_index],
            makefile_lines[contract_index],
        )
        makefile_path.write_text("\n".join(makefile_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_lines = read_text(makefile_path).splitlines()
        direct_index = makefile_lines.index(f"\t{DIRECT_WORKFLOW_MAKEFILE_LINES[0]}")
        next_index = makefile_lines.index(f"\t{DIRECT_WORKFLOW_MAKEFILE_LINES[1]}")
        makefile_lines[direct_index], makefile_lines[next_index] = (
            makefile_lines[next_index],
            makefile_lines[direct_index],
        )
        makefile_path.write_text("\n".join(makefile_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_lines = read_text(makefile_path).splitlines()
        direct_tail = makefile_lines.index(f"\t{DIRECT_WORKFLOW_MAKEFILE_LINES[-1]}")
        shared_head = makefile_lines.index(f"\t{SHARED_SURFACE_MAKEFILE_LINES[0]}")
        makefile_lines[direct_tail], makefile_lines[shared_head] = (
            makefile_lines[shared_head],
            makefile_lines[direct_tail],
        )
        makefile_path.write_text("\n".join(makefile_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_lines = read_text(makefile_path).splitlines()
        shared_index = makefile_lines.index(f"\t{SHARED_SURFACE_MAKEFILE_LINES[0]}")
        next_index = makefile_lines.index(f"\t{SHARED_SURFACE_MAKEFILE_LINES[1]}")
        makefile_lines[shared_index], makefile_lines[next_index] = (
            makefile_lines[next_index],
            makefile_lines[shared_index],
        )
        makefile_path.write_text("\n".join(makefile_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_lines = read_text(makefile_path).splitlines()
        cross_header = makefile_lines.index(REQUIRED_CROSS_TARGET)
        validate_header = makefile_lines.index(REQUIRED_VALIDATE_TARGET)
        makefile_lines[cross_header], makefile_lines[validate_header] = (
            makefile_lines[validate_header],
            makefile_lines[cross_header],
        )
        makefile_path.write_text("\n".join(makefile_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        resolve_path(root, DIRECT_WORKFLOW_ALIGNMENT).unlink()
        assert run_check(root) == 1
        checks += 1

    print("PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Lane 21 validator-side Makefile commands ordered around the "
            "phase2-cross and phase2-validate targets."
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