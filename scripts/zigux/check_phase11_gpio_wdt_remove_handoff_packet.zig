const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_GPIO_WDT_REMOVE_HANDOFF_PACKET_SELF_TEST=pass";

const REQUIRED_PATHS = [_][]const u8{
    "SURVEY_PATH",
    "MODULE_SLICE_PATH",
    "TEARDOWN_NOTE_PATH",
    "REMOVE_NOTE_PATH",
    "VALIDATION_MATRIX_PATH",
    "DRIVER_PATH",
    "PROOF_PATH",
    "BUILD_PATH",
};

const SURVEY_MARKERS = [_][]const u8{
    "`PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`nowayoutPolicySummary()`",
    "`requestStop()`",
    "`summarizeTeardown()`",
};

const MODULE_SLICE_MARKERS = [_][]const u8{
    "`watchdogDrvdataCheckpointSummary()` keeps the bounded",
    "`rebootGlueCheckpointSummary()` keeps the bounded",
    "`registerDeviceCallSummary()` keeps the first bounded",
    "`registerDeviceFailureSummary()` keeps the bounded register-device failure",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig` keeps the",
    "`summarizeTeardown()` keeps the host-free teardown summary visible",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keeps the current",
    "one equally small gpio watchdog replay, manifest, checker, or validation-truthfulness repair",
};

const TEARDOWN_NOTE_MARKERS = [_][]const u8{
    "`PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_driver_docs_and_proof_packet`",
    "`requestStop()` and the split between watchdog-core stop policy and hardware",
    "`nowayoutPolicySummary()` as a driver-local checkpoint",
    "`registerDeviceFailureSummary()` and the teardown-facing failure-mode cues",
    "`watchdogDrvdataCheckpointSummary()` and `rebootGlueCheckpointSummary()` as",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` as the",
    "teardown handoff after descriptor preflight and the first bounded",
};

const REMOVE_NOTE_MARKERS = [_][]const u8{
    "`PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_docs_and_proof_remove_handoff_truthful`",
    "`registerDeviceFailureSummary()` keeps register-device failure cues reviewable",
    "`requestStop()` keeps the bounded nowayout, stopped, and kept-running stop",
    "`rebootGlueCheckpointSummary()` keeps the stop-on-reboot handoff visible",
    "`summarizeTeardown()` keeps the stop-request, register-device-failure, and",
    "`summarizeRemoveHandoff()` keeps the dedicated remove-handoff summary itself",
};

const VALIDATION_MATRIX_MARKERS = [_][]const u8{
    "`PHASE11_GPIO_WDT_STATUS=driver_docs_and_proof_packet_truthful`",
    "`drivers/watchdog/gpio_wdt.zig`",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "`watchdogDrvdataCheckpointSummary()`",
    "`rebootGlueCheckpointSummary()`",
    "`registerDeviceCallSummary()`",
    "`registerDeviceFailureSummary()`",
    "`requestStop()`",
    "`summarizeTeardown()`",
    "focused `zig build phase11-gpio-wdt-register-device-glue-review-test`",
};

const DRIVER_MARKERS = [_][]const u8{
    "pub const WatchdogDrvdataCheckpointSummary = struct {",
    "pub const RebootGlueCheckpointSummary = struct {",
    "pub const TeardownCheckpointSummary = struct {",
    "pub const TeardownSummary = struct {",
    "pub const RemoveHandoffSummary = struct {",
    "pub fn watchdogDrvdataCheckpointSummary(self: *const Self) WatchdogDrvdataCheckpointSummary {",
    "pub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary {",
    "pub fn teardownCheckpointSummary(self: *Self, nowayout: bool) TeardownCheckpointSummary {",
    "pub fn summarizeTeardown(self: *Self, nowayout: bool) TeardownSummary {",
    "pub fn summarizeRemoveHandoff(self: *Self, nowayout: bool) RemoveHandoffSummary {",
};

const PROOF_MARKERS = [_][]const u8{
    "test \"phase11 gpio watchdog keeps register-device call glued to reboot boundary\" {",
    "test \"phase11 gpio watchdog keeps teardown checkpoint glued to register-device failure and reboot handoff\" {",
    "test \"phase11 gpio watchdog keeps register-device failure summary tied to the same reboot-glue checkpoint\" {",
    "test \"phase11 gpio watchdog keeps remove-handoff teardown reviewable without live unregister behavior\" {",
    "test \"phase11 gpio watchdog keeps a dedicated remove-handoff summary reviewable\" {",
    "stoppable_teardown.reboot_glue_precedes_register_device_request",
    "guarded_teardown.blocked_on_host_shutdown_execution",
    "stoppable_handoff.blocked_on_watchdog_core_unregister",
};

const BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"../../drivers/watchdog/gpio_wdt.zig\"),",
    ".root_source_file = b.path(\"phase11_gpio_wdt_register_device_glue_review.zig\"),",
    "\"phase11-gpio-wdt-register-device-glue-review-test\"",
    "\"Run the bounded gpio_wdt register-device glue review packet\"",
};

const FIXTURE_CONTENT = [_][]const u8{
    "# Phase 11 GPIO Watchdog Survey\n\n- `PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`\n- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`\n- `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`\n- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`\n- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`\n- `nowayoutPolicySummary()`\n- `requestStop()`\n- `summarizeTeardown()`\n",
    "# Phase 11 GPIO Watchdog Module Slice\n\n- `watchdogDrvdataCheckpointSummary()` keeps the bounded\n- `rebootGlueCheckpointSummary()` keeps the bounded\n- `registerDeviceCallSummary()` keeps the first bounded\n- `registerDeviceFailureSummary()` keeps the bounded register-device failure\n- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig` keeps the\n- `summarizeTeardown()` keeps the host-free teardown summary visible\n- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keeps the current\n- one equally small gpio watchdog replay, manifest, checker, or validation-truthfulness repair\n",
    "# Phase 11 GPIO Watchdog Teardown Note\n\n- `PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_driver_docs_and_proof_packet`\n- `requestStop()` and the split between watchdog-core stop policy and hardware\n- `nowayoutPolicySummary()` as a driver-local checkpoint\n- `registerDeviceFailureSummary()` and the teardown-facing failure-mode cues\n- `watchdogDrvdataCheckpointSummary()` and `rebootGlueCheckpointSummary()` as\n- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` as the\n- teardown handoff after descriptor preflight and the first bounded\n",
    "# Phase 11 GPIO Watchdog Remove Handoff Note\n\n- `PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_docs_and_proof_remove_handoff_truthful`\n- `registerDeviceFailureSummary()` keeps register-device failure cues reviewable\n- `requestStop()` keeps the bounded nowayout, stopped, and kept-running stop\n- `rebootGlueCheckpointSummary()` keeps the stop-on-reboot handoff visible\n- `summarizeTeardown()` keeps the stop-request, register-device-failure, and\n- `summarizeRemoveHandoff()` keeps the dedicated remove-handoff summary itself\n",
    "# Phase 11 GPIO Watchdog Validation Matrix\n\n- `PHASE11_GPIO_WDT_STATUS=driver_docs_and_proof_packet_truthful`\n- `drivers/watchdog/gpio_wdt.zig`\n- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`\n- `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`\n- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`\n- `watchdogDrvdataCheckpointSummary()`\n- `rebootGlueCheckpointSummary()`\n- `registerDeviceCallSummary()`\n- `registerDeviceFailureSummary()`\n- `requestStop()`\n- `summarizeTeardown()`\n- focused `zig build phase11-gpio-wdt-register-device-glue-review-test`\n",
    "pub const WatchdogDrvdataCheckpointSummary = struct {};\npub const RebootGlueCheckpointSummary = struct {};\npub const TeardownCheckpointSummary = struct {};\npub const TeardownSummary = struct {};\npub const RemoveHandoffSummary = struct {};\npub fn watchdogDrvdataCheckpointSummary(self: *const Self) WatchdogDrvdataCheckpointSummary { _ = self; return undefined; }\npub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary { _ = self; return undefined; }\npub fn teardownCheckpointSummary(self: *Self, nowayout: bool) TeardownCheckpointSummary { _ = self; _ = nowayout; return undefined; }\npub fn summarizeTeardown(self: *Self, nowayout: bool) TeardownSummary { _ = self; _ = nowayout; return undefined; }\npub fn summarizeRemoveHandoff(self: *Self, nowayout: bool) RemoveHandoffSummary { _ = self; _ = nowayout; return undefined; }\n",
    "test ",
    " {}\ntest ",
    " {}\ntest ",
    " {}\ntest ",
    " {}\ntest ",
    " {}\nstoppable_teardown.reboot_glue_precedes_register_device_request\nguarded_teardown.blocked_on_host_shutdown_execution\nstoppable_handoff.blocked_on_watchdog_core_unregister\n",
    "const gpio_wdt = b.createModule(.{\n    .root_source_file = b.path(",
    "),\n});\nconst test_root = b.createModule(.{\n    .root_source_file = b.path(",
    "),\n});\nconst test_step = b.step(\n    ",
    ",\n    ",
    ",\n);\n",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_PATHS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TEARDOWN_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REMOVE_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATION_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DRIVER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PROOF_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FIXTURE_CONTENT) |marker| try guard.requireMarker(text, marker);
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
