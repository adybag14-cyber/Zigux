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
        .failure => error.ExpectedRequestCommand,
    };
}

test "explicit terminator keeps option-shaped tail data out of parser state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "input.c",
        "-d",
        "--",
        "--help",
        "-V",
        "-r",
        "after.symref",
        "--reference=late.symref",
        "-Tlate.symtypes",
    };

    const request = try expectRequest(arena_state.allocator(), &args);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqualSlices([]const u8, &[_][]const u8{
        "--version",
        "-d",
        "--",
        "input.c",
        "--help",
        "-V",
        "-r",
        "after.symref",
        "--reference=late.symref",
        "-Tlate.symtypes",
    }, request.rendered_args);
}

test "explicit terminator leaves earlier required options parsed and later lookalikes inert" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference",
        "before.symref",
        "-Tbefore.symtypes",
        "--",
        "--reference=tail.symref",
        "--dump-types=tail.symtypes",
        "-d",
        "--warnings",
    };

    const request = try expectRequest(arena_state.allocator(), &args);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("before.symref", request.reference_files[0]);
    try testing.expectEqualStrings("before.symtypes", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "bridge output preserves terminator tail argv without synthesized options" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-q",
        "left.c",
        "--",
        "--version",
        "--preserve",
        "-r",
        "tail.symref",
    };

    const request = try expectRequest(arena_state.allocator(), &args);
    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-q\",\"--\",\"left.c\",\"--version\",\"--preserve\",\"-r\",\"tail.symref\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
