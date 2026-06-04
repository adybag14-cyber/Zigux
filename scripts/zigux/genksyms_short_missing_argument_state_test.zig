const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "short required-argument failures keep earlier version side effects" {
    const missing_dump_types = [_][]const u8{"-VVT"};
    const dump_types_outcome = try genksyms.parseArgs(testing.allocator, &missing_dump_types);
    switch (dump_types_outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("T", option),
                else => return error.ExpectedMissingDumpTypesArgument,
            }
        },
        else => return error.ExpectedMissingDumpTypesFailure,
    }

    const missing_reference = [_][]const u8{"-VVr"};
    const reference_outcome = try genksyms.parseArgs(testing.allocator, &missing_reference);
    switch (reference_outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("r", option),
                else => return error.ExpectedMissingReferenceArgument,
            }
        },
        else => return error.ExpectedMissingReferenceFailure,
    }
}

test "attached short required-argument suffix is data after version flags" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VTr",
        "-d",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(request.dump_types_file != null);
                try testing.expectEqualStrings("r", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 2), request.rendered_args.len);
                try testing.expectEqualStrings("-VTr", request.rendered_args[0]);
                try testing.expectEqualStrings("-d", request.rendered_args[1]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestOutcome,
    }
}

test "attached short suffix bridge JSON preserves normalized request state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VTr",
        "--reference",
        "ref.sym",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("ref.sym", request.reference_files[0]);
                try testing.expectEqualStrings("r", request.dump_types_file.?);

                try testing.expectEqual(@as(usize, 3), request.rendered_args.len);
                try testing.expectEqualStrings("-VTr", request.rendered_args[0]);
                try testing.expectEqualStrings("--reference", request.rendered_args[1]);
                try testing.expectEqualStrings("ref.sym", request.rendered_args[2]);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expect(std.mem.containsAtLeast(
                    u8,
                    output.written(),
                    1,
                    "\"argv\":[\"scripts/genksyms/genksyms\",\"-VTr\",\"--reference\",\"ref.sym\"]",
                ));
                try testing.expect(std.mem.containsAtLeast(
                    u8,
                    output.written(),
                    1,
                    "\"reference_files\":[\"ref.sym\"],\"dump_types_file\":\"r\"",
                ));
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestOutcome,
    }
}
