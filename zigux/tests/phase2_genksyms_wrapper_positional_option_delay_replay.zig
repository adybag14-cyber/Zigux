const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectRequest(outcome: genksyms.ParseOutcome) !genksyms.Request {
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "long options render before delayed positional input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "left.c",
        "--version",
        "--debug",
        "--reference",
        "abi.symref",
        "right.h",
        "--dump-types=types.symtypes",
    };

    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("abi.symref", request.reference_files[0]);
    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);

    const expected_rendered_args = [_][]const u8{
        "--version",
        "--debug",
        "--reference",
        "abi.symref",
        "--dump-types=types.symtypes",
        "left.c",
        "right.h",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered_args, request.rendered_args);
}

test "short options render before delayed lone dash and positional input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-",
        "-V",
        "-d",
        "tail.c",
        "-Ttypes.symtypes",
        "-p",
    };

    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(request.preserve);
    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);

    const expected_rendered_args = [_][]const u8{
        "-V",
        "-d",
        "-Ttypes.symtypes",
        "-p",
        "-",
        "tail.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered_args, request.rendered_args);
}

test "rendered bridge output keeps normalized option-first argv" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "left.c",
        "--version",
        "--debug",
        "--reference",
        "abi.symref",
        "right.h",
        "--dump-types=types.symtypes",
    };

    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"--debug\",\"--reference\",\"abi.symref\",\"--dump-types=types.symtypes\",\"left.c\",\"right.h\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"abi.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
        output.written(),
    );
}
