const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_WATCHDOG_NEXT_STEP_BOUNDARY_SELF_TEST=pass";

const BCM_SURVEY_MARKERS = [_][]const u8{
    "* archival packet identity remains `P11-L08`",
    "* the Phase 11 simple-driver roadmap gap is closed at starter depth",
    "* remaining blocked work is still live platform registration, PM-base plumbing, watchdog-core registration, shared poweroff-handler execution, and hardware-backed validation beyond the current helper-backed packet",
    "* bounded watchdog-lab state transitions for `start()`, `stop()`, `restart()`, and `poweroff()`",
    "The next honest same-lane follow-through is no longer another reminder-surface add.",
    "Keep future bcm2835 work inside a later driver-local or explicit validation-plan step",
};

const DW_GAP_MARKERS = [_][]const u8{
    "- current `master` no longer has a matrix-versus-manifest continuity split",
    "- `drivers/watchdog/dw_wdt_pm.zig` now also keeps bounded suspend and resume handoff summaries explicit",
    "- nearby continuity notes in the memory folder already treat this alignment drift as closed",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` also marks `phase11-dw-wdt-live-platform-pm` as `starter_landed` at `drivers/watchdog/dw_wdt_pm.zig` and keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`",
    "- the next substantive non-doc move should now remain the manifest-backed live-MMIO validation step",
};

const FILES = [_][]const u8{
    "bcm_survey",
    "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "dw_gap",
    "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "dw_manifest",
    "zigux/tests/phase11_dw_wdt_manifest.json",
};

const EXPECTED_GAPS = [_][]const u8{
    "phase11-dw-wdt-live-platform-pm",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/watchdog/dw_wdt_pm.zig",
    "phase11-dw-wdt-live-mmio-validation",
    "status",
    "ready_next",
    "zigux_destination",
    "zigux/tests/phase11_dw_wdt.zig",
};

const EXPECTED_MANIFEST_PIN = [_][]const u8{
    "75f8336c4305beed127d7abfae37d3999b7cc57c",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (BCM_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DW_GAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FILES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GAPS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_MANIFEST_PIN) |marker| try guard.requireMarker(text, marker);
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
