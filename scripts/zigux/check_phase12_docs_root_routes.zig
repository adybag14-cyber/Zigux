const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_DOCS_ROOT_ROUTES_SELF_TEST=pass";

const README_MARKERS = [_][]const u8{
    "Phase 12 notes - `Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`scripts/zigux/check_build_only_phase12_surface.zig`",
    "`scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `make -C zigux phase12` keep the shipped validator-first then smoke-first release order visible",
};

const REVIEW_MARKERS = [_][]const u8{
    "if the change touches the shared Phase 12 complex-driver packet",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`scripts/zigux/check_build_only_phase12_surface.zig`",
    "`make -C zigux phase12-smoke`",
    "`make -C zigux phase12`",
    "the direct `phase12_libbpf_*` replay files stay recorded only through the shared fallback, survey, verify-shard, or anti-overlap notes until they actually land on `master`",
    "avoid implying a broader shared `check-phase12-*.py` family",
    "the shipped `make -C zigux phase12-validate` route explicit as support-bundle evidence rather than as a second direct replay route",
};

const RELEASE_READINESS_MARKERS = [_][]const u8{
    "support-bundle cross companion: `scripts/zigux/check_phase12_cross.zig`",
    "support checker: `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "Keep the same degraded-workflow validation quartet explicit too: `zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase12_cross.zig -- --self-test`, `zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test`, and `make -C zigux phase12-validate`",
    "The public fallback split must stay explicit: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the only commit-pinned direct replay fallback artifact",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_MARKERS) |marker| try guard.requireMarker(text, marker);
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
