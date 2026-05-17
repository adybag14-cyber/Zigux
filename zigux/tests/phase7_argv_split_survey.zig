const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(64 * 1024));
}

test "phase 7 argv_split survey keeps reusable leaf-library ownership evidence explicit" {
    const allocator = std.testing.allocator;

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_argv_split_manifest.json");
    defer allocator.free(manifest);
    const helper = try readRepoFile(allocator, "lib/argv_split.zig");
    defer allocator.free(helper);
    const tests = try readRepoFile(allocator, "zigux/tests/phase7_argv_split.zig");
    defer allocator.free(tests);
    const slice = try readRepoFile(allocator, "Documentation/zigux/phase7-argv-split-slice.md");
    defer allocator.free(slice);
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-argv-split-packet.py");
    defer allocator.free(checker);

    for ([_][]const u8{
        "\"lane_key\": \"P7-L09\"",
        "\"anchor\": \"lib/argv_split.c\"",
        "\"current_replay_status\": \"route_present_on_master\"",
        "\"lib/argv_split.zig\"",
        "\"zigux/tests/phase7_argv_split.zig\"",
        "\"zigux/tests/phase7_argv_split_survey.zig\"",
        "\"scripts/zigux/check-phase7-argv-split-packet.py\"",
        "\"lib/rbtree.zig\"",
        "\"zigux/tests/phase7_rbtree.zig\"",
        "copied token-buffer ownership and later source-mutation isolation",
        "owned-storage reuse keeps token pointers inside caller-managed storage",
        "non-blank results keep storage, argv slices, and C-argv views distinct across callers",
        "argvFree on one live non-blank result does not disturb another caller-owned split result",
        "deinit on one live non-blank result does not disturb another caller-owned split result",
        "blank-input sentinel reuse stays stable across argvFree and deinit, including shared empty-sentinel teardown beside another blank caller",
    }) |needle| {
        try expectContains(manifest, needle);
    }

    for ([_][]const u8{
        "pub fn argvFree",
        "pub fn deinit",
        "pub const ArgvSplitResult",
    }) |needle| {
        try expectContains(helper, needle);
    }

    for ([_][]const u8{
        "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
        "phase 7 deinit keeps non-blank argv_split ownership distinct across live results",
        "phase 7 blank argv_split sentinel reuse stays stable across teardown paths",
    }) |needle| {
        try expectContains(tests, needle);
    }

    for ([_][]const u8{
        "`argv_free()` via `argvFree()`",
        "copied token-buffer ownership and later source-mutation isolation",
        "blank-input sentinel reuse stays stable across argvFree and deinit",
    }) |needle| {
        try expectContains(slice, needle);
    }

    for ([_][]const u8{
        "phase7_argv_split_manifest.json",
        "phase7_argv_split_survey.zig",
        "phase7-argv-split-slice.md",
        "route_present_on_master",
    }) |needle| {
        try expectContains(checker, needle);
    }
}
