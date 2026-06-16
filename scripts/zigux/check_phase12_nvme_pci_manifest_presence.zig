const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_NVME_PCI_MANIFEST_PRESENCE_SELF_TEST=pass";

const REQUIRED_PRESENCE_FLAGS = [_][]const u8{
    "preexisting_nvme_pci_zig_present",
    "drivers/nvme/host/pci.zig",
    "preexisting_nvme_pci_verifier_present",
    "drivers/nvme/host/pci_verify.zig",
    "preexisting_phase12_direct_test_present",
    "zigux/tests/phase12_nvme_pci.zig",
    "preexisting_phase12_build_present",
    "zigux/tests/phase12_build.zig",
    "preexisting_phase12_make_targets_present",
    "zigux/Makefile",
    "preexisting_phase12_fallback_note_present",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "preexisting_phase12_reopen_governance_present",
    "Documentation/zigux/phase12-nvme-pci-reopen-governance.md",
    "preexisting_phase12_slice_note_present",
    "Documentation/zigux/phase12-nvme-pci-slice.md",
    "preexisting_phase12_survey_note_present",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "preexisting_phase12_survey_gate_present",
    "zigux/tests/phase12_nvme_pci_survey.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_PRESENCE_FLAGS) |marker| try guard.requireMarker(text, marker);
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
