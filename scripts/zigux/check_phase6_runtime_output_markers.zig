const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_RUNTIME_OUTPUT_MARKERS=pass";
pub const self_test_pass_marker = "PHASE6_RUNTIME_OUTPUT_MARKERS_SELF_TEST=pass";

const EXPECTED_CHECKSUM_PAYLOAD_LABELS = [_][]const u8{
    "64B",
    "1501B",
};

const EXPECTED_CHECKSUM_FAST_PATH_LABELS = [_][]const u8{
    "IPV4_20B",
    "IPV4_20B_UPDATED",
    "IPV4_24B",
    "IPV4_60B",
};

const EXPECTED_HEXDUMP_LABELS = [_][]const u8{
    "16B-plain-g1",
    "32B-ascii-g2",
    "16B-ascii-g4",
    "16B-ascii-g8",
};

const CHECKSUM_PAYLOAD_FIELDS = [_][]const u8{
    "ITERATIONS",
    "HELPER_NS",
    "REFERENCE_NS",
    "SLOWDOWN_PCT",
    "THRESHOLD_PCT",
    "CHECKSUM",
};

const CHECKSUM_FAST_PATH_FIELDS = [_][]const u8{
    "ITERATIONS",
    "HELPER_NS",
    "COMPUTE_NS",
    "SLOWDOWN_PCT",
    "THRESHOLD_PCT",
    "CHECKSUM",
};

const HEXDUMP_FIELDS = [_][]const u8{
    "ITERATIONS",
    "HELPER_NS",
    "REFERENCE_NS",
    "SLOWDOWN_PCT",
    "THRESHOLD_PCT",
    "ACCUMULATOR",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_checksum_payload_labels_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_checksum_perf.zig");
    defer allocator.free(text_expected_checksum_payload_labels_path);
    const text_expected_checksum_payload_labels = try guard.readUtf8File(io, allocator, text_expected_checksum_payload_labels_path);
    defer allocator.free(text_expected_checksum_payload_labels);
    for (EXPECTED_CHECKSUM_PAYLOAD_LABELS) |marker| try guard.requireMarker(text_expected_checksum_payload_labels, marker);
    const text_expected_checksum_fast_path_labels_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_checksum_perf.zig");
    defer allocator.free(text_expected_checksum_fast_path_labels_path);
    const text_expected_checksum_fast_path_labels = try guard.readUtf8File(io, allocator, text_expected_checksum_fast_path_labels_path);
    defer allocator.free(text_expected_checksum_fast_path_labels);
    for (EXPECTED_CHECKSUM_FAST_PATH_LABELS) |marker| try guard.requireMarker(text_expected_checksum_fast_path_labels, marker);
    const text_expected_hexdump_labels_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_checksum_perf.zig");
    defer allocator.free(text_expected_hexdump_labels_path);
    const text_expected_hexdump_labels = try guard.readUtf8File(io, allocator, text_expected_hexdump_labels_path);
    defer allocator.free(text_expected_hexdump_labels);
    for (EXPECTED_HEXDUMP_LABELS) |marker| try guard.requireMarker(text_expected_hexdump_labels, marker);
    const text_checksum_payload_fields_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_checksum_perf.zig");
    defer allocator.free(text_checksum_payload_fields_path);
    const text_checksum_payload_fields = try guard.readUtf8File(io, allocator, text_checksum_payload_fields_path);
    defer allocator.free(text_checksum_payload_fields);
    for (CHECKSUM_PAYLOAD_FIELDS) |marker| try guard.requireMarker(text_checksum_payload_fields, marker);
    const text_checksum_fast_path_fields_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_checksum_perf.zig");
    defer allocator.free(text_checksum_fast_path_fields_path);
    const text_checksum_fast_path_fields = try guard.readUtf8File(io, allocator, text_checksum_fast_path_fields_path);
    defer allocator.free(text_checksum_fast_path_fields);
    for (CHECKSUM_FAST_PATH_FIELDS) |marker| try guard.requireMarker(text_checksum_fast_path_fields, marker);
    const text_hexdump_fields_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_checksum_perf.zig");
    defer allocator.free(text_hexdump_fields_path);
    const text_hexdump_fields = try guard.readUtf8File(io, allocator, text_hexdump_fields_path);
    defer allocator.free(text_hexdump_fields);
    for (HEXDUMP_FIELDS) |marker| try guard.requireMarker(text_hexdump_fields, marker);
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
