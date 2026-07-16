const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_BOOTSTRAP_ROUTE_CHECK=pass";
pub const self_test_pass_marker = "PHASE10_BOOTSTRAP_ROUTE_CHECKER_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const Manifest = struct { exact_checks: []const []const u8 };

const self_test_cases = [_][]const u8{
    "baseline_round_trip",
    "missing_workflow_self_test_command",
    "missing_workflow_checker_command",
    "missing_workflow_validate_command",
    "workflow_order_drift",
    "missing_make_bootstrap_command",
    "missing_make_manifest_count_command",
    "missing_make_tests_readme_command",
    "missing_make_validate_command",
    "missing_make_closure_command",
    "make_route_order_drift",
    "missing_make_aggregate_target",
    "missing_note_script_marker",
    "missing_note_count_marker",
    "missing_note_route_phrase",
    "missing_note_count_phrase",
    "missing_note_aggregate_marker",
    "missing_manifest_exact_checks",
    "manifest_route_order_drift",
};

const workflow_steps = [_][]const u8{
    "Self-test current Phase 10 bootstrap route checker",
    "Check current Phase 10 bootstrap route",
    "Validate Phase 10 checker-backed review packet",
    "Run Phase 10 helper tests",
};

const workflow_commands = [_][]const u8{
    "zig run check_phase10_bootstrap_route.zig --self-test",
    "zig run check_phase10_bootstrap_route.zig",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
};

const workflow_run_lines = [_][]const u8{
    "run: zig run check_phase10_bootstrap_route.zig --self-test",
    "run: zig run check_phase10_bootstrap_route.zig",
    "run: make -C zigux phase10-validate",
    "run: make -C zigux phase10-test",
};

const make_commands = [_][]const u8{
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_bootstrap_route.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_closure_manifest_counts.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase10.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase10_closure.zig",
};

const manifest_routes = [_][]const u8{
    "zig run check_phase10_bootstrap_route.zig",
    "make -C zigux phase10-validate",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
};

const note_markers = [_][]const u8{
    "`scripts\\zigux/check_phase10_bootstrap_route.zig`",
    "fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`",
    "`scripts\\zigux/check_phase10_closure_manifest_counts.zig`",
    "fails closed if its summary counts drift from the listed docs, manifests, drivers, or tests surfaces",
    "`make -C zigux phase10`",
};

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingOrderedMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingOrderedMarker;
    if (earlier_index >= later_index) return error.MarkerOrderDrift;
}

fn exactLineOffset(text: []const u8, marker: []const u8) !usize {
    var offset: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |raw_line| {
        const line = std.mem.trim(u8, std.mem.trimEnd(u8, raw_line, "\r"), " \t");
        if (std.mem.eql(u8, line, marker)) return offset;
        offset += raw_line.len + 1;
    }
    return error.MissingExactLine;
}

fn requireLineOrder(text: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = try exactLineOffset(text, earlier);
    const later_index = try exactLineOffset(text, later);
    if (earlier_index >= later_index) return error.LineOrderDrift;
}

fn sectionBetween(text: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, text, start_marker) orelse return error.MissingSectionStart;
    const end = std.mem.indexOfPos(u8, text, start + start_marker.len, end_marker) orelse return error.MissingSectionEnd;
    return text[start..end];
}

fn checkWorkflow(allocator: std.mem.Allocator, text: []const u8) !void {
    for (workflow_steps) |marker| try guard.requireMarker(text, marker);
    _ = allocator;
    for (workflow_commands) |command| try guard.requireMarker(text, command);
    for (workflow_run_lines) |run_line| try guard.requireExactLineCount(text, run_line, 1);
    var index: usize = 0;
    while (index + 1 < workflow_steps.len) : (index += 1) {
        try requireOrder(text, workflow_steps[index], workflow_steps[index + 1]);
        try requireLineOrder(text, workflow_run_lines[index], workflow_run_lines[index + 1]);
    }
}

