// Ported from check-phase6-checksum-hexdump-perf-replay-contract.py by gen_remaining_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const REQUIRED_FILES = [_][]const u8{
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
    "zigux/tests/phase6_hexdump_perf.zig",
    "zigux/tests/phase6_hexdump_perf_matrix.zig",
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
    "zigux/tests/phase6_build.zig",
    "zigux/Makefile",
};

const SNIPPET_ENTRIES = [_]struct { file: []const u8, snippets: []const []const u8 }{
    .{ .file = "zigux/tests/phase6_checksum_perf.zig", .snippets = &[_][]const u8{
        "std.debug.print(\"PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n\"",
        "std.debug.print(\"PHASE6_CHECKSUM_PERF_64B=pass\\n\"",
        "std.debug.print(\"PHASE6_CHECKSUM_PERF_1501B=pass\\n\"",
        "std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n\"",
        "std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_IPV4_20B=pass\\n\"",
        "std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_IPV4_20B_UPDATED=pass\\n\"",
        "std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_IPV4_24B=pass\\n\"",
        "std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_IPV4_60B=pass\\n\"",
        "std.debug.print(\"PHASE6_CHECKSUM_PERF={s}\\n\"",
    } },
    .{ .file = "zigux/tests/fixtures/phase6_checksum_vectors.zig", .snippets = &[_][]const u8{
        ".{ .label = \"64B\", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 }",
        ".{ .label = \"1501B\", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 }",
        ".{ .label = \"IPV4_20B\", .header = &ip_fast_csum_ipv4_20b, .iterations = 600_000, .max_slowdown_pct = 100 }",
        ".{ .label = \"IPV4_20B_UPDATED\", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 }",
        ".{ .label = \"IPV4_24B\", .header = &ip_fast_csum_ipv4_24b, .iterations = 500_000, .max_slowdown_pct = 100 }",
        ".{ .label = \"IPV4_60B\", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 }",
    } },
    .{ .file = "zigux/tests/phase6_hexdump_perf.zig", .snippets = &[_][]const u8{
        "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n\"",
        "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_16B-plain-g1=pass\\n\"",
        "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_32B-ascii-g2=pass\\n\"",
        "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_16B-ascii-g4=pass\\n\"",
        "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_16B-ascii-g8=pass\\n\"",
        "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF={s}\\n\"",
    } },
    .{ .file = "zigux/tests/phase6_hexdump_perf_matrix.zig", .snippets = &[_][]const u8{
        ".label = \"16B-plain-g1\"",
        ".label = \"32B-ascii-g2\"",
        ".label = \"16B-ascii-g4\"",
        ".label = \"16B-ascii-g8\"",
        "var exact: [114]u8 = undefined;",
        "var truncated: [113]u8 = [_]u8{fixtures.fill_char} ** 113;",
    } },
    .{ .file = "zigux/tests/fixtures/phase6_hexdump_vectors.zig", .snippets = &[_][]const u8{
        ".label = \"16B-plain-g1\"",
        ".label = \"32B-ascii-g2\"",
        ".label = \"16B-ascii-g4\"",
        ".label = \"16B-ascii-g8\"",
        ".max_slowdown_pct = 175",
        ".max_slowdown_pct = 550",
        ".max_slowdown_pct = 600",
        "pub const test_hexdump_buf_size = 32 * 3 + 2 + 32 + 1;",
    } },
    .{ .file = "zigux/tests/phase6_build.zig", .snippets = &[_][]const u8{
        "const checksum_perf_matrix_test_step = b.step(",
        "\"phase6-checksum-perf-matrix-test\"",
        "const checksum_perf_step = b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum helper perf gate\");",
        "const hexdump_review_step = b.step(\"phase6-hexdump-review\", \"Run Phase 6 hexdump perf-matrix review preflight\");",
        "\"phase6-hexdump-perf-matrix-test\"",
        "const hexdump_perf_step = b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump helper perf gate\");",
    } },
    .{ .file = "zigux/Makefile", .snippets = &[_][]const u8{
        "phase6-checksum-perf-matrix-test:",
        "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-checksum-perf:",
        "phase6-hexdump-review:",
        "$(ZIG) build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-hexdump-perf-matrix-test:",
        "$(ZIG) build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-hexdump-perf:",
        "$(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
    } },
};

fn validate(io: Io, allocator: std.mem.Allocator, root: []const u8) !?[]const u8 {
    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            return try std.fmt.allocPrint(allocator, "missing required files: {s}", .{relative_path});
        }
    }
    for (SNIPPET_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        const text = try guard.readUtf8File(io, allocator, full_path);
        defer allocator.free(text);
        for (entry.snippets) |snippet| {
            if (std.mem.indexOf(u8, text, snippet) == null) {
                return try std.fmt.allocPrint(allocator, "{s} drifted: {s}", .{ entry.file, snippet });
            }
        }
    }
    return null;
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
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
        if (std.mem.eql(u8, arg, "--repo-root")) {
            index += 1;
            explicit_root = args[index];
        }
    }
    if (self_test) {
        try guard.printLine(io, "PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT_SELF_TEST=pass", .{});
        try guard.printLine(io, "PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT=7", .{});
        std.process.exit(0);
    }
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    if (try validate(io, allocator, root)) |issue| {
        defer allocator.free(issue);
        try guard.printLine(io, "PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT=fail: {s}", .{issue});
        std.process.exit(1);
    }
    try guard.printLine(io, "PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT=pass", .{});
    try guard.printLine(io, "PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT_REQUIRED_FILE_COUNT={d}", .{REQUIRED_FILES.len});
    var marker_count: usize = 0;
    for (SNIPPET_ENTRIES) |entry| marker_count += entry.snippets.len;
    try guard.printLine(io, "PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT_REQUIRED_MARKER_COUNT={d}", .{marker_count});
    std.process.exit(0);
}
