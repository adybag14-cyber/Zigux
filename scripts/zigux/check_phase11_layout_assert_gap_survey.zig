const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_LAYOUT_ASSERT_GAP_SURVEY_SELF_TEST=pass";

const DEFAULT_ROOT = [_][]const u8{
    "Path.resolve.parents[2]iflen>3elsePath.cwd",
};

const RETIRED_SHARED_REPLAY_PATHS = [_][]const u8{
    "Pathzigux/tests/phase11_uapi_header_parity_manifest.json",
    "Pathzigux/tests/phase11_uapi_header_parity_survey.zig",
};

const SURVEY_MARKERS = [_][]const u8{
    "`zigux/helpers/layout_assert.zig`",
    "that narrower proof packet remains `layout_assert`-backed",
    "current `master` still lacks the broader shared ABI replay",
    "`phase11-shared-reminder-surface-gap`",
};

const HV_OPS_PROOF_MARKERS = [_][]const u8{
    "const layout_assert = @import(\"layout_assert\");",
    "try layout_assert.expectSize(HvOps, 72);",
    "try layout_assert.expectOffset(HvOps, \"dtr_rts\", 64);",
    "try layout_assert.expectSize(hvc_console.HvOps, 72);",
    "try layout_assert.expectOffset(hvc_console.HvOps, \"notifier_hangup\", 40);",
    "@FieldType(hvc_console.HvOps, \"notifier_hangup\")",
};

const EXPORT_PROOF_MARKERS = [_][]const u8{
    "const layout_assert = @import(\"layout_assert\");",
    "try layout_assert.expectSize(WinsizeLayout, 8);",
    "try layout_assert.expectOffset(WinsizeLayout, \"ws_ypixel\", 6);",
    "try layout_assert.expectSize(HvcExportSurface, 72);",
    "try layout_assert.expectOffset(HvcExportSurface, \"notifier_hangup_irq\", 64);",
    "@TypeOf(hvc_console.notifier_hangup_irq)",
    "void notifier_hangup_irq(struct hvc_struct *hp, int irq);",
};

const INVENTORY_MARKERS = [_][]const u8{
    "\"phase11-hvc-hv-ops-layout-proof-tests\"",
    "\"phase11-hvc-export-surface-layout-proof-tests\"",
    "\"zigux/tests/phase11_hvc_hv_ops_layout_build.zig\"",
    "\"zigux/tests/phase11_hvc_export_surface_layout_build.zig\"",
};

const SIMPLE_DRIVER_BUILD_MARKERS = [_][]const u8{
    "\"phase11-gpio-wdt-verify-tests\"",
    "\"phase11-hvc-console-verify-tests\"",
    "\"phase11-simple-drivers\"",
    "Run Phase 11 simple-driver verification replays",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (DEFAULT_ROOT) |marker| try guard.requireMarker(text, marker);
    for (RETIRED_SHARED_REPLAY_PATHS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HV_OPS_PROOF_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPORT_PROOF_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (INVENTORY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SIMPLE_DRIVER_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
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
