const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_TESTS_README_ALIGNMENT_SELF_TEST=pass";

const REQUIRED_SHIPPED_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`Documentation/zigux/phase13-shared-summary-guard-gap.md`",
    "`Documentation/zigux/phase13-notifier-summary-gap.md`",
    "`scripts/zigux/check_phase13_shared_summary_surfaces.zig`",
    "`scripts/zigux/check_phase13_tests_readme_alignment.zig`",
    "`scripts\zigux/validate_phase13_release.zig`",
    "`Documentation/zigux/phase13-landlock-ruleset-survey.md`",
    "`scripts/zigux/check_phase13_landlock_ruleset_packet.zig`",
    "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-slice.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-survey.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`",
    "`scripts/zigux/check_phase13_landlock_syscalls_packet.zig`",
    "`security/landlock/ruleset.zig`",
    "`security/landlock/syscalls.zig`",
    "`zigux/tests/phase13_landlock_ruleset.zig`",
    "`zigux/tests/phase13_landlock_ruleset_manifest.json`",
};

const REQUIRED_GAP_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-landlock-ruleset-slice.md`",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "`zigux/helpers/notifier_chain_view.zig`",
    "`include/zigux/notifier_abi.h`",
};

const REQUIRED_TEXT = [_][]const u8{
    "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality gaps rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
    "Current `master` also materializes the helper-owned Landlock survey-and-checker packet through `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `scripts/zigux/check_phase13_landlock_ruleset_packet.zig`, `scripts/zigux/check_phase13_landlock_syscalls_packet.zig`, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, and `zigux/tests/phase13_landlock_ruleset_manifest.json`, so contributor workflow wording should keep those shipped helper anchors explicit while `Documentation/zigux/phase13-landlock-ruleset-ownership.md` and `Documentation/zigux/phase13-landlock-ruleset-slice.md` stay framed as repo-reality gaps and the direct syscall replay companions stay separate repo-reality gaps.",
    "Current `master` still does not materialize `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/helpers/notifier_chain_view.zig`, or `include/zigux/notifier_abi.h`, so keep those Landlock ruleset-note, direct Landlock syscall replay, and adjacent notifier helper or header surfaces framed as repo-reality gaps rather than shipped tests-root evidence.",
    "- Does the bounded Phase 13 reminder keep the stable contributor-facing handle, the shipped helper-local `libfs`, `devres`, and Landlock anchors, the shared-summary guard, the shared release-discipline validator, the adjacent notifier checker-backed evidence, the returned-but-still-non-owner `zigux/Makefile` file, and the still-missing Phase 13 build-route, deeper devres replay, Landlock ruleset ownership and slice notes, Landlock syscall replay, adjacent notifier helper and header, and notifier-priority surfaces aligned without promoting repo-reality gaps back into shipped tests-root proof?",
};

const FORBIDDEN_SHIPPED_LINES = [_][]const u8{
    "- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "- `Documentation/zigux/phase13-landlock-ruleset-slice.md`",
    "- `zigux/tests/phase13_landlock_syscalls.zig`",
    "- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "- `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "- `zigux/helpers/notifier_chain_view.zig`",
    "- `include/zigux/notifier_abi.h`",
    "- `make -C zigux phase13-validate`",
    "- `make -C zigux phase13`",
};

const FORBIDDEN_TEXT = [_][]const u8{
    "Current `master` also materializes the helper-owned Landlock ownership and syscall-governance notes",
    "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
    "Keep `make -C zigux phase13-validate` as the stable contributor-facing handle",
};

const PHASE13_HEADING = [_][]const u8{
    "## Phase 13 shared-helper packet",
};

const PHASE13_SECTION_END = [_][]const u8{
    "Tests-root reviewer prompt:",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_SHIPPED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_GAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_TEXT) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_SHIPPED_LINES) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_TEXT) |marker| try guard.requireMarker(text, marker);
    for (PHASE13_HEADING) |marker| try guard.requireMarker(text, marker);
    for (PHASE13_SECTION_END) |marker| try guard.requireMarker(text, marker);
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
