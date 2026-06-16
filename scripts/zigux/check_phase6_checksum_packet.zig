const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_CHECKSUM_PACKET=pass";
pub const self_test_pass_marker = "PHASE6_CHECKSUM_PACKET_SELF_TEST=pass";

const SELF_TEST_CASES = [_][]const u8{
    "(SLICE_PATH",
    "`PHASE6_SLICE=checksum-leaf-helper`",
    "`PHASE6_SLICE=checksum`)",
    "(SLICE_PATH",
    "`zigux/tests/phase6_checksum_perf.zig`",
    "`zigux/tests/phase6_checksum.zig`)",
    "(LIB_PATH",
    "pub fn ipFastCsum(header: []const u8) u16 {",
    "pub fn ipFastCsumAligned(header: []const u8) u16 {)",
    "(LIB_PATH",
    "test \"pseudo-header helpers match direct checksum recomputation over pseudo-header bytes and payload\" {",
    "test \"pseudo-header helpers match checksum recomputation\" {)",
    "(HELPER_TEST_PATH",
    "test \"phase 6 checksum helper packet keeps aligned IPv4 fast paths and carry helpers reviewable\" {",
    "test \"phase 6 checksum helper packet keeps IPv4 fast paths reviewable\" {)",
    "(PERF_PATH",
    "fn validateFastPathMatrix() !void {",
    "fn validateFastPathCases() !void {)",
    "(PERF_PATH",
    "std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n\", .{fixtures.fast_path_cases.len});",
    "std.debug.print(\"PHASE6_CHECKSUM_FAST_PATH_CASE_COUNT={d}\\n\", .{fixtures.fast_path_cases.len});)",
    "(FIXTURES_PATH",
    ".{ .label = \"1501B\", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },",
    ".{ .label = \"1500B\", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },)",
    "(FIXTURES_PATH",
    ".{ .label = \"IPV4_60B\", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },",
    ".{ .label = \"IPV4_64B\", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },)",
    "(C_PARITY_PATH",
    "std.debug.print(\"PHASE6_CHECKSUM_C_PARITY=pass\\n\", .{});",
    "std.debug.print(\"PHASE6_CHECKSUM_PARITY=pass\\n\", .{});)",
    "(C_HARNESS_PATH",
    "uint16_t zigux_phase6_checksum_ip_fast_csum",
    "uint16_t zigux_phase6_checksum_fast_csum)",
    "(C_PARITY_CHECKER_PATH",
    "print(\"PHASE6_CHECKSUM_C_PARITY=pass\")",
    "print(\"PHASE6_CHECKSUM_PARITY=pass\"))",
    "(CORPUS_CHECKER_PATH",
    "print(\"PHASE6_CHECKSUM_CORPUS_EVIDENCE=pass\")",
    "print(\"PHASE6_CHECKSUM_CORPUS=pass\"))",
    "(BUILD_PATH",
    "const checksum_perf_step = b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum helper perf gate\");",
    "const checksum_profile_step = b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum helper perf gate\");)",
    "(MAKEFILE_PATH",
    "phase6-checksum-perf-matrix-test:",
    "phase6-checksum-perf-test:)",
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
