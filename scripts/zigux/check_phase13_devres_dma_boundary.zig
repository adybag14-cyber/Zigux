const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_DMA_BOUNDARY_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "HELPER_PATH",
    "SURVEY_PATH",
    "DMA_REPLAY_PATH",
    "DMA_REPLAY_BUILD_PATH",
    "SCATTERLIST_NOTE_PATH",
    "SCATTERLIST_MANIFEST_PATH",
    "SCATTERLIST_HELPER_PATH",
    "SCATTERLIST_REPLAY_PATH",
    "SCATTERLIST_BUILD_PATH",
};

const HELPER_BLOCKED_MARKERS = [_][]const u8{
    "dmam_alloc_coherent(",
    "dmam_free_coherent(",
    "dma_map_",
    "dma_unmap_",
    "dma_sync_",
    "dma_mmap_",
    "dma_map_sgtable()",
    "struct scatterlist",
    "sg_table",
    "sg_init_table(",
};

const SCATTERLIST_HELPER_BLOCKED_MARKERS = [_][]const u8{
    "dma_map_sg(",
    "dma_unmap_sg(",
    "dma_map_sgtable()",
    "sg_alloc_table(",
    "sg_free_table(",
    "sg_dma_address(",
    "sg_dma_len(",
    "sg_table",
    "struct scatterlist",
};

const SURVEY_MARKERS = [_][]const u8{
    "helper-first scatterlist helper and replay",
    "helper-source readback shows `lib/devres.zig` still omits",
    "`Documentation/zigux/phase13-devres-scatterlist-planner.md` records a landed pure scatterlist lifetime planning surface",
    "`zigux/tests/phase13_devres_scatterlist_planner_manifest.json` marks the packet as `starter_landed`",
    "blocked `phase13-devres-live-scatterlist-ownership`",
    "blocked `phase13-devres-live-sg-table-lifecycle`",
    "blocked `phase13-devres-generic-dma-map-family`",
    "`dmam_alloc_coherent()`",
    "`dmam_free_coherent()`",
    "`dma_sync_*`",
    "`dma_mmap_*`",
    "`dma_map_sgtable()`",
    "`sg_alloc_table()`",
    "`sg_free_table()`",
    "`sg_dma_address()`",
    "`sg_dma_len()`",
    "`dma_map_sg()`",
    "`dma_unmap_sg()`",
    "`sg_table`",
    "`lib/devres_scatterlist.zig` ships a pure scatterlist lifetime planning surface",
    "`zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig` keeps the zero-sized coherent allocation replay directly runnable through its dedicated build shard",
    "`zigux/tests/phase13_devres_scatterlist_build.zig` keeps the helper-first scatterlist replay directly runnable through a dedicated build shard",
};

const DMA_REPLAY_MARKERS = [_][]const u8{
    "test \"phase13 devres dma coherent replay records blocked dma and scatterlist boundaries\" {",
    "test \"phase13 devres dma coherent replay proves lib/devres stays planning-only at the boundary\" {",
    "test \"phase13 devres dma coherent replay anchors the survey-side scatterlist boundary\" {",
    "test \"phase13 devres dma coherent replay keeps scatterlist helper evidence helper-first\" {",
    "test \"phase13 devres dma coherent replay keeps build-shard boundary checks explicit\" {",
    "try requireAbsent(helper, \"dmam_alloc_coherent(\");",
    "try requireAbsent(helper, \"dmam_free_coherent(\");",
    "try requireAbsent(helper, \"dma_map_\");",
    "try requireAbsent(helper, \"dma_unmap_\");",
    "try requireAbsent(helper, \"dma_sync_\");",
    "try requireAbsent(helper, \"dma_mmap_\");",
    "try requireAbsent(helper, \"dma_map_sgtable()\");",
    "try requireAbsent(helper, \"struct scatterlist\");",
    "try requireAbsent(helper, \"sg_table\");",
    "try requireAbsent(helper, \"sg_init_table(\");",
    "try requireContains(survey, \"helper-first scatterlist helper and replay\");",
    "try requireContains(survey, \"helper-source readback shows `lib/devres.zig` still omits\");",
    "try requireContains(survey, \"`dmam_alloc_coherent()`\");",
    "try requireContains(survey, \"`dmam_free_coherent()`\");",
    "try requireContains(survey, \"`dma_map_sgtable()`\");",
    "try requireContains(survey, \"`sg_table`\");",
    "try requireContains(survey, \"`zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`\");",
    "try requireContains(survey, \"`zigux/tests/phase13_devres_scatterlist_build.zig`\");",
    "try requireContains(checker, \"DMA_REPLAY_BUILD_PATH = Path(\"zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig\")\");",
    "try requireContains(checker, \"SCATTERLIST_BUILD_PATH = Path(\"zigux/tests/phase13_devres_scatterlist_build.zig\")\");",
    "try requireAbsent(helper, \"dma_map_sg(\");",
    "try requireAbsent(helper, \"dma_unmap_sg(\");",
    "try requireAbsent(helper, \"sg_alloc_table(\");",
    "try requireAbsent(helper, \"sg_free_table(\");",
    "try requireAbsent(helper, \"sg_dma_address(\");",
    "try requireAbsent(helper, \"sg_dma_len(\");",
};

const SCATTERLIST_NOTE_MARKERS = [_][]const u8{
    "pure scatterlist lifetime planning surface",
    "planManagedScatterlistMap(...)",
    "scatterlistReleaseMatches(...)",
    "planManagedScatterlistUnmap(...)",
    "retains detach-time unmap ownership on success",
    "failed mapping frees the release record",
    "warn-on-release-miss outcome",
    "sg_alloc_table()",
    "sg_free_table()",
    "sg_dma_address()",
    "sg_dma_len()",
    "dma_map_sg()",
    "dma_unmap_sg()",
    "dma_map_sgtable()",
    "sg_table",
};

const SCATTERLIST_MANIFEST_MARKERS = [_][]const u8{
    "\"packet\": \"phase13-devres-scatterlist-planner\"",
    "\"status\": \"starter_landed\"",
    "\"scatterlist_lifetime_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"",
    "\"validation_guard\": \"scripts/zigux/check_phase13_devres_scatterlist_planner.zig\"",
    "\"id\": \"phase13-devres-live-scatterlist-ownership\"",
    "\"id\": \"phase13-devres-live-sg-table-lifecycle\"",
    "\"id\": \"phase13-devres-generic-dma-map-family\"",
};

const SCATTERLIST_HELPER_MARKERS = [_][]const u8{
    ".provides_scatterlist_lifetime_planning = true",
    ".touches_live_dma = false",
    ".touches_live_scatterlist = false",
    "pub fn planManagedScatterlistMap",
    "pub fn scatterlistReleaseMatches",
    "pub fn planManagedScatterlistUnmap",
};

const SCATTERLIST_REPLAY_MARKERS = [_][]const u8{
    "phase13 devres descriptor records helper-first scatterlist planning",
    "phase13 devres scatterlist planner manifest records the dedicated helper-first packet",
    "phase13 devres scatterlist planner note keeps the helper-first scatterlist slice bounded",
    "phase13 devres scatterlist planner checker stays packet-local",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (HELPER_BLOCKED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCATTERLIST_HELPER_BLOCKED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DMA_REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCATTERLIST_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCATTERLIST_MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
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
