const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_GPIO_WDT_REMOVE_HANDOFF_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "`PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_plus_docs_remove_handoff_truthful`",
    "`drivers/watchdog/gpio_wdt.zig`",
    "`Documentation/zigux/phase11-gpio-wdt-survey.md`",
    "`Documentation/zigux/phase11-gpio-wdt-module-slice.md`",
    "`Documentation/zigux/phase11-gpio-wdt-teardown-note.md`",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "do not rematerialize `zigux/tests/phase11_gpio_wdt.zig`",
    "`registerDeviceFailureSummary()` keeps register-device failure cues reviewable before any later remove-hook execution claim",
    "`requestStop()` keeps the bounded nowayout, stopped, and kept-running stop split explicit before any platform cleanup callback claim",
    "`rebootGlueCheckpointSummary()` keeps the stop-on-reboot handoff visible before any later remove-hook execution claim",
    "`summarizeTeardown()` keeps the stop-request, register-device-failure, and reboot-glue checkpoint cues reviewable as a host-free remove-handoff packet",
    "does not claim live platform cleanup callbacks, platform-driver removal, watchdog-core unregister side effects, reboot-backed teardown execution, or hardware-backed validation",
    "focused replay or manifest recovery, or another equally small gpio watchdog truthfulness repair",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "`PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=remove_hook_runtime_validated`",
    "claims live platform cleanup callbacks",
    "claims live platform-driver removal",
    "claims watchdog-core unregister side effects",
};

const NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (NOTE_PATH) |marker| try guard.requireMarker(text, marker);
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
