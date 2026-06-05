const std = @import("std");

const fixture_path = "zigux/tests/fixtures/phase1_helpers.json";

fn loadFixture() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        fixture_path,
        std.testing.allocator,
        .limited(96 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn sectionSlice(fixture: []const u8) ![]const u8 {
    const section_start = std.mem.indexOf(u8, fixture, "\"str_error_r\"") orelse return error.MissingStrErrorRSection;
    const next_section = std.mem.indexOfPos(u8, fixture, section_start, "\"slab\"") orelse return error.MissingSlabSection;
    try std.testing.expect(section_start < next_section);
    return fixture[section_start..next_section];
}

test "phase 1 str_error_r fixture section keeps its lane position" {
    const fixture = try loadFixture();
    defer std.testing.allocator.free(fixture);

    try expectBefore(fixture, "\"zalloc\"", "\"str_error_r\"");
    try expectBefore(fixture, "\"str_error_r\"", "\"slab\"");
    try expectBefore(fixture, "\"str_error_r\"", "\"vsprintf\"");
}

test "phase 1 str_error_r fixture pins known and fallback render strings" {
    const fixture = try loadFixture();
    defer std.testing.allocator.free(fixture);

    const str_error_r = try sectionSlice(fixture);
    try expectContains(str_error_r, "\"enoent\"");
    try expectContains(str_error_r, "No such file or directory");
    try expectContains(str_error_r, "\"unknown\"");
    try expectContains(str_error_r, "INTERNAL ERROR: strerror_r(4096, [buf], 64)=22");
}

test "current tiny_unknown fixture, when present, stays a bounded truncation witness" {
    const fixture = try loadFixture();
    defer std.testing.allocator.free(fixture);

    const str_error_r = try sectionSlice(fixture);
    if (std.mem.indexOf(u8, str_error_r, "\"tiny_unknown\"")) |_| {
        try expectContains(str_error_r, "INTERNA");
    }
}
