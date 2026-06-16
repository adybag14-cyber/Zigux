const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_TESTS_README_NVME_PACKET_CHECK_SELF_TEST=pass";

const NVME_PACKET_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase12-nvme-pci-slice.md`",
    "`Documentation/zigux/phase12-nvme-pci-survey.md`",
    "`zigux/tests/phase12_nvme_pci.zig`",
    "`zigux/tests/phase12_nvme_pci_survey.zig`",
    "`zigux/tests/phase12_nvme_pci_manifest.json`",
};

const NVME_PACKET_PATHS = [_][]const u8{
    "Path(Documentation/zigux/phase12-nvme-pci-slice.md)",
    "Path(Documentation/zigux/phase12-nvme-pci-survey.md)",
    "Path(zigux/tests/phase12_nvme_pci.zig)",
    "Path(zigux/tests/phase12_nvme_pci_survey.zig)",
    "Path(zigux/tests/phase12_nvme_pci_manifest.json)",
};

const PARKED_LIBBPF_CLAUSE = [_][]const u8{
    "the direct `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NVME_PACKET_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (NVME_PACKET_PATHS) |marker| try guard.requireMarker(text, marker);
    for (PARKED_LIBBPF_CLAUSE) |marker| try guard.requireMarker(text, marker);
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
