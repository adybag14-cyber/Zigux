const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "genksyms keeps empty positional payloads after parsed options" {
    const args = [_][]const u8{
        "input.c",
        "",
        "--debug",
        "--reference",
        "ref.sym",
        "tail.h",
        "",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("ref.sym", request.reference_files[0]);

    const rendered = [_][]const u8{
        "--debug",
        "--reference",
        "ref.sym",
        "input.c",
        "",
        "tail.h",
        "",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
}

test "genksyms empty positionals keep required option data classification" {
    const args = [_][]const u8{
        "",
        "-r",
        "",
        "middle.c",
        "-T",
        "--types",
        "",
        "-w",
        "-q",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("", request.reference_files[0]);
    try testing.expectEqualStrings("--types", request.dump_types_file.?);

    const rendered = [_][]const u8{
        "-r",
        "",
        "-T",
        "--types",
        "-w",
        "-q",
        "",
        "middle.c",
        "",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
}

test "genksyms renders empty delayed positionals in bridge json" {
    const args = [_][]const u8{
        "input.c",
        "",
        "-D",
        "-p",
        "--warnings",
        "tail.c",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expect(request.warnings);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-D\",\"-p\",\"--warnings\",\"input.c\",\"\",\"tail.c\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
