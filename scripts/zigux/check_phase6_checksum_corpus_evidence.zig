const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_CHECKSUM_CORPUS_EVIDENCE=pass";
pub const self_test_pass_marker = "PHASE6_CHECKSUM_CORPUS_EVIDENCE_SELF_TEST=pass";

const SELF_TEST_CASES = [_][]const u8{
    "(SLICE_PATH",
    "- the same perf replay also keeps `ipFastCsum()` honest through committed `IPV4_20B`, `IPV4_20B_UPDATED`, `IPV4_24B`, and `IPV4_60B` aligned-header cases that compare the fast path directly against `compute()`",
    "- the same perf replay also keeps `ipFastCsum()` honest through committed `IPV4_20B`, `IPV4_24B`, and `IPV4_60B` aligned-header cases that compare the fast path directly against `compute()`",
    ")",
    "(CATALOG_PATH",
    "- direct C parity companions: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts\\zigux/check_phase6_checksum_c_parity.zig`",
    "- direct C parity companions: `zigux/tests/phase6_checksum_c_parity.zig` and `scripts\\zigux/check_phase6_checksum_c_parity.zig`",
    ")",
    "(HELPER_EVIDENCE_MANIFEST_PATH",
    "\"IPV4_20B_UPDATED\"",
    "\"IPV4_20B_REFRESHED\"",
    ")",
    "(HELPER_PARITY_MANIFEST_PATH",
    "\"IPV4_20B_UPDATED\"",
    "\"IPV4_20B_REFRESHED\"",
    ")",
    "(LIB_PATH",
    "pub fn ipFastCsum(header: []const u8) u16 {",
    "pub fn ipChecksumFast(header: []const u8) u16 {",
    ")",
    "(HELPER_TEST_PATH",
    "test \"phase 6 checksum pseudo-header helpers keep high-length IPv6 carries visible\" {",
    "test \"phase 6 checksum IPv6 pseudo-header helpers keep high-length carries visible\" {",
    ")",
    "(PERF_TEST_PATH",
    "std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n\", .{fixtures.fast_path_cases.len});",
    "std.debug.print(\"PHASE6_CHECKSUM_FAST_PATH_CASE_COUNT={d}\\n\", .{fixtures.fast_path_cases.len});",
    ")",
    "(FIXTURES_PATH",
    ".{ .label = \"IPV4_20B_UPDATED\", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 },",
    ".{ .label = \"IPV4_20B_REFRESHED\", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 },",
    ")",
    "(BUILD_PATH",
    "\"phase6-checksum-perf-matrix-test\",",
    "\"phase6-checksum-matrix-test\",",
    ")",
    "(MAKEFILE_PATH",
    "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "$(ZIG) build phase6-checksum-profile --build-file zigux/tests/phase6_build.zig --summary all",
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
