const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "versioned short required clusters after delayed positionals stay request input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first-pos.c",
        "-VVrref-from-cluster.symref",
        "middle-pos.h",
        "-VTtypes-from-cluster.symtypes",
        "-d",
        "tail-pos.S",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 3), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("ref-from-cluster.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types-from-cluster.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);

                const expected_rendered_args = [_][]const u8{
                    "-VVrref-from-cluster.symref",
                    "-VTtypes-from-cluster.symtypes",
                    "-d",
                    "first-pos.c",
                    "middle-pos.h",
                    "tail-pos.S",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered_args, request.rendered_args);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-VVrref-from-cluster.symref\",\"-VTtypes-from-cluster.symtypes\",\"-d\",\"first-pos.c\",\"middle-pos.h\",\"tail-pos.S\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"ref-from-cluster.symref\"],\"dump_types_file\":\"types-from-cluster.symtypes\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "version side effects before short required cluster failures are preserved" {
    const args = [_][]const u8{
        "unit.c",
        "-VVr",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("r", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
