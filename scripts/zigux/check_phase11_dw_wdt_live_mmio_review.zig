const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_DW_WDT_LIVE_MMIO_REVIEW_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "`drivers/watchdog/dw_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`,",
    "The next bounded same-lane step",
    "hardware-backed MMIO validation around",
    "suspend, resume, and platform-backed probe or remove execution",
};

const MATRIX_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig` keeps timer-clock choice",
    "`drivers/watchdog/dw_wdt.zig` and `zigux/tests/phase11_dw_wdt.zig` now rematerialize on current `master`",
    "The next bounded same-lane follow-up remains the manifest-marked ready-next step: hardware-backed MMIO validation around suspend, resume, and platform-backed probe or remove execution, without widening into unrelated driver behavior.",
};

const BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"phase11_dw_wdt_live_mmio_review.zig\")",
    "live_mmio_review_module.addImport(\"dw_wdt\", dw_wdt_module);",
    "live_mmio_review_module.addImport(\"dw_wdt_pm\", dw_wdt_pm_module);",
    ".name = \"phase11-dw-wdt-live-mmio-review-tests\"",
    "test_step.dependOn(&run_live_mmio_review_tests.step);",
};

const LIVE_MMIO_REVIEW_MARKERS = [_][]const u8{
    "test \"phase11 dw_wdt keeps live mmio timeout barriers aligned across probe and resume\" {",
    "test \"phase11 dw_wdt keeps imported-running handoff free of fabricated live mmio blockers\" {",
    "test \"phase11 dw_wdt keeps remove-time live mmio stop boundaries explicit\" {",
};

const DRIVER_MARKERS = [_][]const u8{
    "pub const PlatformHandoffRequest = struct {",
    "pub const PlatformHandoffSummary = struct {",
    "pub fn platformHandoffSummary(request: PlatformHandoffRequest) PlatformHandoffSummary {",
    "pub fn removeTeardownSummary(request: RemoveTeardownRequest) RemoveTeardownSummary {",
};

const PM_MARKERS = [_][]const u8{
    "test \"phase11 dw_wdt pm resume keeps imported-running handoff explicit\" {",
    "test \"phase11 dw_wdt pm resume keeps timeout reprogram blocker explicit\" {",
};

const FILES = [_][]const u8{
    "survey",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "matrix",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "manifest",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "build_inventory",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "build",
    "zigux/tests/phase11_dw_wdt_build.zig",
    "live_mmio_review",
    "zigux/tests/phase11_dw_wdt_live_mmio_review.zig",
    "driver",
    "drivers/watchdog/dw_wdt.zig",
    "pm",
    "drivers/watchdog/dw_wdt_pm.zig",
};

const EXPECTED_SURVEYED_COMMIT = [_][]const u8{
    "75f8336c4305beed127d7abfae37d3999b7cc57c",
};

const EXPECTED_NEXT_GAP_ID = [_][]const u8{
    "phase11-dw-wdt-live-mmio-validation",
};

const EXPECTED_NEXT_DESTINATION = [_][]const u8{
    "zigux/tests/phase11_dw_wdt.zig",
};

const EXPECTED_SHARED_BUILD = [_][]const u8{
    "zigux/tests/phase11_dw_wdt_build.zig",
};

const EXPECTED_REPLAY_COMMAND = [_][]const u8{
    "zig build test --build-file zigux/tests/phase11_dw_wdt_build.zig",
};

const EXPECTED_BUILD_TEST = [_][]const u8{
    "phase11-dw-wdt-live-mmio-review-tests",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (LIVE_MMIO_REVIEW_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DRIVER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PM_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FILES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SURVEYED_COMMIT) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_NEXT_GAP_ID) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_NEXT_DESTINATION) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SHARED_BUILD) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_REPLAY_COMMAND) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_BUILD_TEST) |marker| try guard.requireMarker(text, marker);
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
