const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "abbreviated warning toggles stop before explicit option terminator" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--warn",
        "left.c",
        "--qui",
        "--",
        "--warnings",
        "--quiet",
        "tail.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(!request.warnings);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
                try testing.expectEqualStrings("--warn", request.rendered_args[0]);
                try testing.expectEqualStrings("--qui", request.rendered_args[1]);
                try testing.expectEqualStrings("left.c", request.rendered_args[2]);
                try testing.expectEqualStrings("--", request.rendered_args[3]);
                try testing.expectEqualStrings("--warnings", request.rendered_args[4]);
                try testing.expectEqualStrings("--quiet", request.rendered_args[5]);
                try testing.expectEqualStrings("tail.c", request.rendered_args[6]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "abbreviated warning terminator request renders tail options as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--warn",
        "--ref",
        "base.symref",
        "unit.c",
        "--",
        "--qui",
        "--ref=tail.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("base.symref", request.reference_files[0]);
                try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
                try testing.expectEqualStrings("--warn", request.rendered_args[0]);
                try testing.expectEqualStrings("--ref", request.rendered_args[1]);
                try testing.expectEqualStrings("base.symref", request.rendered_args[2]);
                try testing.expectEqualStrings("unit.c", request.rendered_args[3]);
                try testing.expectEqualStrings("--", request.rendered_args[4]);
                try testing.expectEqualStrings("--qui", request.rendered_args[5]);
                try testing.expectEqualStrings("--ref=tail.symref", request.rendered_args[6]);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expect(std.mem.indexOf(u8, output.written(), "\"warnings\":true") != null);
                try testing.expect(std.mem.indexOf(u8, output.written(), "\"reference_files\":[\"base.symref\"]") != null);
                try testing.expect(std.mem.indexOf(u8, output.written(), "\"--qui\"") != null);
                try testing.expect(std.mem.indexOf(u8, output.written(), "\"--ref=tail.symref\"") != null);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
