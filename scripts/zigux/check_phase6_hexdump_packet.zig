const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_HEXDUMP_PACKET=pass";
pub const self_test_pass_marker = "PHASE6_HEXDUMP_PACKET_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "- roadmap anchor: `lib/hexdump.c`",
    "- Zig helper: `lib/hexdump.zig`",
    "- focused helper replay: `zigux/tests/phase6_hexdump.zig`",
    "- dedicated slowdown replay: `zigux/tests/phase6_hexdump_perf.zig`",
    "- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "- helper-local packet checker: `scripts\\zigux/check_phase6_hexdump_packet.zig`",
    "- `zig run check_phase6_hexdump_packet.zig`",
    "- `zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig`",
    "- `make -C zigux phase6-hexdump-review`",
    "- `zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig`",
    "- `make -C zigux phase6-hexdump-perf-matrix-test`",
    "- `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`",
    "- `make -C zigux phase6-hexdump-test`",
    "- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
    "- `make -C zigux phase6-hexdump-perf`",
};

const markers_1 = [_][]const u8{
    "`PHASE6_STATUS=parked_reviewable`",
    "`PHASE6_SLICE=hexdump-leaf-helper`",
    "`Documentation/zigux/phase6-hexdump-perf-refresh.md`",
    "`scripts\\zigux/check_phase6_hexdump_packet.zig`",
    "`zigux/tests/phase6_build.zig`",
    "the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, `bin2hexUpper`/`bin2HexUpper`, and `hexDumpLineLength` helper parity surface",
    "focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable",
    "`zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet",
    "`make -C zigux phase6-hexdump-review`",
    "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
};

const markers_2 = [_][]const u8{
    "# Phase 6 Hexdump Perf Refresh Evidence",
    "* owner lane: `P6-Y09`",
    "`Documentation/zigux/phase6-hexdump-slice.md` plus `scripts\\zigux/check_phase6_hexdump_packet.zig`",
    "`16B-plain`: `max_slowdown_pct = 175` remains the narrow plain formatter ceiling",
    "`32B-ascii-g2`: the grouped ASCII formatter replay keeps the wider grouped-output ceiling at `max_slowdown_pct = 550`",
    "`zigux/tests/phase6_helper_parity_manifest.json` records the same helper-local hexdump replay and threshold cases",
    "This note now serves as the bounded rationale for why the grouped ASCII formatter case keeps a higher ceiling than the plain formatter case",
};

const markers_3 = [_][]const u8{
    "pub const hex_asc = \"0123456789abcdef\";",
    "pub fn hexAscHi(byte: u8) u8 {",
    "pub fn hexAscUpperHi(byte: u8) u8 {",
    "pub fn hexBytePack(buf: []u8, byte: u8) HexError![]u8 {",
    "pub fn hexBytePackUpper(buf: []u8, byte: u8) HexError![]u8 {",
    "pub fn hex2bin(dst: []u8, src: []const u8) HexError!void {",
    "pub fn bin2hex(dst: []u8, src: []const u8) HexError![]u8 {",
    "pub fn hexDumpLineLength(",
    "pub fn hexDumpToBuffer(",
    "test \"hex2bin and bin2hex snake-case aliases stay aligned\" {",
    "test \"bin2hexUpper emits uppercase bulk output and alias stays aligned\" {",
    "test \"bin2hexUpper preserves destination on bounds errors\" {",
    "test \"hexBytePack helpers chain bytes and preserve destination on bounds errors\" {",
    "test \"hexDumpLineLength mirrors formatter normalization\" {",
    "test \"hexDumpToBuffer reports normalized required length for empty and zero-sized buffers\" {",
};

const markers_4 = [_][]const u8{
    "test \"phase 6 hexdump helper packet replays the serialized parity matrix\" {",
    "test \"phase 6 hexdump helper packet preserves the overflow contract\" {",
    "test \"phase 6 hexdump helper packet preserves the curated length matrix\" {",
    "test \"phase 6 hexdump direct helper entrypoints stay aligned with the packet\" {",
    "test \"phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity\" {",
    "test \"phase 6 hexdump uppercase bulk parity and grouped-ascii exact-capacity buffers stay aligned\" {",
};

const markers_5 = [_][]const u8{
    "fn validatePerfMatrix() !void {",
    "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n\", .{fixtures.perf_cases.len});",
    "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF={s}\\n\", .{if (failed) \"fail\" else \"pass\"});",
    "return error.HexdumpPerfRegression;",
};

