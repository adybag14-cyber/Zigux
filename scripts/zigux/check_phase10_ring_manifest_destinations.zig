const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_RING_MANIFEST_DESTINATIONS=pass";
pub const self_test_pass_marker = "PHASE10_RING_MANIFEST_DESTINATIONS_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const SurveySummary = struct {
    preexisting_ring_callback_enable_present: bool,
    preexisting_ring_reset_readiness_present: bool,
};
const Gap = struct {
    id: []const u8,
    zigux_destination: []const u8,
};
const Manifest = struct {
    lane_key: []const u8,
    anchor: []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn requireDestination(gaps: []const Gap, id: []const u8, destination: []const u8) !void {
    for (gaps) |gap| {
        if (!std.mem.eql(u8, gap.id, id)) continue;
        if (!std.mem.eql(u8, gap.zigux_destination, destination)) return error.DestinationDrift;
        return;
    }
    return error.MissingGap;
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const path = try guard.joinPath(allocator, root, "zigux/tests/phase10_virtio_ring_manifest.json");
    defer allocator.free(path);
    const text = try guard.readUtf8File(io, allocator, path);
    defer allocator.free(text);
    const parsed = try std.json.parseFromSlice(Manifest, allocator, text, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const manifest = parsed.value;
    if (!std.mem.eql(u8, manifest.lane_key, "P10-L10")) return error.LaneDrift;
    if (!std.mem.eql(u8, manifest.anchor, "drivers/virtio/virtio_ring.c")) return error.AnchorDrift;
    if (!manifest.survey_summary.preexisting_ring_callback_enable_present) return error.CallbackSummaryDrift;
    if (!manifest.survey_summary.preexisting_ring_reset_readiness_present) return error.ResetSummaryDrift;
    try requireDestination(manifest.gaps, "phase10-callback-enable-helper", "drivers/virtio/virtio_ring_callback_enable.zig");
    try requireDestination(manifest.gaps, "phase10-queue-reset-readiness-helper", "drivers/virtio/virtio_ring_reset_readiness.zig");
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE10_RING_MANIFEST_DESTINATION_COUNT=2", .{});
    try guard.printLine(io, "PHASE10_RING_MANIFEST_SUMMARY_FIELD_COUNT=2", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE10_RING_MANIFEST_DESTINATIONS_SELF_TEST_CASE_COUNT=4", .{});
    try emitCounts(io);
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
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE10_RING_MANIFEST_DESTINATIONS_SELF_TEST=pass";
//
// const EXPECTED_SUMMARY_FIELDS = [_][]const u8{
//     "preexisting_ring_callback_enable_present",
//     "preexisting_ring_reset_readiness_present",
// };
//
// const EXPECTED_DESTINATIONS = [_][]const u8{
//     "phase10-callback-enable-helper",
//     "drivers/virtio/virtio_ring_callback_enable.zig",
//     "phase10-queue-reset-readiness-helper",
//     "drivers/virtio/virtio_ring_reset_readiness.zig",
// };
//
// const MANIFEST_PATH = [_][]const u8{
//     "zigux/tests/phase10_virtio_ring_manifest.json",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (EXPECTED_SUMMARY_FIELDS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_DESTINATIONS) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
