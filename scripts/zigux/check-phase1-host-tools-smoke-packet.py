#!/usr/bin/env python3
"""Guard the current Phase 1 host-tools smoke packet across tests root and workflow."""

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

README_MARKERS = (
    "## Phase 1 host-tools review packet",
    "- `zigux/tests/build.zig`",
    "- `zigux/tests/phase1_host_tools_smoke.zig`",
    "- `.github/workflows/zigux-bootstrap.yml`",
    "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
)

BUILD_MARKERS = (
    'root_source_file = b.path("phase1_host_tools_smoke.zig"),',
    'const argv_split_module = b.createModule(.{',
    'const cmdline_module = b.createModule(.{',
    'const find_bit_module = b.createModule(.{',
    'const bitmap_module = b.createModule(.{',
    'const ctype_module = b.createModule(.{',
    'const hweight_module = b.createModule(.{',
    'const list_sort_module = b.createModule(.{',
    'const rbtree_module = b.createModule(.{',
    'const string_module = b.createModule(.{',
    'const slab_module = b.createModule(.{',
    'const str_error_r_module = b.createModule(.{',
    'const vsprintf_module = b.createModule(.{',
    'const zalloc_module = b.createModule(.{',
    'root_module.addImport("argv_split", argv_split_module);',
    'root_module.addImport("cmdline", cmdline_module);',
    'root_module.addImport("find_bit", find_bit_module);',
    'root_module.addImport("bitmap", bitmap_module);',
    'root_module.addImport("ctype", ctype_module);',
    'root_module.addImport("hweight", hweight_module);',
    'root_module.addImport("list_sort", list_sort_module);',
    'root_module.addImport("rbtree", rbtree_module);',
    'root_module.addImport("string", string_module);',
    'root_module.addImport("slab", slab_module);',
    'root_module.addImport("str_error_r", str_error_r_module);',
    'root_module.addImport("vsprintf", vsprintf_module);',
    'root_module.addImport("zalloc", zalloc_module);',
    '.name = "phase1-host-tools-smoke",',
)

SMOKE_MARKERS = (
    'const argv_split = @import("argv_split");',
    'const cmdline = @import("cmdline");',
    'pub const find_bit = @import("find_bit");',
    'const bitmap = @import("bitmap");',
    'const ctype = @import("ctype");',
    'const hweight = @import("hweight");',
    'const list_sort = @import("list_sort");',
    'const rbtree = @import("rbtree");',
    'const string = @import("string");',
    'const slab = @import("slab");',
    'const str_error_r = @import("str_error_r");',
    'const vsprintf = @import("vsprintf");',
    'const zalloc = @import("zalloc");',
    'test "phase1 host-tools smoke imports the live helper modules" {',
    'try std.testing.expect(@hasDecl(slab, "kmallocBytes"));',
    'try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));',
    'try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));',
    'try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));',
    'test "phase1 host-tools smoke exercises live helper behavior" {',
    'const rendered_len = vsprintf.scnprintf(&render_buffer, "{s}:{d}", .{ "zigux", 9 });',
    'try std.testing.expectEqualStrings("Permission denied", str_error_r.strErrorR(13, &error_buffer));',
    'var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);',
    'const allocated = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;',
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-phase1-host-tools-smoke-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-host-tools-smoke-packet.py",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: str, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


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


def collect_issues(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    issues.extend(collect_exact_markers(read_text(root, "zigux/tests/README.md"), "zigux/tests/README.md", README_MARKERS))
    issues.extend(collect_exact_markers(read_text(root, "zigux/tests/build.zig"), "zigux/tests/build.zig", BUILD_MARKERS))
    issues.extend(
        collect_exact_markers(
            read_text(root, "zigux/tests/phase1_host_tools_smoke.zig"),
            "zigux/tests/phase1_host_tools_smoke.zig",
            SMOKE_MARKERS,
        )
    )
    issues.extend(
        collect_stripped_line_markers(
            read_text(root, ".github/workflows/zigux-bootstrap.yml"),
            ".github/workflows/zigux-bootstrap.yml",
            WORKFLOW_MARKERS,
        )
    )
    return issues


def build_sample_repo(root: Path) -> None:
    write_text(root, "zigux/tests/README.md", "\n".join(README_MARKERS) + "\n")
    write_text(root, "zigux/tests/build.zig", "\n".join(BUILD_MARKERS) + "\n")
    write_text(root, "zigux/tests/phase1_host_tools_smoke.zig", "\n".join(SMOKE_MARKERS) + "\n")
    write_text(root, ".github/workflows/zigux-bootstrap.yml", "\n".join(WORKFLOW_MARKERS) + "\n")


def remove_line(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_line(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-host-tools-smoke-packet-success-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("self-test:success:unexpected_failures")
            for item in issues:
                print(item)
            return 1

    cases: list[tuple[str, str, str, str]] = []
    for relative_path in REQUIRED_FILES:
        cases.append(("missing_file", relative_path, "", relative_path))
    for marker in README_MARKERS:
        cases.append(("remove", "zigux/tests/README.md", marker, "readme"))
    for marker in BUILD_MARKERS:
        cases.append(("remove", "zigux/tests/build.zig", marker, "build"))
    for marker in SMOKE_MARKERS:
        cases.append(("remove", "zigux/tests/phase1_host_tools_smoke.zig", marker, "smoke"))
    for marker in WORKFLOW_MARKERS:
        cases.append(("remove", ".github/workflows/zigux-bootstrap.yml", marker, "workflow"))
        cases.append(("duplicate", ".github/workflows/zigux-bootstrap.yml", marker, "workflow"))

    for idx, (kind, relative_path, marker, label) in enumerate(cases, start=1):
        with tempfile.TemporaryDirectory(prefix="phase1-host-tools-smoke-packet-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if kind == "missing_file":
                (root / relative_path).unlink()
            elif kind == "remove":
                remove_line(root, relative_path, marker)
            else:
                duplicate_line(root, relative_path, marker)

            issues = collect_issues(root)
            if not issues:
                print(f"self-test:case_{idx}:{kind}:{label}:expected_failure")
                return 1

    print("PHASE1_HOST_TOOLS_SMOKE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_HOST_TOOLS_SMOKE_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}")
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

    print("PHASE1_HOST_TOOLS_SMOKE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
