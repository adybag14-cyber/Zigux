const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "short reference cluster before terminator keeps tail option lookalikes as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-drattached.symref",
        "before.c",
        "--",
        "--reference",
        "tail.symref",
        "-Ttail.types",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("attached.symref", request.reference_files[0]);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
                try testing.expectEqualStrings("-drattached.symref", request.rendered_args[0]);
                try testing.expectEqualStrings("before.c", request.rendered_args[1]);
                try testing.expectEqualStrings("--", request.rendered_args[2]);
                try testing.expectEqualStrings("--reference", request.rendered_args[3]);
                try testing.expectEqualStrings("tail.symref", request.rendered_args[4]);
                try testing.expectEqualStrings("-Ttail.types", request.rendered_args[5]);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();
                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-drattached.symref\",\"before.c\",\"--\",\"--reference\",\"tail.symref\",\"-Ttail.types\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"attached.symref\"],\"dump_types_file\":null}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "short dump-types cluster before terminator preserves version and warning state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VTinline.types",
        "--warnings",
        "--",
        "--quiet",
        "-r",
        "tail.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expectEqualStrings("inline.types", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
                try testing.expectEqualStrings("-VTinline.types", request.rendered_args[0]);
                try testing.expectEqualStrings("--warnings", request.rendered_args[1]);
                try testing.expectEqualStrings("--", request.rendered_args[2]);
                try testing.expectEqualStrings("--quiet", request.rendered_args[3]);
                try testing.expectEqualStrings("-r", request.rendered_args[4]);
                try testing.expectEqualStrings("tail.symref", request.rendered_args[5]);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();
                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-VTinline.types\",\"--warnings\",\"--\",\"--quiet\",\"-r\",\"tail.symref\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":\"inline.types\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
