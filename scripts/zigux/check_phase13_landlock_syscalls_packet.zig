const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "security/landlock/syscalls.zig",
    "provides_abi_errata_query_planning",
    "provides_ruleset_fd_lookup_planning",
    "provides_ruleset_fd_install_planning",
    "provides_ruleset_fd_stub_planning",
    "provides_ruleset_release_planning",
    "LANDLOCK_CREATE_RULESET_ERRATA",
    "LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON",
    "LANDLOCK_RESTRICT_SELF_TSYNC",
    "planLandlockCreateRuleset",
    "planGetRulesetFromFd",
    "planLandlockRestrictSelf",
    "planLandlockAddRule",
    "planInstallRulesetFd",
    "planRulesetFdStub",
    "planFopRulesetRelease",
    "ruleset_fops_present",
    "required_ruleset_fd_mode_bits",
    "FMODE_CAN_READ",
    "FMODE_CAN_WRITE",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "phase13 landlock syscalls create-handle path reuses the fd install planner",
    "phase13 landlock syscalls restrict-self planner keeps logging and tsync flags explicit",
    "phase13 landlock syscalls add-rule planner reuses fd lookup and delegated tree helpers",
    "phase13 landlock syscalls stub and release helpers stay planning-only",
    "Documentation/zigux/phase13-landlock-syscalls-slice.md",
    "active materialized helper-local, direct replay, and reviewability packet companions",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "historical breadcrumb for older lane notes and review references, not as active packet evidence",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json` and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps",
    "Documentation/zigux/phase13-landlock-syscalls-governance.md",
    "helper-local packet plus the direct replay and direct reviewability companions",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "Current `master` now materializes this helper-local, direct replay, and reviewability packet through:",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "historical breadcrumb for older lane notes and review references, not as active packet evidence",
    "Current `master` still leaves these directly coupled companions absent:",
    "Documentation/zigux/phase13-landlock-syscalls-survey-gap.md",
    "`zigux/tests/phase13_landlock_syscalls.zig` as a returned direct replay companion",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig` as a returned reviewability companion",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "phase13 landlock syscalls direct replay covers the current planner packet",
    "active materialized helper-local, direct replay, and reviewability packet companions",
    "historical breadcrumb for older lane notes and review references, not as active packet evidence",
    "Current `master` now materializes this helper-local, direct replay, and reviewability packet through:",
    "current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "Documentation/zigux/phase13-landlock-syscalls-slice.md",
    "`zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps",
    "Documentation/zigux/phase13-landlock-syscalls-governance.md",
    "`zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and `zigux/tests/phase13_build.zig`",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "Current `master` still leaves these directly coupled companions absent:n- `zigux/tests/phase13_landlock_syscalls.zig`",
    "Documentation/zigux/phase13-landlock-syscalls-survey-gap.md",
    "The remaining directly coupled gaps stay outside this bounded helper-local step:n- `zigux/tests/phase13_landlock_syscalls.zig`",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "## Repo-Reality GapsnnKeep the remaining current gaps explicit:n- docs-root `Documentation/zigux/README.md` still lacks a dedicated Phase 13 reminder blockn- `make -C zigux phase13-validate`n- `make -C zigux phase13`n- `zigux/tests/phase13_build.zig`n- `zigux/tests/phase13_devres.zig`n- `zigux/tests/phase13_devres_reviewability.zig`n- `zigux/tests/phase13_devres_boundary_evidence.zig`n- `zigux/tests/phase13_devres_manifest.json`n- `scripts/zigux/check_phase13_devres_packet.zig`n- `scripts/zigux/check_phase13_devres_packet_alignment.zig`n- `zigux/tests/phase13_landlock_syscalls.zig`",
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
