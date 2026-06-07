const std = @import("std");

const install_zig_py = @embedFile("install-zig.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "policy loader tracks duplicate object keys before validation" {
    try expectContains(install_zig_py, "class DuplicateTrackingDict(dict[str, object]):");
    try expectContains(install_zig_py, "self.duplicate_keys: list[str] = []");
    try expectContains(install_zig_py, "if key in self and key not in self.duplicate_keys:");
    try expectContains(install_zig_py, "self.duplicate_keys.append(key)");
    try expectContains(install_zig_py, "object_pairs_hook=DuplicateTrackingDict");
}

test "top level policy duplicate keys fail closed with explicit diagnostics" {
    try expectContains(install_zig_py, "if isinstance(payload, DuplicateTrackingDict) and payload.duplicate_keys:");
    try expectContains(install_zig_py, "duplicate toolchain policy keys in {policy_path}: ");
    try expectContains(install_zig_py, "', '.join(payload.duplicate_keys)");
    try expectContains(install_zig_py, "{\"channel\":\"0.17.0-dev.758+748e7c5e3\",\"channel\":\"0.17.0-dev.90+abcdef\"}");
    try expectContains(install_zig_py, "assert 'duplicate toolchain policy keys' in str(exc)");
}

test "archive sha256 duplicate targets fail closed separately" {
    try expectContains(install_zig_py, "if isinstance(archive_sha256, DuplicateTrackingDict) and archive_sha256.duplicate_keys:");
    try expectContains(install_zig_py, "duplicate archive_sha256 targets in {policy_path}: ");
    try expectContains(install_zig_py, "', '.join(archive_sha256.duplicate_keys)");
    try expectContains(install_zig_py, "{\"channel\":\"0.17.0-dev.758+748e7c5e3\",\"archive_sha256\":{\"x86_64-linux\":\"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\",\"x86_64-linux\":\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"}}");
    try expectContains(install_zig_py, "assert 'duplicate archive_sha256 targets' in str(exc)");
}

test "duplicate key checks remain part of installer self test output contract" {
    try expectContains(install_zig_py, "def run_self_test() -> int:");
    try expectContains(install_zig_py, "print('ZIG_INSTALL_SELF_TEST=pass')");
    try expectContains(install_zig_py, "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=46')");
    try expectContains(install_zig_py, "parser.add_argument('--self-test'");
    try expectContains(install_zig_py, "if args.self_test:");
    try expectContains(install_zig_py, "return run_self_test()");
}
