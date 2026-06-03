const std = @import("std");
const Io = std.Io;

const pinned_target = "x86_64-linux";
const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const pinned_size = "59410844";
const pinned_filename = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const pinned_archive_path = "third_party/" ++ pinned_filename;
const pinned_parts_path = pinned_archive_path ++ ".parts";

fn readFirst(allocator: std.mem.Allocator, paths: []const []const u8) ![]u8 {
    var last_err: anyerror = error.FileNotFound;
    for (paths) |path| {
        return Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024)) catch |err| {
            last_err = err;
            continue;
        };
    }
    return last_err;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingMarker;
    try std.testing.expect(before_index < after_index);
}

test "Lane 05 policy and README pin the same archive packet" {
    const allocator = std.testing.allocator;
    const policy = try readFirst(allocator, &.{
        "scripts/zigux/zig-toolchain-policy.json",
        "../../scripts/zigux/zig-toolchain-policy.json",
    });
    defer allocator.free(policy);
    const readme = try readFirst(allocator, &.{
        "third_party/README.md",
        "../../third_party/README.md",
    });
    defer allocator.free(readme);

    try expectContains(policy, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\": \"" ++ pinned_sha256 ++ "\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\"");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-validate\"");

    try expectContains(readme, "`" ++ pinned_target ++ "`");
    try expectContains(readme, "`" ++ pinned_channel ++ "`");
    try expectContains(readme, "`" ++ pinned_archive_path ++ "`");
    try expectContains(readme, "`" ++ pinned_parts_path ++ "`");
    try expectContains(readme, "`" ++ pinned_sha256 ++ "`");
    try expectContains(readme, "`" ++ pinned_size ++ "` bytes");
    try expectContains(readme, "`scripts/zigux/zig-toolchain-policy.json`");
}

test "Lane 05 README checker keeps missing payload separate from byte validation" {
    const allocator = std.testing.allocator;
    const checker = try readFirst(allocator, &.{
        "scripts/zigux/check-lane05-local-archive-readme.py",
        "../../scripts/zigux/check-lane05-local-archive-readme.py",
    });
    defer allocator.free(checker);

    try expectContains(checker, "EXPECTED_ARCHIVE_SIZES");
    try expectContains(checker, "\"" ++ pinned_target ++ "\": 59_410_844");
    try expectContains(checker, "payload_status = \"missing_allowed\"");
    try expectContains(checker, "payload_status = \"present\"");
    try expectContains(checker, "actual_size != expected_size");
    try expectContains(checker, "actual_sha != expected_sha");
    try expectContains(checker, "duplicate-suffix archive copies");
    try expectOrder(checker, "payload_status = \"missing_allowed\"", "payload_status = \"present\"");
}

test "Lane 05 stage helper still reconstructs base64 archive parts" {
    const allocator = std.testing.allocator;
    const stage_helper = try readFirst(allocator, &.{
        "scripts/zigux/stage-pinned-zig-archive.py",
        "../../scripts/zigux/stage-pinned-zig-archive.py",
    });
    defer allocator.free(stage_helper);

    try expectContains(stage_helper, "def reconstruct_archive_from_parts");
    try expectContains(stage_helper, "manifest.json");
    try expectContains(stage_helper, "require_manifest_string(manifest, \"filename\"");
    try expectContains(stage_helper, "require_manifest_string(manifest, \"encoding\"");
    try expectContains(stage_helper, "require_manifest_string(manifest, \"sha256\"");
    try expectContains(stage_helper, "require_manifest_int(manifest, \"size\"");
    try expectContains(stage_helper, "require_manifest_int(manifest, \"part_count\"");
    try expectContains(stage_helper, "require_manifest_int(manifest, \"chunk_bytes\"");
    try expectContains(stage_helper, "require_manifest_string(manifest, \"parts_glob\"");
    try expectContains(stage_helper, "encoding != \"base64\"");
    try expectContains(stage_helper, "parts_glob != \"part-*.b64\"");
    try expectContains(stage_helper, "part-{index:03d}.b64");
    try expectContains(stage_helper, "base64.b64decode(encoded, validate=True)");
}
