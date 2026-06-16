const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_GOLDEN_OUTPUT_TOOLING_GAP_SELF_TEST=pass";

const REQUIREMENTS = [_][]const u8{
    "deterministic artifact generation where applicable",
    "fixture or known-vector parity",
    "hardware validation matrix",
    "teardown and failure-mode parity",
};

const ROUTES = [_][]const u8{
    "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig",
};

const STATUSES = [_][]const u8{
    "starter_landed",
    "shared_gap_current_head",
    "ready_next",
};

const BLOCKED = [_][]const u8{
    "zigux/tests/phase11_gpio_wdt_manifest.json",
    "older wider manifest has not returned on current master",
    "zigux/tests/phase11_gpio_wdt_survey.zig",
    "older wider survey gate has not returned on current master",
    "zigux/tests/phase11_gpio_wdt.zig",
    "wider replay remains outside the current-head packet",
    "zigux/tests/phase11_gpio_wdt_platform_drvdata.zig",
    "live drvdata replay remains outside the current-head packet",
    "zigux/tests/phase11_build.zig",
    "shared Phase 11 build route has not returned on current master",
};

const DOC_MARKERS = [_][]const u8{
    "older wider replay and manifest route surfaces such as",
    "`zigux/tests/phase11_gpio_wdt_manifest.json`",
    "`zigux/tests/phase11_build.zig`",
    "hardware-backed validation",
    "current-head manifest",
    "The older wider replay and route surfaces",
    "`zigux/tests/phase11_gpio_wdt_manifest.json`",
    "`zigux/tests/phase11_build.zig`",
    "hardware-backed validation",
    "machine-readable current-head manifest",
};

const GAP = [_][]const u8{
    "zigux/tests/phase11_golden_output_tooling_gap.json",
};

const MANIFEST = [_][]const u8{
    "zigux/tests/phase11_gpio_wdt_current_head_manifest.json",
};

const SURVEY = [_][]const u8{
    "Documentation/zigux/phase11-gpio-wdt-survey.md",
};

const MATRIX = [_][]const u8{
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIREMENTS) |marker| try guard.requireMarker(text, marker);
    for (ROUTES) |marker| try guard.requireMarker(text, marker);
    for (STATUSES) |marker| try guard.requireMarker(text, marker);
    for (BLOCKED) |marker| try guard.requireMarker(text, marker);
    for (DOC_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (GAP) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST) |marker| try guard.requireMarker(text, marker);
    for (SURVEY) |marker| try guard.requireMarker(text, marker);
    for (MATRIX) |marker| try guard.requireMarker(text, marker);
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
