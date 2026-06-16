const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_OWNERSHIP_MATRIX=pass";
pub const self_test_pass_marker = "PHASE4_OWNERSHIP_MATRIX_SELF_TEST=pass";

const EXPECTED_PERF_COORDINATION_OWNERS = [_][]const u8{
    "ABI and Runtime Team",
    "Shared Subsystems Pod",
};

const EXPECTED_PROMOTION_STATUS = [_][]const u8{
    "shared CI perf promotion pending",
};

const EXPECTED_PERF_ROW_THRESHOLD = [_][]const u8{
    "approved_local_only_for_atomic64_and_bitmap_commands_shared_ci_perf_promotion_pending",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_perf_coordination_owners_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_expected_perf_coordination_owners_path);
    const text_expected_perf_coordination_owners = try guard.readUtf8File(io, allocator, text_expected_perf_coordination_owners_path);
    defer allocator.free(text_expected_perf_coordination_owners);
    for (EXPECTED_PERF_COORDINATION_OWNERS) |marker| try guard.requireMarker(text_expected_perf_coordination_owners, marker);
    const text_expected_promotion_status_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_expected_promotion_status_path);
    const text_expected_promotion_status = try guard.readUtf8File(io, allocator, text_expected_promotion_status_path);
    defer allocator.free(text_expected_promotion_status);
    for (EXPECTED_PROMOTION_STATUS) |marker| try guard.requireMarker(text_expected_promotion_status, marker);
    const text_expected_perf_row_threshold_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_expected_perf_row_threshold_path);
    const text_expected_perf_row_threshold = try guard.readUtf8File(io, allocator, text_expected_perf_row_threshold_path);
    defer allocator.free(text_expected_perf_row_threshold);
    for (EXPECTED_PERF_ROW_THRESHOLD) |marker| try guard.requireMarker(text_expected_perf_row_threshold, marker);
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
