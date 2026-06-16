const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_LAYOUT_PROOF_PACKET_SELF_TEST=pass";

const PACKET_FILES = [_][]const u8{
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "layout_assert.expectSize(HvOps, 72);",
    "layout_assert.expectAlign(HvOps, 8);",
    "layout_assert.expectOffset(HvOps, \"dtr_rts\", 64);",
    "try expectContains(hvc_header, \"struct hv_ops {\");",
    "try expectContains(hvc_header, \"(*notifier_hangup)\");",
    "try expectContains(hvc_header, \"(*dtr_rts)\");",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "const hvc_console = @import(\"hvc_console\");",
    "test \"phase11 HVC exported helper proof keeps imported winsize field types tied to current module\" {",
    "@FieldType(hvc_console.Winsize, \"ws_row\")",
    "@FieldType(hvc_console.Winsize, \"ws_ypixel\")",
    "layout_assert.expectSize(HvOpsLayout, 72);",
    "layout_assert.expectOffset(HvcExportSurface, \"notifier_hangup_irq\", 64);",
    "assertExactType(",
    "@FieldType(HvOpsLayout, \"get_chars\")",
    "@FieldType(HvcExportSurface, \"hvc_alloc\")",
    "test \"phase11 HVC exported helper proof keeps exported HVC constants exact\" {",
    "try std.testing.expectEqual(@as(u32, 16), hvc_console.MAX_NR_HVC_CONSOLES);",
    "try std.testing.expectEqual(@as(u32, 0x01), hvc_console.HVC_ALLOC_TTY_ADAPTERS);",
    "try expectContains(hvc_header, \"#define MAX_NR_HVC_CONSOLES 16\");",
    "try expectContains(hvc_header, \"#define HVC_ALLOC_TTY_ADAPTERS 1\");",
    "try expectContains(hvc_header, \"int hvc_instantiate(uint32_t vtermno, int index, const struct hv_ops *ops);\");",
    "try expectContains(hvc_header, \"void notifier_hangup_irq(struct hvc_struct *hp, int irq);\");",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    ".root_source_file = b.path(\"../../drivers/tty/hvc/hvc_console.zig\"),",
    "export_surface_proof_module.addImport(\"hvc_console\", hvc_console_module);",
    ".root_source_file = b.path(\"phase11_hvc_hv_ops_layout_proof.zig\"),",
    ".root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\"),",
    ".name = \"phase11-hvc-hv-ops-layout-proof-tests\",",
    ".name = \"phase11-hvc-export-surface-layout-proof-tests\",",
    "b.step(\"test\", \"Run the focused Phase 11 exported-header proofs\");",
    "test_step.dependOn(&run_hv_ops_proof_tests.step);",
    "test_step.dependOn(&run_export_surface_proof_tests.step);",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (PACKET_FILES) |marker| try guard.requireMarker(text, marker);
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