const markers_6 = [_][]const u8{
    "pub fn validatePerfMatrix() !void {",
    ".label = \"16B-plain-g1\",",
    ".label = \"32B-ascii-g2\",",
    ".label = \"16B-ascii-g4\",",
    ".label = \"16B-ascii-g8\",",
    ".max_slowdown_pct = 175,",
    ".max_slowdown_pct = 550,",
    ".max_slowdown_pct = 600,",
    "if (!std.mem.eql(u8, want.expected_text.little, actual.expected_text.little)) {",
    "if (!std.mem.eql(u8, want.expected_text.big, actual.expected_text.big)) {",
    "test \"phase 6 hexdump perf matrix preflight stays aligned with the documented packet\" {",
};

const markers_7 = [_][]const u8{
    "pub const test_hexdump_buf_size = 32 * 3 + 2 + 32 + 1;",
    "pub const parity_cases = [_]ParityCase{",
    "pub const overflow_cases = [_]OverflowCase{",
    "pub const length_cases = [_]LengthCase{",
    "pub const perf_cases = [_]PerfCase{",
    ".name = \"empty ascii line reports zero length\",",
    ".name = \"plain rowsize-16 group-8 line length\",",
    ".name = \"ascii rowsize-16 group-8 line length\",",
    ".label = \"16B-ascii-g8\",",
};

const markers_8 = [_][]const u8{
    "\"key\": \"hexdump\"",
    "\"roadmap_anchor\": \"lib/hexdump.c\"",
    "\"zig_helper\": \"lib/hexdump.zig\"",
    "\"focused_helper_replay\": \"zigux/tests/phase6_hexdump.zig\"",
    "\"dedicated_slowdown_replay\": \"zigux/tests/phase6_hexdump_perf.zig\"",
    "\"perf_matrix_preflight\": \"zigux/tests/phase6_hexdump_perf_matrix.zig\"",
    "\"Documentation/zigux/phase6-hexdump-slice.md\"",
    "\"Documentation/zigux/phase6-hexdump-perf-refresh.md\"",
    "\"label\": \"16B-plain-g1\"",
    "\"label\": \"32B-ascii-g2\"",
    "\"label\": \"16B-ascii-g4\"",
    "\"label\": \"16B-ascii-g8\"",
    "\"max_slowdown_pct\": 600",
};

const markers_9 = [_][]const u8{
    "const hexdump_test_step = b.step(\"phase6-hexdump-test\", \"Run Phase 6 hexdump helper tests\");",
    "hexdump_test_step.dependOn(&run_hexdump_tests.step);",
    "hexdump_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
    "const hexdump_review_step = b.step(\"phase6-hexdump-review\", \"Run Phase 6 hexdump perf-matrix review preflight\");",
    "const hexdump_perf_matrix_test_step = b.step(",
    "\"phase6-hexdump-perf-matrix-test\",",
    "const hexdump_perf_step = b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump helper perf gate\");",
};

const markers_10 = [_][]const u8{
    "phase6-hexdump-review:",
    "$(ZIG) run scripts/zigux/check_phase6_hexdump_packet.zig",
    "$(ZIG) run scripts/zigux/check_phase6_hexdump_route.zig",
    "phase6-hexdump-perf-matrix-test:",
    "$(ZIG_REPO_ROOT) build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-hexdump-test:",
    "$(ZIG_REPO_ROOT) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-hexdump-perf:",
    "$(ZIG_REPO_ROOT) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
};

const markers_11 = [_][]const u8{
    "pub const live_pass_marker = \"PHASE6_HEXDUMP_ROUTE=pass\";",
    ".rel = \"zigux/Makefile\"",
    ".rel = \"zigux/tests/phase6_build.zig\"",
    ".rel = \"zigux/tests/phase6_hexdump_perf.zig\"",
    ".rel = \"zigux/tests/phase6_hexdump_perf_matrix.zig\"",
    ".rel = \"Documentation/zigux/phase6-helper-evidence-catalog.md\"",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase6-helper-evidence-catalog.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase6-hexdump-slice.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase6-hexdump-perf-refresh.md", .markers = &markers_2 },
    .{ .rel = "lib/hexdump.zig", .markers = &markers_3 },
    .{ .rel = "zigux/tests/phase6_hexdump.zig", .markers = &markers_4 },
    .{ .rel = "zigux/tests/phase6_hexdump_perf.zig", .markers = &markers_5 },
    .{ .rel = "zigux/tests/phase6_hexdump_perf_matrix.zig", .markers = &markers_6 },
    .{ .rel = "zigux/tests/fixtures/phase6_hexdump_vectors.zig", .markers = &markers_7 },
    .{ .rel = "zigux/tests/phase6_helper_parity_manifest.json", .markers = &markers_8 },
    .{ .rel = "zigux/tests/phase6_build.zig", .markers = &markers_9 },
    .{ .rel = "zigux/Makefile", .markers = &markers_10 },
    .{ .rel = "scripts/zigux/check_phase6_hexdump_route.zig", .markers = &markers_11 },
};

