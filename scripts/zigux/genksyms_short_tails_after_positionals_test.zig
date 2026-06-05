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

test "genksyms keeps short reference cluster tails as data after positionals" {
    const args = [_][]const u8{
        "leftover.c",
        "-V",
        "-rVd-inline.symref",
        "middle.h",
        "-w",
        "-r",
        "-D-separated.symref",
        "tail.c",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("Vd-inline.symref", request.reference_files[0]);
    try testing.expectEqualStrings("-D-separated.symref", request.reference_files[1]);

    const rendered = [_][]const u8{
        "-V",
        "-rVd-inline.symref",
        "-w",
        "-r",
        "-D-separated.symref",
        "leftover.c",
        "middle.h",
        "tail.c",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
}

test "genksyms keeps short dump-types cluster tails as data after positionals" {
    const args = [_][]const u8{
        "first.c",
        "-Tdp-types.symtypes",
        "-D",
        "second.c",
        "-T",
        "-w-final.symtypes",
        "-p",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqualStrings("-w-final.symtypes", request.dump_types_file.?);

    const rendered = [_][]const u8{
        "-Tdp-types.symtypes",
        "-D",
        "-T",
        "-w-final.symtypes",
        "-p",
        "first.c",
        "second.c",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
}

test "genksyms renders short-tail data after positionals in bridge json" {
    const args = [_][]const u8{
        "input.c",
        "-rVsym.ref",
        "-T",
        "-p-types.symtypes",
        "--warnings",
        "input.h",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("Vsym.ref", request.reference_files[0]);
    try testing.expectEqualStrings("-p-types.symtypes", request.dump_types_file.?);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-rVsym.ref\",\"-T\",\"-p-types.symtypes\",\"--warnings\",\"input.c\",\"input.h\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"Vsym.ref\"],\"dump_types_file\":\"-p-types.symtypes\"}}\n",
        output.written(),
    );
}
