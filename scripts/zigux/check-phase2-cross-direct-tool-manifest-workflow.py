#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
TOOL_MANIFEST_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-tool-manifest-contract.py"
TOOL_MANIFEST_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-tool-manifest-contract-selftest-alignment.py"
)

TOOL_MANIFEST_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross-tool-manifest-contract.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-tool-manifest-contract.py",
    "run: python3 scripts/zigux/check-phase2-cross-tool-manifest-contract-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-tool-manifest-contract-selftest-alignment.py",
)
CROSS_ROUTE = "run: make -C zigux phase2-cross"
SHARED_SURFACE_START = "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface.py --self-test"
VALIDATE_ROUTE = "run: make -C zigux phase2-validate"
REQUIRED_PATHS = (
    WORKFLOW,
    TOOL_MANIFEST_CHECKER,
    TOOL_MANIFEST_ALIGNMENT,
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
    indices: dict[str, int] = {}
    for index, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if stripped in markers and stripped not in indices:
            indices[stripped] = index
    return indices


def ordered_marker_sequence(text: str, markers: tuple[str, ...]) -> list[str]:
    marker_set = set(markers)
    return [line.strip() for line in text.splitlines() if line.strip() in marker_set]


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
    required_lines = (
        CROSS_ROUTE,
        *TOOL_MANIFEST_WORKFLOW_LINES,
        SHARED_SURFACE_START,
        VALIDATE_ROUTE,
    )
    for marker in required_lines:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    if issues:
        return issues

    index_map = line_index_map(workflow_text, required_lines)
    ordered_markers = ordered_marker_sequence(workflow_text, required_lines)
    cross_index = ordered_markers.index(CROSS_ROUTE)
    shared_surface_index = ordered_markers.index(SHARED_SURFACE_START)
    validate_index = ordered_markers.index(VALIDATE_ROUTE)
    tool_manifest_positions = [ordered_markers.index(line) for line in TOOL_MANIFEST_WORKFLOW_LINES]

    if tool_manifest_positions != sorted(tool_manifest_positions):
        issues.append(("INVALID_TOOL_MANIFEST_BLOCK_ORDER", ",".join(TOOL_MANIFEST_WORKFLOW_LINES)))
    if validate_index <= cross_index:
        issues.append(("INVALID_ROUTE_ANCHOR_ORDER", "phase2-cross,phase2-validate"))
    if tool_manifest_positions[0] != cross_index + 1:
        issues.append(("TOOL_MANIFEST_NOT_DIRECT_AFTER_CROSS", TOOL_MANIFEST_WORKFLOW_LINES[0]))
    if shared_surface_index <= cross_index or shared_surface_index >= validate_index:
        issues.append(("INVALID_SHARED_SURFACE_ANCHOR_PLACEMENT", SHARED_SURFACE_START))
    if shared_surface_index != tool_manifest_positions[-1] + 1:
        issues.append(("TOOL_MANIFEST_NOT_DIRECT_BEFORE_SHARED_SURFACE", SHARED_SURFACE_START))
    for position, marker in zip(tool_manifest_positions, TOOL_MANIFEST_WORKFLOW_LINES):
        if position <= cross_index or position >= shared_surface_index:
            issues.append(("INVALID_TOOL_MANIFEST_PLACEMENT", marker))

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_WORKFLOW_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_WORKFLOW_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_WORKFLOW=pass")
    print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_WORKFLOW_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_WORKFLOW_LINE_COUNT={len(TOOL_MANIFEST_WORKFLOW_LINES) + 3}")
    return 0


def build_sample_root(root: Path) -> None:
    workflow_lines = (
        "name: zigux-bootstrap",
        CROSS_ROUTE,
        *TOOL_MANIFEST_WORKFLOW_LINES,
        SHARED_SURFACE_START,
        VALIDATE_ROUTE,
    )
    write_text(resolve_path(root, WORKFLOW), "\n".join(workflow_lines) + "\n")
    write_text(resolve_path(root, TOOL_MANIFEST_CHECKER), "# present\n")
    write_text(resolve_path(root, TOOL_MANIFEST_ALIGNMENT), "# present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_direct_tool_manifest_workflow_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert run_check(root) == 0
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            read_text(workflow_path).replace(TOOL_MANIFEST_WORKFLOW_LINES[0] + "\n", "", 1),
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            read_text(workflow_path) + TOOL_MANIFEST_WORKFLOW_LINES[0] + "\n",
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_lines = read_text(workflow_path).splitlines()
        cross_index = workflow_lines.index(CROSS_ROUTE)
        first_tool_manifest_index = workflow_lines.index(TOOL_MANIFEST_WORKFLOW_LINES[0])
        workflow_lines[cross_index], workflow_lines[first_tool_manifest_index] = (
            workflow_lines[first_tool_manifest_index],
            workflow_lines[cross_index],
        )
        workflow_path.write_text("\n".join(workflow_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_lines = read_text(workflow_path).splitlines()
        shared_surface_index = workflow_lines.index(SHARED_SURFACE_START)
        last_tool_manifest_index = workflow_lines.index(TOOL_MANIFEST_WORKFLOW_LINES[-1])
        workflow_lines[shared_surface_index], workflow_lines[last_tool_manifest_index] = (
            workflow_lines[last_tool_manifest_index],
            workflow_lines[shared_surface_index],
        )
        workflow_path.write_text("\n".join(workflow_lines) + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        resolve_path(root, TOOL_MANIFEST_ALIGNMENT).unlink()
        assert run_check(root) == 1
        checks += 1

    print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_WORKFLOW_SELF_TEST=pass")
    print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_WORKFLOW_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Lane 21 direct tool-manifest workflow block anchored between "
            "phase2-cross and the shared-surface checker block."
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