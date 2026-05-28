const std = @import("std");
const testing = std.testing;

const expected_filename = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";
const expected_channel = "0.17.0-dev.87+9b177a7d2";
const expected_target = "x86_64-linux";
const expected_sha256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77";
const expected_size = "58159088";
const expected_chunk_bytes = "1048576";
const expected_part_count = "56";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, comptime path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    const candidates = [_][]const u8{
        path,
        "../" ++ path,
        "../../" ++ path,
    };

    for (candidates) |candidate| {
        return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), candidate, allocator, .limited(max_bytes)) catch |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        };
    }

    return error.FileNotFound;
}

fn readOptionalRepoFile(allocator: std.mem.Allocator, comptime path: []const u8, max_bytes: usize) !?[]u8 {
    return readRepoFile(allocator, path, max_bytes) catch |err| switch (err) {
        error.FileNotFound => null,
        else => return err,
    };
}

test "lane05 pinned archive policy matches optional parts manifest" {
    var arena = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const policy = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json", 64 * 1024);
    try expectContains(policy, "\"channel\": \"" ++ expected_channel ++ "\"");
    try expectContains(policy, "\"minimum_version\": \"" ++ expected_channel ++ "\"");
    try expectContains(policy, "\"" ++ expected_target ++ "\": \"" ++ expected_sha256 ++ "\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"" ++ expected_target ++ "\"");

    const manifest_path = "third_party/" ++ expected_filename ++ ".parts/manifest.json";
    const manifest = try readOptionalRepoFile(allocator, manifest_path, 64 * 1024) orelse return;

    try expectContains(manifest, "\"filename\": \"" ++ expected_filename ++ "\"");
    try expectContains(manifest, "\"encoding\": \"base64\"");
    try expectContains(manifest, "\"sha256\": \"" ++ expected_sha256 ++ "\"");
    try expectContains(manifest, "\"size\": " ++ expected_size);
    try expectContains(manifest, "\"chunk_bytes\": " ++ expected_chunk_bytes);
    try expectContains(manifest, "\"part_count\": " ++ expected_part_count);
    try expectContains(manifest, "\"parts_glob\": \"part-*.b64\"");
}
