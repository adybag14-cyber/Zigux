const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative_index| {
        count += 1;
        cursor += relative_index + needle.len;
    }
    return count;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "tests root keeps the parked Phase 2 closure note and validators visible" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);
    const tests_readme = try readRepoFile("zigux/tests/README.md", 512 * 1024);
    defer std.testing.allocator.free(tests_readme);
    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 512 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(closure_note, "PHASE2_STATUS=parked");
    try expectContains(closure_note, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");

    try expectContains(tests_readme, "`Documentation/zigux/phase2-closure.md`");
    try expectContains(tests_readme, "`scripts/zigux/validate-phase2.py`");
    try expectContains(tests_readme, "`scripts/zigux/validate-phase2-closure.py`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/phase2_tool_manifest.json`");
    try expectBefore(tests_readme, "## Phase 2 review packet", "## Phase 3 review packet");

    try expectContains(manifest, "\"Documentation/zigux/phase2-closure.md\"");
    try expectContains(manifest, "\"zigux/tests/README.md\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(manifest, "\"status\": \"active\"");
}

test "tests root and closure note preserve the shared Phase 2 make-wrapper packet" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);
    const tests_readme = try readRepoFile("zigux/tests/README.md", 512 * 1024);
    defer std.testing.allocator.free(tests_readme);
    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 512 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    const wrappers = [_][]const u8{
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    };

    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");
    try expectContains(tests_readme, "Keep the rematerialized make-wrapper packet explicit");
    try expectContains(scripts_readme, "keep the required wrapper route packet explicit");

    for (wrappers) |wrapper| {
        try expectContains(closure_note, wrapper);
        try expectContains(tests_readme, wrapper);
        try expectContains(scripts_readme, wrapper);
    }
}

test "genksyms survey and process-output packets stay aligned across closure, tests root, and manifest" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);
    const tests_readme = try readRepoFile("zigux/tests/README.md", 512 * 1024);
    defer std.testing.allocator.free(tests_readme);
    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 512 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(closure_note, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    try expectContains(closure_note, "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py");
    try expectContains(closure_note, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=");
    try expectContains(closure_note, "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json");

    try expectContains(tests_readme, "`Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-genksyms-bridge.py`");
    try expectContains(tests_readme, "`scripts/zigux/genksyms.zig`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/genksyms_bridge/manifest.json`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`");

    try expectContains(manifest, "\"scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py\"");
    try expectContains(manifest, "\"zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json\"");
}

test "kconfig repo-reality gap stays separate from live helper-local packets" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);
    const tests_readme = try readRepoFile("zigux/tests/README.md", 512 * 1024);
    defer std.testing.allocator.free(tests_readme);
    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 512 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectOnce(closure_note, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
    try expectContains(closure_note, "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`");
    try expectContains(closure_note, "allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`");

    try expectContains(tests_readme, "`scripts/zigux/kconfig/conf_bridge.zig`");
    try expectContains(tests_readme, "`scripts/zigux/kconfig/confdata_bridge.zig`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`");

    try expectContains(manifest, "\"scripts/zigux/kconfig/conf_bridge.zig\"");
    try expectContains(manifest, "\"scripts/zigux/kconfig/confdata_bridge.zig\"");
    try expectAbsent(manifest, "\"Documentation/zigux/phase2-kconfig-bridge-gap-survey.md\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
}

test "fixdep governance remains visible beside closure shared tooling" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);
    const tests_readme = try readRepoFile("zigux/tests/README.md", 512 * 1024);
    defer std.testing.allocator.free(tests_readme);
    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 512 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    try expectContains(closure_note, "`python3 scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(closure_note, "`python3 scripts/zigux/check-fixdep-diff.py`");
    try expectContains(closure_note, "`make -C zigux phase2-fixdep`");

    try expectContains(tests_readme, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(tests_readme, "`scripts/zigux/fixdep.zig`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/fixdep/cases.json`");

    try expectContains(scripts_readme, "current fixdep governance, determinism, helper, fixture, and CI packet");
    try expectContains(scripts_readme, "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`");
    try expectContains(scripts_readme, "`zig test scripts/zigux/fixdep.zig`");
}
