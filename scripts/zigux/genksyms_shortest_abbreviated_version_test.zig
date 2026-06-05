const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "shortest abbreviated version stays a pure version command" {
    const args = [_][]const u8{
        "--v",
        "--v",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .version => |version_count| try testing.expectEqual(@as(usize, 2), version_count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "shortest abbreviated version becomes side effect once request inputs appear" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--v",
        "--reference",
        "baseline.symref",
        "leftover.c",
        "--v",
        "--dump-types=types.symtypes",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("baseline.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
                try testing.expectEqualStrings("--v", request.rendered_args[0]);
                try testing.expectEqualStrings("--reference", request.rendered_args[1]);
                try testing.expectEqualStrings("baseline.symref", request.rendered_args[2]);
                try testing.expectEqualStrings("--v", request.rendered_args[3]);
                try testing.expectEqualStrings("--dump-types=types.symtypes", request.rendered_args[4]);
                try testing.expectEqualStrings("leftover.c", request.rendered_args[5]);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--v\",\"--reference\",\"baseline.symref\",\"--v\",\"--dump-types=types.symtypes\",\"leftover.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"baseline.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "shortest abbreviated version side effect survives later parse failure" {
    const args = [_][]const u8{
        "--v",
        "-x",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("x", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
