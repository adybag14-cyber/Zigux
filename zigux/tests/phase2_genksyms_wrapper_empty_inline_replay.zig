const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay preserves empty inline long required arguments" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference=",
        "--dump-types=",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 0), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("", request.reference_files[0]);
                try std.testing.expect(request.dump_types_file != null);
                try std.testing.expectEqualStrings("", request.dump_types_file.?);
                try std.testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay keeps empty inline payloads after version side effects and positional reordering" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--reference=",
        "leftover.c",
        "--dump-t=",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 1), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("", request.reference_files[0]);
                try std.testing.expect(request.dump_types_file != null);
                try std.testing.expectEqualStrings("", request.dump_types_file.?);
                try std.testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try std.testing.expectEqualStrings("--ver", request.rendered_args[0]);
                try std.testing.expectEqualStrings("--reference=", request.rendered_args[1]);
                try std.testing.expectEqualStrings("--dump-t=", request.rendered_args[2]);
                try std.testing.expectEqualStrings("--ver", request.raw_args[0]);
                try std.testing.expectEqualStrings("leftover.c", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay renders empty inline payloads in the invocation plan" {
    const rendered_args = [_][]const u8{
        "--reference=",
        "--dump-types=",
    };
    const reference_files = [_][]const u8{""};
    const request = genksyms.Request{
        .raw_args = &rendered_args,
        .rendered_args = &rendered_args,
        .reference_files = &reference_files,
        .dump_types_file = "",
    };

    var output: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference=\",\"--dump-types=\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"\"],\"dump_types_file\":\"\"}}\n",
        output.written(),
    );
}
