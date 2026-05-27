const std = @import("std");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireDoesNotContain(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1 << 20));
}

test "phase13 landlock syscalls helper keeps the planner-expanded syscall packet explicit" {
    const helper = try readRepoFile(std.testing.allocator, "security/landlock/syscalls.zig");
    defer std.testing.allocator.free(helper);

    try requireContains(helper, "provides_abi_errata_query_planning");
    try requireContains(helper, "provides_ruleset_fd_lookup_planning");
    try requireContains(helper, "provides_ruleset_fd_install_planning");
    try requireContains(helper, "provides_ruleset_fd_stub_planning");
    try requireContains(helper, "provides_ruleset_release_planning");
    try requireContains(helper, "LANDLOCK_CREATE_RULESET_ERRATA");
    try requireContains(helper, "LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON");
    try requireContains(helper, "LANDLOCK_RESTRICT_SELF_TSYNC");
    try requireContains(helper, "planLandlockCreateRuleset");
    try requireContains(helper, "planGetRulesetFromFd");
    try requireContains(helper, "planLandlockRestrictSelf");
    try requireContains(helper, "planLandlockAddRule");
    try requireContains(helper, "planInstallRulesetFd");
    try requireContains(helper, "planRulesetFdStub");
    try requireContains(helper, "planFopRulesetRelease");
    try requireContains(helper, "ruleset_fops_present");
    try requireContains(helper, "required_ruleset_fd_mode_bits");
    try requireContains(helper, "FMODE_CAN_READ");
    try requireContains(helper, "FMODE_CAN_WRITE");
}

test "phase13 landlock syscalls direct replay covers the current planner packet" {
    const direct = try readRepoFile(std.testing.allocator, "zigux/tests/phase13_landlock_syscalls.zig");
    defer std.testing.allocator.free(direct);

    try requireContains(direct, "phase13 landlock syscalls create-handle path reuses the fd install planner");
    try requireContains(direct, "phase13 landlock syscalls restrict-self planner keeps logging and tsync flags explicit");
    try requireContains(direct, "phase13 landlock syscalls add-rule planner reuses fd lookup and delegated tree helpers");
    try requireContains(direct, "phase13 landlock syscalls stub and release helpers stay planning-only");
    try requireContains(direct, "planLandlockCreateRuleset");
    try requireContains(direct, "planLandlockRestrictSelf");
    try requireContains(direct, "planLandlockAddRule");
    try requireContains(direct, "planRulesetFdStub");
    try requireContains(direct, "planFopRulesetRelease");
}

test "phase13 landlock syscalls docs keep the survey-gap note breadcrumb-only" {
    const slice = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-landlock-syscalls-slice.md");
    defer std.testing.allocator.free(slice);
    try requireContains(slice, "`zigux/tests/phase13_landlock_syscalls.zig`");
    try requireContains(slice, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try requireContains(slice, "active materialized helper-local, direct replay, and reviewability packet companions");
    try requireContains(slice, "`Documentation/zigux/phase13-landlock-syscalls-survey-gap.md` adjacent only as a historical breadcrumb for older lane notes and review references, not as active packet evidence");
    try requireContains(slice, "`zigux/tests/phase13_landlock_syscalls_manifest.json` and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps");
    try requireDoesNotContain(slice, "`zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps");

    const governance = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-landlock-syscalls-governance.md");
    defer std.testing.allocator.free(governance);
    try requireContains(governance, "helper-local packet plus the direct replay and direct reviewability companions");
    try requireContains(governance, "`zigux/tests/phase13_landlock_syscalls.zig`");
    try requireContains(governance, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try requireContains(governance, "`zigux/tests/phase13_landlock_syscalls_manifest.json`");
    try requireContains(governance, "historical breadcrumb for older lane notes and review references");
    try requireDoesNotContain(governance, "`zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and `zigux/tests/phase13_build.zig`");
}

test "phase13 landlock syscalls survey and breadcrumb narrow the remaining gaps after the direct replay lands" {
    const survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-landlock-syscalls-survey.md");
    defer std.testing.allocator.free(survey);
    try requireContains(survey, "Current `master` now materializes this helper-local, direct replay, and reviewability packet through:");
    try requireContains(survey, "`zigux/tests/phase13_landlock_syscalls.zig`");
    try requireContains(survey, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try requireContains(survey, "`Documentation/zigux/phase13-landlock-syscalls-survey-gap.md` adjacent only as a historical breadcrumb for older lane notes and review references, not as active packet evidence");
    try requireContains(survey, "Current `master` still leaves these directly coupled companions absent:");
    try requireContains(survey, "`zigux/tests/phase13_landlock_syscalls_manifest.json`");
    try requireDoesNotContain(survey, "Current `master` still leaves these directly coupled companions absent:\n- `zigux/tests/phase13_landlock_syscalls.zig`");

    const survey_gap = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-landlock-syscalls-survey-gap.md");
    defer std.testing.allocator.free(survey_gap);
    try requireContains(survey_gap, "`zigux/tests/phase13_landlock_syscalls.zig` as a returned direct replay companion");
    try requireContains(survey_gap, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig` as a returned reviewability companion");
    try requireContains(survey_gap, "`zigux/tests/phase13_landlock_syscalls_manifest.json`");
    try requireContains(survey_gap, "The active packet summary is now the restored survey, not this historical gap note.");
    try requireDoesNotContain(survey_gap, "The remaining directly coupled gaps stay outside this bounded helper-local step:\n- `zigux/tests/phase13_landlock_syscalls.zig`");
}

test "phase13 roadmap traceability keeps the shared-subsystems anchor map honest after the direct replay returns" {
    const traceability = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-roadmap-traceability.md");
    defer std.testing.allocator.free(traceability);

    try requireContains(traceability, "`zigux/tests/phase13_landlock_syscalls.zig`");
    try requireContains(traceability, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try requireContains(traceability, "`zigux/tests/phase13_landlock_syscalls_manifest.json`");
    try requireContains(traceability, "current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions");
    try requireDoesNotContain(traceability, "## Repo-Reality Gaps\n\nKeep the remaining current gaps explicit:\n- docs-root `Documentation/zigux/README.md` still lacks a dedicated Phase 13 reminder block\n- `make -C zigux phase13-validate`\n- `make -C zigux phase13`\n- `zigux/tests/phase13_build.zig`\n- `zigux/tests/phase13_devres.zig`\n- `zigux/tests/phase13_devres_reviewability.zig`\n- `zigux/tests/phase13_devres_boundary_evidence.zig`\n- `zigux/tests/phase13_devres_manifest.json`\n- `scripts/zigux/check-phase13-devres-packet.py`\n- `scripts/zigux/check-phase13-devres-packet-alignment.py`\n- `zigux/tests/phase13_landlock_syscalls.zig`");
}

test "phase13 landlock syscalls packet checker keeps the breadcrumb-only survey-gap classification explicit" {
    const checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase13-landlock-syscalls-packet.py");
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "\"zigux/tests/phase13_landlock_syscalls.zig\": [");
    try requireContains(checker, "\"phase13 landlock syscalls direct replay covers the current planner packet\"");
    try requireContains(checker, "\"active materialized helper-local, direct replay, and reviewability packet companions\"");
    try requireContains(checker, "\"historical breadcrumb for older lane notes and review references, not as active packet evidence\"");
    try requireContains(checker, "\"Current `master` now materializes this helper-local, direct replay, and reviewability packet through:\"");
    try requireContains(checker, "\"current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions\"");
}
