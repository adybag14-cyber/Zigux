const std = @import("std");
const options = @import("contract_options");

const helper_build_markers = [_][]const u8{
    ".root_source_file = b.path(\"../../tools/lib/argv_split.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/cmdline.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/find_bit.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/bitmap.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/ctype.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/hweight.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/list_sort.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/rbtree.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/string.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/slab.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/str_error_r.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/vsprintf.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/zalloc.zig\"),",
};

const helper_smoke_imports = [_][]const u8{
    "const argv_split = @import(\"argv_split\");",
    "const cmdline = @import(\"cmdline\");",
    "pub const find_bit = @import(\"find_bit\");",
    "const bitmap = @import(\"bitmap\");",
    "const ctype = @import(\"ctype\");",
    "const hweight = @import(\"hweight\");",
    "const list_sort = @import(\"list_sort\");",
    "const rbtree = @import(\"rbtree\");",
    "const string = @import(\"string\");",
    "const slab = @import(\"slab\");",
    "const str_error_r = @import(\"str_error_r\");",
    "const vsprintf = @import(\"vsprintf\");",
    "const zalloc = @import(\"zalloc\");",
};

fn readSource(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, options.source_path, allocator, .limited(256 * 1024));
}

fn requireContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, text, 1, needle));
}

fn requireOnce(text: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, text, needle));
}

fn requireBefore(text: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "host tools smoke checker owns the live build and smoke files" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireOnce(source, "BUILD_REL = Path(\"zigux/tests/build.zig\")");
    try requireOnce(source, "SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")");
    try requireOnce(source, "EXPECTED_BUILD_LINES = (");
    try requireOnce(source, "EXPECTED_SMOKE_LINES = (");
    try requireOnce(source, "fn addPhase1HostToolsSmoke(");
    try requireOnce(source, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\"),");
    try requireOnce(source, ".name = \"phase1-host-tools-smoke\",");
    try requireOnce(source, "zigux/tests/build.zig");
    try requireOnce(source, "zigux/tests/phase1_host_tools_smoke.zig");

    for (helper_build_markers) |marker| {
        try requireOnce(source, marker);
    }
    for (helper_smoke_imports) |marker| {
        try requireOnce(source, marker);
    }
}

test "host tools smoke checker keeps exact-marker enforcement" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireOnce(source, "def require_once(text: str, label: str, needle: str) -> list[str]:");
    try requireOnce(source, "count = text.count(needle)");
    try requireOnce(source, "return [] if count == 1 else [f\"{label}:expected_once:actual_count={count}:{needle}\"]");
    try requireOnce(source, "def collect_failures(root: Path) -> list[str]:");
    try requireOnce(source, "if not build_path.is_file():");
    try requireOnce(source, "if not smoke_path.is_file():");
    try requireOnce(source, "for line in EXPECTED_BUILD_LINES:");
    try requireOnce(source, "failures.extend(require_once(build_text, BUILD_REL.as_posix(), line))");
    try requireOnce(source, "for line in EXPECTED_SMOKE_LINES:");
    try requireOnce(source, "failures.extend(require_once(smoke_text, SMOKE_REL.as_posix(), line))");

    try requireBefore(source, "build_text = load_text(root, BUILD_REL)", "for line in EXPECTED_BUILD_LINES:");
    try requireBefore(source, "smoke_text = load_text(root, SMOKE_REL)", "for line in EXPECTED_SMOKE_LINES:");
    try requireBefore(source, "for line in EXPECTED_BUILD_LINES:", "for line in EXPECTED_SMOKE_LINES:");
}

test "host tools smoke checker preserves self-test and public output markers" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireOnce(source, "def write_fixture_file(root: Path, relative_path: Path, lines: tuple[str, ...]) -> None:");
    try requireOnce(source, "def run_self_test() -> int:");
    try requireOnce(source, "write_fixture_file(root, BUILD_REL, EXPECTED_BUILD_LINES)");
    try requireOnce(source, "write_fixture_file(root, SMOKE_REL, EXPECTED_SMOKE_LINES)");
    try requireOnce(source, "PHASE1_HOST_TOOLS_SMOKE_SELF_TEST=pass");
    try requireOnce(source, "PHASE1_HOST_TOOLS_SMOKE_SELF_TEST=fail");
    try requireOnce(source, "PHASE1_HOST_TOOLS_SMOKE=pass");
    try requireOnce(source, "PHASE1_HOST_TOOLS_SMOKE=fail");
    try requireOnce(source, "print(f\"PHASE1_HOST_TOOLS_SMOKE_EXPECTED_BUILD_MARKER_COUNT={len(EXPECTED_BUILD_LINES)}\")");
    try requireOnce(source, "print(f\"PHASE1_HOST_TOOLS_SMOKE_EXPECTED_SMOKE_MARKER_COUNT={len(EXPECTED_SMOKE_LINES)}\")");
    try requireOnce(source, "print(f\"EXPECTED_BUILD_MARKER_COUNT={len(EXPECTED_BUILD_LINES)}\")");
    try requireOnce(source, "print(f\"EXPECTED_SMOKE_MARKER_COUNT={len(EXPECTED_SMOKE_LINES)}\")");

    try requireBefore(source, "if args.self_test:", "failures = collect_failures(Path(args.root).resolve())");
    try requireBefore(source, "PHASE1_HOST_TOOLS_SMOKE=pass", "CHECKED_BUILD_FILE=");
    try requireBefore(source, "CHECKED_BUILD_FILE=", "CHECKED_SMOKE_FILE=");
}
