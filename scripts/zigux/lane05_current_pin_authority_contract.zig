const std = @import("std");

const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_target = "x86_64-linux";
const pinned_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const pinned_size = "59410844";
const canonical_release_repo = "adybag14-cyber/zig";
const canonical_release_tag = "upstream-748e7c5e39fc";
const pinned_filename = "zig-" ++ pinned_target ++ "-" ++ pinned_channel ++ ".tar.xz";
const pinned_path = "third_party/" ++ pinned_filename;
const pinned_parts_path = pinned_path ++ ".parts";

const policy_markers = [_][]const u8{
    "\"channel\": \"" ++ pinned_channel ++ "\"",
    "\"minimum_version\": \"" ++ pinned_channel ++ "\"",
    "\"" ++ pinned_target ++ "\": \"" ++ pinned_sha256 ++ "\"",
    "\"archive_target_scope\": [\n      \"" ++ pinned_target ++ "\"\n    ]",
    "\"channel_minimum_lockstep\": true",
};

const readme_markers = [_][]const u8{
    "- target: `" ++ pinned_target ++ "`",
    "- channel: `" ++ pinned_channel ++ "`",
    "- file: `" ++ pinned_path ++ "`",
    "- sha256: `" ++ pinned_sha256 ++ "`",
    "- size: `" ++ pinned_size ++ "` bytes",
    "falls back to the canonical `adybag14-cyber/zig` release before `community-mirrors.txt` and the direct `ziglang.org` download URL",
};

const installer_markers = [_][]const u8{
    "CANONICAL_RELEASE_CHANNEL = '" ++ pinned_channel ++ "'",
    "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', '" ++ canonical_release_repo ++ "')",
    "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', '" ++ canonical_release_tag ++ "')",
    "return (\n            f'https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/'\n            f'{CANONICAL_RELEASE_TAG}/zig-{target_key}-{channel}{suffix}'\n        )",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
};

const workflow_order_markers = [_][]const u8{
    "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
    "canonical_repo = \"" ++ canonical_release_repo ++ "\"",
    "canonical_tag = \"" ++ canonical_release_tag ++ "\"",
    "filename = f\"zig-{target}-{channel}.tar.xz\"",
    "canonical_url = f\"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}\"",
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "if try_local_archive; then",
    "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
    "if try_download \"$ZIGUX_ZIG_URL\"; then",
    "echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2",
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectAll(source: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try expectContains(source, marker);
    }
}

fn markerIndex(source: []const u8, marker: []const u8) !usize {
    return std.mem.indexOf(u8, source, marker) orelse error.MissingMarker;
}

fn expectOrdered(source: []const u8, markers: []const []const u8) !void {
    var previous: ?usize = null;
    for (markers) |marker| {
        const current = try markerIndex(source, marker);
        if (previous) |prev| {
            try std.testing.expect(current > prev);
        }
        previous = current;
    }
}

test "current policy and third_party README agree on the pinned archive authority" {
    const allocator = std.testing.allocator;
    const policy = try readFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);
    const readme = try readFile(allocator, "third_party/README.md");
    defer allocator.free(readme);

    try expectAll(policy, &policy_markers);
    try expectAll(readme, &readme_markers);
    try expectContains(readme, pinned_parts_path);
}

test "installer canonical release route stays pinned to the current policy packet" {
    const allocator = std.testing.allocator;
    const installer = try readFile(allocator, "scripts/zigux/install-zig.py");
    defer allocator.free(installer);

    try expectAll(installer, &installer_markers);
    try expectContains(installer, "f'{CANONICAL_RELEASE_TAG}/zig-{target_key}-{channel}{suffix}'");
    try expectContains(installer, "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'");

    const canonical_index = try markerIndex(installer, "if channel == CANONICAL_RELEASE_CHANNEL:");
    const explicit_dev_index = try markerIndex(installer, "if '-dev.' in channel:");
    try std.testing.expect(canonical_index < explicit_dev_index);
}

test "bootstrap setup ladder derives and tries the same pinned archive in fail-closed order" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectOrdered(workflow, &workflow_order_markers);
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(workflow, "--archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
}
