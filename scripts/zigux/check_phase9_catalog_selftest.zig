const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_CATALOG_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "CATALOG_PATH",
    "README_PATH",
    "OWNERSHIP_MAP_PATH",
    "MANIFEST_PATH",
    "VALIDATOR_PATH",
};

const EXPECTED_PACKET_FILES = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/phase9-runtime-pilot-ownership-map.md",
    "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/phase9_catalog.zig",
    "scripts/zigux/check_phase9_catalog_selftest.zig",
    "scripts\zigux/validate_phase9.zig",
    "scripts/zigux/check_phase9_runtime_loader_shared_packet.zig",
    "scripts/zigux/check_phase9_atomic64_runtime_packet.zig",
    "scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig",
    "scripts/zigux/check_phase9_freeze_map_study_boundaries.zig",
    "scripts/zigux/check_phase9_trace_events_runtime_packet.zig",
    "scripts/zigux/check_phase9_trace_events_direct_summary.zig",
    "scripts/zigux/check_phase9_trace_events_summary_preservation.zig",
    "scripts/zigux/check_phase9_kretprobe_runtime_packet.zig",
    "zigux/kernel/runtime_loader.zig",
    "zigux/kernel/runtime_loader_contract.zig",
    "zigux/kernel/runtime_loader_command_env_boundary_guard.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase9_build.zig",
    "zigux/tests/runtime_pilot_manifest.json",
    "zigux/tests/runtime_loader_allocator_init_flow.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_module.zig",
    "zigux/tests/runtime_bitmap_manifest.json",
    "zigux/tests/runtime_bitmap_survey.zig",
    "zigux/tests/runtime_bitmap_module.zig",
    "zigux/tests/runtime_bitmap_diff.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
    "zigux/tests/runtime_trace_events_module.zig",
    "zigux/tests/runtime_kretprobe_survey.zig",
    "zigux/tests/runtime_kretprobe_module.zig",
    "zigux/tests/runtime_first_loadable_parity_behavior.zig",
    "samples/zigux/runtime_atomic64.zig",
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    "samples/zigux/runtime_bitmap.zig",
    "samples/zigux/runtime_bitmap_direct_init_contract.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_cold_stage_guard.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
    "samples/zigux/runtime_kretprobe.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig",
    "samples/zigux/runtime_kretprobe_registration_reentry_gate.zig",
    "samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig",
};

const EXPECTED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts/zigux/check_phase9_catalog_selftest.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_catalog_selftest.zig --",
    "zig run scripts/zigux/phase9_catalog.zig -- --pretty",
    "zig run scripts/zigux/validate_phase9.zig -- --self-test",
    "zig run scripts/zigux/validate_phase9.zig",
    "zig run scripts/zigux/check_phase9_runtime_loader_shared_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_runtime_loader_shared_packet.zig --",
    "zig run scripts/zigux/check_phase9_atomic64_runtime_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_atomic64_runtime_packet.zig --",
    "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_kretprobe_runtime_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_kretprobe_runtime_packet.zig --",
    "zig build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig",
};

const CATALOG_MARKERS = [_][]const u8{
    "PHASE9_CATALOG_PHASE = \"Phase 9\"",
    "PHASE9_CATALOG_LANE = \"P9-L11\"",
    "MANIFEST_PATH = Path(\"zigux/tests/runtime_pilot_manifest.json\")",
    "OWNERSHIP_MAP_PATH = Path(\"Documentation/zigux/phase9-runtime-pilot-ownership-map.md\")",
    "\"blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof\"",
    "\"scripts/zigux/check_phase9_catalog_selftest.zig\"",
    "\"scripts\zigux/validate_phase9.zig\"",
    "\"zig run scripts/zigux/phase9_catalog.zig -- --pretty\"",
    "\"zig run scripts/zigux/validate_phase9.zig\"",
    "print(\"PHASE9_CATALOG_SELF_TEST=pass\")",
};

const OWNERSHIP_MAP_MARKERS = [_][]const u8{
    "PHASE9_RUNTIME_PILOT_MANIFEST=zigux/tests/runtime_pilot_manifest.json",
    "PHASE9_RUNTIME_PILOT_CATALOG=scripts/zigux/phase9_catalog.zig",
    "PHASE9_RUNTIME_PILOT_CATALOG_SELFTEST=scripts/zigux/check_phase9_catalog_selftest.zig",
    "PHASE9_RUNTIME_PILOT_VALIDATOR=scripts\zigux/validate_phase9.zig",
    "PHASE9_RUNTIME_PILOT_SCRIPTS_ROOT=scripts/zigux/README.md",
    "PHASE9_RUNTIME_PILOT_SHARED_NOTE=Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "PHASE9_RUNTIME_PILOT_SHARED_BUILD=zigux/tests/phase9_build.zig",
    "PHASE9_RUNTIME_PILOT_BLOCKED_DEPMOD_BRIDGE_SURVEY=Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
};

const README_MARKERS = [_][]const u8{
    "scripts/zigux/phase9_catalog.zig",
    "scripts/zigux/check_phase9_catalog_selftest.zig",
    "zig run scripts/zigux/check_phase9_catalog_selftest.zig -- --self-test",
    "Documentation/zigux/phase9-runtime-pilot-ownership-map.md",
    "zigux/tests/runtime_pilot_manifest.json",
    "scripts\zigux/validate_phase9.zig",
    "zig run scripts/zigux/validate_phase9.zig -- --self-test",
    "zig run scripts/zigux/validate_phase9.zig",
};

const README_FORBIDDEN_MARKERS = [_][]const u8{
    "there is still no dedicated shared `validate-phase9.py` rerun path",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"phase\": \"Phase 9\"",
    "\"lane_key\": \"P9-L11\"",
    "\"ownership_map_path\": \"Documentation/zigux/phase9-runtime-pilot-ownership-map.md\"",
    "\"blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof\"",
    "\"scripts/zigux/phase9_catalog.zig\"",
    "\"scripts\zigux/validate_phase9.zig\"",
    "\"zigux/tests/runtime_pilot_manifest.json\"",
};

const VALIDATOR_MARKERS = [_][]const u8{
    "EXPECTED_PACKET_FILES = (",
    "\"scripts\zigux/validate_phase9.zig\",",
    "\"blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof\",",
    "EXPECTED_REPLAY_ROUTES = (",
    "\"zig run scripts/zigux/validate_phase9.zig\",",
    "PHASE9_VALIDATE_SELF_TEST=pass",
};

const EXPECTED_GAPS = [_][]const u8{
    "blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_PACKET_FILES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_REPLAY_ROUTES) |marker| try guard.requireMarker(text, marker);
    for (CATALOG_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (OWNERSHIP_MAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (README_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GAPS) |marker| try guard.requireMarker(text, marker);
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
