const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_EXPORT_SURFACE_PROOF_NOTE_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "`PHASE11_HVC_EXPORT_SURFACE_PROOF_STATUS=companion_proof_landed`",
    "lane continuity: `P11-L16`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "does not replace `zigux/tests/phase11_hvc_console_survey.zig`",
    "size `72` with alignment `8`",
    "`notifier_hangup_irq`",
    "does not claim that the dedicated proof already runs through `make -C zigux phase11-hvc-survey`",
};

const PROOF_MARKERS = [_][]const u8{
    "test \"phase11 HVC exported helper proof keeps the exported helper surface layout explicit\" {",
    "layout_assert.assertSize(HvcExportSurface, 72);",
    "layout_assert.assertAlign(HvcExportSurface, 8);",
    "layout_assert.assertOffset(HvcExportSurface, \"hvc_instantiate\", 0);",
    "layout_assert.assertOffset(HvcExportSurface, \"notifier_hangup_irq\", 64);",
    "test \"phase11 HVC exported helper proof keeps exported helper signatures exact\" {",
    "assertExactType(@FieldType(HvcExportSurface, \"notifier_hangup_irq\"), HvcNotifierHangupIrqFn);",
};

const BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\"),",
    ".name = \"phase11-hvc-export-surface-layout-proof\",",
    "b.step(\"test\", \"Run the focused Phase 11 HVC exported-helper ABI proof\");",
};

const REQUIRED_FILES = [_][]const u8{
    "note",
    "Documentation/zigux/phase11-hvc-export-surface-proof-note.md",
    "proof",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "build",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PROOF_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
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
