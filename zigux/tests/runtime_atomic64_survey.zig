const std = @import("std");

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 9 runtime atomic64 survey keeps the restored direct packet and remaining loader blocker explicit" {
    const survey_note = try readRepoFileAlloc(std.testing.allocator, "Documentation/zigux/phase9-runtime-atomic64-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "`samples/zigux/runtime_atomic64.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_module.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_diff.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_survey.zig`");
    try expectContains(survey_note, "`samples/zigux/runtime_atomic64_loader.zig`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(survey_note, "not a completed loadable runtime-module path");
}
