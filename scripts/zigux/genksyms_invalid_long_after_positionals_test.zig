const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "unknown long option after delayed positional stays canonical invalid failure" {
    const args = [_][]const u8{
        "delayed.c",
        "--version",
        "--definitely-not-genksyms",
        "--reference",
        "unreached.symref",
    };

    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("--definitely-not-genksyms", option),
                else => return error.ExpectedInvalidLongOption,
            }
        },
        else => return error.ExpectedInvalidLongOptionFailure,
    }
}

test "unknown inline long option value after delayed positional stays in failure token" {
    const args = [_][]const u8{
        "delayed.c",
        "-V",
        "--not-a-real-option=value",
        "-d",
    };

    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("--not-a-real-option=value", option),
                else => return error.ExpectedInvalidLongOption,
            }
        },
        else => return error.ExpectedInvalidLongOptionFailure,
    }
}

test "unknown long-looking args after terminator stay positional data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "delayed.c",
        "--version",
        "--",
        "--definitely-not-genksyms",
        "--not-a-real-option=value",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqual(@as(usize, 5), request.rendered_args.len);
                try testing.expectEqualStrings("--version", request.rendered_args[0]);
                try testing.expectEqualStrings("delayed.c", request.rendered_args[1]);
                try testing.expectEqualStrings("--", request.rendered_args[2]);
                try testing.expectEqualStrings("--definitely-not-genksyms", request.rendered_args[3]);
                try testing.expectEqualStrings("--not-a-real-option=value", request.rendered_args[4]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "bridge JSON renders post-terminator invalid long-looking data" {
    const rendered_args = [_][]const u8{
        "--version",
        "delayed.c",
        "--",
        "--definitely-not-genksyms",
        "--not-a-real-option=value",
    };
    const request = genksyms.Request{
        .raw_args = &rendered_args,
        .rendered_args = &rendered_args,
        .version_count = 1,
    };

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"delayed.c\",\"--\",\"--definitely-not-genksyms\",\"--not-a-real-option=value\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
