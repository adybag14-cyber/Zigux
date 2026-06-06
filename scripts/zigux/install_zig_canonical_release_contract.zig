const std = @import("std");

const install_zig_source = @embedFile("install-zig.py");
const policy_source = @embedFile("zig-toolchain-policy.json");

const canonical_channel = "0.17.0-dev.758+748e7c5e3";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-748e7c5e39fc";
const canonical_target = "x86_64-linux";
const canonical_archive = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const canonical_url = "https://github.com/adybag14-cyber/zig/releases/download/upstream-748e7c5e39fc/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const canonical_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const historical_runtime_channel = "0.17.0-dev.87+9b177a7d2";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "canonical release constants stay aligned with the policy channel" {
    try expectContains(install_zig_source, "CANONICAL_RELEASE_CHANNEL = '" ++ canonical_channel ++ "'");
    try expectContains(install_zig_source, "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', '" ++ canonical_repo ++ "')");
    try expectContains(install_zig_source, "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', '" ++ canonical_tag ++ "')");

    try expectContains(policy_source, "\"channel\": \"" ++ canonical_channel ++ "\"");
    try expectContains(policy_source, "\"minimum_version\": \"" ++ canonical_channel ++ "\"");
    try expectContains(policy_source, "\"" ++ canonical_target ++ "\": \"" ++ canonical_sha256 ++ "\"");
    try expectNotContains(policy_source, historical_runtime_channel);
}

test "canonical pinned channel resolves through the trusted GitHub release" {
    try expectContains(install_zig_source, "if channel == CANONICAL_RELEASE_CHANNEL:");
    try expectContains(install_zig_source, "f'https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/'");
    try expectContains(install_zig_source, "f'{CANONICAL_RELEASE_TAG}/zig-{target_key}-{channel}{suffix}'");
    try expectContains(install_zig_source, "if '-dev.' in channel:");
    try expectContains(install_zig_source, "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'");

    try expectContains(install_zig_source, canonical_url);
    try expectContains(install_zig_source, canonical_archive);
}

test "installer self-test pins the canonical release target tuple" {
    try expectContains(install_zig_source, "assert resolve_target(sample_index, '" ++ canonical_channel ++ "', 'x86_64', 'linux') == (");
    try expectContains(install_zig_source, "'" ++ canonical_target ++ "',");
    try expectContains(install_zig_source, "'" ++ canonical_channel ++ "',");
    try expectContains(install_zig_source, "'" ++ canonical_url ++ "',");
}

test "policy archive verification remains mandatory for local archive installs" {
    try expectContains(install_zig_source, "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)");
    try expectContains(install_zig_source, "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:");
    try expectContains(install_zig_source, "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:");
    try expectContains(install_zig_source, "no pinned archive sha256 for target {archive_target_key}");
    try expectContains(install_zig_source, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectContains(install_zig_source, "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified");
}

test "installer self-test covers offline canonical fallback and duplicate policy rejection" {
    try expectContains(install_zig_source, "assert load_index('" ++ canonical_channel ++ "') == {}");
    try expectContains(install_zig_source, "duplicate toolchain policy keys");
    try expectContains(install_zig_source, "duplicate archive_sha256 targets");
    try expectContains(install_zig_source, "ZIG_INSTALL_SELF_TEST=pass");
    try expectContains(install_zig_source, "ZIG_INSTALL_SELF_TEST_CASE_COUNT=46");
}
