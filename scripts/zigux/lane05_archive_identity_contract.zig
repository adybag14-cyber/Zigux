const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const installer_path = "scripts/zigux/install-zig.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const readme_path = "third_party/README.md";

const target = "x86_64-linux";
const channel = "0.17.0-dev.758+748e7c5e3";
const archive_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-748e7c5e39fc";
const archive_filename = "zig-" ++ target ++ "-" ++ channel ++ ".tar.xz";
const archive_path = "third_party/" ++ archive_filename;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn requireCount(text: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, text[offset..], needle)) |relative_index| {
        count += 1;
        offset += relative_index + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn requirePolicyIdentity(policy: []const u8) !void {
    try requireContains(policy, "\"channel\": \"" ++ channel ++ "\"");
    try requireContains(policy, "\"minimum_version\": \"" ++ channel ++ "\"");
    try requireContains(policy, "\"" ++ target ++ "\": \"" ++ archive_sha256 ++ "\"");
    try requireContains(policy, "\"archive_target_scope\": [");
    try requireContains(policy, "\"" ++ target ++ "\"");
    try requireCount(policy, "\"" ++ target ++ "\"", 2);
    try requireCount(policy, archive_sha256, 1);
}

fn requireReadmeIdentity(readme: []const u8) !void {
    try requireContains(readme, "- target: `" ++ target ++ "`");
    try requireContains(readme, "- channel: `" ++ channel ++ "`");
    try requireContains(readme, "- file: `" ++ archive_path ++ "`");
    try requireContains(readme, "- sha256: `" ++ archive_sha256 ++ "`");
    try requireContains(readme, "canonical `" ++ canonical_repo ++ "` release");
    try requireContains(readme, archive_filename ++ ".parts");
    try requireOrder(readme, archive_path, "canonical `" ++ canonical_repo ++ "` release");
}

fn requireWorkflowIdentity(workflow: []const u8) !void {
    try requireContains(workflow, "target = targets[0]");
    try requireContains(workflow, "channel = policy[\"channel\"]");
    try requireContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try requireContains(workflow, "canonical_repo = \"" ++ canonical_repo ++ "\"");
    try requireContains(workflow, "canonical_tag = \"" ++ canonical_tag ++ "\"");
    try requireContains(workflow, "url = f\"https://ziglang.org/builds/{filename}\"");
    try requireContains(workflow, "canonical_url = f\"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}\"");
    try requireContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requireContains(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireContains(workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try requireContains(workflow, "if try_download \"$ZIGUX_ZIG_URL\"; then");

    try requireCount(workflow, "canonical_repo = \"" ++ canonical_repo ++ "\"", 1);
    try requireCount(workflow, "canonical_tag = \"" ++ canonical_tag ++ "\"", 1);
    try requireCount(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"", 1);
    try requireCount(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"", 1);

    try requireOrder(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireOrder(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try requireOrder(workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}

fn requireInstallerIdentity(installer: []const u8) !void {
    try requireContains(installer, "CANONICAL_RELEASE_CHANNEL = '" ++ channel ++ "'");
    try requireContains(installer, "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', '" ++ canonical_repo ++ "')");
    try requireContains(installer, "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', '" ++ canonical_tag ++ "')");
    try requireContains(installer, "channel = load_policy_channel()");
    try requireContains(installer, "if channel == CANONICAL_RELEASE_CHANNEL:");
    try requireContains(installer, "return f'https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/{CANONICAL_RELEASE_TAG}/{tarball}'");
    try requireContains(installer, "return f'https://ziglang.org/builds/{tarball}'");
    try requireOrder(installer, "if channel == CANONICAL_RELEASE_CHANNEL:", "return f'https://ziglang.org/builds/{tarball}'");
}

test "Lane 05 pinned archive policy and README agree on identity" {
    const allocator = std.testing.allocator;
    const policy = try readFile(allocator, policy_path);
    defer allocator.free(policy);
    const readme = try readFile(allocator, readme_path);
    defer allocator.free(readme);

    try requirePolicyIdentity(policy);
    try requireReadmeIdentity(readme);
}

test "Lane 05 workflow derives the same canonical archive identity" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try requireWorkflowIdentity(workflow);
}

test "Lane 05 Python installer keeps the canonical release identity in lockstep" {
    const allocator = std.testing.allocator;
    const installer = try readFile(allocator, installer_path);
    defer allocator.free(installer);

    try requireInstallerIdentity(installer);
}

test "Lane 05 archive identity is not duplicated across guarded repo files" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);
    const installer = try readFile(allocator, installer_path);
    defer allocator.free(installer);
    const policy = try readFile(allocator, policy_path);
    defer allocator.free(policy);
    const readme = try readFile(allocator, readme_path);
    defer allocator.free(readme);

    try requireCount(workflow, canonical_repo, 2);
    try requireCount(installer, canonical_repo, 1);
    try requireCount(installer, canonical_tag, 1);
    try requireCount(policy, channel, 2);
    try requireCount(readme, archive_path, 3);
}
