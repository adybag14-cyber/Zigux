const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_MMIO_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "SLICE_PATH",
    "SURVEY_PATH",
    "IOUNMAP_NOTE_PATH",
    "IOUNMAP_MANIFEST_PATH",
    "IOUNMAP_REPLAY_PATH",
    "IOMAP_NOTE_PATH",
    "IOMAP_MANIFEST_PATH",
    "IOMAP_REPLAY_PATH",
    "HELPER_PATH",
    "DMA_BOUNDARY_CHECKER_PATH",
    "IOUNMAP_CHECKER_PATH",
    "IOMAP_CHECKER_PATH",
    "CURRENT_PACKET_CHECKER_PATH",
};

const DIRECT_PACKET_GAP_PATHS = [_][]const u8{
    "Path(zigux/tests/phase13_devres.zig)",
    "Path(zigux/tests/phase13_devres_reviewability.zig)",
    "Path(zigux/tests/phase13_devres_manifest.json)",
    "Path(scripts/zigux/check_phase13_devres_packet.zig)",
    "Path(scripts/zigux/check_phase13_devres_packet_alignment.zig)",
};

const SLICE_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase13-devres-iounmap-planner.md`",
    "`zigux/tests/phase13_devres_iounmap_planner.zig`",
    "`scripts/zigux/check_phase13_devres_dma_boundary.zig`",
    "`scripts/zigux/check_phase13_devres_iounmap_planner.zig`",
    "`Documentation/zigux/phase13-devres-iomap-planner.md`",
    "`zigux/tests/phase13_devres_iomap_planner.zig`",
    "`scripts/zigux/check_phase13_devres_iomap_planner.zig`",
    "current packet helper-first, planning-only, and MMIO-bounded",
};

const SURVEY_MARKERS = [_][]const u8{
    "helper-first iomap planning evidence",
    "`Documentation/zigux/phase13-devres-iounmap-planner.md` records a landed pure `devm_iounmap()` cleanup planning surface",
    "`zigux/tests/phase13_devres_iounmap_planner_manifest.json` marks the packet as `starter_landed`",
    "`Documentation/zigux/phase13-devres-iomap-planner.md` records a landed pure `devm_of_iomap()` planning surface",
    "`zigux/tests/phase13_devres_iomap_planner_manifest.json` marks the packet as `starter_landed`",
    "helper-first iomap planning through `planDeviceTreeIomap(...)`",
    "helper-side iomap cleanup handoff in `lib/devres.zig`",
    "`.provides_of_iomap_cleanup_handoff_planning = true` and `planDeviceTreeIomapCleanupHandoff(...)`",
    "`scripts/zigux/check_phase13_devres_dma_boundary.zig`",
    "`zigux/tests/phase13_devres.zig`",
    "`zigux/tests/phase13_devres_reviewability.zig`",
    "`zigux/tests/phase13_devres_manifest.json`",
    "`scripts/zigux/check_phase13_devres_packet.zig`",
    "`scripts/zigux/check_phase13_devres_packet_alignment.zig`",
    "blocked `phase13-devres-missing-devm-ioremap-np-surface`",
    "blocked `phase13-devres-missing-devm-arch-phys-wc-add-surface`",
    "blocked `phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface`",
    "blocked `phase13-devres-live-mmio-mapping-state`",
    "blocked `phase13-devres-live-device-tree-walks`",
    "blocked `phase13-devres-live-arch-memtype-mutation`",
};

const IOUNMAP_NOTE_MARKERS = [_][]const u8{
    "pure `devm_iounmap()` cleanup planning surface",
    "planManagedIounmapCleanup(...)",
    "tracked mapping owner generates cleanup work",
    "warn-on-release-miss outcome",
    "devm_ioremap_np()",
    "devm_of_iomap()",
    "devm_arch_phys_wc_add()",
    "devm_arch_io_reserve_memtype_wc()",
};

const IOUNMAP_MANIFEST_MARKERS = [_][]const u8{
    "\"packet\": \"phase13-devres-iounmap-planner\"",
    "\"status\": \"starter_landed\"",
    "\"iounmap_cleanup_owner\": \"zigux/tests/phase13_devres_iounmap_planner.zig\"",
    "\"warn_on_release_miss_owner\": \"zigux/tests/phase13_devres_iounmap_planner.zig\"",
    "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"",
    "\"id\": \"phase13-devres-missing-devm-arch-phys-wc-add-surface\"",
    "\"id\": \"phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface\"",
    "\"id\": \"phase13-devres-live-mmio-mapping-state\"",
    "\"id\": \"phase13-devres-live-device-tree-walks\"",
    "\"id\": \"phase13-devres-live-arch-memtype-mutation\"",
};

const IOUNMAP_REPLAY_MARKERS = [_][]const u8{
    "phase13 devres descriptor records helper-first iounmap cleanup planning",
    "phase13 devres iounmap planner manifest records the landed helper-first mmio scope",
    "phase13 devres iounmap planner note keeps the helper-first mmio slice bounded",
    "phase13 devres iounmap planner checker stays packet-local",
};

const IOMAP_NOTE_MARKERS = [_][]const u8{
    "pure `devm_of_iomap()` planning surface",
    "planDeviceTreeIomap(...)",
    "translated size is preserved when a requested region is denied as busy",
    "requested region is released again when remap later fails",
    "requested non-posted mapping type stays attached to the planning surface",
    "successful helper-first remap hands off to `devm_iounmap()` cleanup planning",
    "cleanup handoff consumes the matching release record or still warns when the release record is missing",
    "devm_ioremap_np()",
    "devm_iounmap()",
    "devm_arch_phys_wc_add()",
    "devm_arch_io_reserve_memtype_wc()",
};

const IOMAP_MANIFEST_MARKERS = [_][]const u8{
    "\"packet\": \"phase13-devres-iomap-planner\"",
    "\"status\": \"starter_landed\"",
    "\"translation_miss_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"request_region_denial_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"nonposted_wrapper_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"remap_failure_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"cleanup_handoff_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"cleanup_release_miss_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "planDeviceTreeIomapCleanupHandoff",
    "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"",
    "\"id\": \"phase13-devres-missing-devm-arch-phys-wc-add-surface\"",
    "\"id\": \"phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface\"",
    "\"id\": \"phase13-devres-live-mmio-mapping-state\"",
    "\"id\": \"phase13-devres-live-device-tree-walks\"",
    "\"id\": \"phase13-devres-live-arch-memtype-mutation\"",
};

const IOMAP_REPLAY_MARKERS = [_][]const u8{
    "phase13 devres descriptor records helper-first iomap planning",
    "phase13 devres iomap cleanup handoff materializes helper-first iounmap cleanup after successful remap",
    "phase13 devres iomap cleanup handoff keeps missing release records warnable",
    "phase13 devres iomap planner manifest records the landed helper-first mmio scope",
    "phase13 devres iomap planner note keeps the helper-first mmio slice bounded",
    "phase13 devres iomap planner checker stays packet-local",
};

const HELPER_REQUIRED_MARKERS = [_][]const u8{
    ".provides_of_iomap_planning = true",
    ".provides_of_iomap_cleanup_handoff_planning = true",
    ".provides_iounmap_cleanup_planning = true",
    ".touches_live_mmio = false",
    "pub fn planDeviceTreeIomap",
    "pub fn planDeviceTreeIomapCleanupHandoff",
    "pub fn planManagedIounmapCleanup",
};

const HELPER_FORBIDDEN_MARKERS = [_][]const u8{
    "devm_iounmap(",
    "devm_ioremap_np(",
    "devm_of_iomap(",
    "devm_arch_phys_wc_add(",
    "devm_arch_io_reserve_memtype_wc(",
};

const DMA_BOUNDARY_CHECKER_MARKERS = [_][]const u8{
    "HELPER_PATH = Path(\"lib/devres.zig\")",
    "SURVEY_PATH = Path(\"Documentation/zigux/phase13-devres-survey.md\")",
    "DMA_REPLAY_PATH = Path(\"zigux/tests/phase13_devres_dma_coherent.zig\")",
    "SCATTERLIST_NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-scatterlist-planner.md\")",
    "SCATTERLIST_MANIFEST_PATH = Path(\"zigux/tests/phase13_devres_scatterlist_planner_manifest.json\")",
    "SCATTERLIST_HELPER_PATH = Path(\"lib/devres_scatterlist.zig\")",
    "SCATTERLIST_REPLAY_PATH = Path(\"zigux/tests/phase13_devres_scatterlist.zig\")",
    "PHASE13_DEVRES_DMA_BOUNDARY_SELF_TEST=pass",
    "PHASE13_DEVRES_DMA_BOUNDARY=pass",
};

const IOUNMAP_CHECKER_MARKERS = [_][]const u8{
    "HELPER_PATH = Path(\"lib/devres.zig\")",
    "NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-iounmap-planner.md\")",
    "MANIFEST_PATH = Path(\"zigux/tests/phase13_devres_iounmap_planner_manifest.json\")",
    "REPLAY_PATH = Path(\"zigux/tests/phase13_devres_iounmap_planner.zig\")",
    "PHASE13_DEVRES_IOUNMAP_PLANNER_SELF_TEST=pass",
    "PHASE13_DEVRES_IOUNMAP_PLANNER=pass",
};

const IOMAP_CHECKER_MARKERS = [_][]const u8{
    "HELPER_PATH = Path(\"lib/devres.zig\")",
    "NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-iomap-planner.md\")",
    "MANIFEST_PATH = Path(\"zigux/tests/phase13_devres_iomap_planner_manifest.json\")",
    "REPLAY_PATH = Path(\"zigux/tests/phase13_devres_iomap_planner.zig\")",
    "PHASE13_DEVRES_IOMAP_PLANNER_SELF_TEST=pass",
    "PHASE13_DEVRES_IOMAP_PLANNER=pass",
};

const CURRENT_PACKET_CHECKER_MARKERS = [_][]const u8{
    "MMIO_PACKET_CHECKER_PATH = Path(\"scripts/zigux/check_phase13_devres_mmio_packet.zig\")",
    "PHASE13_DEVRES_CURRENT_PACKET_SELF_TEST=pass",
    "PHASE13_DEVRES_CURRENT_PACKET=pass",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (DIRECT_PACKET_GAP_PATHS) |marker| try guard.requireMarker(text, marker);
    for (SLICE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (IOUNMAP_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (IOUNMAP_MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (IOUNMAP_REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (IOMAP_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (IOMAP_MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (IOMAP_REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HELPER_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HELPER_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DMA_BOUNDARY_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (IOUNMAP_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (IOMAP_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CURRENT_PACKET_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
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
