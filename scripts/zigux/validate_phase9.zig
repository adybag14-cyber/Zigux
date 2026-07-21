const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE9_VALIDATE=pass";
pub const self_test_pass_marker = "PHASE9_VALIDATE_SELF_TEST=pass";

const EXPECTED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase9_catalog_selftest.zig -- --self-test",
    "zig run scripts\\zigux/check_phase9_catalog_selftest.zig",
    "zig run scripts/zigux/phase9_catalog.zig -- --pretty",
    "zig run scripts\\zigux/validate_phase9.zig -- --self-test",
    "zig run scripts\\zigux/validate_phase9.zig",
    "zig run scripts\\zigux/check_phase9_runtime_loader_shared_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase9_runtime_loader_shared_packet.zig",
    "zig run scripts\\zigux/check_phase9_atomic64_runtime_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase9_atomic64_runtime_packet.zig",
    "zig run scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig -- --self-test",
    "zig run scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig -- --self-test",
    "zig run scripts\\zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase9_trace_events_direct_summary.zig -- --self-test",
    "zig run scripts\\zigux/check_phase9_trace_events_summary_preservation.zig -- --self-test",
    "zig run scripts\\zigux/check_phase9_kretprobe_runtime_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase9_kretprobe_runtime_packet.zig",
    "zig build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig",
};

const EXPECTED_GAPS = [_][]const u8{
    "blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof",
};

const EXPECTED_NEXT_SAFE_STEP = [_][]const u8{
    "tighten one shared reminder surface at a time where current master still undercounts the blocked module-metadata and depmod bridge boundary before widening into runtime behavior, build wiring, or install-root claims",
};

const REQUIRED_OWNERSHIP_MARKERS = [_][]const u8{
    "PHASE9_RUNTIME_PILOT_MANIFEST=zigux/tests/runtime_pilot_manifest.json",
    "PHASE9_RUNTIME_PILOT_CATALOG=scripts/zigux/phase9_catalog.zig",
    "PHASE9_RUNTIME_PILOT_CATALOG_SELFTEST=scripts\\zigux/check_phase9_catalog_selftest.zig",
    "PHASE9_RUNTIME_PILOT_VALIDATOR=scripts\\zigux/validate_phase9.zig",
    "PHASE9_RUNTIME_PILOT_BLOCKED_DEPMOD_BRIDGE_SURVEY=Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
};

const REQUIRED_README_MARKERS = [_][]const u8{
    "scripts\\zigux/validate_phase9.zig",
    "zig run scripts\\zigux/validate_phase9.zig -- --self-test",
    "zig run scripts\\zigux/validate_phase9.zig",
};

const FORBIDDEN_README_MARKERS = [_][]const u8{
    "there is still no dedicated shared `validate-phase9.py` rerun path",
};

const CHECKERS = [_][]const u8{
    "Pathscripts\\zigux/check_phase9_runtime_loader_shared_packet.zig",
    "Pathscripts\\zigux/check_phase9_atomic64_runtime_packet.zig",
    "Pathscripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig",
    "Pathscripts\\zigux/check_phase9_freeze_map_study_boundaries.zig",
    "Pathscripts\\zigux/check_phase9_trace_events_runtime_packet.zig",
    "Pathscripts\\zigux/check_phase9_trace_events_direct_summary.zig",
    "Pathscripts\\zigux/check_phase9_trace_events_summary_preservation.zig",
    "Pathscripts\\zigux/check_phase9_kretprobe_runtime_packet.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md");
    defer allocator.free(text_expected_replay_routes_path);
    const text_expected_replay_routes = try guard.readUtf8File(io, allocator, text_expected_replay_routes_path);
    defer allocator.free(text_expected_replay_routes);
    for (EXPECTED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_expected_replay_routes, marker);
    const text_expected_gaps_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md");
    defer allocator.free(text_expected_gaps_path);
    const text_expected_gaps = try guard.readUtf8File(io, allocator, text_expected_gaps_path);
    defer allocator.free(text_expected_gaps);
    for (EXPECTED_GAPS) |marker| try guard.requireMarker(text_expected_gaps, marker);
    const text_expected_next_safe_step_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md");
    defer allocator.free(text_expected_next_safe_step_path);
    const text_expected_next_safe_step = try guard.readUtf8File(io, allocator, text_expected_next_safe_step_path);
    defer allocator.free(text_expected_next_safe_step);
    for (EXPECTED_NEXT_SAFE_STEP) |marker| try guard.requireMarker(text_expected_next_safe_step, marker);
    const text_required_ownership_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md");
    defer allocator.free(text_required_ownership_markers_path);
    const text_required_ownership_markers = try guard.readUtf8File(io, allocator, text_required_ownership_markers_path);
    defer allocator.free(text_required_ownership_markers);
    for (REQUIRED_OWNERSHIP_MARKERS) |marker| try guard.requireMarker(text_required_ownership_markers, marker);
    const text_required_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md");
    defer allocator.free(text_required_readme_markers_path);
    const text_required_readme_markers = try guard.readUtf8File(io, allocator, text_required_readme_markers_path);
    defer allocator.free(text_required_readme_markers);
    for (REQUIRED_README_MARKERS) |marker| try guard.requireMarker(text_required_readme_markers, marker);
    const text_forbidden_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md");
    defer allocator.free(text_forbidden_readme_markers_path);
    const text_forbidden_readme_markers = try guard.readUtf8File(io, allocator, text_forbidden_readme_markers_path);
    defer allocator.free(text_forbidden_readme_markers);
    for (FORBIDDEN_README_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_readme_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_checkers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_checkers_path);
    const text_checkers = try guard.readUtf8File(io, allocator, text_checkers_path);
    defer allocator.free(text_checkers);
    for (CHECKERS) |marker| try guard.requireMarker(text_checkers, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
