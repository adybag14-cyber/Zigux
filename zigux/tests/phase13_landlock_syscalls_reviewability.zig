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

test "phase13 landlock syscalls docs promote the reviewability companion into current packet truth" {
    const slice = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-landlock-syscalls-slice.md");
    defer std.testing.allocator.free(slice);
    try requireContains(slice, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try requireContains(slice, "active materialized helper-local and reviewability packet companions");
    try requireContains(slice, "`zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps");
    try requireDoesNotContain(slice, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps");

    const governance = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-landlock-syscalls-governance.md");
    defer std.testing.allocator.free(governance);
    try requireContains(governance, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try requireContains(governance, "helper-local packet plus the direct reviewability companion");
    try requireContains(governance, "`zigux/tests/phase13_landlock_syscalls.zig`");
    try requireContains(governance, "`zigux/tests/phase13_landlock_syscalls_manifest.json`");
    try requireDoesNotContain(governance, "`zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and `zigux/tests/phase13_build.zig`");
}

test "phase13 landlock syscalls survey and breadcrumb narrow the remaining gaps after reviewability lands" {
    const survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-landlock-syscalls-survey.md");
    defer std.testing.allocator.free(survey);
    try requireContains(survey, "Current `master` now materializes this helper-local and reviewability packet through:");
    try requireContains(survey, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try requireContains(survey, "Current `master` still leaves these directly coupled companions absent:");
    try requireContains(survey, "`zigux/tests/phase13_landlock_syscalls.zig`");
    try requireContains(survey, "`zigux/tests/phase13_landlock_syscalls_manifest.json`");
    try requireDoesNotContain(survey, "- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`");

    const survey_gap = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-landlock-syscalls-survey-gap.md");
    defer std.testing.allocator.free(survey_gap);
    try requireContains(survey_gap, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig` as a returned reviewability companion");
    try requireContains(survey_gap, "`zigux/tests/phase13_landlock_syscalls.zig`");
    try requireContains(survey_gap, "`zigux/tests/phase13_landlock_syscalls_manifest.json`");
    try requireDoesNotContain(survey_gap, "- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
}

test "phase13 roadmap traceability keeps the shared-subsystems anchor map honest after reviewability returns" {
    const traceability = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-roadmap-traceability.md");
    defer std.testing.allocator.free(traceability);

    try requireContains(traceability, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try requireContains(traceability, "direct reviewability companion");
    try requireContains(traceability, "`zigux/tests/phase13_landlock_syscalls_manifest.json`");
    try requireContains(traceability, "current `master` materializes the helper-local packet plus the direct reviewability companion");
    try requireDoesNotContain(traceability, "- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
}

test "phase13 landlock syscalls packet checker requires the reviewability companion" {
    const checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase13-landlock-syscalls-packet.py");
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "\"zigux/tests/phase13_landlock_syscalls_reviewability.zig\": [");
    try requireContains(checker, "\"phase13 landlock syscalls docs promote the reviewability companion into current packet truth\"");
    try requireContains(checker, "\"active materialized helper-local and reviewability packet companions\"");
    try requireContains(checker, "\"Current `master` now materializes this helper-local and reviewability packet through:\"");
    try requireContains(checker, "\"current `master` materializes the helper-local packet plus the direct reviewability companion\"");
}
