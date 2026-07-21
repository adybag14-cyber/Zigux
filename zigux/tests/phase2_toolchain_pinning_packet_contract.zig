const std = @import("std");

const max_file_size = 512 * 1024;

const RootFiles = struct {
    scripts_readme: []const u8,
    pinning_checker: []const u8,
    toolchain_checker: []const u8,
    policy: []const u8,
};

fn readRootFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn loadRootFiles(allocator: std.mem.Allocator) !RootFiles {
    return .{
        .scripts_readme = try readRootFile(allocator, "scripts/zigux/README.md"),
        .pinning_checker = try readRootFile(allocator, "scripts\zigux/check_phase2_toolchain_pinning.zig"),
        .toolchain_checker = try readRootFile(allocator, "scripts\zigux/check_zig_toolchain.zig"),
        .policy = try readRootFile(allocator, "scripts/zigux/zig-toolchain-policy.json"),
    };
}

fn freeRootFiles(allocator: std.mem.Allocator, files: RootFiles) void {
    allocator.free(files.scripts_readme);
    allocator.free(files.pinning_checker);
    allocator.free(files.toolchain_checker);
    allocator.free(files.policy);
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

test "scripts README keeps the Phase 2 toolchain pinning packet visible" {
    const files = try loadRootFiles(std.testing.allocator);
    defer freeRootFiles(std.testing.allocator, files);

    try expectContains(files.scripts_readme, "`scripts\zigux/check_phase2_toolchain_pinning.zig`");
    try expectContains(files.scripts_readme, "`zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only`");
    try expectContains(files.scripts_readme, "`zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing`");
    try expectContains(files.scripts_readme, "`scripts\zigux/check_phase2_toolchain_pin_scope.zig`");
    try expectContains(files.scripts_readme, "`make -C zigux phase2-toolchain`");
    try expectContains(files.scripts_readme, "`make -C zigux phase2-tools`");
    try expectContains(files.scripts_readme, "`make -C zigux phase2-kconfig`");
    try expectContains(files.scripts_readme, "`make -C zigux phase2-cross`");
    try expectContains(files.scripts_readme, "`make -C zigux phase2-genksyms`");
    try expectContains(files.scripts_readme, "`make -C zigux phase2-fixdep`");
    try expectContains(files.scripts_readme, "`make -C zigux phase2-validate`");
    try expectContains(files.scripts_readme, "`make -C zigux phase2`");
}

test "pinning checker records the current archive and workflow guard packet" {
    const files = try loadRootFiles(std.testing.allocator);
    defer freeRootFiles(std.testing.allocator, files);

    try expectContains(files.pinning_checker, "POLICY = \"scripts/zigux/zig-toolchain-policy.json\"");
    try expectContains(files.pinning_checker, "ARCHIVE_TARGET = \"x86_64-linux\"");
    try expectContains(files.pinning_checker, "ARCHIVE_CHANNEL = \"0.17.0-dev.877+a3ae499dc\"");
    try expectContains(files.pinning_checker, "ARCHIVE_SIZE = 59_410_844");
    try expectContains(files.pinning_checker, "EXPECTED_SELF_TEST_CASE_COUNT = 55");
    try expectContains(files.pinning_checker, "run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only");
    try expectContains(files.pinning_checker, "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing");
    try expectContains(files.pinning_checker, "run: zig run scripts/zigux/check_phase2_toolchain_pinning.zig -- --self-test");
    try expectContains(files.pinning_checker, "run: zig run scripts/zigux/check_phase2_toolchain_pinning.zig");
    try expectContains(files.pinning_checker, "No current repo-reality gaps remain inside the bounded toolchain");
}

test "policy and checker keep channel lockstep and route scope explicit" {
    const files = try loadRootFiles(std.testing.allocator);
    defer freeRootFiles(std.testing.allocator, files);

    try expectContains(files.policy, "\"phase\": \"Phase 2\"");
    try expectContains(files.policy, "\"channel\": \"0.17.0-dev.877+a3ae499dc\"");
    try expectContains(files.policy, "\"minimum_version\": \"0.17.0-dev.877+a3ae499dc\"");
    try expectContains(files.policy, "\"x86_64-linux\": \"c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8\"");
    try expectContains(files.policy, "\"channel_minimum_lockstep\": true");
    try expectContains(files.policy, "\"archive_target_scope\"");
    try expectContains(files.policy, "\"required_make_routes\"");

    try expectContains(files.toolchain_checker, "minimum_version must match channel when channel_minimum_lockstep is true");
    try expectContains(files.toolchain_checker, "archive_target_scope references missing archive_sha256 entries");
    try expectContains(files.toolchain_checker, "archive_sha256 contains targets outside archive_target_scope");
    try expectContains(files.toolchain_checker, "\"phase\", \"channel\", \"minimum_version\", \"archive_sha256\", \"upgrade_policy\"");
    try expectContains(files.toolchain_checker, "\"channel_minimum_lockstep\", \"archive_target_scope\", \"required_make_routes\"");
}
