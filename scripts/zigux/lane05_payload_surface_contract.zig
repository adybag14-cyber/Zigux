const std = @import("std");

const current_channel = "0.17.0-dev.758+748e7c5e3";
const current_target = "x86_64-linux";
const current_digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const current_size = "59410844";
const current_filename = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const current_archive_path = "third_party/" ++ current_filename;
const current_parts_path = current_archive_path ++ ".parts";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-748e7c5e39fc";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle);
    try std.testing.expect(first != null);
    const after_first = first.? + needle.len;
    try std.testing.expect(std.mem.indexOf(u8, haystack[after_first..], needle) == null);
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle);
        try std.testing.expect(found != null);
        cursor += found.? + needle.len;
    }
}

test "policy and README agree on the current pinned payload surface" {
    const policy = try readRepoFile(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);
    const readme = try readRepoFile(std.testing.allocator, "third_party/README.md");
    defer std.testing.allocator.free(readme);

    try requireContains(policy, "\"channel\": \"" ++ current_channel ++ "\"");
    try requireContains(policy, "\"minimum_version\": \"" ++ current_channel ++ "\"");
    try requireContains(policy, "\"" ++ current_target ++ "\": \"" ++ current_digest ++ "\"");
    try requireContains(policy, "\"archive_target_scope\"");
    try requireContains(policy, "\"" ++ current_target ++ "\"");

    try requireContains(readme, "target: `" ++ current_target ++ "`");
    try requireContains(readme, "channel: `" ++ current_channel ++ "`");
    try requireContains(readme, "file: `" ++ current_archive_path ++ "`");
    try requireContains(readme, "sha256: `" ++ current_digest ++ "`");
    try requireContains(readme, "size: `" ++ current_size ++ "` bytes");
    try requireContains(readme, "`" ++ current_parts_path ++ "`");
    try requireContains(readme, "duplicate-suffix archives are rejected before staging");

    try requireAbsent(policy, "0.17.0-dev.87+9b177a7d2");
    try requireAbsent(readme, "0.17.0-dev.87+9b177a7d2");
}

test "workflow keeps the full archive and parts packet as the local-first inputs" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "name: Setup pinned Zig toolchain");
    try requireContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try requireContains(workflow, "canonical_repo = \"" ++ canonical_repo ++ "\"");
    try requireContains(workflow, "canonical_tag = \"" ++ canonical_tag ++ "\"");
    try requireContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");

    try requireOrdered(workflow, &.{
        "try_local_archive() {",
        "if [ ! -f \"$repo_archive_path\" ]; then",
        "if [ ! -d \"$repo_archive_parts_dir\" ]; then",
        "python3 scripts/zigux/stage-pinned-zig-archive.py",
        "--parts-dir \"$repo_archive_parts_dir\"",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "try_download() {",
        "if try_local_archive; then",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "community-mirrors.txt",
        "try_download \"$ZIGUX_ZIG_URL\"",
        "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org",
    });
}

test "stage helper output names the same payload and parts recovery path" {
    const stage_helper = try readRepoFile(std.testing.allocator, "scripts/zigux/stage-pinned-zig-archive.py");
    defer std.testing.allocator.free(stage_helper);

    try requireContains(stage_helper, "TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")");
    try requireContains(stage_helper, "THIRD_PARTY_DIR = Path(\"third_party\")");
    try requireContains(stage_helper, "\"x86_64-linux\": 59_410_844");
    try requireContains(stage_helper, "\"filename\": f\"zig-{target}-{channel}.tar.xz\"");
    try requireContains(stage_helper, "return f\"{stem} (1).tar.xz\"");

    try requireContains(stage_helper, "parser.add_argument(\"--parts-dir\"");
    try requireContains(stage_helper, "manifest_path = parts_dir / \"manifest.json\"");
    try requireContains(stage_helper, "if filename != expected_filename:");
    try requireContains(stage_helper, "if encoding != \"base64\":");
    try requireContains(stage_helper, "if sha256 != expected_sha:");
    try requireContains(stage_helper, "if size != expected_size:");
    try requireContains(stage_helper, "if parts_glob != \"part-*.b64\":");
    try requireContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}");
    try requireContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_FILENAME={metadata['filename']}");
    try requireContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE={metadata['size']}");
    try requireContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={metadata['sha256']}");
    try requireContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}");
}

test "bootstrap guard still treats the trusted payload as missing-allowed but not solved" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);
    const readme = try readRepoFile(std.testing.allocator, "third_party/README.md");
    defer std.testing.allocator.free(readme);

    try requireExactlyOnce(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try requireContains(readme, "reserved for trusted archive payloads that Lane 05 bootstrap CI");
    try requireContains(readme, "can validate locally before it falls back to network downloads");
    try requireContains(readme, "If the repo-local archive is unavailable");
    try requireContains(readme, "falls back to the canonical `" ++ canonical_repo ++ "` release before `community-mirrors.txt` and the direct `ziglang.org` download URL");
    try requireAbsent(workflow, "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz");
    try requireAbsent(readme, "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz");
}
