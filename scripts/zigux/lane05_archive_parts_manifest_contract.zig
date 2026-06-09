const std = @import("std");
const testing = std.testing;

const DocFile = struct {
    contents: []u8,
};

fn readFile(path: []const u8, limit: usize) !DocFile {
    return .{
        .contents = try std.Io.Dir.cwd().readFileAlloc(
            testing.io,
            path,
            testing.allocator,
            .limited(limit),
        ),
    };
}

fn unloadFile(file: DocFile) void {
    testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_target = "x86_64-linux";
const pinned_filename = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const pinned_digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const pinned_size_readme = "59410844";
const pinned_parts_dir = "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts";

test "lane05 pinned archive policy and README agree on the parts payload" {
    const policy = try readFile("scripts/zigux/zig-toolchain-policy.json", 64 * 1024);
    defer unloadFile(policy);
    const readme = try readFile("third_party/README.md", 64 * 1024);
    defer unloadFile(readme);

    try expectContains(policy.contents, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy.contents, "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy.contents, "\"" ++ pinned_target ++ "\": \"" ++ pinned_digest ++ "\"");
    try expectContains(policy.contents, "\"archive_target_scope\"");
    try expectContains(policy.contents, "\"" ++ pinned_target ++ "\"");

    try expectContains(readme.contents, "channel: `" ++ pinned_channel ++ "`");
    try expectContains(readme.contents, "file: `third_party/" ++ pinned_filename ++ "`");
    try expectContains(readme.contents, "sha256: `" ++ pinned_digest ++ "`");
    try expectContains(readme.contents, "size: `" ++ pinned_size_readme ++ "` bytes");
    try expectContains(readme.contents, "`" ++ pinned_parts_dir ++ "`");
    try expectContains(readme.contents, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(readme.contents, "before canonical release, mirror, or direct-download fallback");
}

test "lane05 split helper keeps manifest and shard contract stable" {
    const split_helper = try readFile("scripts/zigux/split-pinned-zig-archive.py", 256 * 1024);
    defer unloadFile(split_helper);

    try expectContains(split_helper.contents, "DEFAULT_CHUNK_BYTES = 786_432");
    try expectContains(split_helper.contents, "\"" ++ pinned_target ++ "\": 59_410_844");
    try expectContains(split_helper.contents, "\"filename\": filename");
    try expectContains(split_helper.contents, "\"encoding\": \"base64\"");
    try expectContains(split_helper.contents, "\"sha256\": sha256");
    try expectContains(split_helper.contents, "\"size\": size");
    try expectContains(split_helper.contents, "\"chunk_bytes\": chunk_bytes");
    try expectContains(split_helper.contents, "\"part_count\": part_count");
    try expectContains(split_helper.contents, "\"parts_glob\": \"part-*.b64\"");
    try expectContains(split_helper.contents, "output_dir / f\"part-{index:03d}.b64\"");
    try expectContains(split_helper.contents, "base64.b64encode(chunk).decode(\"ascii\")");
    try expectContains(split_helper.contents, "base64.b64decode(encoded, validate=True)");
    try expectContains(split_helper.contents, "missing expected shard: {path.name}");

    try expectBefore(split_helper.contents, "\"filename\": filename", "\"encoding\": \"base64\"");
    try expectBefore(split_helper.contents, "\"encoding\": \"base64\"", "\"sha256\": sha256");
    try expectBefore(split_helper.contents, "\"sha256\": sha256", "\"size\": size");
    try expectBefore(split_helper.contents, "\"size\": size", "\"chunk_bytes\": chunk_bytes");
    try expectBefore(split_helper.contents, "\"chunk_bytes\": chunk_bytes", "\"part_count\": part_count");
    try expectBefore(split_helper.contents, "\"part_count\": part_count", "\"parts_glob\": \"part-*.b64\"");
}

test "lane05 stage helper validates the reconstructed archive before fallback paths" {
    const stage_helper = try readFile("scripts/zigux/stage-pinned-zig-archive.py", 256 * 1024);
    defer unloadFile(stage_helper);
    const workflow = try readFile(".github/workflows/zigux-bootstrap.yml", 512 * 1024);
    defer unloadFile(workflow);

    try expectContains(stage_helper.contents, "\"" ++ pinned_target ++ "\": 59_410_844");
    try expectContains(stage_helper.contents, "source archive is not a regular file");
    try expectContains(stage_helper.contents, "expected {source} to be {expected_size} bytes");
    try expectContains(stage_helper.contents, "expected {source} to have sha256 {expected_sha}");
    try expectContains(stage_helper.contents, "duplicate-suffix archive copies");
    try expectContains(stage_helper.contents, "--parts-dir");

    try expectContains(workflow.contents, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow.contents, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow.contents, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow.contents, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(workflow.contents, "if try_local_archive; then");
    try expectContains(workflow.contents, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectContains(workflow.contents, "elif curl --fail");
    try expectContains(workflow.contents, "if try_download \"$ZIGUX_ZIG_URL\"; then");

    try expectBefore(workflow.contents, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectBefore(workflow.contents, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow.contents, "https://ziglang.org/download/community-mirrors.txt", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "lane05 archive parts guard stays bounded to missing-payload shape" {
    const workflow = try readFile(".github/workflows/zigux-bootstrap.yml", 512 * 1024);
    defer unloadFile(workflow);
    const readme = try readFile("third_party/README.md", 64 * 1024);
    defer unloadFile(readme);

    try expectContains(workflow.contents, "Check current pinned Zig archive packet");
    try expectContains(workflow.contents, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectContains(workflow.contents, "Self-test current staged pinned Zig archive helper");
    try expectContains(workflow.contents, "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");
    try expectContains(readme.contents, "trusted archive payloads that Lane 05 bootstrap CI");
    try expectContains(readme.contents, "If the exact archive file is absent but");
    try expectContains(readme.contents, "`.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally");

    try testing.expectEqual(@as(usize, 1), countOccurrences(readme.contents, pinned_parts_dir));
    try expectNotContains(readme.contents, "0.17.0-dev.87+9b177a7d2");
    try expectNotContains(workflow.contents, "actions/checkout@");
}

test "lane05 archive-parts contract covers the live companion workflow" {
    const companion_workflow = try readFile(".github/workflows/zigux-bootstrap-archive-parts-packet.yml", 128 * 1024);
    defer unloadFile(companion_workflow);

    try expectContains(companion_workflow.contents, "name: zigux-bootstrap-archive-parts-packet");
    try expectContains(companion_workflow.contents, "- 'scripts/zigux/check-lane05-archive-parts-workflow.py'");
    try expectContains(companion_workflow.contents, "- 'scripts/zigux/check-lane05-archive-parts-packet.py'");
    try expectContains(companion_workflow.contents, "- 'scripts/zigux/zig-toolchain-policy.json'");
    try expectContains(companion_workflow.contents, "- 'third_party/**'");
    try expectContains(companion_workflow.contents, "- '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'");
    try expectContains(companion_workflow.contents, "python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test");
    try expectContains(companion_workflow.contents, "python3 scripts/zigux/check-lane05-archive-parts-workflow.py");
    try expectContains(companion_workflow.contents, "python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing");

    try expectBefore(companion_workflow.contents, "python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test", "python3 scripts/zigux/check-lane05-archive-parts-workflow.py\n");
    try expectBefore(companion_workflow.contents, "python3 scripts/zigux/check-lane05-archive-parts-workflow.py\n", "python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test");
    try expectBefore(companion_workflow.contents, "python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test", "python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing");
}
