#!/usr/bin/env python3
"""Guard the current shared Phase 1 smoke packet across tests-root build, smoke, README, and workflow surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
)

MARKERS = {
    "zigux/tests/README.md": (
        "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "- `zigux/tests/build.zig`",
        "- `zigux/tests/phase1_host_tools_smoke.zig`",
        "- `.github/workflows/zigux-bootstrap.yml`",
    ),
    "zigux/tests/build.zig": (
        "fn addPhase1HostToolsSmoke(",
        '.root_source_file = b.path("phase1_host_tools_smoke.zig"),',
        'root_module.addImport("argv_split", argv_split_module);',
        'root_module.addImport("zalloc", zalloc_module);',
        '.name = "phase1-host-tools-smoke",',
        '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests"',
    ),
    "zigux/tests/phase1_host_tools_smoke.zig": (
        'const argv_split = @import("argv_split");',
        'const zalloc = @import("zalloc");',
        'test "phase1 host-tools smoke imports the live helper modules" {',
        'test "phase1 host-tools smoke exercises live helper behavior" {',
        'test "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned" {',
        'test "phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned" {',
    ),
    ".github/workflows/zigux-bootstrap.yml": (
        "- name: Run current Phase 1 shared tests-root smoke",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_stripped_line_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line.strip() == marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_missing_markers(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        if relative_path == ".github/workflows/zigux-bootstrap.yml":
            issues.extend(collect_stripped_line_markers(text, relative_path, markers))
        else:
            issues.extend(collect_exact_markers(text, relative_path, markers))
    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        markers = MARKERS[relative_path]
        write_text(root, relative_path, "\n".join(markers) + "\n")


def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-shared-smoke-success-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_missing_markers(root)
        if issues:
            print("self-test:success:unexpected_failures")
            for item in issues:
                print(item)
            return 1

    def make_missing_file_case(relative_path: str):
        return (
            f"missing_file_{relative_path.replace('/', '_').replace('.', '_')}",
            lambda root, relative_path=relative_path: (root / relative_path).unlink(),
        )

    def make_marker_case(relative_path: str, marker: str, mutation: str):
        mutator = mutate_remove_marker if mutation == "remove" else mutate_duplicate_marker
        return (
            f"{mutation}_{relative_path.replace('/', '_').replace('.', '_')}_{abs(hash(marker))}",
            lambda root, relative_path=relative_path, marker=marker, mutator=mutator: mutator(
                root, relative_path, marker
            ),
        )

    cases: list[tuple[str, object]] = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append(make_missing_file_case(relative_path))
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append(make_marker_case(relative_path, marker, "remove"))
            cases.append(make_marker_case(relative_path, marker, "duplicate"))

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-shared-smoke-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            issues = collect_missing_markers(root)
            if name == "success":
                if issues:
                    print("self-test:success:unexpected_failures")
                    for item in issues:
                        print(item)
                    return 1
            elif not issues:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_SHARED_SMOKE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SHARED_SMOKE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
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
    issues = collect_missing_markers(root)
    if issues:
        for item in issues:
            print(item)
        return 1

    print("PHASE1_SHARED_SMOKE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
