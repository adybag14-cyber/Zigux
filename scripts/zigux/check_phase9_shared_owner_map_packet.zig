const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_SHARED_OWNER_MAP_PACKET_SELF_TEST=pass";

const DOCS_README_REQUIRED_MARKERS = [_][]const u8{
    "SEQUENCING_PATH_MARKER",
    "REVIEW_CHECKLIST_PATH_MARKER",
    "CHECKLIST_BOUNDARY_CHECKER_MARKER",
    "TRACE_EVENTS_PACKET_CHECKER_MARKER",
    "TESTS_README_MARKER",
    "TRACE_EVENTS_SAMPLE_MARKER",
    "UNREGISTERED_GATE_MARKER",
    "SELFTEST_HOOK_MARKER",
    "LIFECYCLE_MARKER",
    "ABSENT_SHARED_LOADER_MARKER",
    "ABSENT_PHASE9_BUILD_MARKER",
    "ABSENT_RUNTIME_TEST_FAMILY_MARKER",
    "ABSENT_RUNTIME_LOADER_KERNEL_MARKER",
    "ABSENT_RUNTIME_LOADER_CONTRACT_MARKER",
    "ABSENT_MAKEFILE_MARKER",
    "ABSENT_WORKFLOW_MARKER",
    "ABSENT_LOADER_SCAFFOLD_MARKER",
    "PHASE2_CONF_BRIDGE_MARKER",
    "PHASE2_CONFDATA_BRIDGE_MARKER",
    "PHASE3_EXPORTS_MARKER",
    "PHASE3_EXPORT_SHIM_MARKER",
    "BITMAP_BACKLOG_MARKER",
};

const REVIEW_CHECKLIST_REQUIRED_MARKERS = [_][]const u8{
    "SEQUENCING_PATH_MARKER",
    "REVIEW_CHECKLIST_PATH_MARKER",
    "CHECKLIST_BOUNDARY_CHECKER_MARKER",
    "TRACE_EVENTS_PACKET_CHECKER_MARKER",
    "TESTS_README_MARKER",
    "TRACE_EVENTS_SAMPLE_MARKER",
    "UNREGISTERED_GATE_MARKER",
    "SELFTEST_HOOK_MARKER",
    "LIFECYCLE_MARKER",
    "ABSENT_SHARED_LOADER_MARKER",
    "ABSENT_PHASE9_BUILD_MARKER",
    "ABSENT_RUNTIME_TEST_FAMILY_MARKER",
    "ABSENT_RUNTIME_LOADER_KERNEL_MARKER",
    "ABSENT_RUNTIME_LOADER_CONTRACT_MARKER",
    "ABSENT_MAKEFILE_MARKER",
    "ABSENT_WORKFLOW_MARKER",
    "ABSENT_LOADER_SCAFFOLD_MARKER",
    "PHASE2_CONF_BRIDGE_MARKER",
    "PHASE2_CONFDATA_BRIDGE_MARKER",
    "PHASE3_EXPORTS_MARKER",
    "PHASE3_EXPORT_SHIM_MARKER",
    "BITMAP_BACKLOG_MARKER",
};

const SCRIPTS_README_REQUIRED_MARKERS = [_][]const u8{
    "SEQUENCING_PATH_MARKER",
    "REVIEW_CHECKLIST_PATH_MARKER",
    "CHECKLIST_BOUNDARY_CHECKER_MARKER",
    "TRACE_EVENTS_PACKET_CHECKER_MARKER",
    "TESTS_README_MARKER",
    "TRACE_EVENTS_SAMPLE_MARKER",
    "UNREGISTERED_GATE_MARKER",
    "SELFTEST_HOOK_MARKER",
    "LIFECYCLE_MARKER",
    "ABSENT_PHASE9_BUILD_MARKER",
    "ABSENT_RUNTIME_TEST_FAMILY_MARKER",
    "ABSENT_RUNTIME_LOADER_KERNEL_MARKER",
    "ABSENT_RUNTIME_LOADER_CONTRACT_MARKER",
    "ABSENT_MAKEFILE_MARKER",
    "ABSENT_WORKFLOW_MARKER",
    "ABSENT_LOADER_SCAFFOLD_MARKER",
    "PHASE2_CONF_BRIDGE_MARKER",
    "PHASE2_CONFDATA_BRIDGE_MARKER",
    "PHASE3_EXPORTS_MARKER",
    "PHASE3_EXPORT_SHIM_MARKER",
};

const SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
};

const DOCS_README_PATH = [_][]const u8{
    "Documentation/zigux/README.md",
};

const REVIEW_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/review-checklist.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const SEQUENCING_PATH_MARKER = [_][]const u8{
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
};

const REVIEW_CHECKLIST_PATH_MARKER = [_][]const u8{
    "`Documentation/zigux/review-checklist.md`",
};

const SCRIPTS_README_PATH_MARKER = [_][]const u8{
    "`scripts/zigux/README.md`",
};

const CHECKLIST_BOUNDARY_CHECKER_MARKER = [_][]const u8{
    "`scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`",
};

const TRACE_EVENTS_PACKET_CHECKER_MARKER = [_][]const u8{
    "`scripts/zigux/check_phase9_trace_events_runtime_packet.zig`",
};

const TESTS_README_MARKER = [_][]const u8{
    "`zigux/tests/README.md`",
};

const TRACE_EVENTS_SAMPLE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events.zig`",
};

const UNREGISTERED_GATE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
};

const SELFTEST_HOOK_MARKER = [_][]const u8{
    "`.provides_selftest_hook = true`",
};

const LIFECYCLE_MARKER = [_][]const u8{
    "initialized, selftest_complete, and exited lifecycle tracking",
};

const ABSENT_SHARED_LOADER_MARKER = [_][]const u8{
    "does not currently expose the broader shared runtime-loader packet",
};

const ABSENT_PHASE9_BUILD_MARKER = [_][]const u8{
    "`zigux/tests/phase9_build.zig`",
};

const ABSENT_RUNTIME_TEST_FAMILY_MARKER = [_][]const u8{
    "shared `zigux/tests/runtime_*` replay family",
};

const ABSENT_RUNTIME_LOADER_KERNEL_MARKER = [_][]const u8{
    "`zigux/kernel/runtime_loader.zig`",
};

const ABSENT_RUNTIME_LOADER_CONTRACT_MARKER = [_][]const u8{
    "`zigux/kernel/runtime_loader_contract.zig`",
};

const ABSENT_MAKEFILE_MARKER = [_][]const u8{
    "`zigux/Makefile`",
};

const ABSENT_WORKFLOW_MARKER = [_][]const u8{
    "`.github/workflows/zigux-bootstrap.yml`",
};

const ABSENT_LOADER_SCAFFOLD_MARKER = [_][]const u8{
    "`samples/zigux/runtime_*_loader.zig` scaffolds",
};

const PHASE2_CONF_BRIDGE_MARKER = [_][]const u8{
    "`scripts/zigux/kconfig/conf_bridge.zig`",
};

const PHASE2_CONFDATA_BRIDGE_MARKER = [_][]const u8{
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
};

const PHASE3_EXPORTS_MARKER = [_][]const u8{
    "`rust/exports.c`",
};

const PHASE3_EXPORT_SHIM_MARKER = [_][]const u8{
    "`zigux/kernel/export_shim.zig`",
};

const BITMAP_BACKLOG_MARKER = [_][]const u8{
    "runtime bitmap family stays framed as backlog-only Phase 9 support material",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (DOCS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (SEQUENCING_PATH_MARKER) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_PATH_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH_MARKER) |marker| try guard.requireMarker(text, marker);
    for (CHECKLIST_BOUNDARY_CHECKER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (TRACE_EVENTS_PACKET_CHECKER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_MARKER) |marker| try guard.requireMarker(text, marker);
    for (TRACE_EVENTS_SAMPLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SELFTEST_HOOK_MARKER) |marker| try guard.requireMarker(text, marker);
    for (LIFECYCLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_SHARED_LOADER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_PHASE9_BUILD_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_RUNTIME_TEST_FAMILY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_RUNTIME_LOADER_KERNEL_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_RUNTIME_LOADER_CONTRACT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_MAKEFILE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_WORKFLOW_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_LOADER_SCAFFOLD_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE2_CONF_BRIDGE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE2_CONFDATA_BRIDGE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE3_EXPORTS_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE3_EXPORT_SHIM_MARKER) |marker| try guard.requireMarker(text, marker);
    for (BITMAP_BACKLOG_MARKER) |marker| try guard.requireMarker(text, marker);
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
