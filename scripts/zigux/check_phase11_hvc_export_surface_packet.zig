const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_EXPORT_SURFACE_PACKET_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "focused export-surface proofs",
    "`zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
};

const MATRIX_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "focused exported surface proofs",
    "`zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
};

const PROOF_MARKERS = [_][]const u8{
    "const HvcExportSurface = extern struct {",
    "try layout_assert.expectSize(HvcExportSurface, 72);",
    "try layout_assert.expectOffset(HvcExportSurface, \"hvc_instantiate\", 0);",
    "try layout_assert.expectOffset(HvcExportSurface, \"notifier_hangup_irq\", 64);",
    "assertExactType(@FieldType(HvcExportSurface, \"hvc_alloc\"), HvcAllocFn);",
    "try expectContains(hvc_header, \"int hvc_instantiate(uint32_t vtermno, int index, const struct hv_ops *ops);\");",
};

const BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\"),",
    "proof_module.addImport(\"hvc_console\", hvc_console_module);",
    ".name = \"phase11-hvc-export-surface-layout-proof\",",
    "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC exported-helper ABI proof\");",
};

const SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase11-hvc-console-survey.md",
};

const MATRIX_PATH = [_][]const u8{
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
};

const PROOF_PATH = [_][]const u8{
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
};

const BUILD_PATH = [_][]const u8{
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PROOF_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
    for (PROOF_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_PATH) |marker| try guard.requireMarker(text, marker);
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