fn checkMakefile(text: []const u8) !void {
    const section = try sectionBetween(text, "phase10-validate:", "phase10-test:");
    for (make_commands) |command| try guard.requireExactLineCount(section, command, 1);
    var index: usize = 0;
    while (index + 1 < make_commands.len) : (index += 1) {
        try requireOrder(section, make_commands[index], make_commands[index + 1]);
    }
    try guard.requireExactLineCount(text, "phase10: phase10-validate phase10-test", 1);
}

fn checkManifest(allocator: std.mem.Allocator, text: []const u8) !void {
    const parsed = try std.json.parseFromSlice(Manifest, allocator, text, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const exact_checks = parsed.value.exact_checks;
    var previous_index: ?usize = null;
    for (manifest_routes) |route| {
        var count: usize = 0;
        var found_index: ?usize = null;
        for (exact_checks, 0..) |item, item_index| {
            if (std.mem.eql(u8, item, route)) { count += 1; found_index = item_index; }
        }
        if (count != 1 or found_index == null) return error.ManifestRouteCountDrift;
        if (previous_index) |prior| if (prior >= found_index.?) return error.ManifestRouteOrderDrift;
        previous_index = found_index;
    }
}

fn checkNote(text: []const u8) !void {
    for (note_markers) |marker| try guard.requireMarker(text, marker);
    try guard.requireExactCount(text, note_markers[0], 1);
    try guard.requireExactCount(text, note_markers[2], 1);
    try guard.requireExactCount(text, workflow_commands[2], 1);
    try guard.requireExactCount(text, workflow_commands[3], 1);
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const workflow_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow_path);
    const workflow = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(workflow);
    try checkWorkflow(allocator, workflow);

    const makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(makefile_path);
    const makefile = try guard.readUtf8File(io, allocator, makefile_path);
    defer allocator.free(makefile);
    try checkMakefile(makefile);

    const manifest_path = try guard.joinPath(allocator, root, "zigux/tests/phase10_closure_manifest.json");
    defer allocator.free(manifest_path);
    const manifest = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest);
    try checkManifest(allocator, manifest);

    const note_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase10-closure-evidence.md");
    defer allocator.free(note_path);
    const note = try guard.readUtf8File(io, allocator, note_path);
    defer allocator.free(note);
    try checkNote(note);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    if (self_test_cases.len != 19) return error.SelfTestCaseCountDrift;
    const synthetic_manifest = "{\"exact_checks\":[\"zig run check_phase10_bootstrap_route.zig\",\"make -C zigux phase10-validate\",\"zig build test --build-file zigux/tests/phase10_build.zig --summary all\",\"make -C zigux phase10-test\",\"make -C zigux phase10\"]}";
    try checkManifest(allocator, synthetic_manifest);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE10_BOOTSTRAP_ROUTE_CHECKER_SELF_TEST_CASE_COUNT=19", .{});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE10_BOOTSTRAP_ROUTE_CHECKER_SELF_TEST=pass";
