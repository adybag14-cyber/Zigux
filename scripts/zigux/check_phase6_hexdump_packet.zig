const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_HEXDUMP_PACKET=pass";
pub const self_test_pass_marker = "PHASE6_HEXDUMP_PACKET_SELF_TEST=pass";

const SELF_TEST_CASES = [_][]const u8{
    "(CATALOG_PATH",
    "- helper-local packet checker: `scripts\\zigux/check_phase6_hexdump_packet.zig`",
    "- helper-local packet checker: `scripts\\zigux/check_phase6_hexdump_proof.zig`",
    ")",
    "(CATALOG_PATH",
    "- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
    "- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`",
    ")",
    "(SLICE_PATH",
    "`PHASE6_STATUS=parked_reviewable`",
    "`PHASE6_STATUS=parked`",
    ")",
    "(SLICE_PATH",
    "the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, `bin2hexUpper`/`bin2HexUpper`, and `hexDumpLineLength` helper parity surface",
    "the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, and `hexDumpLineLength` helper parity surface",
    ")",
    "(SLICE_PATH",
    "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
    "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`",
    ")",
    "(PERF_REFRESH_PATH",
    "`32B-ascii-g2`: the grouped ASCII formatter replay keeps the wider grouped-output ceiling at `max_slowdown_pct = 550`",
    "`32B-ascii-g2`: the grouped ASCII formatter replay keeps the wider grouped-output ceiling at `max_slowdown_pct = 450`",
    ")",
    "(PERF_REFRESH_PATH",
    "This note now serves as the bounded rationale for why the grouped ASCII formatter case keeps a higher ceiling than the plain formatter case",
    "This note now serves as bounded rationale for grouped ASCII ceilings",
    ")",
    "(LIB_PATH",
    "pub fn hexBytePackUpper(buf: []u8, byte: u8) HexError![]u8 {",
    "pub fn hexBytePackUpper(dst: []u8, byte: u8) HexError![]u8 {",
    ")",
    "(LIB_PATH",
    "test \"bin2hexUpper preserves destination on bounds errors\" {",
    "test \"bin2hexUpper preserves destination on overflow\" {",
    ")",
    "(LIB_PATH",
    "test \"hexDumpLineLength mirrors formatter normalization\" {",
    "test \"hexDumpLength mirrors formatter normalization\" {",
    ")",
    "(LIB_PATH",
    "test \"hexDumpToBuffer reports normalized required length for empty and zero-sized buffers\" {",
    "test \"hexDumpToBuffer reports normalized required length for empty buffers\" {",
    ")",
    "(HELPER_TEST_PATH",
    "test \"phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity\" {",
    "test \"phase 6 hexdump direct pack helpers keep nibble parity\" {",
    ")",
    "(HELPER_TEST_PATH",
    "test \"phase 6 hexdump uppercase bulk parity and grouped-ascii exact-capacity buffers stay aligned\" {",
    "test \"phase 6 hexdump grouped-ascii exact-capacity buffers stay aligned\" {",
    ")",
    "(PERF_PATH",
    "return error.HexdumpPerfRegression;",
    "return error.HexdumpPerfDrift;",
    ")",
    "(PERF_MATRIX_PATH",
    ".label = \"16B-ascii-g8\",",
    ".label = \"16B-ascii-g16\",",
    ")",
    "(PERF_MATRIX_PATH",
    "if (!std.mem.eql(u8, want.expected_text.little, actual.expected_text.little)) {",
    "if (!std.mem.eql(u8, expected[idx].expected_text.little, actual.expected_text.little)) {",
    ")",
    "(PERF_MATRIX_PATH",
    "if (!std.mem.eql(u8, want.expected_text.big, actual.expected_text.big)) {",
    "if (!std.mem.eql(u8, expected[idx].expected_text.big, actual.expected_text.big)) {",
    ")",
    "(FIXTURES_PATH",
    ".name = \"ascii rowsize-16 group-8 line length\",",
    ".name = \"ascii rowsize-16 group-16 line length\",",
    ")",
    "(MANIFEST_PATH",
    "\"Documentation/zigux/phase6-hexdump-perf-refresh.md\"",
    "\"Documentation/zigux/phase6-hexdump-perf-proof.md\"",
    ")",
    "(BUILD_PATH",
    "const hexdump_perf_step = b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump helper perf gate\");",
    "const hexdump_perf_step = b.step(\"phase6-hexdump-profile\", \"Run Phase 6 hexdump helper perf gate\");",
    ")",
    "(MAKEFILE_PATH",
    "$(ZIG_REPO_ROOT) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
    "$(ZIG) build phase6-hexdump-profile --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
    ")",
    "(ROUTE_PATH",
    "\"PHASE6_HEXDUMP_ROUTE=pass\"",
    "\"PHASE6_HEXDUMP_REVIEW_ROUTE=pass\"",
    ")",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
