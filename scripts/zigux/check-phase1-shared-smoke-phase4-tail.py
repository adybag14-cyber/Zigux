#!/usr/bin/env python3
"""Guard the current Phase 1 shared-smoke to Phase 4 workflow tail packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
)

WORKFLOW_TAIL_LINES = (
    "run: python3 scripts/zigux/validate_phase3_selftest.py",
    "run: python3 scripts/zigux/run-phase3-checks.py",
    "run: python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "run: zig build phase3-test --build-file zigux/tests/build.zig",
    "run: zig build phase3-dump --build-file zigux/tests/build.zig",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    "run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
    "run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
)

FILE_MARKERS = {
    "scripts/zigux/validate_phase3_selftest.py": (
        '"""Run the current bounded Phase 3 interop self-test packet."""',
        'print("PHASE3_VALIDATE_SELFTEST=pass")',
    ),
    "scripts/zigux/run-phase3-checks.py": (
        '"""Run the current bounded Phase 3 validator packet."""',
        'print("PHASE3_CHECK_RUNNER=pass")',
    ),
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py": (
        '"""Compile and run the current Phase 3 export/UAPI C header smoke."""',
        'print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass")',
    ),
    "scripts/zigux/check-phase4-repo-reality-warning.py": (
        '"""Guard the current-head Phase 4 reversible-delivery repo-reality packet."""',
        "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 32",
        'print("PHASE4_REPO_REALITY_WARNING_SELF_TEST=pass")',
        'print("PHASE4_REPO_REALITY_WARNING=pass")',
    ),
    "zigux/tests/build.zig": (
        '.name = "phase1-host-tools-smoke",',
        '.name = "phase3-abi-dump",',
        'const phase3_test_step = b.step(',
        'const phase3_dump_step = b.step(',
        'const phase1_step = b.step(',
        '"Run the current shared Phase 3 starter packet bundle from zigux/tests",',
        '"Dump the current shared Phase 3 ABI snapshot from zigux/tests",',
        '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests",',
    ),
    "zigux/tests/phase1_host_tools_smoke.zig": (
        'test "phase1 host-tools smoke imports the live helper modules" {',
        'test "phase1 host-tools smoke exercises live helper behavior" {',
        'test "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned" {',
    ),
}

FORBIDDEN_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase1-bench.py",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_file_marker_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in FILE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                issues.append(f"{relative_path}:expected_marker_once:actual={count}:{marker}")
    return issues


def collect_workflow_issues(root: Path) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in read_text(root, ".github/workflows/zigux-bootstrap.yml").splitlines()]

    positions: list[int] = []
    for marker in WORKFLOW_TAIL_LINES:
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            issues.append(f".github/workflows/zigux-bootstrap.yml:expected_line_once:actual={count}:{marker}")
            continue
        positions.append(next(index for index, line in enumerate(lines) if line == marker))

    if len(positions) == len(WORKFLOW_TAIL_LINES):
        if positions != sorted(positions):
            issues.append(".github/workflows/zigux-bootstrap.yml:tail_order_drift")

    for marker in FORBIDDEN_WORKFLOW_LINES:
        count = sum(1 for line in lines if line == marker)
        if count != 0:
            issues.append(f".github/workflows/zigux-bootstrap.yml:forbidden_line:actual={count}:{marker}")

    return issues


def collect_issues(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues
    issues.extend(collect_file_marker_issues(root))
    issues.extend(collect_workflow_issues(root))
    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == ".github/workflows/zigux-bootstrap.yml":
            write_text(root, relative_path, "\n".join(WORKFLOW_TAIL_LINES) + "\n")
            continue
        markers = FILE_MARKERS.get(relative_path, ())
        write_text(root, relative_path, "\n".join(markers) + ("\n" if markers else ""))


def mutate_remove_line(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_line(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_append_line(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append(
            (
                f"missing_{relative_path.replace('/', '_').replace('.', '_')}",
                lambda root, relative_path=relative_path: (root / relative_path).unlink(),
            )
        )

    for relative_path, markers in FILE_MARKERS.items():
        for marker in markers:
            cases.append(
                (
                    f"remove_{relative_path.replace('/', '_').replace('.', '_')}_{abs(hash(marker))}",
                    lambda root, relative_path=relative_path, marker=marker: mutate_remove_line(
                        root, relative_path, marker
                    ),
                )
            )
            cases.append(
                (
                    f"duplicate_{relative_path.replace('/', '_').replace('.', '_')}_{abs(hash(marker))}",
                    lambda root, relative_path=relative_path, marker=marker: mutate_duplicate_line(
                        root, relative_path, marker
                    ),
                )
            )

    for marker in WORKFLOW_TAIL_LINES:
        cases.append(
            (
                f"remove_workflow_{abs(hash(marker))}",
                lambda root, marker=marker: mutate_remove_line(
                    root, ".github/workflows/zigux-bootstrap.yml", marker
                ),
            )
        )
        cases.append(
            (
                f"duplicate_workflow_{abs(hash(marker))}",
                lambda root, marker=marker: mutate_duplicate_line(
                    root, ".github/workflows/zigux-bootstrap.yml", marker
                ),
            )
        )

    for marker in FORBIDDEN_WORKFLOW_LINES:
        cases.append(
            (
                f"forbidden_workflow_{abs(hash(marker))}",
                lambda root, marker=marker: mutate_append_line(
                    root, ".github/workflows/zigux-bootstrap.yml", marker
                ),
            )
        )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-shared-smoke-phase4-tail-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            issues = collect_issues(root)
            if name == "success":
                if issues:
                    print("self-test:success:unexpected_failures")
                    for item in issues:
                        print(item)
                    return 1
            elif not issues:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_SHARED_SMOKE_PHASE4_TAIL_SELF_TEST=pass")
    print(f"PHASE1_SHARED_SMOKE_PHASE4_TAIL_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        "--root",
        dest="repo_root",
        help="override the repository root used for checks",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the guard against synthetic positive and negative cases",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = repo_root(args.repo_root)
    issues = collect_issues(root)
    if issues:
        for item in issues:
            print(item)
        return 1

    print("PHASE1_SHARED_SMOKE_PHASE4_TAIL=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
