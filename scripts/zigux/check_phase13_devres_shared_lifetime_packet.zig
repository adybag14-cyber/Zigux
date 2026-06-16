const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_SHARED_LIFETIME_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "SLICE_PATH",
    "SURVEY_PATH",
    "PLANNER_NOTE_PATH",
    "PLANNER_REPLAY_PATH",
    "PLANNER_MANIFEST_PATH",
    "DMA_REPLAY_PATH",
    "SCATTERLIST_HELPER_PATH",
    "SCATTERLIST_REPLAY_PATH",
};

const SLICE_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase13-devres-survey.md` now records the current DMA and scatterlist boundary",
    "`lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, and `zigux/tests/phase13_devres_manifest.json` remain repo-reality gaps",
    "`scripts/zigux/check_phase13_devres_packet_alignment.zig` stays in the same repo-reality gaps bucket",
    "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only",
    "The bounded current evidence is the survey note, the direct DMA-boundary replay, the planning-only `dmam_alloc_coherent()` note and manifest, and the helper-first scatterlist helper plus replay",
    "compare those survey, planner, replay, and helper surfaces together on current `master` before widening anything else",
};

const SURVEY_MARKERS = [_][]const u8{
    "reviewed against live `master` `master-readback-2026-05-18`",
    "the docs-side devres slice note, the planning-only `dmam_alloc_coherent()` note and manifest, the direct DMA-boundary replay, the helper-first scatterlist helper and replay, and the roadmap-backed `lib/devres.c` anchor",
    "`lib/devres_scatterlist.zig` now provides a helper-first scatterlist lifetime planner",
    "`zigux/tests/phase13_devres_scatterlist.zig` replays that scatterlist helper surface directly",
    "current `master` does not ship `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, or `scripts/zigux/check_phase13_devres_packet_alignment.zig`",
    "blocked `phase13-devres-live-dmam-alloc-side-effects`",
    "blocked `phase13-devres-live-scatterlist-ownership`",
    "blocked `phase13-devres-live-sg-table-lifecycle`",
    "blocked `phase13-devres-generic-dma-map-family`",
};

const PLANNER_NOTE_MARKERS = [_][]const u8{
    "pure `dmam_alloc_coherent()` planning surface",
    "detach-time cleanup intent",
    "`zigux/tests/phase13_devres_dma_coherent.zig` materialized on current `master`",
    "`lib/devres.zig` itself remains an explicit repo-reality gap",
    "does not treat the replay as proof",
    "dma_map_*",
    "dma_unmap_*",
    "dma_sync_*",
    "dma_mmap_*",
    "dma_map_sgtable()",
    "struct scatterlist",
    "sg_table",
    "sg_*",
    "zig test zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig",
    "zig test zigux/tests/phase13_devres_dma_coherent.zig",
};

const PLANNER_REPLAY_MARKERS = [_][]const u8{
    "test \"phase13 devres dmam_alloc_coherent planner manifest records planning-only dma scope\" {",
    "\"phase13-devres-dmam-alloc-coherent-planner\"",
    "\"planning_only\"",
    "\"phase13-devres-live-dmam-alloc-side-effects\"",
    "\"blocked_on_dma_state\"",
    "\"phase13-devres-live-scatterlist-ownership\"",
    "\"blocked_on_scatterlist_state\"",
    "test \"phase13 devres dmam_alloc_coherent planner note keeps the slice helper-first and bounded\" {",
    "\"detach-time cleanup intent\"",
    "\"`lib/devres.zig` itself remains an explicit repo-reality gap\"",
    "test \"phase13 devres dmam_alloc_coherent planner note preserves standalone replay handles\" {",
};

