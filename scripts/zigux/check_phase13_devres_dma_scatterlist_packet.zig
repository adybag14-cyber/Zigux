const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{CHECK_NAME}_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Documentation/zigux/phase13-devres-survey.md",
    "PHASE13_SLICE=devres-dma-scatterlist-boundary-survey",
    "phase13-devres-dmam-alloc-coherent-planner-note",
    "phase13-devres-dmam-alloc-coherent-planner-manifest",
    "phase13-devres-scatterlist-helper",
    "phase13-devres-scatterlist-replay",
    "blocked `phase13-devres-live-scatterlist-ownership`",
    "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md",
    "pure `dmam_alloc_coherent()` planning surface",
    "detach-time cleanup intent",
    "avoid retaining detach-time cleanup ownership",
    "does not treat the replay as proof",
    "dma_map_*",
    "dma_unmap_*",
    "dma_sync_*",
    "dma_mmap_*",
    "dma_map_sgtable()",
    "struct scatterlist",
    "sg_table",
    "sg_*",
    "zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json",
    "\"lane_key\": \"P13-L08\"",
    "\"packet\": \"phase13-devres-dmam-alloc-coherent-planner\"",
    "\"status\": \"planning_only\"",
    "\"id\": \"phase13-devres-live-dmam-alloc-side-effects\"",
    "\"status\": \"blocked_on_dma_state\"",
    "\"id\": \"phase13-devres-live-scatterlist-ownership\"",
    "\"status\": \"blocked_on_scatterlist_state\"",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "test \"phase13 devres dma coherent replay records blocked dma and scatterlist boundaries\"",
    "test \"phase13 devres dma coherent replay anchors the current slice reality\"",
    "test \"phase13 devres dma coherent replay keeps missing checker surfaces framed as gaps\"",
    "test \"phase13 devres dma coherent replay keeps the planner note helper-first\"",
    "lib/devres_scatterlist.zig",
    "provides_scatterlist_lifetime_planning = true",
    "touches_live_dma = false",
    "touches_live_scatterlist = false",
    "pub fn planManagedScatterlistMap",
    "pub fn planManagedScatterlistUnmap",
    "zigux/tests/phase13_devres_scatterlist.zig",
    "test \"phase13 devres descriptor records helper-first scatterlist planning\"",
    "test \"phase13 devres retains the release record when helper-first scatterlist planning succeeds\"",
    "test \"phase13 devres rejects scatterlist planning when the release record cannot be allocated\"",
    "test \"phase13 devres scatterlist release matching stays exact across original and mapped counts\"",
};

const CHECK_NAME = [_][]const u8{
    "PHASE13_DEVRES_DMA_SCATTERLIST_PACKET",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CHECK_NAME) |marker| try guard.requireMarker(text, marker);
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
