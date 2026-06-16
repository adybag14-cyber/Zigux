const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_SCATTERLIST_PLANNER_SELF_TEST=pass";

const FORBIDDEN_HELPER_MARKERS = [_][]const u8{
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

const REQUIRED_MARKERS = [_][]const u8{
    ".provides_scatterlist_lifetime_planning = true",
    ".provides_scatterlist_table_teardown_planning = true",
    ".touches_live_dma = false",
    ".touches_live_scatterlist = false",
    "pub fn planManagedScatterlistMap",
    "pub fn scatterlistReleaseMatches",
    "pub fn planManagedScatterlistUnmap",
    "pub fn planManagedScatterlistTableTeardown",
    "warns_on_empty_table: bool",
    ".warns_on_empty_table = input.table_initialized and input.original_entries == 0",
    "pure scatterlist lifetime planning surface",
    "`Documentation/zigux/phase13-devres-scatterlist-slice.md` keeps the helper-local scope and non-goals aligned with this planner note, the manifest, and the replay",
    "`zigux/tests/phase13_devres_scatterlist_build.zig` keeps the dedicated build shard aligned with the helper-first scatterlist replay",
    "retains detach-time unmap ownership on success",
    "failed mapping frees the release record",
    "warn-on-release-miss outcome",
    "helper-first `sg_table` free eligibility stays reviewable",
    "records whether uninitialized tables stay neither free-ready nor unmap-requiring until table initialization is explicit",
    "records whether initialized zero-entry tables warn as malformed teardown inputs instead of silently becoming free-ready",
    "requires unmap-before-free planning",
    "warn rather than claiming live `sg_table` lifecycle mutation",
    "zigux/tests/phase13_devres_scatterlist_empty_table.zig",
    "dma_map_sgtable()",
    "sg_table",
    "zig build test --build-file zigux/tests/phase13_devres_scatterlist_build.zig",
    "helper-first scatterlist planner beside the existing `lib/devres.zig` and `lib/devres_dma_coherent.zig` packet",
    "focused replay: `zigux/tests/phase13_devres_scatterlist.zig`",
    "empty-table replay: `zigux/tests/phase13_devres_scatterlist_empty_table.zig`",
    "provides_scatterlist_table_teardown_planning = true",
    "`planManagedScatterlistTableTeardown()` models helper-first `sg_table` teardown readiness",
    "uninitialized-table hold",
    "initialized zero-entry tables warn instead of silently becoming free-ready",
    "no live `dma_map_sgtable()` or `dma_unmap_sgtable()` execution",
    "no `struct scatterlist`, `sg_table`, or `sg_*` iteration helpers",
    "no live `sg_free_table()` lifecycle mutation or `sg_alloc_table()` ownership claims",
    "\"packet\": \"phase13-devres-scatterlist-planner\"",
    "\"status\": \"starter_landed\"",
    "\"scatterlist_lifetime_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"",
    "\"scatterlist_table_teardown_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"",
    "\"empty_table_warning_owner\": \"zigux/tests/phase13_devres_scatterlist_empty_table.zig\"",
    "\"slice_note_owner\": \"Documentation/zigux/phase13-devres-scatterlist-slice.md\"",
    "\"build_shard_owner\": \"zigux/tests/phase13_devres_scatterlist_build.zig\"",
    "\"validation_guard\": \"scripts/zigux/check_phase13_devres_scatterlist_planner.zig\"",
    "planManagedScatterlistTableTeardown",
    "warns_on_empty_table",
    "initialized zero-entry tables warn",
    "helper-first `sg_table` free eligibility stays reviewable",
    "\"id\": \"phase13-devres-live-scatterlist-ownership\"",
    "\"id\": \"phase13-devres-live-sg-table-lifecycle\"",
    "\"id\": \"phase13-devres-generic-dma-map-family\"",
    "phase13 devres descriptor records helper-first scatterlist planning",
    "phase13 devres scatterlist table teardown becomes free-ready once mapped entries drain",
    "phase13 devres scatterlist table teardown requires unmap before free when mapped entries remain",
    "phase13 devres scatterlist table teardown stays inert until the table is initialized",
    "phase13 devres scatterlist table teardown warns when the release record is missing",
    "phase13 devres scatterlist table teardown warns on overmapped release drift",
    "phase13 devres scatterlist planner checker stays packet-local",
    "phase13 devres scatterlist table teardown warns on initialized empty tables",
    "phase13 devres scatterlist empty-table replay stays helper-local",
    "warns_on_empty_table",
    ".touches_live_dma = false",
    ".touches_live_scatterlist = false",
    "phase13-devres-scatterlist-tests",
    "phase13-devres-scatterlist-empty-table-tests",
    "Run Phase 13 devres scatterlist helper tests",
    "../../lib/devres_scatterlist.zig",
    "phase13_devres_scatterlist.zig",
    "phase13_devres_scatterlist_empty_table.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (FORBIDDEN_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
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
