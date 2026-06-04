const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "genksyms keeps empty separate long values after positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "prelude.c",
        "--reference",
        "",
        "middle.c",
        "--dump-types",
        "",
        "tail.c",
    };

    const outcome = try genksyms.parseArgs(arena, &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("", request.reference_files[0]);
    try testing.expect(request.dump_types_file != null);
    try testing.expectEqualStrings("", request.dump_types_file.?);

    const expected_rendered = [_][]const u8{
        "--reference",
        "",
        "--dump-types",
        "",
        "prelude.c",
        "middle.c",
        "tail.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    const written = output.written();
    try testing.expect(std.mem.containsAtLeast(u8, written, 1, "\"reference_files\":[\"\"]"));
    try testing.expect(std.mem.containsAtLeast(u8, written, 1, "\"dump_types_file\":\"\""));

    const parsed = try std.json.parseFromSlice(std.json.Value, testing.allocator, written, .{});
    defer parsed.deinit();
}
