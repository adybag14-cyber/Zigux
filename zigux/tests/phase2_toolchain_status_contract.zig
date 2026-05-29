const std = @import("std");

const required_toolchain_arguments = [_][]const u8{
    "--allow-missing",
    "--policy-only",
    "--archive-only",
    "--archive",
    "--archive-target",
    "--zig",
    "--self-test",
};

const required_status_outputs = [_][]const u8{
    "ZIG_TOOLCHAIN_STATUS=invalid",
    "ZIG_TOOLCHAIN_STATUS=missing",
    "ZIG_TOOLCHAIN_STATUS={status}",
    "ZIG_TOOLCHAIN_PATH=",
    "ZIG_TOOLCHAIN_VERSION=",
    "ZIG_TOOLCHAIN_MIN_SUPPORTED=",
    "ZIG_TOOLCHAIN_PINNED_CHANNEL=",
    "ZIG_TOOLCHAIN_PIN_POLICY=exact",
    "ZIG_TOOLCHAIN_PIN_POLICY=minimum_only",
    "ZIG_TOOLCHAIN_PIN_POLICY=unresolved",
    "ZIG_TOOLCHAIN_SEARCH_ROOTS=",
    "ZIG_TOOLCHAIN_NOTE=",
};

const required_archive_outputs = [_][]const u8{
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid",
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing",
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}",
    "ZIG_TOOLCHAIN_ARCHIVE_PATH=",
    "ZIG_TOOLCHAIN_ARCHIVE_TARGET=",
    "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME=",
    "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256=",
    "ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256=",
    "ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS=",
    "ZIG_TOOLCHAIN_NOTE=",
};

const required_policy_outputs = [_][]const u8{
    "ZIG_TOOLCHAIN_POLICY_STATUS=missing",
    "ZIG_TOOLCHAIN_POLICY_STATUS=present",
    "ZIG_TOOLCHAIN_POLICY_STATUS=invalid",
    "ZIG_TOOLCHAIN_POLICY_PATH=",
    "ZIG_TOOLCHAIN_PHASE=",
    "ZIG_TOOLCHAIN_PINNED_CHANNEL=",
    "ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT=",
    "ZIG_TOOLCHAIN_ARCHIVE_TARGETS=",
    "ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=",
    "ZIG_TOOLCHAIN_PIN_POLICY=",
};

const required_fail_closed_markers = [_][]const u8{
    "duplicate toolchain policy keys",
    "unexpected toolchain policy keys",
    "duplicate archive_sha256 targets",
    "unexpected upgrade_policy keys",
    "duplicate upgrade_policy keys",
    "duplicate required_make_routes entry",
    "archive target must be explicit when policy covers multiple archive targets",
    "archive target {target!r} is outside archive_target_scope",
    "explicit archive path is a directory, expected a regular file",
    "explicit zig path is a directory, expected an executable file",
    "expected pinned Zig channel",
    "minimum_version must match channel when channel_minimum_lockstep is true",
};

const required_policy_values = [_][]const u8{
    "\"phase\": \"Phase 2\"",
    "\"channel\": \"0.17.0-dev.87+9b177a7d2\"",
    "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"",
    "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"",
    "\"channel_minimum_lockstep\": true",
    "\"phase2-toolchain\"",
    "\"phase2-tools\"",
    "\"phase2-kconfig\"",
    "\"phase2-cross\"",
    "\"phase2-genksyms\"",
    "\"phase2-fixdep\"",
    "\"phase2-validate\"",
};

fn loadFile(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try expectContains(haystack, needle);
    }
}

test "phase 2 toolchain checker keeps the status output contract visible" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const checker = try loadFile(io_instance.io(), "scripts/zigux/check-zig-toolchain.py", 96 * 1024);
    defer std.testing.allocator.free(checker);

    try expectAll(checker, &required_toolchain_arguments);
    try expectAll(checker, &required_status_outputs);
    try expectAll(checker, &required_policy_outputs);
    try expectContains(checker, "ZIG_TOOLCHAIN_SELF_TEST=pass");
    try expectContains(checker, "ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT={case_count}");
}

test "phase 2 toolchain checker keeps archive validation fail-closed" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const checker = try loadFile(io_instance.io(), "scripts/zigux/check-zig-toolchain.py", 96 * 1024);
    defer std.testing.allocator.free(checker);

    try expectAll(checker, &required_archive_outputs);
    try expectAll(checker, &required_fail_closed_markers);
    try expectContains(checker, "archive_name_has_duplicate_suffix");
    try expectContains(checker, "archive_name_matches_policy");
    try expectContains(checker, "validate_policy_archive");
    try expectContains(checker, "compute_sha256(path)");
}

test "phase 2 pinned policy stays aligned with the checker contract" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const policy = try loadFile(io_instance.io(), "scripts/zigux/zig-toolchain-policy.json", 16 * 1024);
    defer std.testing.allocator.free(policy);

    try expectAll(policy, &required_policy_values);
}
