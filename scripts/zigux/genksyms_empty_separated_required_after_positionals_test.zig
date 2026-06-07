const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "short required options consume empty separated values after positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "unit.c",
        "-r",
        "",
        "--warnings",
        "-T",
        "",
        "tail.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("", request.reference_files[0]);
                try testing.expectEqualStrings("", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
                try testing.expectEqualStrings("-r", request.rendered_args[0]);
                try testing.expectEqualStrings("", request.rendered_args[1]);
                try testing.expectEqualStrings("--warnings", request.rendered_args[2]);
                try testing.expectEqualStrings("-T", request.rendered_args[3]);
                try testing.expectEqualStrings("", request.rendered_args[4]);
                try testing.expectEqualStrings("unit.c", request.rendered_args[5]);
                try testing.expectEqualStrings("tail.c", request.rendered_args[6]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "long required options consume empty separated values after positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "early.c",
        "--reference",
        "",
        "--dump-types",
        "",
        "--preserve",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("", request.reference_files[0]);
                try testing.expectEqualStrings("", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
                try testing.expectEqualStrings("--version", request.rendered_args[0]);
                try testing.expectEqualStrings("--reference", request.rendered_args[1]);
                try testing.expectEqualStrings("", request.rendered_args[2]);
                try testing.expectEqualStrings("--dump-types", request.rendered_args[3]);
                try testing.expectEqualStrings("", request.rendered_args[4]);
                try testing.expectEqualStrings("--preserve", request.rendered_args[5]);
                try testing.expectEqualStrings("early.c", request.rendered_args[6]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "abbreviated long required options preserve empty separated values in bridge json" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "delayed.c",
        "--ref",
        "",
        "--dump-t",
        "",
        "-d",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("", request.reference_files[0]);
                try testing.expectEqualStrings("", request.dump_types_file.?);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expect(std.mem.indexOf(u8, output.written(), "\"argv\":[\"scripts/genksyms/genksyms\",\"--ref\",\"\",\"--dump-t\",\"\",\"-d\",\"delayed.c\"]") != null);
                try testing.expect(std.mem.indexOf(u8, output.written(), "\"reference_files\":[\"\"]") != null);
                try testing.expect(std.mem.indexOf(u8, output.written(), "\"dump_types_file\":\"\"") != null);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
