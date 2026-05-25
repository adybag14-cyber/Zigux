#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"

PATH_MARKERS = (
    '    "scripts/zigux/check-phase2-cross-validate-contract.py",',
    '    "scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py",',
    '    "scripts/zigux/check-phase2-cross-validate-route-policy.py",',
    '    "scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py",',
    '    "scripts/zigux/check-phase2-cross-validate-shared-surface.py",',
    '    "scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py",',
    '    "scripts/zigux/check-phase2-cross-validate-workflow-order.py",',
    '    "scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py",',
    '    "scripts/zigux/check-phase2-cross-validate-makefile-order.py",',
    '    "scripts/zigux/check-phase2-cross-validate-makefile-order-selftest-alignment.py",',
)

WORKFLOW_PRE_CROSS_MARKERS = (
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-contract-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py",',
)

WORKFLOW_POST_CROSS_MARKERS = (
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order-selftest-alignment.py",',
)

MAKEFILE_CROSS_MARKERS = (
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy-selftest-alignment.py",',
)

MAKEFILE_VALIDATE_MARKERS = (
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-makefile-order.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-makefile-order.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-makefile-order-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-makefile-order-selftest-alignment.py",',
)

CROSS_WORKFLOW_ANCHOR = '    "run: make -C zigux phase2-cross",'
VALIDATE_WORKFLOW_ANCHOR = '    "run: make -C zigux phase2-validate",'
CROSS_TARGET_ANCHOR = '    "phase2-cross:",'
GENKSYMS_TARGET_ANCHOR = '    "phase2-genksyms:",'
VALIDATE_TARGET_ANCHOR = (
    '    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",'
)
PHASE2_TARGET_ANCHOR = '    "phase2: phase2-validate",'

