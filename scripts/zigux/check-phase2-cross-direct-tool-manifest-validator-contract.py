#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-direct-tool-manifest-workflow.py"
WORKFLOW_ALIGNMENT = (
    ROOT
    / "scripts"
    / "zigux"
    / "check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py"
)

REQUIRED_PATHS = (
    VALIDATE,
    WORKFLOW_CHECKER,
    WORKFLOW_ALIGNMENT,
)

PATH_PRECEDING_MARKER = '    "scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py",'
PATH_DIRECT_MARKERS = (
    '    "scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow.py",',
    '    "scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py",',
)
PATH_FOLLOWING_MARKER = '    "scripts/zigux/check-phase2-cross-validate-shared-surface.py",'
WORKFLOW_PRECEDING_MARKER = (
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-route-policy-selftest-alignment.py",'
)
WORKFLOW_DIRECT_MARKERS = (
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-workflow-selftest-alignment.py",',
)
WORKFLOW_FOLLOWING_MARKER = (
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface.py --self-test",'
)

REQUIRED_VALIDATE_MARKERS = (
    *PATH_DIRECT_MARKERS,
    *WORKFLOW_DIRECT_MARKERS,
)
ORDER_MARKERS = (
    PATH_PRECEDING_MARKER,
    *PATH_DIRECT_MARKERS,
    PATH_FOLLOWING_MARKER,
    WORKFLOW_PRECEDING_MARKER,
    *WORKFLOW_DIRECT_MARKERS,
    WORKFLOW_FOLLOWING_MARKER,
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

    for anchor in (PATH_PRECEDING_MARKER, PATH_FOLLOWING_MARKER, WORKFLOW_PRECEDING_MARKER, WORKFLOW_FOLLOWING_MARKER):
        count = count_exact_lines(validate_text, anchor)
        if count == 0:
            issues.append(("MISSING_ORDER_ANCHOR", anchor))
        elif count != 1:
            issues.append(("DUPLICATE_ORDER_ANCHOR", f"{anchor}:count={count}"))

    if issues:
        return issues

    index_map = line_index_map(validate_text, ORDER_MARKERS)
    order_positions = [index_map[marker.strip()] for marker in ORDER_MARKERS]
    if order_positions != sorted(order_positions):
        issues.append(("INVALID_VALIDATE_MARKER_ORDER", ",".join(ORDER_MARKERS)))

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT=pass")
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_REQUIRED_PATH_COUNT="
        f"{len(REQUIRED_PATHS)}"
    )
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_MARKER_COUNT="
        f"{len(REQUIRED_VALIDATE_MARKERS)}"
    )
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_ORDER_MARKER_COUNT="
        f"{len(ORDER_MARKERS)}"
    )
    return 0


def build_sample_root(root: Path) -> None:
    validate_lines = [
        "CHECKS = (",
        PATH_PRECEDING_MARKER,
        *PATH_DIRECT_MARKERS,
        PATH_FOLLOWING_MARKER,
        WORKFLOW_PRECEDING_MARKER,
        *WORKFLOW_DIRECT_MARKERS,
        WORKFLOW_FOLLOWING_MARKER,
        ")",
    ]
    write_text(resolve_path(root, VALIDATE), "\n".join(validate_lines) + "\n")
    write_text(resolve_path(root, WORKFLOW_CHECKER), "# present\n")
    write_text(resolve_path(root, WORKFLOW_ALIGNMENT), "# present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase2_cross_direct_tool_manifest_validator_contract_"
    ) as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert run_check(root) == 0
        checks += 1

        build_sample_root(root)
        write_text(resolve_path(root, VALIDATE), "CHECKS = ()\n")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        write_text(
            validate_path,
            "CHECKS = (\n"
            + "\n".join((PATH_PRECEDING_MARKER, *PATH_DIRECT_MARKERS, PATH_DIRECT_MARKERS[0]))
            + "\n)\n",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        lines = validate_path.read_text(encoding="utf-8").splitlines()
        moved = lines.pop(lines.index(PATH_DIRECT_MARKERS[0]))
        lines.insert(lines.index(PATH_FOLLOWING_MARKER), moved)
        write_text(validate_path, "\n".join(lines) + "\n")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        validate_path = resolve_path(root, VALIDATE)
        lines = validate_path.read_text(encoding="utf-8").splitlines()
        moved = lines.pop(lines.index(WORKFLOW_DIRECT_MARKERS[-1]))
        lines.insert(lines.index(WORKFLOW_PRECEDING_MARKER), moved)
        write_text(validate_path, "\n".join(lines) + "\n")
        assert run_check(root) == 1
        checks += 1

        for path in REQUIRED_PATHS[1:]:
            build_sample_root(root)
            resolve_path(root, path).unlink()
            assert run_check(root) == 1
            checks += 1

        build_sample_root(root)
        resolve_path(root, VALIDATE).unlink()
        assert run_check(root) == 1
        checks += 1

    print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_SELF_TEST=pass")
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_CONTRACT_SELF_TEST_CASE_COUNT="
        f"{checks}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Lane 21 validator packet aware of the direct tool-manifest "
            "workflow checker pair."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())