const PLANNER_MANIFEST_MARKERS = [_][]const u8{
    "\"lane_key\": \"P13-L08\"",
    "\"phase\": \"Phase 13\"",
    "\"surveyed_commit\": \"master-readback-2026-05-17\"",
    "\"anchor\": \"lib/devres.c\"",
    "\"packet\": \"phase13-devres-dmam-alloc-coherent-planner\"",
    "\"status\": \"planning_only\"",
    "\"Documentation/zigux/phase13-devres-slice.md\"",
    "\"Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md\"",
    "\"zigux/tests/phase13_devres_dma_coherent.zig\"",
    "\"pure `dmam_alloc_coherent()` planning surface\"",
    "\"detach-time cleanup intent\"",
    "\"avoid retaining detach-time cleanup ownership\"",
    "\"dma_map_*\"",
    "\"dma_unmap_*\"",
    "\"dma_sync_*\"",
    "\"dma_mmap_*\"",
    "\"dma_map_sgtable()\"",
    "\"struct scatterlist\"",
    "\"sg_table\"",
    "\"sg_*\"",
    "\"id\": \"phase13-devres-live-dmam-alloc-side-effects\"",
    "\"status\": \"blocked_on_dma_state\"",
    "\"id\": \"phase13-devres-live-scatterlist-ownership\"",
    "\"status\": \"blocked_on_scatterlist_state\"",
};

const DMA_REPLAY_MARKERS = [_][]const u8{
    "test \"phase13 devres dma coherent replay records blocked dma and scatterlist boundaries\" {",
    "\"phase13-devres-dmam-alloc-coherent-planner\"",
    "\"phase13-devres-live-dmam-alloc-side-effects\"",
    "\"blocked_on_dma_state\"",
    "\"phase13-devres-live-scatterlist-ownership\"",
    "\"blocked_on_scatterlist_state\"",
    "test \"phase13 devres dma coherent replay anchors the current slice reality\" {",
    "\"`Documentation/zigux/phase13-devres-survey.md`\"",
    "\"`lib/devres.zig`\"",
    "\"repo-reality gaps\"",
    "test \"phase13 devres dma coherent replay keeps missing checker surfaces framed as gaps\" {",
    "\"`scripts/zigux/check_phase13_devres_packet_alignment.zig`\"",
    "\"paired survey, helper, manifest, and broader direct replay packet\"",
    "test \"phase13 devres dma coherent replay anchors the survey-side scatterlist boundary\" {",
    "\"helper-first scatterlist helper and replay\"",
    "\"blocked `phase13-devres-live-sg-table-lifecycle`\"",
    "\"blocked `phase13-devres-generic-dma-map-family`\"",
    "test \"phase13 devres dma coherent replay keeps scatterlist helper evidence helper-first\" {",
    "\".provides_scatterlist_lifetime_planning = true\"",
    "\"phase13 devres scatterlist release matching stays exact across original and mapped counts\"",
};

const SCATTERLIST_HELPER_MARKERS = [_][]const u8{
    "pub const ModuleDescriptor = struct {",
    "provides_scatterlist_lifetime_planning: bool,",
    "touches_live_dma: bool,",
    "touches_live_scatterlist: bool,",
    "pub const ManagedScatterlistMapResult = struct {",
    "pub const ManagedScatterlistUnmapPlan = struct {",
    ".name = \"devres_scatterlist_helper\",",
    ".anchor = \"lib/devres.c\",",
    ".provides_scatterlist_lifetime_planning = true,",
    ".touches_live_dma = false,",
    ".touches_live_scatterlist = false,",
    "pub fn planManagedScatterlistMap(",
    "pub fn planManagedScatterlistUnmap(",
    ".warns_on_release_miss = !release_matches,",
};

const SCATTERLIST_REPLAY_MARKERS = [_][]const u8{
    "test \"phase13 devres descriptor records helper-first scatterlist planning\" {",
    "test \"phase13 devres retains the release record when helper-first scatterlist planning succeeds\" {",
    "test \"phase13 devres frees the scatterlist release record when no mapped segments are returned\" {",
    "test \"phase13 devres frees the scatterlist release record when mapped segments exceed the original count\" {",
    "test \"phase13 devres rejects scatterlist planning when the release record cannot be allocated\" {",
    "test \"phase13 devres scatterlist release matching stays exact across original and mapped counts\" {",
    "try std.testing.expect(descriptor.provides_scatterlist_lifetime_planning);",
    "try std.testing.expect(!descriptor.touches_live_dma);",
    "try std.testing.expect(!descriptor.touches_live_scatterlist);",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (SLICE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PLANNER_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PLANNER_REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PLANNER_MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DMA_REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCATTERLIST_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCATTERLIST_REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
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