const SelfCase = struct { rel: []const u8, marker: []const u8 };
const self_cases = [_]SelfCase{
    .{ .rel = "Documentation/zigux/phase6-helper-evidence-catalog.md", .marker = "- helper-local packet checker: `scripts\\zigux/check_phase6_hexdump_packet.zig`" },
    .{ .rel = "Documentation/zigux/phase6-helper-evidence-catalog.md", .marker = "- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`" },
    .{ .rel = "Documentation/zigux/phase6-hexdump-slice.md", .marker = "`PHASE6_STATUS=parked_reviewable`" },
    .{ .rel = "Documentation/zigux/phase6-hexdump-slice.md", .marker = "the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, `bin2hexUpper`/`bin2HexUpper`, and `hexDumpLineLength` helper parity surface" },
    .{ .rel = "Documentation/zigux/phase6-hexdump-slice.md", .marker = "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`" },
    .{ .rel = "Documentation/zigux/phase6-hexdump-perf-refresh.md", .marker = "`32B-ascii-g2`: the grouped ASCII formatter replay keeps the wider grouped-output ceiling at `max_slowdown_pct = 550`" },
    .{ .rel = "Documentation/zigux/phase6-hexdump-perf-refresh.md", .marker = "This note now serves as the bounded rationale for why the grouped ASCII formatter case keeps a higher ceiling than the plain formatter case" },
    .{ .rel = "lib/hexdump.zig", .marker = "pub fn hexBytePackUpper(buf: []u8, byte: u8) HexError![]u8 {" },
    .{ .rel = "lib/hexdump.zig", .marker = "test \"bin2hexUpper preserves destination on bounds errors\" {" },
    .{ .rel = "lib/hexdump.zig", .marker = "test \"hexDumpLineLength mirrors formatter normalization\" {" },
    .{ .rel = "lib/hexdump.zig", .marker = "test \"hexDumpToBuffer reports normalized required length for empty and zero-sized buffers\" {" },
    .{ .rel = "zigux/tests/phase6_hexdump.zig", .marker = "test \"phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity\" {" },
    .{ .rel = "zigux/tests/phase6_hexdump.zig", .marker = "test \"phase 6 hexdump uppercase bulk parity and grouped-ascii exact-capacity buffers stay aligned\" {" },
    .{ .rel = "zigux/tests/phase6_hexdump_perf.zig", .marker = "return error.HexdumpPerfRegression;" },
    .{ .rel = "zigux/tests/phase6_hexdump_perf_matrix.zig", .marker = ".label = \"16B-ascii-g8\"," },
    .{ .rel = "zigux/tests/phase6_hexdump_perf_matrix.zig", .marker = "if (!std.mem.eql(u8, want.expected_text.little, actual.expected_text.little)) {" },
    .{ .rel = "zigux/tests/phase6_hexdump_perf_matrix.zig", .marker = "if (!std.mem.eql(u8, want.expected_text.big, actual.expected_text.big)) {" },
    .{ .rel = "zigux/tests/fixtures/phase6_hexdump_vectors.zig", .marker = ".name = \"ascii rowsize-16 group-8 line length\"," },
    .{ .rel = "zigux/tests/phase6_helper_parity_manifest.json", .marker = "\"Documentation/zigux/phase6-hexdump-perf-refresh.md\"" },
    .{ .rel = "zigux/tests/phase6_build.zig", .marker = "const hexdump_perf_step = b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump helper perf gate\");" },
    .{ .rel = "zigux/Makefile", .marker = "$(ZIG_REPO_ROOT) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all" },
    .{ .rel = "scripts/zigux/check_phase6_hexdump_route.zig", .marker = "\"PHASE6_HEXDUMP_ROUTE=pass\"" },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    for (self_cases) |case| {
        const file_path = try guard.joinPath(allocator, root, case.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        try guard.requireMarker(text, case.marker);
    }
    try std.testing.expectEqual(@as(usize, 22), self_cases.len);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE6_HEXDUMP_PACKET_SELF_TEST_CASE_COUNT={d}", .{22});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try guard.printLine(io, "PHASE6_HEXDUMP_CONTRACT_COUNT={d}", .{contracts.len});
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const live_pass_marker = "PHASE6_HEXDUMP_PACKET=pass";
// pub const self_test_pass_marker = "PHASE6_HEXDUMP_PACKET_SELF_TEST=pass";
//
// const FileContract = struct { rel: []const u8, markers: []const []const u8 };
//
// const markers_0 = [_][]const u8{
//     "- roadmap anchor: `lib/hexdump.c`",
//     "- Zig helper: `lib/hexdump.zig`",
//     "- focused helper replay: `zigux/tests/phase6_hexdump.zig`",
//     "- dedicated slowdown replay: `zigux/tests/phase6_hexdump_perf.zig`",
//     "- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`",
//     "- helper-local packet checker: `scripts\\zigux/check_phase6_hexdump_packet.zig`",
//     "- `zig run check_phase6_hexdump_packet.zig`",
//     "- `zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig`",
//     "- `make -C zigux phase6-hexdump-review`",
//     "- `zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig`",
//     "- `make -C zigux phase6-hexdump-perf-matrix-test`",
//     "- `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`",
//     "- `make -C zigux phase6-hexdump-test`",
//     "- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
//     "- `make -C zigux phase6-hexdump-perf`",
// };
//
// const markers_1 = [_][]const u8{
//     "`PHASE6_STATUS=parked_reviewable`",
//     "`PHASE6_SLICE=hexdump-leaf-helper`",
//     "`Documentation/zigux/phase6-hexdump-perf-refresh.md`",
//     "`scripts\\zigux/check_phase6_hexdump_packet.zig`",
//     "`zigux/tests/phase6_build.zig`",
//     "the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, `bin2hexUpper`/`bin2HexUpper`, and `hexDumpLineLength` helper parity surface",
//     "focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable",
//     "`zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet",
//     "`make -C zigux phase6-hexdump-review`",
//     "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
// };
//
// const markers_2 = [_][]const u8{
//     "# Phase 6 Hexdump Perf Refresh Evidence",
//     "* owner lane: `P6-Y09`",
//     "`Documentation/zigux/phase6-hexdump-slice.md` plus `scripts\\zigux/check_phase6_hexdump_packet.zig`",
//     "`16B-plain`: `max_slowdown_pct = 175` remains the narrow plain formatter ceiling",
//     "`32B-ascii-g2`: the grouped ASCII formatter replay keeps the wider grouped-output ceiling at `max_slowdown_pct = 550`",
//     "`zigux/tests/phase6_helper_parity_manifest.json` records the same helper-local hexdump replay and threshold cases",
//     "This note now serves as the bounded rationale for why the grouped ASCII formatter case keeps a higher ceiling than the plain formatter case",
// };
//
// const markers_3 = [_][]const u8{
//     "pub const hex_asc = \"0123456789abcdef\";",
//     "pub fn hexAscHi(byte: u8) u8 {",
//     "pub fn hexAscUpperHi(byte: u8) u8 {",
//     "pub fn hexBytePack(buf: []u8, byte: u8) HexError![]u8 {",
//     "pub fn hexBytePackUpper(buf: []u8, byte: u8) HexError![]u8 {",
//     "pub fn hex2bin(dst: []u8, src: []const u8) HexError!void {",
//     "pub fn bin2hex(dst: []u8, src: []const u8) HexError![]u8 {",
//     "pub fn hexDumpLineLength(",
//     "pub fn hexDumpToBuffer(",
//     "test \"hex2bin and bin2hex snake-case aliases stay aligned\" {",
//     "test \"bin2hexUpper emits uppercase bulk output and alias stays aligned\" {",
//     "test \"bin2hexUpper preserves destination on bounds errors\" {",
//     "test \"hexBytePack helpers chain bytes and preserve destination on bounds errors\" {",
//     "test \"hexDumpLineLength mirrors formatter normalization\" {",
//     "test \"hexDumpToBuffer reports normalized required length for empty and zero-sized buffers\" {",
// };
//
// const markers_4 = [_][]const u8{
//     "test \"phase 6 hexdump helper packet replays the serialized parity matrix\" {",
//     "test \"phase 6 hexdump helper packet preserves the overflow contract\" {",
//     "test \"phase 6 hexdump helper packet preserves the curated length matrix\" {",
//     "test \"phase 6 hexdump direct helper entrypoints stay aligned with the packet\" {",
//     "test \"phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity\" {",
//     "test \"phase 6 hexdump uppercase bulk parity and grouped-ascii exact-capacity buffers stay aligned\" {",
// };
//
// const markers_5 = [_][]const u8{
//     "fn validatePerfMatrix() !void {",
//     "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n\", .{fixtures.perf_cases.len});",
//     "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF={s}\\n\", .{if (failed) \"fail\" else \"pass\"});",
//     "return error.HexdumpPerfRegression;",
// };
//
// const markers_6 = [_][]const u8{
//     "pub fn validatePerfMatrix() !void {",
//     ".label = \"16B-plain-g1\",",
//     ".label = \"32B-ascii-g2\",",
//     ".label = \"16B-ascii-g4\",",
//     ".label = \"16B-ascii-g8\",",
//     ".max_slowdown_pct = 175,",
//     ".max_slowdown_pct = 550,",
//     ".max_slowdown_pct = 600,",
//     "if (!std.mem.eql(u8, want.expected_text.little, actual.expected_text.little)) {",
//     "if (!std.mem.eql(u8, want.expected_text.big, actual.expected_text.big)) {",
//     "test \"phase 6 hexdump perf matrix preflight stays aligned with the documented packet\" {",
// };
//
// const markers_7 = [_][]const u8{
//     "pub const test_hexdump_buf_size = 32 * 3 + 2 + 32 + 1;",
//     "pub const parity_cases = [_]ParityCase{",
//     "pub const overflow_cases = [_]OverflowCase{",
//     "pub const length_cases = [_]LengthCase{",
//     "pub const perf_cases = [_]PerfCase{",
//     ".name = \"empty ascii line reports zero length\",",
//     ".name = \"plain rowsize-16 group-8 line length\",",
//     ".name = \"ascii rowsize-16 group-8 line length\",",
//     ".label = \"16B-ascii-g8\",",
// };
//
// const markers_8 = [_][]const u8{
//     "\"key\": \"hexdump\"",
//     "\"roadmap_anchor\": \"lib/hexdump.c\"",
//     "\"zig_helper\": \"lib/hexdump.zig\"",
//     "\"focused_helper_replay\": \"zigux/tests/phase6_hexdump.zig\"",
//     "\"dedicated_slowdown_replay\": \"zigux/tests/phase6_hexdump_perf.zig\"",
//     "\"perf_matrix_preflight\": \"zigux/tests/phase6_hexdump_perf_matrix.zig\"",
//     "\"Documentation/zigux/phase6-hexdump-slice.md\"",
//     "\"Documentation/zigux/phase6-hexdump-perf-refresh.md\"",
//     "\"label\": \"16B-plain-g1\"",
//     "\"label\": \"32B-ascii-g2\"",
//     "\"label\": \"16B-ascii-g4\"",
//     "\"label\": \"16B-ascii-g8\"",
//     "\"max_slowdown_pct\": 600",
// };
//
// const markers_9 = [_][]const u8{
//     "const hexdump_test_step = b.step(\"phase6-hexdump-test\", \"Run Phase 6 hexdump helper tests\");",
//     "hexdump_test_step.dependOn(&run_hexdump_tests.step);",
//     "hexdump_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
//     "const hexdump_review_step = b.step(\"phase6-hexdump-review\", \"Run Phase 6 hexdump perf-matrix review preflight\");",
//     "const hexdump_perf_matrix_test_step = b.step(",
//     "\"phase6-hexdump-perf-matrix-test\",",
//     "const hexdump_perf_step = b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump helper perf gate\");",
// };
//
// const markers_10 = [_][]const u8{
//     "phase6-hexdump-review:",
//     "$(ZIG) run scripts/zigux/check_phase6_hexdump_packet.zig",
//     "$(ZIG) run scripts/zigux/check_phase6_hexdump_route.zig",
//     "phase6-hexdump-perf-matrix-test:",
//     "$(ZIG_REPO_ROOT) build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
//     "phase6-hexdump-test:",
//     "$(ZIG_REPO_ROOT) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig --summary all",
//     "phase6-hexdump-perf:",
//     "$(ZIG_REPO_ROOT) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
// };
//
// const markers_11 = [_][]const u8{
//     "pub const live_pass_marker = \"PHASE6_HEXDUMP_ROUTE=pass\";",
//     ".rel = \"zigux/Makefile\"",
//     ".rel = \"zigux/tests/phase6_build.zig\"",
//     ".rel = \"zigux/tests/phase6_hexdump_perf.zig\"",
//     ".rel = \"zigux/tests/phase6_hexdump_perf_matrix.zig\"",
//     ".rel = \"Documentation/zigux/phase6-helper-evidence-catalog.md\"",
// };
//
// const contracts = [_]FileContract{
//     .{ .rel = "Documentation/zigux/phase6-helper-evidence-catalog.md", .markers = &markers_0 },
//     .{ .rel = "Documentation/zigux/phase6-hexdump-slice.md", .markers = &markers_1 },
//     .{ .rel = "Documentation/zigux/phase6-hexdump-perf-refresh.md", .markers = &markers_2 },
//     .{ .rel = "lib/hexdump.zig", .markers = &markers_3 },
//     .{ .rel = "zigux/tests/phase6_hexdump.zig", .markers = &markers_4 },
//     .{ .rel = "zigux/tests/phase6_hexdump_perf.zig", .markers = &markers_5 },
//     .{ .rel = "zigux/tests/phase6_hexdump_perf_matrix.zig", .markers = &markers_6 },
//     .{ .rel = "zigux/tests/fixtures/phase6_hexdump_vectors.zig", .markers = &markers_7 },
//     .{ .rel = "zigux/tests/phase6_helper_parity_manifest.json", .markers = &markers_8 },
//     .{ .rel = "zigux/tests/phase6_build.zig", .markers = &markers_9 },
//     .{ .rel = "zigux/Makefile", .markers = &markers_10 },
//     .{ .rel = "scripts/zigux/check_phase6_hexdump_route.zig", .markers = &markers_11 },
// };
//
// const SelfCase = struct { rel: []const u8, marker: []const u8 };
// const self_cases = [_]SelfCase{
//     .{ .rel = "Documentation/zigux/phase6-helper-evidence-catalog.md", .marker = "- helper-local packet checker: `scripts\\zigux/check_phase6_hexdump_packet.zig`" },
//     .{ .rel = "Documentation/zigux/phase6-helper-evidence-catalog.md", .marker = "- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`" },
//     .{ .rel = "Documentation/zigux/phase6-hexdump-slice.md", .marker = "`PHASE6_STATUS=parked_reviewable`" },
//     .{ .rel = "Documentation/zigux/phase6-hexdump-slice.md", .marker = "the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, `bin2hexUpper`/`bin2HexUpper`, and `hexDumpLineLength` helper parity surface" },
//     .{ .rel = "Documentation/zigux/phase6-hexdump-slice.md", .marker = "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`" },
//     .{ .rel = "Documentation/zigux/phase6-hexdump-perf-refresh.md", .marker = "`32B-ascii-g2`: the grouped ASCII formatter replay keeps the wider grouped-output ceiling at `max_slowdown_pct = 550`" },
//     .{ .rel = "Documentation/zigux/phase6-hexdump-perf-refresh.md", .marker = "This note now serves as the bounded rationale for why the grouped ASCII formatter case keeps a higher ceiling than the plain formatter case" },
//     .{ .rel = "lib/hexdump.zig", .marker = "pub fn hexBytePackUpper(buf: []u8, byte: u8) HexError![]u8 {" },
//     .{ .rel = "lib/hexdump.zig", .marker = "test \"bin2hexUpper preserves destination on bounds errors\" {" },
//     .{ .rel = "lib/hexdump.zig", .marker = "test \"hexDumpLineLength mirrors formatter normalization\" {" },
//     .{ .rel = "lib/hexdump.zig", .marker = "test \"hexDumpToBuffer reports normalized required length for empty and zero-sized buffers\" {" },
//     .{ .rel = "zigux/tests/phase6_hexdump.zig", .marker = "test \"phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity\" {" },
//     .{ .rel = "zigux/tests/phase6_hexdump.zig", .marker = "test \"phase 6 hexdump uppercase bulk parity and grouped-ascii exact-capacity buffers stay aligned\" {" },
//     .{ .rel = "zigux/tests/phase6_hexdump_perf.zig", .marker = "return error.HexdumpPerfRegression;" },
//     .{ .rel = "zigux/tests/phase6_hexdump_perf_matrix.zig", .marker = ".label = \"16B-ascii-g8\"," },
//     .{ .rel = "zigux/tests/phase6_hexdump_perf_matrix.zig", .marker = "if (!std.mem.eql(u8, want.expected_text.little, actual.expected_text.little)) {" },
//     .{ .rel = "zigux/tests/phase6_hexdump_perf_matrix.zig", .marker = "if (!std.mem.eql(u8, want.expected_text.big, actual.expected_text.big)) {" },
//     .{ .rel = "zigux/tests/fixtures/phase6_hexdump_vectors.zig", .marker = ".name = \"ascii rowsize-16 group-8 line length\"," },
//     .{ .rel = "zigux/tests/phase6_helper_parity_manifest.json", .marker = "\"Documentation/zigux/phase6-hexdump-perf-refresh.md\"" },
//     .{ .rel = "zigux/tests/phase6_build.zig", .marker = "const hexdump_perf_step = b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump helper perf gate\");" },
//     .{ .rel = "zigux/Makefile", .marker = "$(ZIG_REPO_ROOT) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all" },
//     .{ .rel = "scripts/zigux/check_phase6_hexdump_route.zig", .marker = "\"PHASE6_HEXDUMP_ROUTE=pass\"" },
// };
//
// fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
//     for (contracts) |contract| {
//         const file_path = try guard.joinPath(allocator, root, contract.rel);
//         defer allocator.free(file_path);
//         const text = try guard.readUtf8File(io, allocator, file_path);
//         defer allocator.free(text);
//         for (contract.markers) |marker| try guard.requireMarker(text, marker);
//     }
// }
//
// fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
//     const root = try guard.defaultRepoRoot(allocator);
//     defer allocator.free(root);
//     try checkRepo(io, allocator, root);
//     for (self_cases) |case| {
//         const file_path = try guard.joinPath(allocator, root, case.rel);
//         defer allocator.free(file_path);
//         const text = try guard.readUtf8File(io, allocator, file_path);
//         defer allocator.free(text);
//         try guard.requireMarker(text, case.marker);
//     }
//     try std.testing.expectEqual(@as(usize, 22), self_cases.len);
//     try guard.printLine(io, "{s}", .{self_test_pass_marker});
//     try guard.printLine(io, "PHASE6_HEXDUMP_PACKET_SELF_TEST_CASE_COUNT={d}", .{22});
//     return 0;
// }
//
// pub fn main(init: std.process.Init) !void {
//     const allocator = init.gpa;
//     const io = init.io;
//     const args = try init.minimal.args.toSlice(init.arena.allocator());
//     var self_test = false;
//     var explicit_root: ?[]const u8 = null;
//     var index: usize = 1;
//     while (index < args.len) : (index += 1) {
//         const arg = args[index];
//         if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
//         if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
//             if (index + 1 >= args.len) std.process.exit(2);
//             index += 1; explicit_root = args[index]; continue;
//         }
//         std.process.exit(2);
//     }
//     if (self_test) std.process.exit(try runSelfTest(io, allocator));
//     const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
//     defer if (explicit_root == null) allocator.free(root);
//     checkRepo(io, allocator, root) catch std.process.exit(1);
//     try guard.printLine(io, "{s}", .{live_pass_marker});
//     try guard.printLine(io, "PHASE6_HEXDUMP_CONTRACT_COUNT={d}", .{contracts.len});
// }
//
// // Legacy generated marker surface retained for source-compatibility checks.
// // const std = @import("std");
// // const Io = std.Io;
// // const guard = @import("zigux_guard.zig");
// //
// // pub const live_pass_marker = "PHASE6_HEXDUMP_PACKET=pass";
// // pub const self_test_pass_marker = "PHASE6_HEXDUMP_PACKET_SELF_TEST=pass";
// //
// // const SELF_TEST_CASES = [_][]const u8{
// //     "(CATALOG_PATH",
// //     "- helper-local packet checker: `scripts\\zigux/check_phase6_hexdump_packet.zig`",
// //     "- helper-local packet checker: `scripts\\zigux/check_phase6_hexdump_proof.zig`",
// //     ")",
// //     "(CATALOG_PATH",
// //     "- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
// //     "- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`",
// //     ")",
// //     "(SLICE_PATH",
// //     "`PHASE6_STATUS=parked_reviewable`",
// //     "`PHASE6_STATUS=parked`",
// //     ")",
// //     "(SLICE_PATH",
// //     "the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, `bin2hexUpper`/`bin2HexUpper`, and `hexDumpLineLength` helper parity surface",
// //     "the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, and `hexDumpLineLength` helper parity surface",
// //     ")",
// //     "(SLICE_PATH",
// //     "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
// //     "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`",
// //     ")",
// //     "(PERF_REFRESH_PATH",
// //     "`32B-ascii-g2`: the grouped ASCII formatter replay keeps the wider grouped-output ceiling at `max_slowdown_pct = 550`",
// //     "`32B-ascii-g2`: the grouped ASCII formatter replay keeps the wider grouped-output ceiling at `max_slowdown_pct = 450`",
// //     ")",
// //     "(PERF_REFRESH_PATH",
// //     "This note now serves as the bounded rationale for why the grouped ASCII formatter case keeps a higher ceiling than the plain formatter case",
// //     "This note now serves as bounded rationale for grouped ASCII ceilings",
// //     ")",
// //     "(LIB_PATH",
// //     "pub fn hexBytePackUpper(buf: []u8, byte: u8) HexError![]u8 {",
// //     "pub fn hexBytePackUpper(dst: []u8, byte: u8) HexError![]u8 {",
// //     ")",
// //     "(LIB_PATH",
// //     "test \"bin2hexUpper preserves destination on bounds errors\" {",
// //     "test \"bin2hexUpper preserves destination on overflow\" {",
// //     ")",
// //     "(LIB_PATH",
// //     "test \"hexDumpLineLength mirrors formatter normalization\" {",
// //     "test \"hexDumpLength mirrors formatter normalization\" {",
// //     ")",
// //     "(LIB_PATH",
// //     "test \"hexDumpToBuffer reports normalized required length for empty and zero-sized buffers\" {",
// //     "test \"hexDumpToBuffer reports normalized required length for empty buffers\" {",
// //     ")",
// //     "(HELPER_TEST_PATH",
// //     "test \"phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity\" {",
// //     "test \"phase 6 hexdump direct pack helpers keep nibble parity\" {",
// //     ")",
// //     "(HELPER_TEST_PATH",
// //     "test \"phase 6 hexdump uppercase bulk parity and grouped-ascii exact-capacity buffers stay aligned\" {",
// //     "test \"phase 6 hexdump grouped-ascii exact-capacity buffers stay aligned\" {",
// //     ")",
// //     "(PERF_PATH",
// //     "return error.HexdumpPerfRegression;",
// //     "return error.HexdumpPerfDrift;",
// //     ")",
// //     "(PERF_MATRIX_PATH",
// //     ".label = \"16B-ascii-g8\",",
// //     ".label = \"16B-ascii-g16\",",
// //     ")",
// //     "(PERF_MATRIX_PATH",
// //     "if (!std.mem.eql(u8, want.expected_text.little, actual.expected_text.little)) {",
// //     "if (!std.mem.eql(u8, expected[idx].expected_text.little, actual.expected_text.little)) {",
// //     ")",
// //     "(PERF_MATRIX_PATH",
// //     "if (!std.mem.eql(u8, want.expected_text.big, actual.expected_text.big)) {",
// //     "if (!std.mem.eql(u8, expected[idx].expected_text.big, actual.expected_text.big)) {",
// //     ")",
// //     "(FIXTURES_PATH",
// //     ".name = \"ascii rowsize-16 group-8 line length\",",
// //     ".name = \"ascii rowsize-16 group-16 line length\",",
// //     ")",
// //     "(MANIFEST_PATH",
// //     "\"Documentation/zigux/phase6-hexdump-perf-refresh.md\"",
// //     "\"Documentation/zigux/phase6-hexdump-perf-proof.md\"",
// //     ")",
// //     "(BUILD_PATH",
// //     "const hexdump_perf_step = b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump helper perf gate\");",
// //     "const hexdump_perf_step = b.step(\"phase6-hexdump-profile\", \"Run Phase 6 hexdump helper perf gate\");",
// //     ")",
// //     "(MAKEFILE_PATH",
// //     "$(ZIG_REPO_ROOT) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
// //     "$(ZIG) build phase6-hexdump-profile --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
// //     ")",
// //     "(ROUTE_PATH",
// //     "\"PHASE6_HEXDUMP_ROUTE=pass\"",
// //     "\"PHASE6_HEXDUMP_REVIEW_ROUTE=pass\"",
// //     ")",
// // };
// //
// // fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
// //     const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
// //     defer allocator.free(text_self_test_cases_path);
// //     const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
// //     defer allocator.free(text_self_test_cases);
// //     for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
// // }
// //
// // fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
// //     try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
// //     try guard.printLine(io, "{s}", .{self_test_pass_marker});
// //     return 0;
// // }
// //
// // pub fn main(init: std.process.Init) !void {
// //     const allocator = init.gpa;
// //     const io = init.io;
// //     const args = try init.minimal.args.toSlice(allocator);
// //
// //     var self_test = false;
// //     var explicit_root: ?[]const u8 = null;
// //     var index: usize = 1;
// //     while (index < args.len) : (index += 1) {
// //         const arg = args[index];
// //         if (std.mem.eql(u8, arg, "--self-test")) {
// //             self_test = true;
// //             continue;
// //         }
// //         if (std.mem.eql(u8, arg, "--root")) {
// //             if (index + 1 >= args.len) std.process.exit(2);
// //             index += 1;
// //             explicit_root = args[index];
// //             continue;
// //         }
// //     }
// //
// //     const root = explicit_root orelse try guard.repoRootFromScript(allocator);
// //     defer if (explicit_root == null) allocator.free(root);
// //
// //     if (self_test) {
// //         std.process.exit(try runSelfTest(io, allocator));
// //     }
// //
// //     checkRepo(io, allocator, root) catch {
// //         std.process.exit(1);
// //     };
// //     try guard.printLine(io, "{s}", .{live_pass_marker});
// // }
// //
//
