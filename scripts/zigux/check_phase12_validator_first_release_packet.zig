const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VALIDATOR_FIRST_RELEASE_PACKET_SELF_TEST=pass";

const REQUIRED_EXISTING_PATHS = [_][]const u8{
    "Path(Documentation/zigux/phase12-release-sequencing.md)",
    "Path(Documentation/zigux/phase12-release-closure-checklist.md)",
    "Path(Documentation/zigux/phase12-release-readiness-survey.md)",
    "Path(Documentation/zigux/phase12-release-coordination-matrix.md)",
    "Path(scripts/zigux/README.md)",
    "Path(scripts/zigux/check_build_only_phase12_surface.zig)",
    "Path(scripts/zigux/check_phase12_cross.zig)",
    "Path(scripts/zigux/check_phase12_release_readiness_packet.zig)",
    "Path(scripts\zigux/validate_phase12.zig)",
    "Path(zigux/tests/README.md)",
    "Path(zigux/tests/phase12_build.zig)",
};

const REQUIRED_MARKERS = [_][]const u8{
    "`PHASE12_STATUS=active`",
    "`PHASE12_RELEASE_CLOSED=no`",
    "release-sequencing companion: `Documentation/zigux/phase12-release-sequencing.md`",
    "release-coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`",
    "release-closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`",
    "support-bundle checkers: `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_cross.zig`, and `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "shared validator route: `scripts\zigux/validate_phase12.zig` and `make -C zigux phase12-validate`",
    "keep the validator-first support bundle explicit before the smoke-first replay order: `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`",
    "if `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order through `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`",
    "do not widen this note into a focused libbpf-only replay, a shared cross-build replay, or a broader shared `check-phase12-*.py` family",
    "the direct `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_EXISTING_PATHS) |marker| try guard.requireMarker(text, marker);
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
