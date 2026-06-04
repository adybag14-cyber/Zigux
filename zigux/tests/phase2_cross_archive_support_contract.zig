const std = @import("std");

const archive_target = "x86_64-linux";
const route_contract_target = "aarch64-linux";
const channel = "0.17.0-dev.758+748e7c5e3";
const digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const archive_path = "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const parts_path = "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 cross validator keeps archive support alternatives explicit" {
    const validate_phase2 = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase2.py");
    defer std.testing.allocator.free(validate_phase2);

    try expectContains(validate_phase2, "ARCHIVE_PAYLOAD_PATH");
    try expectContains(validate_phase2, "ARCHIVE_PARTS_MANIFEST_PATH");
    try expectContains(validate_phase2, "ARCHIVE_SUPPORT_ALTERNATIVES");
    try expectContains(validate_phase2, "ARCHIVE_SUPPORT_DESCRIPTION");
    try expectContains(validate_phase2, "MISSING_REQUIRED_ARCHIVE_SUPPORT");
    try expectContains(validate_phase2, archive_path);
    try expectContains(validate_phase2, parts_path ++ "/manifest.json");
    try expectContains(validate_phase2, "canonical `adybag14-cyber/zig` release");
}

test "phase2 cross validator accepts documented canonical fallback markers" {
    const validate_phase2 = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase2.py");
    defer std.testing.allocator.free(validate_phase2);

    try expectContains(validate_phase2, "canonical `adybag14-cyber/zig` release");
    try expectContains(validate_phase2, "`scripts/zigux/check-lane05-local-first-archive-workflow.py`");
    try expectContains(validate_phase2, "`scripts/zigux/check-lane05-local-archive-readme.py`");
    try expectContains(validate_phase2, "all(marker in readme_text for marker in required_markers)");
    try expectContains(validate_phase2, "return []");
}

test "phase2 cross policy and readme pin the same archive identity" {
    const toolchain_policy = try readRepoFile(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(toolchain_policy);
    const third_party_readme = try readRepoFile(std.testing.allocator, "third_party/README.md");
    defer std.testing.allocator.free(third_party_readme);

    for ([_][]const u8{ archive_target, channel, digest }) |marker| {
        try expectContains(toolchain_policy, marker);
        try expectContains(third_party_readme, marker);
    }

    try expectContains(toolchain_policy, "\"archive_target_scope\"");
    try expectContains(toolchain_policy, "\"x86_64-linux\"");
    try expectContains(third_party_readme, "`" ++ archive_path ++ "`");
    try expectContains(third_party_readme, "`" ++ parts_path ++ "`");
    try expectContains(third_party_readme, "canonical `adybag14-cyber/zig` release");
}

test "phase2 cross fixture keeps archive and route-only targets partitioned" {
    const cross_targets = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer std.testing.allocator.free(cross_targets);

    try expectContains(cross_targets, "\"archive_target_scope\"");
    try expectContains(cross_targets, "\"target\": \"" ++ archive_target ++ "\"");
    try expectContains(cross_targets, "\"validation_mode\": \"archive_required\"");
    try expectContains(cross_targets, "\"target\": \"" ++ route_contract_target ++ "\"");
    try expectContains(cross_targets, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(cross_targets, "\"target\": \"riscv64-linux\"");
    try expectContains(cross_targets, "\"route\": \"make -C zigux phase2-cross\"");
}
