const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_CURRENT_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "SLICE_PATH",
    "SURVEY_PATH",
    "HELPER_PATH",
    "SCATTERLIST_HELPER_PATH",
    "DMA_NOTE_PATH",
    "DMA_MANIFEST_PATH",
    "DMA_REPLAY_PATH",
    "DMA_REPLAY_BUILD_PATH",
    "DMA_CHECKER_PATH",
    "DMA_BOUNDARY_CHECKER_PATH",
    "SCATTERLIST_NOTE_PATH",
    "SCATTERLIST_MANIFEST_PATH",
    "SCATTERLIST_REPLAY_PATH",
    "SCATTERLIST_BUILD_PATH",
    "SCATTERLIST_CHECKER_PATH",
    "IOUNMAP_NOTE_PATH",
    "IOUNMAP_MANIFEST_PATH",
    "IOUNMAP_REPLAY_PATH",
    "IOUNMAP_CHECKER_PATH",
    "IOMAP_NOTE_PATH",
    "IOMAP_MANIFEST_PATH",
    "IOMAP_REPLAY_PATH",
    "IOMAP_CHECKER_PATH",
    "MMIO_PACKET_CHECKER_PATH",
};

const SLICE_MARKERS = [_][]const u8{
    "`scripts/zigux/check_phase13_devres_current_packet.zig` keeps the same-lane survey, planner, helper, replay, and checker surfaces aligned before widening into any missing non-posted, live ioport-unmap, or arch-memtype helper work",
    "the dedicated packet checkers, and the new current-packet checker",
    "helper-local ioport unmap planning",
    "helper-local arch-WC add or detach-cleanup footholds",
    "`planManagedIoportUnmap(...)` as a helper-local ioport release-match foothold",
    "`planManagedArchPhysWcAdd(...)` and `planManagedArchPhysWcDetachCleanup(...)` as helper-local arch-WC footholds",
    "rerun `zig run scripts/zigux/check_phase13_devres_current_packet.zig --` before widening anything else",
};

const SURVEY_MARKERS = [_][]const u8{
    "the dedicated current-packet checker",
    "`scripts/zigux/check_phase13_devres_current_packet.zig` now fail-closes across the slice, survey, helper, planner, replay, and existing checker surfaces",
    "scripts/zigux/check_phase13_devres_current_packet.zig",
    "landed `phase13-devres-current-packet-checker`",
    "Only rematerialize a helper-first non-posted, live ioport-unmap, or arch-memtype planner if `scripts/zigux/check_phase13_devres_current_packet.zig`",
    "helper-local ioport unmap planning",
    "helper-local arch-WC add and detach-cleanup footholds",
    "`.provides_ioport_unmap_call_planning = true`, `.provides_arch_phys_wc_add_planning = true`, `planDeviceTreeIomapCleanupHandoff(...)`, `planManagedIoportUnmap(...)`, `planManagedArchPhysWcAdd(...)`, and `planManagedArchPhysWcDetachCleanup(...)`",
};

const HELPER_MARKERS = [_][]const u8{
    ".provides_dmam_alloc_coherent_planning = true",
    ".provides_release_record_lifetime_planning = true",
    ".provides_release_call_planning = true",
    ".provides_dmam_detach_cleanup_transition_planning = true",
    ".provides_of_iomap_planning = true",
    ".provides_of_iomap_cleanup_handoff_planning = true",
    ".provides_iounmap_cleanup_planning = true",
    ".provides_ioport_unmap_call_planning = true",
    ".provides_arch_phys_wc_add_planning = true",
    ".touches_live_dma = false",
    ".touches_live_scatterlist = false",
    ".touches_live_mmio = false",
    "pub fn planManagedDmamAllocCoherent",
    "pub fn planManagedDmamDetachCleanup(",
    "pub fn planDeviceTreeIomap(",
    "pub fn planDeviceTreeIomapCleanupHandoff(",
    "pub fn planManagedIounmapCleanup(",
    "pub fn planManagedIoportUnmap(",
    "pub fn planManagedArchPhysWcAdd(",
    "pub fn planManagedArchPhysWcDetachCleanup(",
};

