const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_PLANNER_BOUNDARY_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "# Phase 13 devres DMA, scatterlist, and MMIO Boundary Survey",
    "the shipped DMA and scatterlist boundary evidence, plus the still-missing MMIO and iomap safety gaps that remain open against the Phase 13 roadmap.",
    "`Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`",
    "`zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`",
    "`Documentation/zigux/phase13-devres-scatterlist-planner.md`",
    "`zigux/tests/phase13_devres_scatterlist_planner_manifest.json`",
    "`zigux/tests/phase13_devres_dma_coherent.zig`",
    "`lib/devres_scatterlist.zig`",
    "`zigux/tests/phase13_devres_scatterlist.zig`",
    "current `master` does not ship `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, or `scripts/zigux/check_phase13_devres_packet_alignment.zig`.",
    "blocked `phase13-devres-live-dmam-alloc-side-effects`",
    "blocked `phase13-devres-live-scatterlist-ownership`",
    "blocked `phase13-devres-live-sg-table-lifecycle`",
    "blocked `phase13-devres-generic-dma-map-family`",
    "blocked `phase13-devres-missing-devm-ioremap-np-surface`",
    "blocked `phase13-devres-broader-direct-helper-packet`",
    "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only",
    "`scripts/zigux/check_phase13_devres_packet_alignment.zig`",
    "the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker remain repo-reality gaps",
    "the broader direct helper packet stays an explicit repo-reality gap",
    "lands one pure `dmam_alloc_coherent()` planning surface in `lib/devres.zig`",
    "routes `planManagedDmamAllocCoherent(...)` through `planManagedReleaseRecordLifetime(...)`",
    "routes `planManagedDmamFreeCoherent(...)` through one private `planReleaseCall(...)` helper",
    "retains detach-time cleanup ownership on success",
    "failed allocation frees the release record",
    "`zigux/tests/phase13_devres_dma_coherent.zig` remains adjacent boundary evidence only",
    "does not claim live DMA allocation side effects",
    "dma_map_sgtable()",
    "struct scatterlist",
    "sg_table",
    "lands one pure scatterlist lifetime planning surface in `lib/devres_scatterlist.zig`",
    "routes `planManagedScatterlistMap(...)` through one helper-local release-record outcome",
    "retains detach-time unmap ownership on success",
    "failed mapping frees the release record",
    "routes `planManagedScatterlistUnmap(...)` through exact original-entry and mapped-entry matching",
    "exposes `scatterlistReleaseMatches(...)` as the helper-first exact-match check",
    "`zigux/tests/phase13_devres_dma_coherent.zig` remains adjacent boundary evidence only",
    "sg_alloc_table()",
    "dma_map_sgtable()",
    "sg_table",
    "\"lane_key\": \"P13-L08\"",
    "\"packet\": \"phase13-devres-dmam-alloc-coherent-planner\"",
    "\"status\": \"starter_landed\"",
    "\"detach_cleanup_owner\": \"zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig\"",
    "\"id\": \"phase13-devres-live-dmam-alloc-side-effects\"",
    "\"status\": \"blocked_on_dma_state\"",
    "\"id\": \"phase13-devres-live-scatterlist-ownership\"",
    "\"status\": \"blocked_on_scatterlist_state\"",
    "\"lane_key\": \"P13-L08\"",
    "\"packet\": \"phase13-devres-scatterlist-planner\"",
    "\"status\": \"starter_landed\"",
    "\"release_match_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"",
    "\"id\": \"phase13-devres-live-scatterlist-ownership\"",
    "\"status\": \"blocked_on_scatterlist_state\"",
    "\"id\": \"phase13-devres-live-sg-table-lifecycle\"",
    "\"status\": \"blocked_on_sg_table_lifecycle\"",
    "\"id\": \"phase13-devres-generic-dma-map-family\"",
    "\"status\": \"blocked_on_dma_mapping_state\"",
    "test \"phase13 devres dma coherent replay records blocked dma and scatterlist boundaries\"",
    "test \"phase13 devres dma coherent replay proves lib/devres stays planning-only at the boundary\"",
    "test \"phase13 devres dma coherent replay keeps missing checker surfaces framed as gaps\"",
    "test \"phase13 devres dma coherent replay anchors the survey-side scatterlist boundary\"",
    "test \"phase13 devres dma coherent replay keeps scatterlist helper evidence helper-first\"",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "current `master` now ships `zigux/tests/phase13_devres.zig`",
    "current `master` now ships `zigux/tests/phase13_devres_reviewability.zig`",
    "current `master` now ships `zigux/tests/phase13_devres_manifest.json`",
    "current `master` now ships `scripts/zigux/check_phase13_devres_packet_alignment.zig`",
    "the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker now ship on current `master`",
};

const SURVEY = [_][]const u8{
    "Documentation/zigux/phase13-devres-survey.md",
};

const SLICE = [_][]const u8{
    "Documentation/zigux/phase13-devres-slice.md",
};

const DMAM_NOTE = [_][]const u8{
    "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md",
};

const SCATTERLIST_NOTE = [_][]const u8{
    "Documentation/zigux/phase13-devres-scatterlist-planner.md",
};

const DMAM_MANIFEST = [_][]const u8{
    "zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json",
};

const SCATTERLIST_MANIFEST = [_][]const u8{
    "zigux/tests/phase13_devres_scatterlist_planner_manifest.json",
};

const DMA_REPLAY = [_][]const u8{
    "zigux/tests/phase13_devres_dma_coherent.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY) |marker| try guard.requireMarker(text, marker);
    for (SLICE) |marker| try guard.requireMarker(text, marker);
    for (DMAM_NOTE) |marker| try guard.requireMarker(text, marker);
    for (SCATTERLIST_NOTE) |marker| try guard.requireMarker(text, marker);
    for (DMAM_MANIFEST) |marker| try guard.requireMarker(text, marker);
    for (SCATTERLIST_MANIFEST) |marker| try guard.requireMarker(text, marker);
    for (DMA_REPLAY) |marker| try guard.requireMarker(text, marker);
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
