const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "short state cluster after delayed positionals preserves request state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "early.c",
        "-DwqdpV",
        "late.h",
        "-V",
        "-d",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                const rendered = [_][]const u8{
                    "-DwqdpV",
                    "-V",
                    "-d",
                    "early.c",
                    "late.h",
                };

                try testing.expectEqual(@as(usize, 2), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "short state cluster after delayed positionals renders bridge json in normalized order" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "early.c",
        "-DwpV",
        "-q",
        "late.h",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-DwpV\",\"-q\",\"early.c\",\"late.h\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}

test "short state cluster failure after delayed positionals preserves version side effect" {
    const args = [_][]const u8{
        "early.c",
        "-VdqZ",
        "late.h",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("Z", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
