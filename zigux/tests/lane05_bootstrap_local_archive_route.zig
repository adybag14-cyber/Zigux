const std = @import("std");
const testing = std.testing;

const expected_target = "x86_64-linux";
const expected_channel = "0.17.0-dev.87+9b177a7d2";
const expected_filename = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";
const expected_sha256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77";
const expected_repo_archive = "third_party/$ZIGUX_ZIG_FILENAME";
const expected_repo_parts = "${repo_archive_path}.parts";
const expected_ziglang_url = "https://ziglang.org/builds/{filename}";
const expected_mirror_index = "https://ziglang.org/download/community-mirrors.txt";

test "Lane 05 bootstrap route keeps repo-local archive before network downloads" {
    var io_instance: std.Io.Threaded = .init(testing.allocator, .{});
    defer io_instance.deinit();

    const cwd = std.Io.Dir.cwd();
    const workflow = try cwd.readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        testing.allocator,
        .limited(1024 * 1024),
    );
    defer testing.allocator.free(workflow);

    const policy = try cwd.readFileAlloc(
        io_instance.io(),
        "scripts/zigux/zig-toolchain-policy.json",
        testing.allocator,
        .limited(64 * 1024),
    );
    defer testing.allocator.free(policy);

    try requirePolicyPin(policy);
    try requireWorkflowRoute(workflow);
}

fn requirePolicyPin(policy: []const u8) !void {
    try requireContains(policy, "\"channel\": \"" ++ expected_channel ++ "\"");
    try requireContains(policy, "\"minimum_version\": \"" ++ expected_channel ++ "\"");
    try requireContains(policy, "\"" ++ expected_target ++ "\": \"" ++ expected_sha256 ++ "\"");
    try requireContains(policy, "\"archive_target_scope\":");
    try requireContains(policy, "\"" ++ expected_target ++ "\"");
    try requireContains(policy, "\"channel_minimum_lockstep\": true");

    try requireCount(policy, expected_channel, 2);
    try requireOnce(policy, expected_sha256);
}

fn requireWorkflowRoute(workflow: []const u8) !void {
    try requireContains(workflow, "- 'third_party/**'");
    try requireContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try requireContains(workflow, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test");
    try requireContains(workflow, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try requireContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");

    try requireOnce(workflow, "repo_archive_path=\"" ++ expected_repo_archive ++ "\"");
    try requireOnce(workflow, "repo_archive_parts_dir=\"" ++ expected_repo_parts ++ "\"");
    try requireOnce(workflow, "try_local_archive() {");
    try requireOnce(workflow, "if try_local_archive; then");
    try requireOnce(workflow, "if [ ! -f \"$repo_archive_path\" ]; then");
    try requireOnce(workflow, "if [ ! -d \"$repo_archive_parts_dir\" ]; then");
    try requireOnce(workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try requireOnce(workflow, "archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"");
    try requireOnce(workflow, "url = f\"" ++ expected_ziglang_url ++ "\"");
    try requireOnce(workflow, expected_mirror_index);
    try requireOnce(workflow, "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org");

    try requireOrder(workflow, "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))", "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try requireOrder(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"", "url = f\"" ++ expected_ziglang_url ++ "\"");
    try requireOrder(workflow, "repo_archive_path=\"" ++ expected_repo_archive ++ "\"", "repo_archive_parts_dir=\"" ++ expected_repo_parts ++ "\"");
    try requireOrder(workflow, "repo_archive_parts_dir=\"" ++ expected_repo_parts ++ "\"", "try_local_archive() {");
    try requireOrder(workflow, "try_local_archive() {", "try_download() {");
    try requireOrder(workflow, "if try_local_archive; then", "elif curl -L --fail " ++ expected_mirror_index ++ " -o \"$mirror_file\"; then");
    try requireOrder(workflow, "elif curl -L --fail " ++ expected_mirror_index ++ " -o \"$mirror_file\"; then", "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try requireOrder(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing", "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test");
    try requireOrder(workflow, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py", "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    try requireCount(haystack, needle, 1);
}

fn requireCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |offset| {
        count += 1;
        cursor += offset + needle.len;
    }
    try testing.expectEqual(expected, count);
}

fn requireOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

comptime {
    std.debug.assert(std.mem.eql(u8, expected_filename, "zig-" ++ expected_target ++ "-" ++ expected_channel ++ ".tar.xz"));
}