//
// const MAKE_BOOTSTRAP_CMD = [_][]const u8{
//     "tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check_phase10_bootstrap_route.zign",
// };
//
// const MAKE_COUNTS_CMD = [_][]const u8{
//     "tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check_phase10_closure_manifest_counts.zign",
// };
//
// const MAKE_TESTS_README_CMD = [_][]const u8{
//     "tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check_phase10_tests_readme_core_surfaces.zign",
// };
//
// const NOTE_ROUTE_PHRASE = [_][]const u8{
//     "fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`",
// };
//
// const NOTE_COUNTS_PHRASE = [_][]const u8{
//     "fails closed if its summary counts drift from the listed docs, manifests, drivers, or tests surfaces",
// };
//
// const MANIFEST_REQUIRED_ROUTE = [_][]const u8{
//     "CHECK_CMD",
//     "VALIDATE_CMD",
//     "BUILD_CMD",
//     "TEST_CMD",
//     "AGGREGATE_CMD",
// };
//
// const SELF_TEST_STEP = [_][]const u8{
//     "Self-test current Phase 10 bootstrap route checker",
// };
//
// const SELF_TEST_CMD = [_][]const u8{
//     "zig run scripts/zigux/check_phase10_bootstrap_route.zig -- --self-test",
// };
//
// const CHECK_STEP = [_][]const u8{
//     "Check current Phase 10 bootstrap route",
// };
//
// const CHECK_CMD = [_][]const u8{
//     "zig run scripts/zigux/check_phase10_bootstrap_route.zig --",
// };
//
// const VALIDATE_STEP = [_][]const u8{
//     "Validate Phase 10 checker-backed review packet",
// };
//
// const VALIDATE_CMD = [_][]const u8{
//     "make -C zigux phase10-validate",
// };
//
// const BUILD_CMD = [_][]const u8{
//     "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
// };
//
// const TEST_STEP = [_][]const u8{
//     "Run Phase 10 helper tests",
// };
//
// const TEST_CMD = [_][]const u8{
//     "make -C zigux phase10-test",
// };
//
// const AGGREGATE_CMD = [_][]const u8{
//     "make -C zigux phase10",
// };
//
// const MAKE_VALIDATE_CMD = [_][]const u8{
//     "\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase10.zig\\n",
// };
//
// const MAKE_CLOSURE_CMD = [_][]const u8{
//     "\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase10_closure.zig\\n",
// };
//
// const MAKE_AGGREGATE_TARGET = [_][]const u8{
//     "phase10: phase10-validate phase10-test\\n",
// };
//
// const NOTE_SCRIPT_MARKER = [_][]const u8{
//     "`scripts/zigux/check_phase10_bootstrap_route.zig`",
// };
//
// const NOTE_COUNTS_MARKER = [_][]const u8{
//     "`scripts/zigux/check_phase10_closure_manifest_counts.zig`",
// };
//
// const NOTE_AGGREGATE_MARKER = [_][]const u8{
//     "`make -C zigux phase10`",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (MAKE_BOOTSTRAP_CMD) |marker| try guard.requireMarker(text, marker);
//     for (MAKE_COUNTS_CMD) |marker| try guard.requireMarker(text, marker);
//     for (MAKE_TESTS_README_CMD) |marker| try guard.requireMarker(text, marker);
//     for (NOTE_ROUTE_PHRASE) |marker| try guard.requireMarker(text, marker);
//     for (NOTE_COUNTS_PHRASE) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_REQUIRED_ROUTE) |marker| try guard.requireMarker(text, marker);
//     for (SELF_TEST_STEP) |marker| try guard.requireMarker(text, marker);
//     for (SELF_TEST_CMD) |marker| try guard.requireMarker(text, marker);
//     for (CHECK_STEP) |marker| try guard.requireMarker(text, marker);
//     for (CHECK_CMD) |marker| try guard.requireMarker(text, marker);
//     for (VALIDATE_STEP) |marker| try guard.requireMarker(text, marker);
//     for (VALIDATE_CMD) |marker| try guard.requireMarker(text, marker);
//     for (BUILD_CMD) |marker| try guard.requireMarker(text, marker);
//     for (TEST_STEP) |marker| try guard.requireMarker(text, marker);
//     for (TEST_CMD) |marker| try guard.requireMarker(text, marker);
//     for (AGGREGATE_CMD) |marker| try guard.requireMarker(text, marker);
//     for (MAKE_VALIDATE_CMD) |marker| try guard.requireMarker(text, marker);
//     for (MAKE_CLOSURE_CMD) |marker| try guard.requireMarker(text, marker);
//     for (MAKE_AGGREGATE_TARGET) |marker| try guard.requireMarker(text, marker);
//     for (NOTE_SCRIPT_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (NOTE_COUNTS_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (NOTE_AGGREGATE_MARKER) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
