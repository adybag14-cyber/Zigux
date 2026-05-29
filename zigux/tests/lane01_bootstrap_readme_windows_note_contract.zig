const std = @import("std");

const windows_note = "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.";
const prior_rule = "- Treat ZAR as the research and proving repo and Zigux as the product repo.";
const next_heading = "Active product surfaces";
const charter_guard = "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.";

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;

    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }

    return count;
}

fn loadReadme(io: std.Io) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        io,
        "zigux-alpha/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
}

fn expectOrdered(readme: []const u8, before: []const u8, middle: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, readme, before) orelse return error.MissingBeforeMarker;
    const middle_index = std.mem.indexOf(u8, readme, middle) orelse return error.MissingMiddleMarker;
    const after_index = std.mem.indexOf(u8, readme, after) orelse return error.MissingAfterMarker;

    try std.testing.expect(before_index < middle_index);
    try std.testing.expect(middle_index < after_index);
}

test "bootstrap README preserves the Windows case-sensitive filesystem note once" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const readme = try loadReadme(io_instance.io());
    defer std.testing.allocator.free(readme);

    try std.testing.expectEqual(@as(usize, 1), countOccurrences(readme, windows_note));
}

test "Windows filesystem note stays at the end of the bootstrap Rules packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const readme = try loadReadme(io_instance.io());
    defer std.testing.allocator.free(readme);

    try expectOrdered(readme, prior_rule, windows_note, next_heading);
}

test "Windows note remains in the bootstrap charter guarded README packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const readme = try loadReadme(io_instance.io());
    defer std.testing.allocator.free(readme);

    try expectOrdered(readme, windows_note, next_heading, charter_guard);
}
