const std = @import("std");

const install_zig_source = @embedFile("install-zig.py");
const policy_source = @embedFile("zig-toolchain-policy.json");

const canonical_channel = "0.17.0-dev.758+748e7c5e3";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-748e7c5e39fc";
const canonical_target = "x86_64-linux";
const canonical_digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "install-zig keeps the canonical dev.758 release route pinned" {
    try requireContains(install_zig_source, "CANONICAL_RELEASE_CHANNEL = '" ++ canonical_channel ++ "'");
    try requireContains(install_zig_source, "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', '" ++ canonical_repo ++ "')");
    try requireContains(install_zig_source, "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', '" ++ canonical_tag ++ "')");
    try requireContains(install_zig_source, "if channel == CANONICAL_RELEASE_CHANNEL:");
    try requireContains(install_zig_source, "f'https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/'");
    try requireContains(install_zig_source, "f'{CANONICAL_RELEASE_TAG}/zig-{target_key}-{channel}{suffix}'");
    try requireBefore(
        install_zig_source,
        "if channel == CANONICAL_RELEASE_CHANNEL:",
        "if '-dev.' in channel:",
    );
}

test "installer self-test covers canonical release and explicit fallback modes" {
    try requireContains(install_zig_source, "assert resolve_target(sample_index, '" ++ canonical_channel ++ "', 'x86_64', 'linux') == (");
    try requireContains(install_zig_source, "https://github.com/" ++ canonical_repo ++ "/releases/download/" ++ canonical_tag ++ "/zig-x86_64-linux-" ++ canonical_channel ++ ".tar.xz");
    try requireContains(install_zig_source, "assert load_index('" ++ canonical_channel ++ "') == {}");
    try requireContains(install_zig_source, "expected non-explicit channel timeout to fail");
    try requireContains(install_zig_source, "ZIG_INSTALL_SELF_TEST_CASE_COUNT=46");
}

test "installer policy helpers reject ambiguous or untrusted policy data" {
    try requireContains(install_zig_source, "object_pairs_hook=DuplicateTrackingDict");
    try requireContains(install_zig_source, "duplicate toolchain policy keys");
    try requireContains(install_zig_source, "duplicate archive_sha256 targets");
    try requireContains(install_zig_source, "ARCHIVE_SHA256_RE.fullmatch(digest.lower())");
    try requireContains(install_zig_source, "zig archive sha256 mismatch");
    try requireContains(install_zig_source, "no pinned archive sha256 for target {archive_target_key}");
}

test "toolchain policy stays lockstep with one trusted Linux archive target" {
    try requireContains(policy_source, "\"phase\": \"Phase 2\"");
    try requireContains(policy_source, "\"channel\": \"" ++ canonical_channel ++ "\"");
    try requireContains(policy_source, "\"minimum_version\": \"" ++ canonical_channel ++ "\"");
    try requireContains(policy_source, "\"" ++ canonical_target ++ "\": \"" ++ canonical_digest ++ "\"");
    try requireContains(policy_source, "\"channel_minimum_lockstep\": true");
    try requireContains(policy_source, "\"archive_target_scope\"");
    try requireContains(policy_source, "\"" ++ canonical_target ++ "\"");
    try requireContains(policy_source, "\"phase2-toolchain\"");
    try requireContains(policy_source, "\"phase2-cross\"");
    try requireContains(policy_source, "\"phase2-validate\"");
}
