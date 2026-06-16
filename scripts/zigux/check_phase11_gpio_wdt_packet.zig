const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_GPIO_WDT_PACKET_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "`PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`",
    "current authenticated contents readback keeps the bounded gpio watchdog packet",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "That current packet now also keeps the bounded remove-handoff packet explicit",
    "focused replay recovery or another equally small truthfulness repair",
};

const MODULE_SLICE_MARKERS = [_][]const u8{
    "`registerDeviceCallSummary()` keeps the first bounded",
    "`registerDeviceFailureSummary()` keeps the bounded register-device failure",
    "`summarizeTeardown()` keeps the host-free teardown summary visible",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keeps the current remove-handoff packet explicit",
    "one equally small gpio watchdog replay, manifest, checker, or validation-truthfulness repair",
};

const TEARDOWN_MARKERS = [_][]const u8{
    "`PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_driver_docs_and_proof_packet`",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "as the companion surface that keeps the bounded remove-handoff packet explicit",
    "The returned driver-backed packet also keeps the stop-transition",
};

const REMOVE_HANDOFF_MARKERS = [_][]const u8{
    "`PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_docs_and_proof_remove_handoff_truthful`",
    "The current remove-handoff-facing gpio packet on `master` is:",
    "`registerDeviceFailureSummary()` keeps register-device failure cues reviewable",
    "`requestStop()` keeps the bounded nowayout, stopped, and kept-running stop",
    "`summarizeTeardown()` keeps the stop-request, register-device-failure, and",
};

const VALIDATION_MATRIX_MARKERS = [_][]const u8{
    "`PHASE11_GPIO_WDT_STATUS=driver_docs_and_proof_packet_truthful`",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "remove-handoff note: `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "The next honest gpio-only follow-up is still one equally small replay,",
};

const DRIVER_MARKERS = [_][]const u8{
    "pub const WatchdogDrvdataCheckpointSummary = struct {",
    "pub const RegisterDeviceFailureSummary = struct {",
    "pub const RebootGlueCheckpointSummary = struct {",
    "pub const TeardownSummary = struct {",
    "pub fn watchdogDrvdataCheckpointSummary(self: *const Self) WatchdogDrvdataCheckpointSummary {",
    "pub fn registerDeviceFailureSummary(self: *const Self, nowayout: bool) RegisterDeviceFailureSummary {",
    "pub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary {",
    "pub fn summarizeTeardown(self: *Self, nowayout: bool) TeardownSummary {",
    "test \"phase11 gpio watchdog keeps remove-handoff teardown reviewable without live unregister behavior\" {",
};

const PROOF_MARKERS = [_][]const u8{
    "test \"phase11 gpio watchdog keeps register-device call glued to reboot boundary\" {",
    "test \"phase11 gpio watchdog keeps remove-handoff teardown reviewable without live unregister behavior\" {",
};

const FORBIDDEN_SURVEY_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_gpio_wdt.zig` is directly readable on current `master`",
    "`zigux/Makefile` now exposes `make -C zigux phase11-gpio-wdt`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TEARDOWN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REMOVE_HANDOFF_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATION_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DRIVER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PROOF_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
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
