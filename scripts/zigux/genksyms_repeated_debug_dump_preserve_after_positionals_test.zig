const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "repeated debug dump and preserve after positionals accumulates state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.c",
        "--debug",
        "--deb",
        "-dDp",
        "--dump",
        "--preserve",
        "second.h",
        "-d",
        "--debug",
    };
    const expected_rendered = [_][]const u8{
        "--debug",
        "--deb",
        "-dDp",
        "--dump",
        "--preserve",
        "-d",
        "--debug",
        "first.c",
        "second.h",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 5), request.debug_level);
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expect(!request.warnings);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqual(@as(usize, 0), request.version_count);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "bridge output reflects repeated debug dump and preserve normalization" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "before.sym",
        "-d",
        "--dump",
        "--pres",
        "--debug",
        "-p",
        "-D",
        "after.sym",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.debug_level);
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-d\",\"--dump\",\"--pres\",\"--debug\",\"-p\",\"-D\",\"before.sym\",\"after.sym\"],\"options\":{\"debug_level\":2,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
