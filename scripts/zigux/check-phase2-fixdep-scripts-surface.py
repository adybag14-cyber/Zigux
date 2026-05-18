#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXDEP_C = ROOT / "scripts" / "basic" / "fixdep.c"
FIXDEP_ZIG = ROOT / "scripts" / "zigux" / "fixdep.zig"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
FIXDEP_FIXTURES = (
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_dependency_continuation.d",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_dependency_continuation_expected.txt",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_colon.d",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_colon_expected.txt",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_space.d",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_space_expected.txt",
)

WORKFLOW_REQUIRED_MARKERS = (
    "      - name: Self-test current Phase 2 fixdep scripts-surface checker\n"
    "        run: python3 scripts/zigux/check-phase2-fixdep-scripts-surface.py --self-test",
    "      - name: Check current Phase 2 fixdep scripts-surface packet\n"
    "        run: python3 scripts/zigux/check-phase2-fixdep-scripts-surface.py",
    "      - name: Run current Phase 2 fixdep direct replay\n"
    "        run: zig test scripts/zigux/fixdep.zig",
)

WORKFLOW_FORBIDDEN_MARKERS = (
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    return root / path.relative_to(ROOT)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in (FIXDEP_C, FIXDEP_ZIG, *FIXDEP_FIXTURES):
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_REQUIRED_PATH", str(path.relative_to(ROOT))))

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for marker in WORKFLOW_REQUIRED_MARKERS:
        if marker not in workflow_text:
            issues.append(("MISSING_WORKFLOW_MARKER", marker))
    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        if marker in workflow_text:
            issues.append(("STALE_WORKFLOW_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_FIXDEP_SCRIPTS_SURFACE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    for path in (FIXDEP_C, FIXDEP_ZIG, *FIXDEP_FIXTURES):
        write_text(resolve_path(root, path), "# present\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_REQUIRED_MARKERS) + "\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + 2 + len(FIXDEP_FIXTURES) + len(WORKFLOW_REQUIRED_MARKERS) + len(WORKFLOW_FORBIDDEN_MARKERS) + 1
    with tempfile.TemporaryDirectory(prefix="zigux_p2_fixdep_scripts_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for path in (FIXDEP_C, FIXDEP_ZIG, *FIXDEP_FIXTURES):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_REQUIRED_PATH", str(path.relative_to(ROOT))) in issues
            checks_run += 1

        for marker in WORKFLOW_REQUIRED_MARKERS:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                workflow_path.read_text(encoding="utf-8").replace(marker, "", 1),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_MARKER", marker) in issues
            checks_run += 1

        for marker in WORKFLOW_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                workflow_path.read_text(encoding="utf-8") + marker + "\n",
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("STALE_WORKFLOW_MARKER", marker) in issues
            checks_run += 1

        build_self_test_root(root)
        resolve_path(root, WORKFLOW).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing workflow did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_FIXDEP_SCRIPTS_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_SCRIPTS_SURFACE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 2 fixdep workflow and file packet stay aligned with the live repo surface."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_FIXDEP_SCRIPTS_SURFACE=pass")
    print(f"PHASE2_FIXDEP_SCRIPTS_SURFACE_REQUIRED_PATH_COUNT={2 + len(FIXDEP_FIXTURES)}")
    print(f"PHASE2_FIXDEP_SCRIPTS_SURFACE_REQUIRED_WORKFLOW_COUNT={len(WORKFLOW_REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
