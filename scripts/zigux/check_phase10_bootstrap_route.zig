const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_BOOTSTRAP_ROUTE_CHECKER_SELF_TEST=pass";

const MAKE_BOOTSTRAP_CMD = [_][]const u8{
    "tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check_phase10_bootstrap_route.zign",
};

const MAKE_COUNTS_CMD = [_][]const u8{
    "tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check_phase10_closure_manifest_counts.zign",
};

const MAKE_TESTS_README_CMD = [_][]const u8{
    "tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check_phase10_tests_readme_core_surfaces.zign",
};

const NOTE_ROUTE_PHRASE = [_][]const u8{
    "fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`",
};

const NOTE_COUNTS_PHRASE = [_][]const u8{
    "fails closed if its summary counts drift from the listed docs, manifests, drivers, or tests surfaces",
};

const MANIFEST_REQUIRED_ROUTE = [_][]const u8{
    "CHECK_CMD",
    "VALIDATE_CMD",
    "BUILD_CMD",
    "TEST_CMD",
    "AGGREGATE_CMD",
};

const SELF_TEST_STEP = [_][]const u8{
    "Self-test current Phase 10 bootstrap route checker",
};

const SELF_TEST_CMD = [_][]const u8{
    "zig run scripts/zigux/check_phase10_bootstrap_route.zig -- --self-test",
};

const CHECK_STEP = [_][]const u8{
    "Check current Phase 10 bootstrap route",
};

const CHECK_CMD = [_][]const u8{
    "zig run scripts/zigux/check_phase10_bootstrap_route.zig --",
};

const VALIDATE_STEP = [_][]const u8{
    "Validate Phase 10 checker-backed review packet",
};

const VALIDATE_CMD = [_][]const u8{
    "make -C zigux phase10-validate",
};

const BUILD_CMD = [_][]const u8{
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
};

const TEST_STEP = [_][]const u8{
    "Run Phase 10 helper tests",
};

const TEST_CMD = [_][]const u8{
    "make -C zigux phase10-test",
};

const AGGREGATE_CMD = [_][]const u8{
    "make -C zigux phase10",
};

const MAKE_VALIDATE_CMD = [_][]const u8{
    "\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase10.zig\\n",
};

const MAKE_CLOSURE_CMD = [_][]const u8{
    "\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase10_closure.zig\\n",
};

const MAKE_AGGREGATE_TARGET = [_][]const u8{
    "phase10: phase10-validate phase10-test\\n",
};

const NOTE_SCRIPT_MARKER = [_][]const u8{
    "`scripts/zigux/check_phase10_bootstrap_route.zig`",
};

const NOTE_COUNTS_MARKER = [_][]const u8{
    "`scripts/zigux/check_phase10_closure_manifest_counts.zig`",
};

const NOTE_AGGREGATE_MARKER = [_][]const u8{
    "`make -C zigux phase10`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (MAKE_BOOTSTRAP_CMD) |marker| try guard.requireMarker(text, marker);
    for (MAKE_COUNTS_CMD) |marker| try guard.requireMarker(text, marker);
    for (MAKE_TESTS_README_CMD) |marker| try guard.requireMarker(text, marker);
    for (NOTE_ROUTE_PHRASE) |marker| try guard.requireMarker(text, marker);
    for (NOTE_COUNTS_PHRASE) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_REQUIRED_ROUTE) |marker| try guard.requireMarker(text, marker);
    for (SELF_TEST_STEP) |marker| try guard.requireMarker(text, marker);
    for (SELF_TEST_CMD) |marker| try guard.requireMarker(text, marker);
    for (CHECK_STEP) |marker| try guard.requireMarker(text, marker);
    for (CHECK_CMD) |marker| try guard.requireMarker(text, marker);
    for (VALIDATE_STEP) |marker| try guard.requireMarker(text, marker);
    for (VALIDATE_CMD) |marker| try guard.requireMarker(text, marker);
    for (BUILD_CMD) |marker| try guard.requireMarker(text, marker);
    for (TEST_STEP) |marker| try guard.requireMarker(text, marker);
    for (TEST_CMD) |marker| try guard.requireMarker(text, marker);
    for (AGGREGATE_CMD) |marker| try guard.requireMarker(text, marker);
    for (MAKE_VALIDATE_CMD) |marker| try guard.requireMarker(text, marker);
    for (MAKE_CLOSURE_CMD) |marker| try guard.requireMarker(text, marker);
    for (MAKE_AGGREGATE_TARGET) |marker| try guard.requireMarker(text, marker);
    for (NOTE_SCRIPT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (NOTE_COUNTS_MARKER) |marker| try guard.requireMarker(text, marker);
    for (NOTE_AGGREGATE_MARKER) |marker| try guard.requireMarker(text, marker);
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
