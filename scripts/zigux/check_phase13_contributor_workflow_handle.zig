const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_CONTRIBUTOR_WORKFLOW_HANDLE_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "1. `Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "2. `scripts/zigux/README.md`",
    "3. `zigux/tests/README.md`",
    "stable shared-summary guard: `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`",
    "tests-root alignment companion: `zig run scripts/zigux/check_phase13_tests_readme_alignment.zig --`",
    "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the file itself distinct from those missing Phase 13 route names and keep only the route names recorded as repo-reality gaps until the shared build handle returns.",
    "Keep `zigux/helpers/notifier_chain_view.zig`, `scripts/zigux/check_phase13_notifier_priority_signal.zig`, and `include/zigux/notifier_abi.h` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "- Phase 13 flow - the current scripts-root shared-helper packet stays reviewable through the stable contributor-facing handle",
    "- `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `Documentation/zigux/phase13-notifier-summary-gap.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/check_phase13_shared_summary_surfaces.zig`, `scripts/zigux/check_phase13_tests_readme_alignment.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared-summary and tests-root alignment packet explicit from the scripts root.",
    "- `zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep the route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle",
    "Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
    "Keep `scripts/zigux/check_phase13_tests_readme_alignment.zig` explicit as the shipped tests-root alignment companion for that stable handle rather than as a new replay route or a Makefile-backed entrypoint.",
    "Current `master` does materialize `scripts/zigux/check_phase13_shared_summary_surfaces.zig`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.",
    "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "stable shared-summary guard: `make -C zigux phase13-validate`",
    "tests-root alignment companion: `make -C zigux phase13`",
    "`zigux/Makefile` is present on current `master`, and it now exposes `make -C zigux phase13-validate`",
    "keep `make -C zigux phase13` explicit as a shipped shared build handle",
    "Current `master` still does not materialize `scripts/zigux/check_phase13_shared_summary_surfaces.zig`",
    "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
    "- `zigux/helpers/notifier_chain_view.zig`",
    "- `include/zigux/notifier_abi.h`",
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
