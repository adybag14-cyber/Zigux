#!/usr/bin/env python3
"""Guard the current shared Phase 1 smoke packet across tests, scripts, fixture, and workflow."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    ".github/workflows/zigux-bootstrap.yml",
)

MARKERS = {
    "scripts/zigux/README.md": (
        "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
    ),
    "zigux/tests/README.md": (
        "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "- `zigux/tests/build.zig`",
        "- `zigux/tests/phase1_host_tools_smoke.zig`",
        "- `.github/workflows/zigux-bootstrap.yml`",
        "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
    ),
    "zigux/tests/build.zig": (
        "fn addPhase1HostToolsSmoke(",
        '.root_source_file = b.path("phase1_host_tools_smoke.zig"),',
        '.name = "phase1-host-tools-smoke",',
        'root_module.addImport("argv_split", argv_split_module);',
        'root_module.addImport("list_sort", list_sort_module);',
        'root_module.addImport("slab", slab_module);',
        'root_module.addImport("vsprintf", vsprintf_module);',
        'root_module.addImport("zalloc", zalloc_module);',
    ),
    "zigux/tests/phase1_host_tools_smoke.zig": (
        'test "phase1 host-tools smoke imports the live helper modules" {',
        'test "phase1 host-tools smoke exercises live helper behavior" {',
        'try std.testing.expect(@hasDecl(argv_split, "argvSplit"));',
        'try std.testing.expect(@hasDecl(list_sort, "listSort"));',
        'try std.testing.expect(@hasDecl(slab, "kmallocBytes"));',
        'try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));',
        'try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));',
        'try std.testing.expectEqual(word_bits + 1, find_bit.findLastBit(&map, nbits));',
        'const bitmap_rendered_len = bitmap.scnprintf(&map, nbits, &rendered);',
        "const found_duplicate = rbtree.find(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
    ),
    "zigux/tests/fixtures/phase1_helper_manifest.json": (
        '"helper_count": 13,',
        '"phase1_helper_replay_anchor": "test \\"phase1 host-tools smoke exercises live helper behavior\\""',
        '"direct_anchor_followup_helpers": [',
        '"tools/lib/bitmap.zig",',
        '"tools/lib/find_bit.zig",',
        '"tools/lib/rbtree.zig",',
        '"tools/lib/string.zig"',
    ),
    ".github/workflows/zigux-bootstrap.yml": (
        "      - name: Run current Phase 1 shared tests-root smoke",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
        "      - name: Self-test current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "      - name: Check current Phase 1 shared reminder packet",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    ),
}

FORBIDDEN_FRAGMENTS = (
    "      - name: Run Phase 1 helper tests",
    "        run: zig build test --build-file zigux/tests/build.zig",
    "      - name: Run Phase 1 helper benchmark smoke",
    "        run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe",
    "`scripts/zigux/validate-phase1.py`",
    "`zigux/tests/phase1_helpers.zig`",
)

EXPECTED_SELF_TEST_CASE_COUNT = 13


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_forbidden_fragments(text: str, label: str) -> list[str]:
    issues: list[str] = []
    for fragment in FORBIDDEN_FRAGMENTS:
        count = text.count(fragment)
        if count != 0:
            issues.append(f"{label}:forbidden:{fragment}:actual={count}")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        issues.extend(collect_exact_markers(text, relative_path, markers))
        issues.extend(collect_forbidden_fragments(text, relative_path))
    return issues


def build_sample_repo(root: Path) -> None:
    for relative_path, markers in MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")


def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + marker + "\n", encoding="utf-8")


def mutate_append_forbidden_fragment(root: Path, relative_path: str, fragment: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + fragment + "\n", encoding="utf-8")


def expect_issue(tag: str, issues: list[str], expected_fragment: str) -> None:
    if not any(expected_fragment in issue for issue in issues):
        raise AssertionError(f"{tag}: missing expected issue fragment {expected_fragment!r} in {issues!r}")


def run_self_test() -> None:
    cases_run = 0

    def run_case(tag: str, mutate, expected_fragment: str | None = None) -> None:
        nonlocal cases_run
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            issues = collect_issues(root)
            if expected_fragment is None:
                if issues:
                    raise AssertionError(f"{tag}: expected no issues, got {issues!r}")
            else:
                expect_issue(tag, issues, expected_fragment)
        cases_run += 1

    run_case("happy_path", None)
    run_case(
        "missing_tests_readme",
        lambda root: (root / "zigux/tests/README.md").unlink(),
        "missing_file:zigux/tests/README.md",
    )
    run_case(
        "missing_tests_smoke_route",
        lambda root: mutate_remove_marker(
            root,
            "zigux/tests/README.md",
            "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        ),
        "zigux/tests/README.md:* current shared Phase 1 smoke route:",
    )
    run_case(
        "missing_scripts_smoke_route",
        lambda root: mutate_remove_marker(
            root,
            "scripts/zigux/README.md",
            "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        ),
        "scripts/zigux/README.md:`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    )
    run_case(
        "missing_build_root_source",
        lambda root: mutate_remove_marker(
            root,
            "zigux/tests/build.zig",
            '.root_source_file = b.path("phase1_host_tools_smoke.zig"),',
        ),
        'zigux/tests/build.zig:.root_source_file = b.path("phase1_host_tools_smoke.zig"),',
    )
    run_case(
        "missing_build_import",
        lambda root: mutate_remove_marker(
            root,
            "zigux/tests/build.zig",
            'root_module.addImport("slab", slab_module);',
        ),
        'zigux/tests/build.zig:root_module.addImport("slab", slab_module);',
    )
    run_case(
        "missing_smoke_import_test",
        lambda root: mutate_remove_marker(
            root,
            "zigux/tests/phase1_host_tools_smoke.zig",
            'test "phase1 host-tools smoke imports the live helper modules" {',
        ),
        'zigux/tests/phase1_host_tools_smoke.zig:test "phase1 host-tools smoke imports the live helper modules" {',
    )
    run_case(
        "missing_smoke_behavior",
        lambda root: mutate_remove_marker(
            root,
            "zigux/tests/phase1_host_tools_smoke.zig",
            'test "phase1 host-tools smoke exercises live helper behavior" {',
        ),
        'zigux/tests/phase1_host_tools_smoke.zig:test "phase1 host-tools smoke exercises live helper behavior" {',
    )
    run_case(
        "missing_smoke_rbtree_anchor",
        lambda root: mutate_remove_marker(
            root,
            "zigux/tests/phase1_host_tools_smoke.zig",
            "const found_duplicate = rbtree.find(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
        ),
        "zigux/tests/phase1_host_tools_smoke.zig:const found_duplicate = rbtree.find(",
    )
    run_case(
        "missing_manifest_anchor",
        lambda root: mutate_remove_marker(
            root,
            "zigux/tests/fixtures/phase1_helper_manifest.json",
            '"phase1_helper_replay_anchor": "test \\"phase1 host-tools smoke exercises live helper behavior\\""',
        ),
        'zigux/tests/fixtures/phase1_helper_manifest.json:"phase1_helper_replay_anchor"',
    )
    run_case(
        "missing_workflow_smoke_step",
        lambda root: mutate_remove_marker(
            root,
            ".github/workflows/zigux-bootstrap.yml",
            "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
        ),
        ".github/workflows/zigux-bootstrap.yml:        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    )
    run_case(
        "duplicate_workflow_smoke_step",
        lambda root: mutate_duplicate_marker(
            root,
            ".github/workflows/zigux-bootstrap.yml",
            "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
        ),
        ".github/workflows/zigux-bootstrap.yml:        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig:expected=1:actual=2",
    )
    run_case(
        "old_workflow_phase1_test_route",
        lambda root: mutate_append_forbidden_fragment(
            root,
            ".github/workflows/zigux-bootstrap.yml",
            "        run: zig build test --build-file zigux/tests/build.zig",
        ),
        ".github/workflows/zigux-bootstrap.yml:forbidden:        run: zig build test --build-file zigux/tests/build.zig:actual=1",
    )

    if cases_run != EXPECTED_SELF_TEST_CASE_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_SELF_TEST_CASE_COUNT} self-test cases, ran {cases_run}"
        )

    print("PHASE1_SHARED_SMOKE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SHARED_SMOKE_PACKET_SELF_TEST_CASE_COUNT={cases_run}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    root = repo_root(args.root)
    issues = collect_issues(root)
    if issues:
        for issue in issues:
            print(issue)
        raise SystemExit(1)

    print("PHASE1_SHARED_SMOKE_PACKET=pass")
    print(f"PHASE1_SHARED_SMOKE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_SHARED_SMOKE_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )


if __name__ == "__main__":
    main()
