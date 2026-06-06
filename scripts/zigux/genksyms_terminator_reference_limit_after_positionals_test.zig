const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectRequest(args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| return request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "terminator keeps post-tail reference lookalikes out of reference limit" {
    const args = [_][]const u8{
        "leftover.c",
        "--reference",
        "01.symref",
        "-r",
        "02.symref",
        "--ref=03.symref",
        "-r04.symref",
        "--reference",
        "05.symref",
        "-r",
        "06.symref",
        "--reference=07.symref",
        "-r08.symref",
        "--reference",
        "09.symref",
        "-r",
        "10.symref",
        "--ref=11.symref",
        "-r12.symref",
        "--reference",
        "13.symref",
        "-r",
        "14.symref",
        "--reference=15.symref",
        "-r16.symref",
        "--",
        "--reference",
        "17.symref",
        "-r18.symref",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 16), request.reference_files.len);
    try testing.expectEqualStrings("01.symref", request.reference_files[0]);
    try testing.expectEqualStrings("16.symref", request.reference_files[15]);
    for (request.reference_files) |reference| {
        try testing.expect(!std.mem.eql(u8, reference, "17.symref"));
        try testing.expect(!std.mem.eql(u8, reference, "18.symref"));
    }

    var terminator_index: ?usize = null;
    for (request.rendered_args, 0..) |arg, index| {
        if (std.mem.eql(u8, arg, "--")) {
            terminator_index = index;
            break;
        }
    }
    const terminator = terminator_index orelse return error.ExpectedTerminator;
    var saw_tail_long_reference = false;
    var saw_tail_reference_value = false;
    var saw_tail_short_reference = false;
    for (request.rendered_args[terminator + 1 ..]) |arg| {
        if (std.mem.eql(u8, arg, "--reference")) saw_tail_long_reference = true;
        if (std.mem.eql(u8, arg, "17.symref")) saw_tail_reference_value = true;
        if (std.mem.eql(u8, arg, "-r18.symref")) saw_tail_short_reference = true;
    }
    try testing.expect(saw_tail_long_reference);
    try testing.expect(saw_tail_reference_value);
    try testing.expect(saw_tail_short_reference);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"reference_files\":[\"01.symref\""));
    try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"16.symref\"],\"dump_types_file\":null"));
    try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"--reference\",\"17.symref\",\"-r18.symref\""));
}

test "seventeenth pre-terminator reference still fails before tail data is rendered" {
    const args = [_][]const u8{
        "leftover.c",
        "-r",
        "01.symref",
        "-r",
        "02.symref",
        "-r",
        "03.symref",
        "-r",
        "04.symref",
        "-r",
        "05.symref",
        "-r",
        "06.symref",
        "-r",
        "07.symref",
        "-r",
        "08.symref",
        "-r",
        "09.symref",
        "-r",
        "10.symref",
        "-r",
        "11.symref",
        "-r",
        "12.symref",
        "-r",
        "13.symref",
        "-r",
        "14.symref",
        "-r",
        "15.symref",
        "-r",
        "16.symref",
        "-r",
        "17.symref",
        "--",
        "-r18.symref",
    };

    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 0), failure.version_count);
            try testing.expectEqual(genksyms.ParseFailure.too_many_reference_files, failure.reason);
        },
        else => return error.ExpectedReferenceLimitFailure,
    }
}