ALL_MARKERS = (
    *PATH_MARKERS,
    *WORKFLOW_PRE_CROSS_MARKERS,
    CROSS_WORKFLOW_ANCHOR,
    *WORKFLOW_POST_CROSS_MARKERS,
    VALIDATE_WORKFLOW_ANCHOR,
    CROSS_TARGET_ANCHOR,
    *MAKEFILE_CROSS_MARKERS,
    GENKSYMS_TARGET_ANCHOR,
    VALIDATE_TARGET_ANCHOR,
    *MAKEFILE_VALIDATE_MARKERS,
    PHASE2_TARGET_ANCHOR,
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


def line_index_map(text: str, markers: tuple[str, ...]) -> dict[str, int]:
    normalized_markers = {marker.strip() for marker in markers}
    indices: dict[str, int] = {}
    for index, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if stripped in normalized_markers and stripped not in indices:
            indices[stripped] = index
    return indices


def collect_block_order_issue(
    code: str,
    block: tuple[str, ...],
    index_map: dict[str, int],
) -> list[tuple[str, str]]:
    positions = [index_map[marker.strip()] for marker in block]
    if positions == sorted(positions):
        return []
    return [(code, ",".join(block))]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    validate_path = resolve_path(root, VALIDATE)
    validate_text = read_text(validate_path)
    issues: list[tuple[str, str]] = []

    for marker in ALL_MARKERS:
        count = count_exact_lines(validate_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATE_MARKER", f"{marker}:count={count}"))

    if issues:
        return issues

    index_map = line_index_map(validate_text, ALL_MARKERS)
    issues.extend(
        collect_block_order_issue("INVALID_PATH_BLOCK_ORDER", PATH_MARKERS, index_map)
    )
    issues.extend(
        collect_block_order_issue(
            "INVALID_WORKFLOW_PRE_CROSS_BLOCK_ORDER",
            WORKFLOW_PRE_CROSS_MARKERS,
            index_map,
        )
    )
    issues.extend(
        collect_block_order_issue(
            "INVALID_WORKFLOW_POST_CROSS_BLOCK_ORDER",
            WORKFLOW_POST_CROSS_MARKERS,
            index_map,
        )
    )
    issues.extend(
        collect_block_order_issue(
            "INVALID_MAKEFILE_CROSS_BLOCK_ORDER",
            MAKEFILE_CROSS_MARKERS,
            index_map,
        )
    )
    issues.extend(
        collect_block_order_issue(
            "INVALID_MAKEFILE_VALIDATE_BLOCK_ORDER",
            MAKEFILE_VALIDATE_MARKERS,
            index_map,
        )
    )

    cross_workflow_index = index_map[CROSS_WORKFLOW_ANCHOR.strip()]
    validate_workflow_index = index_map[VALIDATE_WORKFLOW_ANCHOR.strip()]
    if validate_workflow_index <= cross_workflow_index:
        issues.append(
            (
                "INVALID_WORKFLOW_ANCHOR_ORDER",
                f"{CROSS_WORKFLOW_ANCHOR},{VALIDATE_WORKFLOW_ANCHOR}",
            )
        )

    for marker in WORKFLOW_PRE_CROSS_MARKERS:
        if index_map[marker.strip()] >= cross_workflow_index:
            issues.append(("INVALID_PRE_CROSS_WORKFLOW_PLACEMENT", marker))
    for marker in WORKFLOW_POST_CROSS_MARKERS:
        if (
            index_map[marker.strip()] <= cross_workflow_index
            or index_map[marker.strip()] >= validate_workflow_index
        ):
            issues.append(("INVALID_POST_CROSS_WORKFLOW_PLACEMENT", marker))

    cross_target_index = index_map[CROSS_TARGET_ANCHOR.strip()]
    genksyms_target_index = index_map[GENKSYMS_TARGET_ANCHOR.strip()]
    validate_target_index = index_map[VALIDATE_TARGET_ANCHOR.strip()]
    phase2_target_index = index_map[PHASE2_TARGET_ANCHOR.strip()]
    if genksyms_target_index <= cross_target_index:
        issues.append(
            (
                "INVALID_CROSS_TARGET_ANCHOR_ORDER",
                f"{CROSS_TARGET_ANCHOR},{GENKSYMS_TARGET_ANCHOR}",
            )
        )
    if phase2_target_index <= validate_target_index:
        issues.append(
            (
                "INVALID_VALIDATE_TARGET_ANCHOR_ORDER",
                f"{VALIDATE_TARGET_ANCHOR},{PHASE2_TARGET_ANCHOR}",
            )
        )

    for marker in MAKEFILE_CROSS_MARKERS:
        if (
            index_map[marker.strip()] <= cross_target_index
            or index_map[marker.strip()] >= genksyms_target_index
        ):
            issues.append(("INVALID_MAKEFILE_CROSS_PLACEMENT", marker))
    for marker in MAKEFILE_VALIDATE_MARKERS:
        if (
            index_map[marker.strip()] <= validate_target_index
            or index_map[marker.strip()] >= phase2_target_index
        ):
            issues.append(("INVALID_MAKEFILE_VALIDATE_PLACEMENT", marker))

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_VALIDATE_VALIDATOR_ORDER_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_VALIDATE_VALIDATOR_ORDER_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_VALIDATE_VALIDATOR_ORDER=pass")
    print(f"PHASE2_CROSS_VALIDATE_VALIDATOR_ORDER_MARKER_COUNT={len(ALL_MARKERS)}")
    return 0


def build_sample_root(root: Path) -> None:
    validate_lines = [
        "REQUIRED_PATHS = (",
        *PATH_MARKERS,
        ")",
        "",
        "REQUIRED_WORKFLOW_LINES = (",
        *WORKFLOW_PRE_CROSS_MARKERS,
        CROSS_WORKFLOW_ANCHOR,
        *WORKFLOW_POST_CROSS_MARKERS,
        VALIDATE_WORKFLOW_ANCHOR,
        ")",
        "",
        "REQUIRED_MAKEFILE_LINES = (",
        CROSS_TARGET_ANCHOR,
        *MAKEFILE_CROSS_MARKERS,
        GENKSYMS_TARGET_ANCHOR,
        VALIDATE_TARGET_ANCHOR,
        *MAKEFILE_VALIDATE_MARKERS,
        PHASE2_TARGET_ANCHOR,
        ")",
        "",
    ]
    write_text(resolve_path(root, VALIDATE), "\n".join(validate_lines))


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase2_cross_validate_validator_order_"
    ) as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert run_check(root) == 0
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        validate_path.write_text(
            read_text(validate_path).replace(PATH_MARKERS[0] + "\n", "", 1),
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        validate_path.write_text(
            read_text(validate_path) + PATH_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        validate_lines = read_text(validate_path).splitlines()
        first = validate_lines.index(WORKFLOW_PRE_CROSS_MARKERS[0])
        second = validate_lines.index(WORKFLOW_PRE_CROSS_MARKERS[1])
        validate_lines[first], validate_lines[second] = validate_lines[second], validate_lines[first]
        validate_path.write_text("\n".join(validate_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        validate_lines = read_text(validate_path).splitlines()
        moved = validate_lines.pop(validate_lines.index(WORKFLOW_POST_CROSS_MARKERS[0]))
        insert_at = validate_lines.index(CROSS_WORKFLOW_ANCHOR)
        validate_lines.insert(insert_at, moved)
        validate_path.write_text("\n".join(validate_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        validate_lines = read_text(validate_path).splitlines()
        moved = validate_lines.pop(validate_lines.index(MAKEFILE_CROSS_MARKERS[0]))
        insert_at = validate_lines.index(GENKSYMS_TARGET_ANCHOR) + 1
        validate_lines.insert(insert_at, moved)
        validate_path.write_text("\n".join(validate_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        validate_lines = read_text(validate_path).splitlines()
        moved = validate_lines.pop(validate_lines.index(MAKEFILE_VALIDATE_MARKERS[0]))
        insert_at = validate_lines.index(VALIDATE_TARGET_ANCHOR)
        validate_lines.insert(insert_at, moved)
        validate_path.write_text("\n".join(validate_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        validate_lines = read_text(validate_path).splitlines()
        cross_index = validate_lines.index(CROSS_WORKFLOW_ANCHOR)
        validate_index = validate_lines.index(VALIDATE_WORKFLOW_ANCHOR)
        validate_lines[cross_index], validate_lines[validate_index] = (
            validate_lines[validate_index],
            validate_lines[cross_index],
        )
        validate_path.write_text("\n".join(validate_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

    print("PHASE2_CROSS_VALIDATE_VALIDATOR_ORDER_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_VALIDATOR_ORDER_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Lane 21 validator-side cross-validate markers ordered inside "
            "scripts/zigux/validate-phase2.py."
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