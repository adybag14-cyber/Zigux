const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_PHASE11_PHASE13_VALIDATOR_FIRST_GUIDE_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Keep `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` aligned with this note when they describe the same contributor-facing packets.",
    "- `make -C zigux phase10-validate`",
    "- `make -C zigux phase10-test`",
    "- `make -C zigux phase10`",
    "- `zig run scripts/zigux/check_phase11_build_inventory.zig --`",
    "- `zig run scripts/zigux/check_phase11_matrix_gap_survey.zig --`",
    "- `zig run scripts/zigux/check_phase11_validation_matrix_gap_survey.zig --`",
    "- `zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig --`",
    "- `zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "- `zigux/Makefile` is present on current `master`, but it still exposes no dedicated `make -C zigux phase11`, `make -C zigux phase11-validate`, or `make -C zigux phase11-contract` routes.",
    "- `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`",
    "- `zig run scripts/zigux/check_phase13_tests_readme_alignment.zig --`",
    "- `zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`.",
    "- `scripts\zigux/validate_phase13_release.zig`, `scripts/zigux/check_phase13_devres_packet_alignment.zig`, `scripts/zigux/check_phase13_landlock_ruleset_packet.zig`, `scripts/zigux/check_phase13_notifier_priority_signal.zig`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` remain repo-reality gaps rather than shipped current-`master` evidence.",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "- `make -C zigux phase11-validate`",
    "- `make -C zigux phase11`",
    "- `zig run scripts/zigux/check_phase11_shared_replay_contract.zig --`",
    "- `zig run scripts/zigux/check_phase13_libfs_packet.zig -- --self-test`",
    "- `make -C zigux phase13-validate`",
    "- `make -C zigux phase13`",
    "- `zigux/tests/phase13_build.zig`",
    "- `zigux/helpers/notifier_chain_view.zig`",
    "- `Documentation/zigux/phase13-landlock-syscalls-survey.md`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