const SCATTERLIST_HELPER_MARKERS = [_][]const u8{
    ".provides_scatterlist_lifetime_planning = true",
    ".provides_scatterlist_table_teardown_planning = true",
    ".touches_live_dma = false",
    ".touches_live_scatterlist = false",
    "pub fn planManagedScatterlistMap",
    "pub fn scatterlistReleaseMatches",
    "pub fn planManagedScatterlistUnmap",
    "pub fn planManagedScatterlistTableTeardown",
};

const FORBIDDEN_HELPER_MARKERS = [_][]const u8{
    "devm_iounmap(",
    "devm_ioremap_np(",
    "devm_of_iomap(",
    "devm_ioport_unmap(",
    "devm_arch_phys_wc_add(",
    "devm_arch_io_reserve_memtype_wc(",
};

const FORBIDDEN_SCATTERLIST_HELPER_MARKERS = [_][]const u8{
    "dma_map_sg(",
    "dma_unmap_sg(",
    "dma_map_sgtable(",
    "sg_alloc_table(",
    "sg_free_table(",
    "sg_dma_address(",
    "sg_dma_len(",
    "struct scatterlist",
    "sg_table",
};

const PATH_MARKERS = [_][]const u8{
    "pure `dmam_alloc_coherent()` planning surface",
    "`scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig` is the packet-local fail-closed checker",
    "\"packet\": \"phase13-devres-dmam-alloc-coherent-planner\"",
    "\"status\": \"starter_landed\"",
    "phase13 devres descriptor records helper-first dmam_alloc_coherent planning",
    "phase13 devres dmam_alloc_coherent checker stays packet-local",
    "phase13-devres-dmam-alloc-zero-size-replay",
    "Run the Phase 13 devres zero-size replay",
    "../../lib/devres.zig",
    "phase13_devres_dmam_alloc_zero_size_replay.zig",
    "PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER_SELF_TEST=pass",
    "PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER=pass",
    "PHASE13_DEVRES_DMA_BOUNDARY_SELF_TEST=pass",
    "PHASE13_DEVRES_DMA_BOUNDARY=pass",
    "DMA_REPLAY_BUILD_PATH = Path(\"zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig\")",
    "SCATTERLIST_BUILD_PATH = Path(\"zigux/tests/phase13_devres_scatterlist_build.zig\")",
    "pure scatterlist lifetime planning surface",
    "`scripts/zigux/check_phase13_devres_scatterlist_planner.zig` is the packet-local validation guard",
    "\"packet\": \"phase13-devres-scatterlist-planner\"",
    "\"status\": \"starter_landed\"",
    "phase13 devres descriptor records helper-first scatterlist planning",
    "phase13 devres scatterlist planner checker stays packet-local",
    "phase13-devres-scatterlist-tests",
    "Run Phase 13 devres scatterlist helper tests",
    "../../lib/devres_scatterlist.zig",
    "phase13_devres_scatterlist.zig",
    "PHASE13_DEVRES_SCATTERLIST_PLANNER_SELF_TEST=pass",
    "PHASE13_DEVRES_SCATTERLIST_PLANNER=pass",
    "pure `devm_iounmap()` cleanup planning surface",
    "`scripts/zigux/check_phase13_devres_iounmap_planner.zig` is the packet-local fail-closed checker",
    "\"packet\": \"phase13-devres-iounmap-planner\"",
    "\"status\": \"starter_landed\"",
    "phase13 devres descriptor records helper-first iounmap cleanup planning",
    "phase13 devres iounmap planner checker stays packet-local",
    "PHASE13_DEVRES_IOUNMAP_PLANNER_SELF_TEST=pass",
    "PHASE13_DEVRES_IOUNMAP_PLANNER=pass",
    "pure `devm_of_iomap()` planning surface",
    "`scripts/zigux/check_phase13_devres_iomap_planner.zig` is the packet-local fail-closed checker",
    "\"packet\": \"phase13-devres-iomap-planner\"",
    "\"status\": \"starter_landed\"",
    "phase13 devres descriptor records helper-first iomap planning",
    "phase13 devres iomap planner checker stays packet-local",
    "PHASE13_DEVRES_IOMAP_PLANNER_SELF_TEST=pass",
    "PHASE13_DEVRES_IOMAP_PLANNER=pass",
    "PHASE13_DEVRES_MMIO_PACKET_SELF_TEST=pass",
    "PHASE13_DEVRES_MMIO_PACKET=pass",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (SLICE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCATTERLIST_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_SCATTERLIST_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PATH_MARKERS) |marker| try guard.requireMarker(text, marker);
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
