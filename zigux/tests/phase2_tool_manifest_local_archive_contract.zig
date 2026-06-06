const std = @import("std");

const repo_paths = .{
    .tool_manifest = "zigux/tests/fixtures/phase2_tool_manifest.json",
    .bootstrap_note = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    .tests_readme = "zigux/tests/README.md",
    .policy = "scripts/zigux/zig-toolchain-policy.json",
    .third_party_readme = "third_party/README.md",
};

const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_archive = "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const pinned_digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";

fn readFile(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "tool manifest keeps the local archive packet explicit" {
    const manifest = try readFile(repo_paths.tool_manifest);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
    try expectContains(manifest, "\"archive_support\"");
    try expectContains(manifest, "\"bootstrap_helpers\"");
    try expectContains(manifest, "\"third_party/README.md\"");
    try expectContains(manifest, pinned_archive);
    try expectContains(manifest, "\"scripts/zigux/stage-pinned-zig-archive.py\"");
    try expectContains(manifest, "\"scripts/zigux/install-zig.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-lane05-local-first-archive-workflow.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-lane05-local-archive-readme.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-lane05-stage-helper-contract.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-lane05-stage-helper-selftest.py\"");
    try expectContains(manifest, "Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit");
    try expectContains(manifest, "Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface");
}

test "bootstrap note and tests root agree on the pinned local archive handoff" {
    const bootstrap_note = try readFile(repo_paths.bootstrap_note);
    defer std.testing.allocator.free(bootstrap_note);
    const tests_readme = try readFile(repo_paths.tests_readme);
    defer std.testing.allocator.free(tests_readme);

    try expectContains(bootstrap_note, "scripts/zigux/install-zig.py");
    try expectContains(bootstrap_note, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(bootstrap_note, "scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try expectContains(bootstrap_note, "scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectContains(bootstrap_note, "scripts/zigux/check-lane05-stage-helper-selftest.py");
    try expectContains(bootstrap_note, pinned_archive);
    try expectContains(bootstrap_note, "repo-local pinned archive filename, digest, size, duplicate-copy boundary");
    try expectContains(bootstrap_note, "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet");

    try expectContains(tests_readme, pinned_archive);
    try expectContains(tests_readme, "repo-local pinned archive packet explicit");
    try expectContains(tests_readme, "local-first `third_party`, canonical `adybag14-cyber/zig` release, mirror, then direct-download bootstrap order");
    try expectContains(tests_readme, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test");
    try expectContains(tests_readme, "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test");
}

test "policy and third party README preserve exact archive identity" {
    const policy = try readFile(repo_paths.policy);
    defer std.testing.allocator.free(policy);
    const third_party_readme = try readFile(repo_paths.third_party_readme);
    defer std.testing.allocator.free(third_party_readme);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"x86_64-linux\"");

    try expectContains(third_party_readme, "target: `x86_64-linux`");
    try expectContains(third_party_readme, "channel: `0.17.0-dev.758+748e7c5e3`");
    try expectContains(third_party_readme, "sha256: `0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6`");
    try expectContains(third_party_readme, "size: `59410844` bytes");
    try expectContains(third_party_readme, "duplicate-copy boundary: duplicate-suffix archives are rejected before staging");
    try expectBefore(third_party_readme, "reuses and validates", "falls back to the canonical `adybag14-cyber/zig` release");
}
