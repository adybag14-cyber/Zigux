const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_LIBFS_PACKET_SELF_TEST=pass";

const SURVEY_STATIC_MARKERS = [_][]const u8{
    "`PHASE13_SLICE=libfs-helper-filesystem-boundary-survey`",
    "`fs/libfs.zig`",
    "`fs/libfs_dcache_cursor.zig`",
    "`zigux/tests/phase13_libfs.zig`",
    "`zigux/tests/phase13_libfs_reviewability.zig`",
    "`zigux/tests/phase13_libfs_dcache_cursor.zig`",
    "`zigux/tests/phase13_libfs_manifest.json`",
    "`zigux/tests/phase13_libfs_dcache_cursor_manifest.json`",
    "`Documentation/zigux/phase13-libfs-dcache-cursor-planner.md`",
    "`scripts/zigux/check_phase13_libfs_packet.zig`",
    "`scripts/zigux/check_phase13_libfs_dcache_cursor_packet.zig`",
    "simple_offset_add()",
    "simple_offset_remove()",
    "simple_transaction_get()",
    "simple_transaction_set()",
    "simple_transaction_release()",
    "generic_check_addressable()",
    "offset-based rename plus rename-exchange planning",
    "`dcache_dir_open()` and `dcache_readdir()` cursor preconditions reviewable",
    "shared `zigux/tests/phase13_build.zig` route",
};

const HELPER_MARKERS = [_][]const u8{
    ".provides_offset_add_planning = true",
    ".provides_offset_remove_planning = true",
    ".provides_offset_readdir_planning = true",
    ".provides_transaction_release_planning = true",
    ".provides_directory_scan_resched_planning = true",
    "pub const TransactionReleasePlan",
    "pub fn simpleTransactionReleasePlan(",
    "pub fn planSimpleOffsetAdd(",
    "pub fn planSimpleOffsetRemove(",
    "pub fn planSimpleOffsetRename(",
    "pub fn planSimpleOffsetRenameExchange(",
    "pub fn genericCheckAddressablePlan(",
    "pub fn planOffsetReaddir(",
};

const REPLAY_STATIC_MARKERS = [_][]const u8{
    "phase13 libfs manifest records the current helper-first filesystem packet",
    "\"phase13-libfs-offset-remove-planner\"",
    "\"phase13-libfs-offset-rename-planner\"",
    "\"phase13-libfs-transaction-release-helper\"",
    "\"phase13-libfs-addressability-helper\"",
    "simple_transaction_release()",
    "offset remove planning",
    "live dcache entry insertion",
};

const REVIEWABILITY_MARKERS = [_][]const u8{
    "descriptor keeps the current bounded helper surface explicit",
    "transaction release planner stays helper-only and unconditional-zero",
    "offset remove planning stays reviewable as erase-only lifecycle bookkeeping",
    "offset rename exchange planning keeps managed-slot swap and rollback expectations explicit",
    "addressability planner stays reviewable without implying live page-cache ownership",
};

const EXPECTED_GAPS = [_][]const u8{
    "phase13-libfs-helper-starter",
    "starter_landed",
    "phase13-libfs-offset-add-planner",
    "starter_landed",
    "phase13-libfs-offset-remove-planner",
    "starter_landed",
    "phase13-libfs-offset-rename-planner",
    "starter_landed",
    "phase13-libfs-transaction-acquire-helper",
    "starter_landed",
    "phase13-libfs-transaction-release-helper",
    "starter_landed",
    "phase13-libfs-transaction-publish-helper",
    "starter_landed",
    "phase13-libfs-addressability-helper",
    "starter_landed",
    "phase13-libfs-reviewability-gate",
    "starter_landed",
    "phase13-libfs-survey-note",
    "starter_landed",
    "phase13-libfs-dcache-cursor-precondition-planner",
    "starter_landed",
    "phase13-build-gate",
    "blocked_on_shared_build_surface",
    "phase13-libfs-live-dcache-mutation",
    "blocked_on_dcache_state",
    "phase13-libfs-live-inode-state",
    "blocked_on_inode_state",
    "phase13-libfs-live-cursor-traversal",
    "blocked_on_dcache_state",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase13_libfs_manifest.json",
};

const SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase13-libfs-survey.md",
};

const HELPER_PATH = [_][]const u8{
    "fs/libfs.zig",
};

const REPLAY_PATH = [_][]const u8{
    "zigux/tests/phase13_libfs.zig",
};

const REVIEWABILITY_PATH = [_][]const u8{
    "zigux/tests/phase13_libfs_reviewability.zig",
};

const FIXTURE_COMMIT = [_][]const u8{
    "master-readback-2026-05-27",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SURVEY_STATIC_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REPLAY_STATIC_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REVIEWABILITY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GAPS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (HELPER_PATH) |marker| try guard.requireMarker(text, marker);
    for (REPLAY_PATH) |marker| try guard.requireMarker(text, marker);
    for (REVIEWABILITY_PATH) |marker| try guard.requireMarker(text, marker);
    for (FIXTURE_COMMIT) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
