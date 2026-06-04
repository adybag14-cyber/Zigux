const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "policy parser tracks duplicate keys before normalization" {
    const checker = try readRepoFile("scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "class DuplicateTrackingDict(dict[str, object]):");
    try expectContains(checker, "self.duplicate_keys: list[str] = []");
    try expectContains(checker, "if key in self and key not in self.duplicate_keys:");
    try expectContains(checker, "object_pairs_hook=DuplicateTrackingDict");
    try expectContains(checker, "duplicate toolchain policy keys in {policy_path}: ");
    try expectContains(checker, "duplicate archive_sha256 targets in {policy_path}: ");
    try expectContains(checker, "duplicate upgrade_policy keys in {policy_path}: ");
    try expectContains(checker, "duplicate required_make_routes entry");

    try expectInOrder(
        checker,
        "if isinstance(payload, DuplicateTrackingDict) and payload.duplicate_keys:",
        "return validate_policy_payload(payload, policy_path)",
    );
}

test "policy schema rejects unexpected and malformed fields" {
    const checker = try readRepoFile("scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "POLICY_KEYS = {\"phase\", \"channel\", \"minimum_version\", \"archive_sha256\", \"upgrade_policy\"}");
    try expectContains(checker, "UPGRADE_POLICY_KEYS = {\"channel_minimum_lockstep\", \"archive_target_scope\", \"required_make_routes\"}");
    try expectContains(checker, "unexpected toolchain policy keys in {policy_path}: ");
    try expectContains(checker, "unexpected upgrade_policy keys in {policy_path}: ");
    try expectContains(checker, "invalid archive_sha256 in {policy_path}");
    try expectContains(checker, "invalid archive_sha256[{normalized_target}] in {policy_path}");
    try expectContains(checker, "invalid channel_minimum_lockstep in {policy_path}");
    try expectContains(checker, "invalid required_make_routes");
}

test "policy cross-field invariants are fail-closed" {
    const checker = try readRepoFile("scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "missing_archive_targets = [target for target in archive_target_scope if target not in normalized_archives]");
    try expectContains(checker, "archive_target_scope references missing archive_sha256 entries in {policy_path}: ");
    try expectContains(checker, "extra_archive_targets = [target for target in normalized_archives if target not in archive_target_scope]");
    try expectContains(checker, "archive_sha256 contains targets outside archive_target_scope in {policy_path}: ");
    try expectContains(checker, "if lockstep and minimum_version != channel:");
    try expectContains(checker, "minimum_version must match channel when channel_minimum_lockstep is true in {policy_path}");
    try expectInOrder(
        checker,
        "parse_zig_version(channel)",
        "parse_zig_version(minimum_version)",
    );
}

test "live policy keeps exact pinned channel and route scope" {
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\": [");
    try expectContains(policy, "\"required_make_routes\": [");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-tools\"");
    try expectContains(policy, "\"phase2-kconfig\"");
    try expectContains(policy, "\"phase2-cross\"");
    try expectContains(policy, "\"phase2-genksyms\"");
    try expectContains(policy, "\"phase2-fixdep\"");
    try expectContains(policy, "\"phase2-validate\"");
}
