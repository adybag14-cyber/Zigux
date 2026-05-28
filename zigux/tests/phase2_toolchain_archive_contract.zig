const std = @import("std");

const expected_channel = "0.17.0-dev.87+9b177a7d2";
const expected_target = "x86_64-linux";
const expected_archive = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";
const expected_sha256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77";

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.ExpectedContractMarker;
}

test "phase 2 toolchain policy pins the archive contract consumed by bootstrap" {
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json", 16 * 1024);
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectCount(policy, "\"channel\": \"" ++ expected_channel ++ "\"", 1);
    try expectCount(policy, "\"minimum_version\": \"" ++ expected_channel ++ "\"", 1);
    try expectCount(policy, "\"" ++ expected_target ++ "\": \"" ++ expected_sha256 ++ "\"", 1);
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\": [");
    try expectContains(policy, "\"" ++ expected_target ++ "\"");

    const required_routes = [_][]const u8{
        "\"phase2-toolchain\"",
        "\"phase2-tools\"",
        "\"phase2-kconfig\"",
        "\"phase2-cross\"",
        "\"phase2-genksyms\"",
        "\"phase2-fixdep\"",
        "\"phase2-validate\"",
    };
    for (required_routes) |route| try expectContains(policy, route);
}

test "bootstrap workflow keeps the pinned archive path local first" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 512 * 1024);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "--root \"$GITHUB_WORKSPACE\"");
    try expectContains(workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectContains(workflow, "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org");

    const local_archive_index = try indexOfRequired(workflow, "if try_local_archive; then");
    const mirror_index = try indexOfRequired(workflow, "https://ziglang.org/download/community-mirrors.txt");
    const direct_download_index = try indexOfRequired(workflow, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try std.testing.expect(local_archive_index < mirror_index);
    try std.testing.expect(mirror_index < direct_download_index);
}

test "installer and stage helper agree on archive verification surfaces" {
    const installer = try readRepoFile("scripts/zigux/install-zig.py", 256 * 1024);
    defer std.testing.allocator.free(installer);

    const stage_helper = try readRepoFile("scripts/zigux/stage-pinned-zig-archive.py", 256 * 1024);
    defer std.testing.allocator.free(stage_helper);

    try expectContains(installer, "def load_policy_archive_sha256");
    try expectContains(installer, "def verify_archive_sha256");
    try expectContains(installer, "parser.add_argument('--archive'");
    try expectContains(installer, "parser.add_argument('--archive-target'");
    try expectContains(installer, "ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256");
    try expectContains(installer, "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified");
    try expectContains(installer, "ZIG_INSTALL_SOURCE={archive_source}");
    try expectContains(installer, "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified");

    try expectContains(stage_helper, "\"" ++ expected_target ++ "\": 58_159_088");
    try expectContains(stage_helper, "\"filename\": f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(stage_helper, "THIRD_PARTY_DIR = Path(\"third_party\")");
    try expectContains(stage_helper, "def reconstruct_archive_from_parts");
    try expectContains(stage_helper, "parts_dir / \"manifest.json\"");
    try expectContains(stage_helper, "parts_glob != \"part-*.b64\"");
    try expectContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}");
    try expectContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={metadata['sha256']}");
}
