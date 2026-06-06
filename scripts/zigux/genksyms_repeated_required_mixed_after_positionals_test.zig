const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(allocator: std.mem.Allocator, args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "mixed repeated required values after positionals accumulate refs and keep last dump types" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "left.c",
        "--reference",
        "first.symref",
        "middle.h",
        "--dump-types",
        "old.types",
        "-rsecond.symref",
        "right.c",
        "-Tnew.types",
        "--reference=third.symref",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 3), request.reference_files.len);
    try testing.expectEqualStrings("first.symref", request.reference_files[0]);
    try testing.expectEqualStrings("second.symref", request.reference_files[1]);
    try testing.expectEqualStrings("third.symref", request.reference_files[2]);
    try testing.expect(request.dump_types_file != null);
    try testing.expectEqualStrings("new.types", request.dump_types_file.?);

    const expected_rendered = [_][]const u8{
        "--reference",
        "first.symref",
        "--dump-types",
        "old.types",
        "-rsecond.symref",
        "-Tnew.types",
        "--reference=third.symref",
        "left.c",
        "middle.h",
        "right.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "mixed repeated required values after positionals render normalized bridge state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "-r",
        "base.symref",
        "--dump-types=first.types",
        "payload.o",
        "--reference=next.symref",
        "-T",
        "final.types",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-r\",\"base.symref\",\"--dump-types=first.types\",\"--reference=next.symref\",\"-T\",\"final.types\",\"input.c\",\"payload.o\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"base.symref\",\"next.symref\"],\"dump_types_file\":\"final.types\"}}\n",
        output.written(),
    );
}
