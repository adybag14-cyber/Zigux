#!/usr/bin/env python3
"""Guard the shared Phase 1 host-tools smoke scaffold against build and smoke drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BUILD_REL = Path("zigux/tests/build.zig")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")

EXPECTED_BUILD_LINES = (
    'fn addPhase1HostToolsSmoke(',
    '.root_source_file = b.path("phase1_host_tools_smoke.zig"),',
    '.root_source_file = b.path("../../tools/lib/argv_split.zig"),',
    '.root_source_file = b.path("../../tools/lib/cmdline.zig"),',
    '.root_source_file = b.path("../../tools/lib/find_bit.zig"),',
    '.root_source_file = b.path("../../tools/lib/bitmap.zig"),',
    '.root_source_file = b.path("../../tools/lib/ctype.zig"),',
    '.root_source_file = b.path("../../tools/lib/hweight.zig"),',
    '.root_source_file = b.path("../../tools/lib/list_sort.zig"),',
    '.root_source_file = b.path("../../tools/lib/rbtree.zig"),',
    '.root_source_file = b.path("../../tools/lib/string.zig"),',
    '.root_source_file = b.path("../../tools/lib/slab.zig"),',
    '.root_source_file = b.path("../../tools/lib/str_error_r.zig"),',
    '.root_source_file = b.path("../../tools/lib/vsprintf.zig"),',
    '.root_source_file = b.path("../../tools/lib/zalloc.zig"),',
    'bitmap_module.addImport("find_bit", find_bit_module);',
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
    'const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);',
    'const phase1_step = b.step(',
    '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests",',
    'phase1_step.dependOn(&phase1_host_tools_smoke.step);',
    'smoke_step.dependOn(&phase1_host_tools_smoke.step);',
    'test_step.dependOn(&phase1_host_tools_smoke.step);',
)

EXPECTED_SMOKE_LINES = (
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
    'try std.testing.expect(@hasDecl(argv_split, "argvSplit"));',
    'try std.testing.expect(@hasDecl(cmdline, "memparse"));',
    'try std.testing.expect(@hasDecl(find_bit, "findFirstBit"));',
    'try std.testing.expect(@hasDecl(bitmap, "setRange"));',
    'try std.testing.expect(@hasDecl(ctype, "isalpha"));',
    'try std.testing.expect(@hasDecl(hweight, "swHweight64"));',
    'try std.testing.expect(@hasDecl(list_sort, "listSort"));',
    'try std.testing.expect(@hasDecl(rbtree, "find"));',
    'try std.testing.expect(@hasDecl(rbtree, "matchIterator"));',
    'try std.testing.expect(@hasDecl(string, "strtobool"));',
    'try std.testing.expect(@hasDecl(slab, "kmallocBytes"));',
    'try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));',
    'try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));',
    'try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));',
    'test "phase1 host-tools smoke exercises live helper behavior" {',
    'var split = try argv_split.argv_split(std.testing.allocator, "  zigux   host\ttools  ");',
    'const parsed = cmdline.memparse("64K tail");',
    'try std.testing.expect(cmdline.parseOptionStr("rootwait,quiet", "quiet"));',
    'try std.testing.expect(ctype.isalpha(\'Q\'));',
    'try std.testing.expectEqual(@as(u64, 32), hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0));',
    'const allocated = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;',
    'try std.testing.expectEqualStrings("Permission denied", str_error_r.strErrorR(13, &error_buffer));',
    'const rendered_len = vsprintf.scnprintf(&render_buffer, "{s}:{d}", .{ "zigux", 9 });',
    'var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);',
    'list_sort.listSort(null, &list_head, list_cmp);',
    'bitmap.setRange(&map, word_bits - 1, 3);',
    'try std.testing.expectEqual(word_bits - 1, find_bit.findFirstBit(&map, nbits));',
    'const bitmap_rendered_len = bitmap.scnprintf(&map, nbits, &rendered);',
    'try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, "auto"));',
    'var iter = rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp);',
    'try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.addCached(&cached_entries[1].node, &cached_root));',
)


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_once(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    build_path = root / BUILD_REL
    smoke_path = root / SMOKE_REL
    if not build_path.is_file():
        failures.append(f"missing_file:{BUILD_REL.as_posix()}")
    if not smoke_path.is_file():
        failures.append(f"missing_file:{SMOKE_REL.as_posix()}")
    if failures:
        return failures

    build_text = load_text(root, BUILD_REL)
    smoke_text = load_text(root, SMOKE_REL)

    for line in EXPECTED_BUILD_LINES:
        failures.extend(require_once(build_text, BUILD_REL.as_posix(), line))
    for line in EXPECTED_SMOKE_LINES:
        failures.extend(require_once(smoke_text, SMOKE_REL.as_posix(), line))

    return failures


def write_fixture_file(root: Path, relative_path: Path, lines: tuple[str, ...]) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-host-tools-smoke-") as tmpdir:
        root = Path(tmpdir)
        write_fixture_file(root, BUILD_REL, EXPECTED_BUILD_LINES)
        write_fixture_file(root, SMOKE_REL, EXPECTED_SMOKE_LINES)

        failures = collect_failures(root)
        if failures:
            print("PHASE1_HOST_TOOLS_SMOKE_SELF_TEST=fail")
            for failure in failures:
                print(f"FAILURE={failure}")
            return 1

    print("PHASE1_HOST_TOOLS_SMOKE_SELF_TEST=pass")
    print(f"PHASE1_HOST_TOOLS_SMOKE_EXPECTED_BUILD_MARKER_COUNT={len(EXPECTED_BUILD_LINES)}")
    print(f"PHASE1_HOST_TOOLS_SMOKE_EXPECTED_SMOKE_MARKER_COUNT={len(EXPECTED_SMOKE_LINES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="repository root containing zigux/tests/")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(Path(args.root).resolve())
    if failures:
        print("PHASE1_HOST_TOOLS_SMOKE=fail")
        for failure in failures:
            print(f"FAILURE={failure}")
        return 1

    print("PHASE1_HOST_TOOLS_SMOKE=pass")
    print(f"CHECKED_BUILD_FILE={BUILD_REL.as_posix()}")
    print(f"CHECKED_SMOKE_FILE={SMOKE_REL.as_posix()}")
    print(f"EXPECTED_BUILD_MARKER_COUNT={len(EXPECTED_BUILD_LINES)}")
    print(f"EXPECTED_SMOKE_MARKER_COUNT={len(EXPECTED_SMOKE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
