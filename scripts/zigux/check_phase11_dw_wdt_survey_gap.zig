const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_DW_WDT_SURVEY_GAP_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "try std.testing.expectEqualStrings(\"P11-L05\", manifest.lane_key);",
    "try std.testing.expectEqualStrings(\"75f8336c4305beed127d7abfae37d3999b7cc57c\", manifest.surveyed_commit);",
    "try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);",
    "try std.testing.expect(manifest.survey_summary.preexisting_phase11_bcm2835_lane_present);",
    "if (std.mem.eql(u8, gap.id, \"phase11-dw-wdt-live-platform-pm\")) {",
};

const FILES = [_][]const u8{
    "survey",
    "zigux/tests/phase11_dw_wdt_survey.zig",
    "manifest",
    "zigux/tests/phase11_dw_wdt_manifest.json",
};

const SURVEY_PIN = [_][]const u8{
    "75f8336c4305beed127d7abfae37d3999b7cc57c",
};

const MANIFEST_PIN = [_][]const u8{
    "6726fdd9da4eef55498fb06c38815317a684bcbf",
};

const VERIFY_GAP_ID = [_][]const u8{
    "phase11-dw-wdt-teardown-parity",
};

const VERIFY_DESTINATION = [_][]const u8{
    "drivers/watchdog/dw_wdt_verify.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FILES) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_PIN) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PIN) |marker| try guard.requireMarker(text, marker);
    for (VERIFY_GAP_ID) |marker| try guard.requireMarker(text, marker);
    for (VERIFY_DESTINATION) |marker| try guard.requireMarker(text, marker);
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
