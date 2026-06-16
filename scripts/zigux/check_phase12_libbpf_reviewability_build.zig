const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{CHECK_NAME}_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "BUILD_PATH",
    "REVIEWABILITY_PATH",
    "VERIFY_NOTE_PATH",
    "SURVEY_PATH",
    "SNAPSHOT_PATH",
    "SNAPSHOT_DETERMINISM_PATH",
};

const BUILD_MARKERS = [_][]const u8{
    "../../tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "../../tools/lib/bpf/zigux_segments/type_names.zig",
    "../../tools/lib/bpf/zigux_segments/logging.zig",
    "../../tools/lib/bpf/zigux_segments/pin_path.zig",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "../../tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
    "phase12_libbpf_reviewability.zig",
    "reviewability_root_module.addImport(\"cpu_mask\", cpu_mask_module);",
    "reviewability_root_module.addImport(\"bpf_type_names\", type_names_module);",
    "reviewability_root_module.addImport(\"logging\", logging_module);",
    "reviewability_root_module.addImport(\"pin_path\", pin_path_module);",
    "reviewability_root_module.addImport(\"perf_buffer_poll\", perf_buffer_poll_module);",
    "reviewability_root_module.addImport(\"online_cpu_routing\", online_cpu_routing_module);",
    ".name = \"phase12-libbpf-reviewability-tests\",",
    "const test_step = b.step(",
    "\"test\"",
    "\"Run the Phase 12 libbpf reviewability tests\"",
};

const REVIEWABILITY_MARKERS = [_][]const u8{
    "test \"phase12 libbpf reviewability gate keeps the current snapshot anchor exact\"",
    "test \"phase12 libbpf reviewability gate keeps the helper-local determinism fixture exact\"",
    "test \"phase12 libbpf reviewability gate keeps the parked replay boundaries and note-owned anchors explicit\"",
    "test \"phase12 libbpf reviewability gate still compiles the surviving helper-first footing\"",
    "\"P12-L16\"",
    "\"P12-L17\"",
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const VERIFY_NOTE_MARKERS = [_][]const u8{
    "- focused reviewability-lab build route: `zig build test --build-file zigux/tests/phase12_libbpf_reviewability_build.zig --summary all`",
    "- lane-marker guard: `scripts/zigux/check_phase12_libbpf_lane_marker.zig`",
    "- snapshot checker: `scripts/zigux/check_phase12_libbpf_snapshot.zig`",
};

const SURVEY_MARKERS = [_][]const u8{
    "checked-in `zigux/tests/phase12_libbpf_reviewability.zig` gate",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
};

const CHECK_NAME = [_][]const u8{
    "PHASE12_LIBBPF_REVIEWABILITY_BUILD",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REVIEWABILITY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VERIFY_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
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
