const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_RING_BUFFER_MAINTENANCE_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "SURVEY_PATH",
    "MANIFEST_PATH",
    "SURVEY_TEST_PATH",
    "PRODUCTIZATION_GAP_PATH",
    "SHARED_SMOKE_GAP_PATH",
    "SMOKE_SURVEY_PATH",
    "CORE_BOUNDARY_TRACEABILITY_PATH",
};

const REQUIRED_MARKERS = [_][]const u8{
    "`PHASE14_STATUS=study_only`",
    "`phase14-ring-buffer-maintenance-handoff`",
    "`phase14-ring-buffer-tracefs-reader-serialization-followup`",
    "`zig test zigux/tests/phase14_ring_buffer_survey.zig`",
    "`zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    "current public raw-file readback now recovers both `zigux/tests/phase14_ring_buffer_survey.zig` and `zigux/tests/phase14_build.zig`",
    "keep those two routes as ring-buffer-local replay vocabulary only",
    "returned survey companion and shared build shard framed as public-raw-backed ring-buffer-local evidence",
    "reader-page import, consume-or-extract serialization, `reader_page` handoff, or mapped-reader lifetime teardown wording",
    "\"lane_key\": \"P14-L08\"",
    "\"current_lane_posture\": \"maintenance_mode\"",
    "\"phase14-ring-buffer-maintenance-handoff\"",
    "\"phase14-ring-buffer-zig-port-blocker\"",
    "\"zig test zigux/tests/phase14_ring_buffer_survey.zig\"",
    "\"zig build test --build-file zigux/tests/phase14_build.zig --summary all\"",
    "\"head-page-reader-handoff\"",
    "\"remote-reader-metadata\"",
    "\"tracefs-mapping-limitations\"",
    "\"read-page-extraction-boundary\"",
    "try std.testing.expectEqualStrings(\"P14-L08\", manifest.lane_key);",
    "try std.testing.expectEqualStrings(\"maintenance_mode\", manifest.maintenance_handoff.current_lane_posture);",
    "try std.testing.expect(std.mem.indexOf(u8, note, \"phase14-ring-buffer-maintenance-handoff\") != null);",
    "try std.testing.expect(std.mem.indexOf(u8, note, \"public raw-file readback now recovers both `zigux/tests/phase14_ring_buffer_survey.zig` and `zigux/tests/phase14_build.zig`\") != null);",
    "try std.testing.expect(std.mem.indexOf(u8, note, \"returned survey companion and shared build shard framed as public-raw-backed ring-buffer-local evidence\") != null);",
    "try std.testing.expect(hasDecisionChecklist(manifest, \"head-page-reader-handoff\", \"stay_in_c\", \"reader-page extraction\", \"rb_set_head_page\", \"page handoff semantics\"));",
    "try std.testing.expect(hasDecisionChecklist(manifest, \"remote-reader-metadata\", \"stay_in_c\", \"remote-reader metadata\", \"__rb_get_reader_page_from_remote\", \"reader-page import rules\"));",
    "try std.testing.expect(hasDecisionChecklist(manifest, \"tracefs-mapping-limitations\", \"stay_in_c\", \"shared tracefs lockout boundary\", \"ring_buffer_map_get_reader\", \"mapped reader pins `resize_disabled`\"));",
    "`zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
    "the directly readable ring-buffer survey companion",
    "`PHASE14_LANE_KEY=P14-L05`",
    "recover the dedicated ring-buffer survey companion again through the current contents path",
    "`zigux/tests/phase14_ring_buffer_survey.zig` is directly readable again through the current contents path as a ring-buffer-local survey companion",
    "the returned ring-buffer survey companion",
    "  * directly readable ring-buffer survey companion in this lane's current evidence split:",
    "    * `zigux/tests/phase14_ring_buffer_survey.zig`",
    "    * ring-buffer-survey drift",
    "`kernel/trace/ring_buffer.c`: `Study / Boundary Only`",
    "the dedicated `P14-L08` survey note and manifest remain ring-buffer-local study evidence",
    "the focused `zigux/tests/phase14_ring_buffer_survey.zig` companion is directly readable again through the shared smoke packet",
    "`cmpxchg()`-guarded `reader_page` handoff",
    "`ring_buffer_alloc_read_page()` import and guarded remote-reader metadata setup",
    "`ring_buffer_read_page()` consume or extract serialization",
    "`rb_remove_pages()` mapped-reader lifetime teardown",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
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
