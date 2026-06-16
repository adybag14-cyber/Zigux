const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_SCRIPTS_README_RELEASE_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "Path(Documentation/zigux/phase12-release-sequencing.md)",
    "Path(Documentation/zigux/phase12-release-readiness-survey.md)",
    "Path(Documentation/zigux/phase12-release-coordination-matrix.md)",
    "Path(Documentation/zigux/phase12-virtio-net-survey.md)",
    "Path(Documentation/zigux/phase12-nvme-pci-slice.md)",
    "Path(Documentation/zigux/phase12-nvme-pci-survey.md)",
    "Path(zigux/tests/phase12_build.zig)",
    "Path(zigux/tests/phase12_nvme_pci.zig)",
    "Path(zigux/tests/phase12_nvme_pci_survey.zig)",
    "Path(zigux/tests/phase12_nvme_pci_manifest.json)",
    "Path(scripts/zigux/check_build_only_phase12_surface.zig)",
    "Path(scripts/zigux/check_phase12_cross.zig)",
    "Path(scripts/zigux/check_phase12_release_readiness_packet.zig)",
    "Path(scripts\zigux/validate_phase12.zig)",
};

const REQUIRED_MARKERS = [_][]const u8{
    "Phase 12 flow - `validate-phase12.py` checks that the current complex-driver packet stays aligned across",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase12-virtio-net-survey.md`",
    "`Documentation/zigux/phase12-nvme-pci-slice.md`",
    "`Documentation/zigux/phase12-nvme-pci-survey.md`",
    "`zigux/tests/phase12_nvme_pci.zig`",
    "`zigux/tests/phase12_nvme_pci_survey.zig`",
    "`zigux/tests/phase12_nvme_pci_manifest.json`",
    "`scripts/zigux/check_phase12_scripts_readme_release_packet.zig`",
    "`zig run scripts/zigux/check_phase12_scripts_readme_release_packet.zig -- --self-test`",
    "`make -C zigux phase12-validate`",
    "`make -C zigux phase12-smoke`",
    "`make -C zigux phase12`",
    "the direct `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
    "broader shared `check-phase12-*.py` family",
    "make -C zigux phase12-smoke ZIG=<attached-zig-path>",
    "make -C zigux phase12 ZIG=<attached-zig-path>",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
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
